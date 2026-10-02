"""La porte de sécurité dans le pipeline : cinq contrôles, vingt points chacun.

## Ce que ces tests lisent

Ce qu'act PRODUIT en jouant le workflow de l'apprenant, dans l'image du runner
épinglée par digest : le résultat du job et les lignes écrites par chaque
step. Le dernier contrôle relit aussi le YAML, parce que « ne demander que le
droit de lire » et « épingler par SHA » sont des propriétés du texte.

## Chaque passage se fait sur une copie

Le rapport du scanner (`rapports/trivy.json`) et l'outil lui-même sont
remplacés dans une COPIE du projet : un rapport propre, un rapport sans
CRITICAL, un outil cassé. Le pipeline doit réagir à chacun comme une vraie
porte, et le projet de l'apprenant n'est jamais touché.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from conftest import (
    copie_temporaire,
    declencheurs,
    ecrire_json,
    exiger_workdir,
    jouer_act,
    lire_workflows,
    references_uses,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "automatisation-dans-la-ci"
OUTIL_CASSE = Path(__file__).resolve().parent / "donnees" / "outil_seuil_exclusif.py"
RAPPORT = Path("rapports") / "trivy.json"


@pytest.fixture(scope="module")
def projet() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    if not (WORKDIR / ".github" / "workflows").is_dir():
        pytest.fail(
            "Aucun workflow dans `.github/workflows/` : GitHub ne cherche les "
            "workflows que là, avec le point devant `.github`. Rien ne peut "
            "tourner tant qu'il n'existe pas.",
            pytrace=False,
        )
    return WORKDIR


def _rapport_trivy(severites: list[str]) -> dict:
    return {"SchemaVersion": 2, "Results": [{"Target": "requirements.txt", "Vulnerabilities": [
        {"VulnerabilityID": f"CVE-2026-{1000 + i}", "PkgName": "paquet", "InstalledVersion": "1.0.0",
         "Severity": s} for i, s in enumerate(severites)]}] if severites else [{"Target": "requirements.txt"}]}


def _jouer(projet: Path, severites: list[str] | None = None, outil: Path | None = None,
           evenement: str = "push"):
    """Joue le workflow sur une copie où le rapport et l'outil peuvent être remplacés."""
    with copie_temporaire(projet) as copie:
        if severites is not None:
            ecrire_json(copie / RAPPORT, _rapport_trivy(severites))
        if outil is not None:
            shutil.copy2(outil, copie / "security_check.py")
        return jouer_act(copie, evenement)


def _job_unique(resultat) -> str:
    assert resultat.jobs, (
        "act n'a joué aucun job : soit aucun workflow ne déclare cet événement "
        "dans son `on:`, soit le fichier est invalide.\n  " + resultat.resume()
    )
    assert len(resultat.jobs) == 1, (
        "Un seul job est attendu, qui teste l'outil puis applique le seuil : "
        "l'ordre des étapes est la garantie qu'un outil cassé ne décide de rien.\n  "
        + resultat.resume()
    )
    return next(iter(resultat.jobs))


def test_un_rapport_propre_laisse_passer(projet: Path) -> None:
    res = _jouer(projet, severites=[])
    job = _job_unique(res)
    assert res.job(job) == "success", (
        "Sur un rapport sans vulnérabilité, la porte doit laisser passer.\n  " + res.resume()
    )
    assert any("TOTAL: 0" in ligne for ligne in res.lignes), (
        "Le job est vert, mais l'outil n'a pas résumé le rapport : il doit "
        "lire `rapports/trivy.json`, celui que le scanner dépose.\n  " + res.resume()
    )
    assert any(" passed" in ligne for ligne in res.lignes), (
        "Les tests de l'outil (`tests/`) ne tournent pas dans le pipeline. "
        "Ils passent avant le seuil : un outil cassé ne doit rien décider.\n  " + res.resume()
    )


def test_un_critique_arrete_le_pipeline(projet: Path) -> None:
    """Le rapport livré : 2 CRITICAL, sortie réelle de Trivy."""
    res = _jouer(projet)
    job = _job_unique(res)
    assert res.job(job) == "failure", (
        "Le rapport livré porte deux vulnérabilités CRITICAL : le job doit "
        "échouer. Le seuil est-il passé à l'outil (`--fail-on CRITICAL`) ?\n  " + res.resume()
    )
    assert any(ligne.startswith("FAILED:") for ligne in res.lignes), (
        "Le job échoue, mais pas sur le seuil : l'outil n'a pas écrit sa ligne "
        "`FAILED: ...`. Un job rouge pour une autre raison n'est pas une porte.\n  "
        + res.resume()
    )


def test_le_seuil_est_critical_et_pas_plus_bas(projet: Path) -> None:
    res = _jouer(projet, severites=["HIGH", "HIGH", "MEDIUM"])
    job = _job_unique(res)
    assert res.job(job) == "success", (
        "Un rapport sans CRITICAL (deux HIGH et un MEDIUM) doit passer : la "
        "porte demandée bloque au seuil CRITICAL, pas avant.\n  " + res.resume()
    )


def test_un_outil_casse_ne_decide_de_rien(projet: Path) -> None:
    """L'outil remplacé par une version au seuil exclusif : ses tests doivent arrêter le job."""
    res = _jouer(projet, severites=[], outil=OUTIL_CASSE)
    job = _job_unique(res)
    assert res.job(job) == "failure", (
        "Avec un outil cassé (seuil exclusif), le pipeline doit s'arrêter sur "
        "ses tests. Le job est vert : les tests ne tournent pas, ou pas avant "
        "le seuil.\n  " + res.resume()
    )
    assert not any(ligne.startswith("TOTAL:") for ligne in res.lignes), (
        "L'outil cassé a quand même résumé le rapport : le seuil s'applique "
        "avant ou malgré l'échec des tests. Les tests passent d'abord, et un "
        "step en échec arrête les suivants.\n  " + res.resume()
    )


def test_les_pull_requests_passent_la_porte_avec_des_droits_minimaux(projet: Path) -> None:
    res = _jouer(projet, severites=[], evenement="pull_request")
    job = _job_unique(res)
    assert res.job(job) == "success", (
        "La porte doit aussi tourner sur chaque pull request, avant la fusion.\n  " + res.resume()
    )
    for chemin, wf in lire_workflows(projet).items():
        if not {"push", "pull_request"} & declencheurs(wf):
            continue
        droits = wf.get("permissions")
        assert droits == {"contents": "read"}, (
            f"{chemin} : `permissions:` vaut {droits!r}. Le job lit le code et "
            "rien d'autre : `contents: read`, au niveau du workflow. Un bloc "
            "absent laisse les droits par défaut du dépôt."
        )
    non_epinglees = [f"{r.fichier}:{r.ligne} {r.action}@{r.ref}" for r in references_uses(projet)
                     if not r.locale and not r.epinglee_par_sha]
    assert not non_epinglees, (
        "Chaque action s'épingle sur le SHA complet de son commit, version en "
        "commentaire : " + ", ".join(non_epinglees)
    )
