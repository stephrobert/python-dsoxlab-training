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

import json
import os
import random
import shutil
import subprocess
import threading
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

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
    for s in severites:
        s = (s or "").upper()
        attendu[s if s in SEVERITES else "UNKNOWN"] += 1
    attendu["TOTAL"] = len(severites)
    return attendu


def tirage(graine: int | None = None) -> random.Random:
    return random.Random(graine if graine is not None else time.time_ns())


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

    `reponses` associe un nom de paquet à la liste des identifiants de
    vulnérabilités à rendre ; `requetes` garde chaque corps reçu, pour vérifier
    ce que l'outil a VRAIMENT demandé. `statut` et `delai` simulent une panne.
    """

    reponses: dict[str, list[str]] = field(default_factory=dict)
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
            vulns = [{"id": i, "summary": f"Vulnerability {i}", "aliases": []}
                     for i in etat.reponses.get(nom, [])]
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
