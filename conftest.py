"""Outils partagés des tests de labs : lancer l'outil de l'apprenant, lui
fabriquer des rapports, et lui servir une API OSV factice.

## Pourquoi `uv run`, et pas l'interpréteur des tests

`dsoxlab check` lance pytest dans SON environnement (voir
`dsoxlab/services/lab_service.py::resolve_pytest_cmd`), qui ne contient ni
`requests` ni `click`. L'outil de l'apprenant a ses propres dépendances,
déclarées dans le `pyproject.toml` de son projet : on le lance donc comme il
le lance lui-même, `uv run python security_check.py`, dans son répertoire.
Une dépendance oubliée y échoue exactement comme chez lui.

## Pourquoi des rapports générés

Un test qui lit toujours le même rapport attend toujours le même résultat, et
un outil qui imprime ce résultat en dur passerait. Les rapports de ces tests
sont tirés au hasard, avec une graine affichée en cas d'échec : le compte
attendu n'est connu qu'au moment du test.
"""

from __future__ import annotations

import contextlib
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import threading
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent
LABS_ROOT = REPO_ROOT / "labs"

# L'ordre d'affichage du résumé, du plus grave au moins grave. C'est aussi
# l'ordre des seuils de `--fail-on`.
SEVERITES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN")
OUTIL = "security_check.py"


def workdir_lab(fichier_test: str | Path) -> Path:
    """Le répertoire de travail du lab dont `fichier_test` est le test."""
    return Path(fichier_test).resolve().parent.parent / "work"


def exiger_workdir(workdir: Path, lab_id: str) -> None:
    if not workdir.is_dir():
        pytest.fail(
            f"Le répertoire de travail {workdir} n'existe pas. Lancez "
            f"`dsoxlab run {lab_id}` : il y pose le point de départ.",
            pytrace=False,
        )
    if not (workdir / OUTIL).is_file():
        pytest.fail(
            f"{OUTIL} est absent de {workdir}. C'est le fichier que le lab "
            "fait évoluer : il doit rester à la racine du projet.",
            pytrace=False,
        )


@dataclass
class Execution:
    code: int
    sortie: str
    erreurs: str
    commande: list[str]

    def resume(self) -> str:
        return (
            f"commande : {' '.join(self.commande)}\n  code de sortie : {self.code}\n"
            f"  sortie : {self.sortie.strip()[-600:] or '(vide)'}\n"
            f"  erreurs : {self.erreurs.strip()[-600:] or '(vide)'}"
        )


def lancer_outil(workdir: Path, *args: str, env: dict[str, str] | None = None,
                 timeout: int = 180) -> Execution:
    """`uv run python security_check.py ARGS`, dans le projet de l'apprenant.

    Les chemins passés en argument doivent être absolus : uv change de
    répertoire courant avant de lancer Python.
    """
    uv = shutil.which("uv")
    if uv is None:
        pytest.fail("uv est introuvable sur le PATH. Lancez `mise install` à la racine du catalogue.",
                    pytrace=False)
    cmd = [uv, "run", "--quiet", "--directory", str(workdir), "python", OUTIL, *args]
    environnement = dict(os.environ)
    # Le VIRTUAL_ENV de dsoxlab ne doit pas détourner uv de celui du projet.
    environnement.pop("VIRTUAL_ENV", None)
    environnement.update(env or {})
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                             env=environnement, check=False)
    except subprocess.TimeoutExpired:
        pytest.fail(f"{OUTIL} n'a pas rendu la main en {timeout} s : `{' '.join(cmd)}`. "
                    "Un appel réseau sans délai maximal attend indéfiniment.", pytrace=False)
    return Execution(res.returncode, res.stdout, res.stderr, cmd)


def lire_resume(sortie: str) -> dict[str, int]:
    """Les lignes `SEVERITE: n` et `TOTAL: n` de la sortie, en dictionnaire."""
    resume: dict[str, int] = {}
    for ligne in sortie.splitlines():
        cle, sep, valeur = ligne.partition(":")
        cle, valeur = cle.strip(), valeur.strip()
        if sep and cle in (*SEVERITES, "TOTAL") and valeur.isdigit():
            resume[cle] = int(valeur)
    return resume


def compter(severites: list[str]) -> dict[str, int]:
    """Le résumé attendu pour une liste de sévérités brutes."""
    attendu = dict.fromkeys(SEVERITES, 0)
    for brute in severites:
        s = (brute or "").upper()
        attendu[s if s in SEVERITES else "UNKNOWN"] += 1
    attendu["TOTAL"] = len(severites)
    return attendu


def tirage(graine: int | None = None) -> random.Random:
    # Des données de test, pas un secret : un générateur ordinaire suffit, et
    # sa graine se rejoue.
    return random.Random(graine if graine is not None else time.time_ns())  # noqa: S311


def findings_au_hasard(rnd: random.Random, n: int | None = None) -> list[dict]:
    """Un export de findings plausible, au format du lab 1."""
    paquets = ["requests", "urllib3", "jinja2", "pyyaml", "flask", "cryptography", "django"]
    poids = {"CRITICAL": 1, "HIGH": 3, "MEDIUM": 4, "LOW": 2, "UNKNOWN": 1}
    n = rnd.randint(4, 30) if n is None else n
    out = []
    for i in range(n):
        sev = rnd.choices(list(poids), weights=list(poids.values()))[0]
        # Des casses variées : un export réel n'est pas toujours normalisé.
        sev = rnd.choice([sev, sev.lower(), sev.capitalize()])
        out.append({
            "id": f"CVE-2026-{rnd.randint(10000, 99999)}-{i}",
            "package": rnd.choice(paquets),
            "version": f"{rnd.randint(0, 5)}.{rnd.randint(0, 30)}.{rnd.randint(0, 9)}",
            "severity": sev,
        })
    return out


def ecrire_json(chemin: Path, donnees: object) -> Path:
    chemin.write_text(json.dumps(donnees, indent=2), encoding="utf-8")
    return chemin


# --- API OSV factice -----------------------------------------------------------


@dataclass
class ServeurOSV:
    """Un serveur HTTP local qui répond comme `POST /v1/query` d'OSV.

    `reponses` associe un nom de paquet aux vulnérabilités à rendre : une
    liste d'identifiants, ou un dictionnaire identifiant -> sévérité, rendue
    comme OSV la porte pour les avis GitHub (`database_specific.severity`,
    `MODERATE` compris) ; une sévérité `None` n'en porte aucune, comme les
    avis PYSEC ; `requetes` garde chaque corps reçu, pour vérifier
    ce que l'outil a VRAIMENT demandé. `statut` et `delai` simulent une panne.
    """

    reponses: dict[str, list[str] | dict[str, str | None]] = field(default_factory=dict)
    requetes: list[dict] = field(default_factory=list)
    statut: int = 200
    delai: float = 0.0
    url: str = ""


@pytest.fixture
def serveur_osv() -> Iterator[ServeurOSV]:
    etat = ServeurOSV()

    class Gestionnaire(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            longueur = int(self.headers.get("Content-Length") or 0)
            brut = self.rfile.read(longueur)
            try:
                corps = json.loads(brut or b"{}")
            except json.JSONDecodeError:
                corps = {"_illisible": brut.decode(errors="replace")}
            etat.requetes.append({"chemin": self.path, "corps": corps})
            if etat.delai:
                time.sleep(etat.delai)
            if etat.statut != 200:
                self.send_response(etat.statut)
                self.end_headers()
                self.wfile.write(b'{"code":13,"message":"internal error"}')
                return
            nom = ((corps.get("package") or {}).get("name") or "") if isinstance(corps, dict) else ""
            connues = etat.reponses.get(nom, [])
            if not isinstance(connues, dict):
                connues = dict.fromkeys(connues)
            vulns = []
            for ident, gravite in connues.items():
                vuln = {"id": ident, "summary": f"Vulnerability {ident}", "aliases": []}
                if gravite is not None:
                    vuln["database_specific"] = {"severity": gravite}
                vulns.append(vuln)
            charge = json.dumps({"vulns": vulns} if vulns else {}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(charge)))
            self.end_headers()
            self.wfile.write(charge)

        def log_message(self, *args: object) -> None:  # silence
            return

    serveur = ThreadingHTTPServer(("127.0.0.1", 0), Gestionnaire)
    serveur.daemon_threads = True
    etat.url = f"http://127.0.0.1:{serveur.server_address[1]}"
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    try:
        yield etat
    finally:
        serveur.shutdown()
        serveur.server_close()


# --- Jouer un workflow avec act (lab automatisation-dans-la-ci) ---------------
#
# Repris de github-actions-training/conftest.py, éprouvé là-bas sur act 0.2.89
# et l'image du runner épinglée par digest. Seul le dernier lab du fil rouge
# s'en sert : c'est le seul qui demande Docker. Toute évolution se fait d'abord
# dans le catalogue GitHub Actions, puis se reporte ici.

LABEL_RUNNER = "ubuntu-24.04"
IMAGE_RUNNER = (
    "catthehacker/ubuntu:act-24.04"
    "@sha256:c58e2b364da03b0c804c7d660f2ecbedf2f221a382b9baa0b344b0144780ff43"
)


_images_verifiees: set[str] = set()


def exiger_outil(nom: str) -> str:
    """Le chemin de l'outil, ou un échec qui dit comment l'installer."""
    chemin = shutil.which(nom)
    if not chemin:
        pytest.fail(
            f"L'outil `{nom}` n'est pas sur le PATH. Il est épinglé dans "
            "mise.toml à la racine du catalogue : lancez `mise install`, puis "
            "rejouez `dsoxlab check`."
        )
    return chemin


def executer(
    cmd: list[str],
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 300,
    entree: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Lance une commande et rend le résultat sans lever : c'est le test qui juge."""
    environnement = dict(os.environ)
    if env:
        environnement.update(env)
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            env=environnement,
            capture_output=True,
            text=True,
            timeout=timeout,
            input=entree,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        sortie = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        return subprocess.CompletedProcess(cmd, 124, stdout=sortie, stderr=f"délai de {timeout} s dépassé")


# Ce qu'on ne copie jamais d'un répertoire de travail : le dépôt git de
# l'apprenant (act en reçoit un neuf), les caches Python et pytest.
EXCLUS_COPIE = (".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache")


@contextlib.contextmanager
def copie_temporaire(depot: Path) -> Iterator[Path]:
    """Une copie du répertoire de travail, à modifier ou à jouer, détruite à la sortie."""
    with tempfile.TemporaryDirectory(prefix="lab-gha-") as tmp:
        cible = Path(tmp) / "depot"
        shutil.copytree(depot, cible, ignore=shutil.ignore_patterns(*EXCLUS_COPIE), symlinks=True)
        yield cible


def _git(*args: str, cwd: Path) -> None:
    cmd = [
        "git",
        "-c", "user.name=lab",
        "-c", "user.email=lab@example.invalid",
        "-c", "commit.gpgsign=false",
        "-c", "init.defaultBranch=main",
        *args,
    ]
    res = executer(cmd, cwd=cwd, timeout=60)
    if res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} a échoué : {res.stderr.strip()}")


def initialiser_git(depot: Path) -> None:
    """act déduit le contexte (ref, sha, dépôt) d'un dépôt git : on lui en donne un neuf."""
    _git("init", "-q", "-b", "main", cwd=depot)
    _git("add", "-A", cwd=depot)
    _git("commit", "-q", "--allow-empty", "-m", "point de depart", cwd=depot)


def image_prete() -> None:
    """L'image du runner est présente, sinon on la tire une fois, par digest."""
    if IMAGE_RUNNER in _images_verifiees:
        return
    if executer(["docker", "image", "inspect", IMAGE_RUNNER], timeout=60).returncode != 0:
        res = executer(["docker", "pull", IMAGE_RUNNER], timeout=900)
        if res.returncode != 0:
            pytest.fail(
                f"Impossible de tirer l'image du runner {IMAGE_RUNNER} : "
                f"{res.stderr.strip()[-400:]}. Docker doit répondre (`docker info`) ; "
                "act ne joue rien sans lui."
            )
    _images_verifiees.add(IMAGE_RUNNER)


# ── act ──────────────────────────────────────────────────────────────────────


@dataclass
class ResultatAct:
    """Ce qu'act a produit, lu depuis sa sortie `--json`."""

    commande: list[str]
    rc: int
    jobs: dict[str, list[str]] = field(default_factory=dict)  # jobID -> résultats
    lignes: list[str] = field(default_factory=list)  # tout ce que les steps ont écrit
    lignes_par_job: dict[str, list[str]] = field(default_factory=dict)
    steps: list[dict[str, str | None]] = field(default_factory=list)
    erreurs: list[str] = field(default_factory=list)
    brut: str = ""

    def job(self, identifiant: str) -> str | None:
        """Le résultat d'un job : `success`, `failure`, ou `None` s'il n'a pas été joué."""
        resultats = self.jobs.get(identifiant) or []
        if not resultats:
            return None
        if len(resultats) == 1:
            return resultats[0]
        # Une matrice produit plusieurs jobs sous le même identifiant : on rend
        # `failure` dès qu'un seul a échoué, c'est ce que GitHub affiche.
        return "failure" if "failure" in resultats else resultats[0]

    @property
    def sortie(self) -> str:
        return "\n".join(self.lignes)

    def contient(self, texte: str) -> bool:
        return texte in self.brut

    def resume(self, n: int = 12) -> str:
        """Un extrait pour les messages d'assertion : jobs, erreurs, dernières lignes."""
        parts = [f"commande : {' '.join(self.commande)}", f"code de retour : {self.rc}"]
        if self.jobs:
            etats = ", ".join(f"{j}={'/'.join(r)}" for j, r in sorted(self.jobs.items()))
            parts.append(f"jobs : {etats}")
        else:
            parts.append("jobs : aucun job n'a été joué")
        if self.erreurs:
            parts.append("erreurs d'act :\n    " + "\n    ".join(e.strip() for e in self.erreurs[-4:]))
        if self.lignes:
            parts.append("dernières lignes écrites :\n    " + "\n    ".join(self.lignes[-n:]))
        return "\n  ".join(parts)


def jouer_act(
    depot: Path,
    evenement: str = "push",
    *,
    workflow: str | None = None,
    job: str | None = None,
    payload: dict | None = None,
    timeout: int = 600,
) -> ResultatAct:
    """Joue un workflow avec act dans une copie neuve du répertoire de travail.

    `workflow` est un chemin relatif au dépôt (`.github/workflows/ci.yml`),
    `job` un identifiant de job, `payload` le corps de l'événement (`-e`).

    Contrairement à github-actions-training, aucun secret ni variable : le
    workflow de ce catalogue n'en lit pas, et écrire des secrets dans un
    fichier, même en 0600, est ce que CodeQL signale à raison
    (py/clear-text-storage-sensitive-data, PR #2).
    """
    exiger_outil("act")
    image_prete()
    with copie_temporaire(depot) as d:
        initialiser_git(d)
        aux = d.parent
        cmd = [
            "act", evenement, "--json", "--pull=false",
            "-P", f"{LABEL_RUNNER}={IMAGE_RUNNER}",
            "--artifact-server-path", str(aux / "artefacts"),
            "--cache-server-path", str(aux / "cache"),
        ]
        if workflow:
            cmd += ["-W", workflow]
        if job:
            cmd += ["-j", job]
        if payload is not None:
            (aux / "event.json").write_text(json.dumps(payload), encoding="utf-8")
            cmd += ["-e", str(aux / "event.json")]
        res = executer(cmd, cwd=d, env={"ACT_DISABLE_VERSION_CHECK": "1"}, timeout=timeout)
        brut = res.stdout + res.stderr
    return _lire_json_act(cmd, res.returncode, brut)


def _lire_json_act(cmd: list[str], rc: int, brut: str) -> ResultatAct:
    res = ResultatAct(commande=cmd, rc=rc, brut=brut)
    for ligne in brut.splitlines():
        try:
            obj = json.loads(ligne)
        except ValueError:
            continue
        if not isinstance(obj, dict):
            continue
        msg = str(obj.get("msg", ""))
        job_id = obj.get("jobID") or obj.get("job") or "?"
        if obj.get("raw_output"):
            for ecrite in msg.split("\n"):
                if ecrite == "" and msg.endswith("\n"):
                    continue
                res.lignes.append(ecrite)
                res.lignes_par_job.setdefault(job_id, []).append(ecrite)
        if obj.get("jobResult"):
            res.jobs.setdefault(job_id, []).append(str(obj["jobResult"]))
        if obj.get("stepResult"):
            res.steps.append({"job": job_id, "step": obj.get("step"), "resultat": str(obj["stepResult"])})
        if obj.get("level") == "error":
            res.erreurs.append(msg)
    if rc != 0 and not res.erreurs and not res.jobs:
        # act a refusé avant de jouer (workflow invalide, aucun job) : la
        # raison est dans la sortie brute.
        res.erreurs.append(brut.strip()[-600:])
    return res


# ── Lecture statique des workflows (compléments) ────────────────────────────


def fichiers_workflows(depot: Path) -> list[Path]:
    dossier = depot / ".github" / "workflows"
    if not dossier.is_dir():
        return []
    return sorted(p for p in dossier.iterdir() if p.suffix in (".yml", ".yaml"))


def exiger_workflows(depot: Path) -> list[Path]:
    fichiers = fichiers_workflows(depot)
    if not fichiers:
        pytest.fail(
            "Aucun fichier `.github/workflows/*.yml` dans le répertoire de travail : "
            "GitHub ne cherche les workflows que dans ce dossier, avec le point devant "
            "`.github` et l'extension .yml ou .yaml. Rien ne peut tourner tant qu'il "
            "n'existe pas."
        )
    return fichiers


def lire_workflows(depot: Path) -> dict[str, dict]:
    """Chaque workflow, analysé. Un YAML invalide est un échec qui nomme le fichier."""
    resultat: dict[str, dict] = {}
    for fichier in exiger_workflows(depot):
        try:
            donnees = yaml.safe_load(fichier.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            pytest.fail(
                f"{fichier.relative_to(depot)} n'est pas un YAML valide : {exc}. "
                "GitHub l'ignorerait, avec une erreur dans l'onglet Actions."
            )
        if not isinstance(donnees, dict):
            pytest.fail(f"{fichier.relative_to(depot)} ne contient pas un workflow (dictionnaire attendu).")
        resultat[str(fichier.relative_to(depot))] = donnees
    return resultat


def declencheurs(workflow: dict) -> set[str]:
    """Les événements d'un workflow. PyYAML lit la clé `on` comme le booléen True."""
    valeur = workflow.get("on", workflow.get(True))
    if valeur is None:
        return set()
    if isinstance(valeur, str):
        return {valeur}
    if isinstance(valeur, list):
        return {str(v) for v in valeur}
    if isinstance(valeur, dict):
        return {str(k) for k in valeur}
    return set()


@dataclass(frozen=True)
class ReferenceUses:
    fichier: str
    ligne: int
    action: str  # owner/repo ou owner/repo/chemin
    ref: str | None  # ce qui suit le @
    commentaire: str | None  # ce qui suit le #

    @property
    def locale(self) -> bool:
        return self.action.startswith("./") or self.action.startswith("docker://")

    @property
    def epinglee_par_sha(self) -> bool:
        return bool(self.ref) and re.fullmatch(r"[0-9a-f]{40}", self.ref or "") is not None


_RE_USES = re.compile(r"^\s*-?\s*uses:\s*['\"]?([^\s'\"#]+)['\"]?\s*(?:#\s*(.*?)\s*)?$")


def references_uses(depot: Path) -> list[ReferenceUses]:
    """Chaque `uses:` des workflows, lu dans le texte pour garder le commentaire."""
    refs: list[ReferenceUses] = []
    for fichier in fichiers_workflows(depot):
        for numero, texte in enumerate(fichier.read_text(encoding="utf-8").splitlines(), 1):
            m = _RE_USES.match(texte)
            if not m:
                continue
            cible, commentaire = m.group(1), m.group(2)
            action, _, ref = cible.partition("@")
            refs.append(
                ReferenceUses(
                    fichier=str(fichier.relative_to(depot)),
                    ligne=numero,
                    action=action,
                    ref=ref or None,
                    commentaire=commentaire or None,
                )
            )
    return refs
