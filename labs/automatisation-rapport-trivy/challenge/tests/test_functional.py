"""Lire un vrai rapport Trivy : cinq contrôles, vingt points chacun.

## D'où vient le rapport de référence

`donnees/trivy-multi.json` est la sortie réelle de `trivy fs --scanners vuln
--format json` (Trivy 0.74.0, le 2026-10-02) sur un projet à trois fichiers
`requirements.txt` : 26 occurrences de vulnérabilités, 22 distinctes, et une
cible sans aucune clé `Vulnerabilities`. Ce sont les deux pièges que le lab
enseigne, relevés et non inventés.

## Ce qui est attendu se calcule, il ne s'écrit pas

Le compte attendu du rapport réel est recalculé ici depuis le fichier, et
celui du rapport généré depuis ce qui a été tiré. Un outil qui imprime 22 en
dur échoue au second.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import (
    SEVERITES,
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
LAB_ID = "automatisation-rapport-trivy"
DONNEES = Path(__file__).resolve().parent / "donnees"


@pytest.fixture(scope="module")
def projet() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    return WORKDIR


def attendu_trivy(rapport: dict) -> dict[str, int]:
    """Le résumé attendu : une vulnérabilité par (id, paquet, version)."""
    uniques = {}
    for r in rapport.get("Results") or []:
        for v in r.get("Vulnerabilities") or []:
            uniques[(v["VulnerabilityID"], v["PkgName"], v["InstalledVersion"])] = v.get("Severity")
    return compter(list(uniques.values()))


def trivy_au_hasard(graine: int) -> dict:
    """Un rapport Trivy plausible : plusieurs cibles, doublons, cibles vides."""
    rnd = tirage(graine)
    pool = findings_au_hasard(rnd, rnd.randint(6, 18))
    resultats = []
    for i in range(rnd.randint(3, 5)):
        cible = {"Target": f"service-{i}/requirements.txt", "Class": "lang-pkgs", "Type": "pip"}
        choisis = rnd.sample(pool, rnd.randint(0, len(pool)))
        if choisis:
            cible["Vulnerabilities"] = [
                {"VulnerabilityID": f["id"], "PkgName": f["package"],
                 "InstalledVersion": f["version"], "Severity": f["severity"].upper()}
                for f in choisis
            ]
        elif rnd.random() < 0.5:
            cible["Vulnerabilities"] = None
        resultats.append(cible)
    return {"SchemaVersion": 2, "ArtifactName": ".", "ArtifactType": "filesystem", "Results": resultats}


def _exiger_resume(execution, attendu: dict[str, int], contexte: str) -> None:
    assert execution.code == 0, (
        f"{contexte} : l'outil devait réussir (code 0). Un rapport Trivy est un "
        "objet JSON, pas une liste : la version 2 le refuse, la version 3 doit "
        f"le reconnaître.\n  {execution.resume()}"
    )
    obtenu = lire_resume(execution.sortie)
    assert obtenu == attendu, (
        f"{contexte} : le résumé ne correspond pas au rapport.\n"
        f"  attendu : {attendu}\n  obtenu  : {obtenu}\n  {execution.resume()}"
    )


def test_le_vrai_rapport_trivy_compte_22_failles_distinctes(projet: Path) -> None:
    chemin = DONNEES / "trivy-multi.json"
    attendu = attendu_trivy(json.loads(chemin.read_text(encoding="utf-8")))
    execution = lancer_outil(projet, str(chemin))
    if execution.code == 0 and lire_resume(execution.sortie).get("TOTAL") == 26:
        pytest.fail(
            "TOTAL vaut 26 : ce sont les occurrences, pas les failles. `requests "
            "2.25.0` est déclaré dans deux fichiers, et ses quatre vulnérabilités "
            "apparaissent dans deux cibles ; chacune ne compte qu'une fois.",
            pytrace=False,
        )
    _exiger_resume(execution, attendu, "rapport réel de Trivy 0.74.0")


def test_un_rapport_trivy_genere_est_dedoublonne(projet: Path, tmp_path: Path) -> None:
    for graine in (tirage().randint(0, 10**6), tirage().randint(0, 10**6)):
        rapport = trivy_au_hasard(graine)
        chemin = ecrire_json(tmp_path / f"trivy-{graine}.json", rapport)
        _exiger_resume(lancer_outil(projet, str(chemin)), attendu_trivy(rapport),
                       f"rapport Trivy tiré avec la graine {graine}")


def test_des_cibles_sans_vulnerabilite_ne_cassent_rien(projet: Path, tmp_path: Path) -> None:
    """Clé absente, liste nulle, liste vide, et aucun résultat du tout."""
    rapport = {"SchemaVersion": 2, "Results": [
        {"Target": "a/requirements.txt"},
        {"Target": "b/requirements.txt", "Vulnerabilities": None},
        {"Target": "c/requirements.txt", "Vulnerabilities": []},
    ]}
    zeros = dict.fromkeys(SEVERITES, 0) | {"TOTAL": 0}
    _exiger_resume(lancer_outil(projet, str(ecrire_json(tmp_path / "propre.json", rapport))), zeros,
                   "cibles sans vulnérabilité (clé absente, null, liste vide)")
    sans_resultat = ecrire_json(tmp_path / "sans-resultat.json", {"SchemaVersion": 2, "Results": None})
    _exiger_resume(lancer_outil(projet, str(sans_resultat)), zeros, "`Results` à null (scan sans cible)")


def test_les_deux_formats_restent_lisibles(projet: Path, tmp_path: Path) -> None:
    """L'export en liste des labs précédents ET le format Trivy."""
    findings = findings_au_hasard(tirage())
    liste = ecrire_json(tmp_path / "liste.json", findings)
    _exiger_resume(lancer_outil(projet, str(liste)), compter([f["severity"] for f in findings]),
                   "export en liste (format des labs précédents)")
    _exiger_resume(lancer_outil(projet, str(DONNEES / "trivy-multi.json")),
                   attendu_trivy(json.loads((DONNEES / "trivy-multi.json").read_text(encoding="utf-8"))),
                   "rapport Trivy")


def test_osv_interroge_les_paquets_du_rapport_trivy(projet: Path, serveur_osv) -> None:
    rapport = json.loads((DONNEES / "trivy-multi.json").read_text(encoding="utf-8"))
    attendus = sorted({(v["PkgName"], v["InstalledVersion"])
                       for r in rapport["Results"] for v in r.get("Vulnerabilities") or []})
    execution = lancer_outil(projet, str(DONNEES / "trivy-multi.json"), "--osv",
                             env={"OSV_API_URL": serveur_osv.url})
    assert execution.code == 0, execution.resume()
    recus = sorted(((r["corps"].get("package") or {}).get("name"), r["corps"].get("version"))
                   for r in serveur_osv.requetes)
    assert recus == attendus, (
        f"Avec un rapport Trivy, `--osv` interroge chaque couple (PkgName, "
        f"InstalledVersion) une fois.\n  attendus : {attendus}\n  reçus    : {recus}"
    )
