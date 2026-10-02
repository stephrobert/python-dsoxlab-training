"""Lire un rapport : cinq contrôles, vingt points chacun.

## Ce que ces tests lisent

Ce que l'outil AFFICHE et le code qu'il REND, lancé comme l'apprenant le lance
(`uv run python security_check.py`). Jamais le code source : l'apprenant
arrive au résultat par le chemin qu'il veut.

## Pourquoi des rapports tirés au hasard

Le rapport d'exemple livré avec le lab a un résultat connu ; un outil qui
l'imprime en dur passerait un test qui ne lirait que lui. Chaque test écrit
donc ses propres rapports, et la graine du tirage figure dans le message
d'échec pour rejouer le cas.

## Les deux derniers contrôles disent ce qu'on attend d'un outil de pipeline

Un fichier absent ou un JSON cassé ne sont pas des pannes de l'outil, mais
des entrées invalides : il les dit en une ligne, sur la sortie d'erreur, et
sort en 2. Une trace Python de quinze lignes dans le journal d'un job n'aide
personne, et un code 1 se confondrait avec « des vulnérabilités ont été
trouvées », ce que le lab 4 lui fera dire.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import (
    compter,
    ecrire_json,
    exiger_workdir,
    findings_au_hasard,
    lancer_outil,
    lire_resume,
    tirage,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "automatisation-lire-un-rapport"


@pytest.fixture(scope="module")
def projet() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    return WORKDIR


def _exiger_resume(execution, attendu: dict[str, int], contexte: str) -> None:
    assert execution.code == 0, (
        f"{contexte} : l'outil devait réussir (code 0).\n  {execution.resume()}"
    )
    obtenu = lire_resume(execution.sortie)
    assert obtenu == attendu, (
        f"{contexte} : le résumé ne correspond pas au rapport.\n"
        f"  attendu : {attendu}\n  obtenu  : {obtenu}\n\n"
        "Une ligne par sévérité, dans l'ordre CRITICAL, HIGH, MEDIUM, LOW, "
        "UNKNOWN, au format `CRITICAL: 2`, puis `TOTAL: n`.\n"
        f"  {execution.resume()}"
    )


def test_le_resume_compte_chaque_severite(projet: Path, tmp_path: Path) -> None:
    """Deux rapports tirés au hasard : chaque compte doit suivre le contenu."""
    for graine in (tirage().randint(0, 10**6), tirage().randint(0, 10**6)):
        findings = findings_au_hasard(tirage(graine))
        # Ce contrôle-ci ne porte que sur des sévérités connues.
        for f in findings:
            if f["severity"].upper() == "UNKNOWN":
                f["severity"] = "LOW"
        rapport = ecrire_json(tmp_path / f"rapport-{graine}.json", findings)
        _exiger_resume(lancer_outil(projet, str(rapport)),
                       compter([f["severity"] for f in findings]),
                       f"rapport tiré avec la graine {graine}")


def test_les_severites_inconnues_ou_absentes_comptent_en_unknown(projet: Path, tmp_path: Path) -> None:
    """Casse variée, sévérité absente, vide, nulle ou hors liste."""
    findings = [
        {"id": "A", "severity": "critical"},
        {"id": "B", "severity": "High"},
        {"id": "C"},
        {"id": "D", "severity": ""},
        {"id": "E", "severity": None},
        {"id": "F", "severity": "SEVERE"},
        {"id": "G", "severity": "medium"},
    ]
    rapport = ecrire_json(tmp_path / "casse.json", findings)
    attendu = {"CRITICAL": 1, "HIGH": 1, "MEDIUM": 1, "LOW": 0, "UNKNOWN": 4, "TOTAL": 7}
    _exiger_resume(lancer_outil(projet, str(rapport)), attendu,
                   "sévérités en minuscules, absentes, vides, nulles ou inconnues")


def test_un_rapport_vide_rend_des_zeros(projet: Path, tmp_path: Path) -> None:
    """Un scan propre n'est pas une erreur : six lignes à zéro, code 0."""
    rapport = ecrire_json(tmp_path / "vide.json", [])
    attendu = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0, "TOTAL": 0}
    _exiger_resume(lancer_outil(projet, str(rapport)), attendu, "rapport vide `[]`")


def _exiger_refus_propre(execution, nom: str, cas: str) -> None:
    assert execution.code == 2, (
        f"{cas} : l'outil doit sortir en 2, le code des entrées invalides.\n"
        f"  {execution.resume()}"
    )
    assert "Traceback" not in execution.erreurs, (
        f"{cas} : l'outil laisse remonter une trace Python. Attrapez l'exception "
        "et dites le problème en une ligne, sur la sortie d'erreur.\n"
        f"  {execution.resume()}"
    )
    assert nom in execution.erreurs, (
        f"{cas} : le message d'erreur doit nommer le fichier en cause ({nom}).\n"
        f"  {execution.resume()}"
    )
    assert not lire_resume(execution.sortie), (
        f"{cas} : aucun résumé ne doit s'afficher pour un rapport illisible.\n"
        f"  {execution.resume()}"
    )


def test_un_fichier_absent_se_dit_sans_trace(projet: Path, tmp_path: Path) -> None:
    nom = f"absent-{tirage().randint(1000, 9999)}.json"
    _exiger_refus_propre(lancer_outil(projet, str(tmp_path / nom)), nom, "fichier absent")


def test_un_json_invalide_se_dit_sans_trace(projet: Path, tmp_path: Path) -> None:
    nom = "casse.json"
    (tmp_path / nom).write_text('[{"id": "A", "severity": "HIGH"},', encoding="utf-8")
    _exiger_refus_propre(lancer_outil(projet, str(tmp_path / nom)), nom, "JSON tronqué")
