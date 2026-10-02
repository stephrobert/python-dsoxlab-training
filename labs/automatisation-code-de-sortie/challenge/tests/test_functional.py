"""Le code de sortie : cinq contrôles, vingt points chacun.

## Pourquoi le code de sortie est tout le sujet

Un pipeline ne lit pas ce qu'un outil affiche : il lit son code de sortie.
0 laisse passer, tout autre code arrête le job. L'outil distingue donc trois
cas que la sortie seule ne dirait pas à une machine : 0, rien n'atteint le
seuil ; 1, le seuil est atteint ; 2, l'entrée est inexploitable. Confondre 1
et 2, c'est arrêter un déploiement pour une faille alors que le rapport était
simplement absent, ou l'inverse.

## Ce qui est attendu se calcule

Les rapports du deuxième contrôle sont tirés au hasard, et le code attendu
pour chaque seuil est recalculé ici.
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
LAB_ID = "automatisation-code-de-sortie"
SEUILS = ("CRITICAL", "HIGH", "MEDIUM", "LOW")


@pytest.fixture(scope="module")
def projet() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    return WORKDIR


def _rapport(tmp_path: Path, severites: list[str], nom: str = "rapport.json") -> Path:
    return ecrire_json(tmp_path / nom, [{"id": f"CVE-{i}", "package": "p", "version": "1",
                                         "severity": s} for i, s in enumerate(severites)])


def _code_attendu(severites: list[str], seuil: str) -> int:
    compte = compter(severites)
    rang = SEUILS.index(seuil)
    return 1 if sum(compte[s] for s in SEUILS[: rang + 1]) else 0


def test_un_critique_arrete_le_pipeline(projet: Path, tmp_path: Path) -> None:
    rapport = _rapport(tmp_path, ["CRITICAL", "HIGH", "LOW"])
    execution = lancer_outil(projet, str(rapport), "--fail-on", "CRITICAL")
    assert execution.code == 1, (
        "Une vulnérabilité CRITICAL avec `--fail-on CRITICAL` : le code doit "
        f"être 1, celui qui arrête le job.\n  {execution.resume()}"
    )
    assert lire_resume(execution.sortie) == compter(["CRITICAL", "HIGH", "LOW"]), (
        "Le résumé reste affiché quand le seuil est atteint : c'est ce que "
        f"l'équipe lit dans le journal du job pour savoir pourquoi.\n  {execution.resume()}"
    )
    assert "1" in execution.erreurs and "Traceback" not in execution.erreurs, (
        "La sortie d'erreur dit combien de vulnérabilités atteignent le seuil, "
        f"en une ligne, sans trace Python.\n  {execution.resume()}"
    )


def test_le_seuil_compte_tout_ce_qui_est_au_dessus(projet: Path, tmp_path: Path) -> None:
    """Un rapport tiré au hasard, les quatre seuils : chaque code est recalculé."""
    graine = tirage().randint(0, 10**6)
    findings = findings_au_hasard(tirage(graine))
    severites = [f["severity"] for f in findings]
    rapport = ecrire_json(tmp_path / "hasard.json", findings)
    for seuil in SEUILS:
        attendu = _code_attendu(severites, seuil)
        execution = lancer_outil(projet, str(rapport), "--fail-on", seuil)
        assert execution.code == attendu, (
            f"Graine {graine}, `--fail-on {seuil}` : code {execution.code}, attendu {attendu}.\n"
            f"  sévérités du rapport : {compter(severites)}\n\n"
            "Le seuil est inclusif et compte tout ce qui est AU MOINS aussi grave : "
            "`--fail-on HIGH` échoue sur un CRITICAL. UNKNOWN n'atteint aucun seuil.\n"
            f"  {execution.resume()}"
        )


def test_sous_le_seuil_ou_sans_seuil_le_pipeline_continue(projet: Path, tmp_path: Path) -> None:
    rapport = _rapport(tmp_path, ["MEDIUM", "LOW", "UNKNOWN", "medium"])
    avec = lancer_outil(projet, str(rapport), "--fail-on", "high")
    assert avec.code == 0, (
        "Rien n'atteint HIGH (le seuil s'écrit aussi en minuscules) : code 0.\n"
        f"  {avec.resume()}"
    )
    sans = lancer_outil(projet, str(_rapport(tmp_path, ["CRITICAL"], "critique.json")))
    assert sans.code == 0, (
        "Sans `--fail-on`, l'outil ne juge pas : il résume et sort en 0, même "
        f"sur un CRITICAL.\n  {sans.resume()}"
    )


def test_une_entree_invalide_reste_un_code_2(projet: Path, tmp_path: Path) -> None:
    """Un seuil inconnu et un rapport absent : 2, jamais 1."""
    rapport = _rapport(tmp_path, ["CRITICAL"])
    inconnu = lancer_outil(projet, str(rapport), "--fail-on", "SEVERE")
    assert inconnu.code == 2 and "critical" in inconnu.erreurs.lower(), (
        "`--fail-on SEVERE` : code 2, et le message liste les seuils acceptés. "
        "Click le fait seul quand l'option déclare ses choix.\n"
        f"  {inconnu.resume()}"
    )
    absent = lancer_outil(projet, str(tmp_path / "absent.json"), "--fail-on", "CRITICAL")
    assert absent.code == 2 and "Traceback" not in absent.erreurs, (
        "Un rapport absent avec `--fail-on` : code 2, l'entrée est inexploitable. "
        "Un code 1 dirait au pipeline « une faille critique », ce qui est faux.\n"
        f"  {absent.resume()}"
    )


def test_l_aide_est_celle_de_click_et_documente_les_options(projet: Path, tmp_path: Path) -> None:
    execution = lancer_outil(projet, "--help")
    assert execution.code == 0, execution.resume()
    aide = execution.sortie
    assert aide.startswith("Usage:"), (
        "L'aide doit être celle de Click, qui commence par `Usage:` (argparse "
        "écrit `usage:`). Si l'outil répond que le module click est "
        "introuvable : `uv add click`.\n"
        f"  {execution.resume()}"
    )
    for option in ("--fail-on", "--osv"):
        assert option in aide, f"L'aide ne mentionne pas `{option}`.\n  {execution.resume()}"
