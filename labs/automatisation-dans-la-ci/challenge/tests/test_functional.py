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
    message,
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
            message(
            en="No workflow in `.github/workflows/`: GitHub only looks for "
            "workflows there, with the dot in front of `.github`. Nothing can "
            "run as long as it does not exist.",
            fr="Aucun workflow dans `.github/workflows/` : GitHub ne cherche les "
            "workflows que là, avec le point devant `.github`. Rien ne peut "
            "tourner tant qu'il n'existe pas.",
        ),
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
    assert resultat.jobs, message(
        en="act ran no job: either no workflow declares this event in its `on:`, "
        "or the file is invalid.\n  " + resultat.resume(),
        fr="act n'a joué aucun job : soit aucun workflow ne déclare cet événement "
        "dans son `on:`, soit le fichier est invalide.\n  " + resultat.resume(),
    )
    assert len(resultat.jobs) == 1, message(
        en="A single job is expected, which tests the tool and then applies the "
        "threshold: the order of the steps is what guarantees a broken tool "
        "decides nothing.\n  "
        + resultat.resume(),
        fr="Un seul job est attendu, qui teste l'outil puis applique le seuil : "
        "l'ordre des étapes est la garantie qu'un outil cassé ne décide de rien.\n  "
        + resultat.resume(),
    )
    return next(iter(resultat.jobs))


def test_un_rapport_propre_laisse_passer(projet: Path) -> None:
    res = _jouer(projet, severites=[])
    job = _job_unique(res)
    assert res.job(job) == "success", message(
        en="On a report with no vulnerability, the gate must let it through.\n  " + res.resume(),
        fr="Sur un rapport sans vulnérabilité, la porte doit laisser passer.\n  " + res.resume(),
    )
    assert any("TOTAL: 0" in ligne for ligne in res.lignes), message(
        en="The job is green, but the tool did not summarise the report: it must "
        "read `rapports/trivy.json`, the one the scanner writes.\n  " + res.resume(),
        fr="Le job est vert, mais l'outil n'a pas résumé le rapport : il doit "
        "lire `rapports/trivy.json`, celui que le scanner dépose.\n  " + res.resume(),
    )
    assert any(" passed" in ligne for ligne in res.lignes), message(
        en="The tool's own tests (`tests/`) do not run in the pipeline. They "
        "come before the threshold: a broken tool must decide nothing.\n  " + res.resume(),
        fr="Les tests de l'outil (`tests/`) ne tournent pas dans le pipeline. "
        "Ils passent avant le seuil : un outil cassé ne doit rien décider.\n  " + res.resume(),
    )


def test_un_critique_arrete_le_pipeline(projet: Path) -> None:
    """Le rapport livré : 2 CRITICAL, sortie réelle de Trivy."""
    res = _jouer(projet)
    job = _job_unique(res)
    assert res.job(job) == "failure", message(
        en="The provided report carries two CRITICAL vulnerabilities: the job "
        "must fail. Is the threshold passed to the tool "
        "(`--fail-on CRITICAL`)?\n  " + res.resume(),
        fr="Le rapport livré porte deux vulnérabilités CRITICAL : le job doit "
        "échouer. Le seuil est-il passé à l'outil (`--fail-on CRITICAL`) ?\n  " + res.resume(),
    )
    assert any(ligne.startswith("FAILED:") for ligne in res.lignes), message(
        en="The job fails, but not on the threshold: the tool did not write its "
        "`FAILED: ...` line. A job red for another reason is not a gate.\n  "
        + res.resume(),
        fr="Le job échoue, mais pas sur le seuil : l'outil n'a pas écrit sa ligne "
        "`FAILED: ...`. Un job rouge pour une autre raison n'est pas une porte.\n  "
        + res.resume(),
    )


def test_le_seuil_est_critical_et_pas_plus_bas(projet: Path) -> None:
    res = _jouer(projet, severites=["HIGH", "HIGH", "MEDIUM"])
    job = _job_unique(res)
    assert res.job(job) == "success", message(
        en="A report with no CRITICAL (two HIGH and one MEDIUM) must pass: the "
        "gate asked for blocks at the CRITICAL threshold, not before.\n  " + res.resume(),
        fr="Un rapport sans CRITICAL (deux HIGH et un MEDIUM) doit passer : la "
        "porte demandée bloque au seuil CRITICAL, pas avant.\n  " + res.resume(),
    )


def test_un_outil_casse_ne_decide_de_rien(projet: Path) -> None:
    """L'outil remplacé par une version au seuil exclusif : ses tests doivent arrêter le job."""
    res = _jouer(projet, severites=[], outil=OUTIL_CASSE)
    job = _job_unique(res)
    assert res.job(job) == "failure", message(
        en="With a broken tool (an exclusive threshold), the pipeline must stop "
        "on its tests. The job is green: the tests do not run, or do not run "
        "before the threshold.\n  " + res.resume(),
        fr="Avec un outil cassé (seuil exclusif), le pipeline doit s'arrêter sur "
        "ses tests. Le job est vert : les tests ne tournent pas, ou pas avant "
        "le seuil.\n  " + res.resume(),
    )
    assert not any(ligne.startswith("TOTAL:") for ligne in res.lignes), message(
        en="The broken tool still summarised the report: the threshold applies "
        "before, or in spite of, the tests failing. The tests come first, "
        "and a failed step stops the ones after it.\n  " + res.resume(),
        fr="L'outil cassé a quand même résumé le rapport : le seuil s'applique "
        "avant ou malgré l'échec des tests. Les tests passent d'abord, et un "
        "step en échec arrête les suivants.\n  " + res.resume(),
    )


def test_les_pull_requests_passent_la_porte_avec_des_droits_minimaux(projet: Path) -> None:
    res = _jouer(projet, severites=[], evenement="pull_request")
    job = _job_unique(res)
    assert res.job(job) == "success", message(
        en="The gate must also run on every pull request, before the merge.\n  " + res.resume(),
        fr="La porte doit aussi tourner sur chaque pull request, avant la fusion.\n  " + res.resume(),
    )
    for chemin, wf in lire_workflows(projet).items():
        if not {"push", "pull_request"} & declencheurs(wf):
            continue
        droits = wf.get("permissions")
        assert droits == {"contents": "read"}, message(
            en=f"{chemin}: `permissions:` is {droits!r}. The job reads the code and "
            "nothing else: `contents: read`, at workflow level. A missing "
            "block leaves the repository's default rights.",
            fr=f"{chemin} : `permissions:` vaut {droits!r}. Le job lit le code et "
            "rien d'autre : `contents: read`, au niveau du workflow. Un bloc "
            "absent laisse les droits par défaut du dépôt.",
        )
    non_epinglees = [f"{r.fichier}:{r.ligne} {r.action}@{r.ref}" for r in references_uses(projet)
                     if not r.locale and not r.epinglee_par_sha]
    assert not non_epinglees, message(
        en="Every action is pinned to the full SHA of its commit, with the "
        "version in a comment: " + ", ".join(non_epinglees),
        fr="Chaque action s'épingle sur le SHA complet de son commit, version en "
        "commentaire : " + ", ".join(non_epinglees),
    )
