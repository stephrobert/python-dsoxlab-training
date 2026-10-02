"""Les tests de security_check.py.

Deux façons de tester un outil en ligne de commande, et cette suite emploie
les deux : appeler ses fonctions directement (rapide, précis), et le lancer
comme le ferait un pipeline avec `CliRunner` de Click, qui rend le code de
sortie et ce qui a été affiché.

    uv add --dev pytest
    uv run pytest -v
"""

import json

import pytest
import security_check
from click.testing import CliRunner


def test_les_severites_vont_de_la_plus_grave_a_la_moins_grave():
    assert security_check.SEVERITES[0] == "CRITICAL"
    assert security_check.SEVERITES[-1] == "UNKNOWN"


@pytest.mark.parametrize(
    ("brute", "attendue"),
    [("CRITICAL", "CRITICAL"), ("high", "HIGH"), ("Medium", "MEDIUM"),
     ("", "UNKNOWN"), (None, "UNKNOWN"), ("SEVERE", "UNKNOWN")],
)
def test_la_severite_est_normalisee(brute, attendue):
    assert security_check.severite({"severity": brute}) == attendue


def test_compter_rend_toutes_les_severites():
    compte = security_check.compter([{"severity": "high"}, {"severity": "HIGH"}, {}])
    assert compte == {"CRITICAL": 0, "HIGH": 2, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 1}


def test_une_faille_repetee_dans_deux_cibles_compte_une_fois():
    faille = {"VulnerabilityID": "CVE-1", "PkgName": "requests",
              "InstalledVersion": "2.25.0", "Severity": "HIGH"}
    rapport = {"Results": [{"Vulnerabilities": [faille]},
                           {"Vulnerabilities": [faille]},
                           {"Target": "propre"}]}
    assert len(security_check.depuis_trivy(rapport)) == 1


def _lancer(tmp_path, findings, *options):
    chemin = tmp_path / "rapport.json"
    chemin.write_text(json.dumps(findings), encoding="utf-8")
    return CliRunner().invoke(security_check.main, [str(chemin), *options])


@pytest.mark.parametrize(
    ("severites", "seuil", "code"),
    [(["HIGH"], "HIGH", 1),
     (["CRITICAL"], "HIGH", 1),
     (["MEDIUM"], "HIGH", 0),
     (["UNKNOWN"], "LOW", 0),
     (["LOW"], "low", 1)],
)
def test_le_seuil_est_inclusif(tmp_path, severites, seuil, code):
    resultat = _lancer(tmp_path, [{"severity": s} for s in severites], "--fail-on", seuil)
    assert resultat.exit_code == code


def test_sans_seuil_le_code_est_0_et_le_resume_s_affiche(tmp_path):
    resultat = _lancer(tmp_path, [{"severity": "CRITICAL"}])
    assert resultat.exit_code == 0
    assert "CRITICAL: 1" in resultat.output
    assert "TOTAL: 1" in resultat.output


def test_un_rapport_absent_rend_2_et_jamais_1(tmp_path):
    resultat = CliRunner().invoke(security_check.main, [str(tmp_path / "absent.json"), "--fail-on", "CRITICAL"])
    assert resultat.exit_code == 2


def test_un_json_invalide_rend_2(tmp_path):
    chemin = tmp_path / "casse.json"
    chemin.write_text("[{", encoding="utf-8")
    assert CliRunner().invoke(security_check.main, [str(chemin)]).exit_code == 2
