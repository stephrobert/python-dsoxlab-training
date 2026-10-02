"""Lire un SBOM : cinq contrôles, vingt points chacun.

## D'où vient le SBOM

`donnees/tableau-de-bord.cdx.json` est la sortie réelle de `syft` 1.51.1
(CycloneDX 1.7), relevée le 2026-10-02 sur un projet à deux fichiers
`requirements.txt` et un `package-lock.json` : six composants PyPI dont un
répété, et deux composants npm. Aucun chemin local n'y figure
(`SYFT_FILE_METADATA_SELECTION=none`).

## OSV fournit les vulnérabilités, la sévérité vient des avis GitHub

L'API factice rend, comme la vraie, une sévérité `database_specific.severity`
pour les avis GitHub (`MODERATE` pour ce que le résumé appelle MEDIUM) et
aucune pour les avis PYSEC. Les comptes attendus se calculent depuis ce que
l'API factice a rendu.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import (
    exiger_workdir,
    lancer_outil,
    lire_resume,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "automatisation-lire-un-sbom"
DONNEES = Path(__file__).resolve().parent / "donnees"
SBOM = DONNEES / "tableau-de-bord.cdx.json"
PYPI = [("click", "8.3.1"), ("jinja2", "2.11.2"), ("pyyaml", "5.3"), ("requests", "2.25.0"), ("urllib3", "1.26.4")]

# Ce que l'API factice rend : de vrais identifiants, des sévérités choisies.
REPONSES = {
    "requests": {"GHSA-j8r2-6x86-q33q": "MODERATE", "GHSA-9wx4-h78v-vm56": "MODERATE", "PYSEC-2023-74": None},
    "urllib3": {"GHSA-v845-jxx5-vc9f": "HIGH", "GHSA-q2q7-5pp4-w6pg": "MODERATE"},
    "jinja2": {"GHSA-h5c8-rqwp-cp95": "MODERATE"},
    "pyyaml": {"GHSA-8q59-q68h-6hv4": "CRITICAL"},
    "click": {"PYSEC-2026-2132": None},
}


@pytest.fixture(scope="module")
def projet() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    return WORKDIR


def _attendu(reponses: dict) -> dict[str, int]:
    traduction = {"CRITICAL": "CRITICAL", "HIGH": "HIGH", "MODERATE": "MEDIUM", "LOW": "LOW"}
    compte = dict.fromkeys(("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"), 0)
    for vulns in reponses.values():
        for gravite in vulns.values():
            compte[traduction.get(gravite or "", "UNKNOWN")] += 1
    compte["TOTAL"] = sum(compte.values())
    return compte


def _sbom(projet: Path, serveur, *options: str):
    return lancer_outil(projet, str(SBOM), "--osv", *options, env={"OSV_API_URL": serveur.url})


def test_chaque_composant_pypi_est_interroge_une_fois(projet: Path, serveur_osv) -> None:
    execution = _sbom(projet, serveur_osv)
    assert execution.code == 0, (
        "Un SBOM CycloneDX avec `--osv` doit être lu. Il se reconnaît à sa clé "
        f"`bomFormat`, et ses composants vivent sous `components`.\n  {execution.resume()}"
    )
    recus = sorted(((r["corps"].get("package") or {}).get("name"), r["corps"].get("version"),
                    (r["corps"].get("package") or {}).get("ecosystem")) for r in serveur_osv.requetes)
    attendus = sorted((n, v, "PyPI") for n, v in PYPI)
    assert recus == attendus, (
        f"Requêtes reçues : {recus}\n  attendues : {attendus}\n\n"
        "Une requête par composant PyPI distinct : `requests 2.25.0` figure deux "
        "fois dans le SBOM. Le `purl` dit l'écosystème (`pkg:pypi/...`) : les "
        "composants npm ne s'interrogent pas comme des paquets PyPI."
    )


def test_le_resume_compte_les_vulnerabilites_connues_d_osv(projet: Path, serveur_osv) -> None:
    serveur_osv.reponses = REPONSES
    execution = _sbom(projet, serveur_osv)
    assert execution.code == 0, execution.resume()
    attendu = _attendu(REPONSES)
    obtenu = lire_resume(execution.sortie)
    assert obtenu == attendu, (
        "Le résumé d'un SBOM compte les vulnérabilités qu'OSV connaît, une par "
        "avis, avec la sévérité de l'avis GitHub.\n"
        f"  attendu : {attendu}\n  obtenu  : {obtenu}\n\n"
        "GitHub écrit MODERATE ce que le résumé appelle MEDIUM, et un avis sans "
        f"sévérité (PYSEC) compte en UNKNOWN.\n  {execution.resume()}"
    )


def test_un_sbom_sans_osv_est_une_entree_inexploitable(projet: Path) -> None:
    execution = lancer_outil(projet, str(SBOM))
    assert execution.code == 2 and "--osv" in execution.erreurs and "Traceback" not in execution.erreurs, (
        "Un SBOM liste des composants, pas des vulnérabilités : sans `--osv`, "
        "l'outil n'a rien à compter. Il le dit en une ligne qui nomme `--osv`, "
        "avec le code 2, au lieu d'afficher un résumé à zéro qui ferait croire "
        f"le projet sain.\n  {execution.resume()}"
    )


def test_le_seuil_s_applique_a_un_sbom(projet: Path, serveur_osv) -> None:
    serveur_osv.reponses = REPONSES
    haut = _sbom(projet, serveur_osv, "--fail-on", "HIGH")
    assert haut.code == 1, (
        "Le SBOM porte un HIGH (urllib3) et un CRITICAL (pyyaml) d'après OSV : "
        f"`--fail-on HIGH` doit rendre 1.\n  {haut.resume()}"
    )
    serveur_osv.reponses = {"requests": {"GHSA-j8r2-6x86-q33q": "MODERATE"}}
    modere = _sbom(projet, serveur_osv, "--fail-on", "HIGH")
    assert modere.code == 0, (
        "Avec un seul avis MODERATE, rien n'atteint HIGH : code 0. MODERATE "
        f"est un MEDIUM, pas un HIGH.\n  {modere.resume()}"
    )


def test_les_rapports_restent_lisibles_et_les_composants_npm_ignores(projet: Path, serveur_osv, tmp_path: Path) -> None:
    """Le rapport Trivy des labs précédents, et un SBOM sans aucun composant PyPI."""
    trivy = lancer_outil(projet, str(DONNEES / "trivy-multi.json"))
    assert trivy.code == 0 and lire_resume(trivy.sortie).get("TOTAL") == 22, (
        f"Le rapport Trivy doit toujours donner ses 22 failles distinctes.\n  {trivy.resume()}"
    )
    sbom = json.loads(SBOM.read_text(encoding="utf-8"))
    sbom["components"] = [c for c in sbom["components"] if not str(c.get("purl", "")).startswith("pkg:pypi/")]
    npm = tmp_path / "npm.cdx.json"
    npm.write_text(json.dumps(sbom), encoding="utf-8")
    execution = lancer_outil(projet, str(npm), "--osv", env={"OSV_API_URL": serveur_osv.url})
    assert execution.code == 0 and lire_resume(execution.sortie).get("TOTAL") == 0, execution.resume()
    assert not serveur_osv.requetes, (
        "Un SBOM sans composant PyPI ne doit déclencher aucune requête PyPI : "
        f"{[r['corps'] for r in serveur_osv.requetes]}"
    )
