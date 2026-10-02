"""Tester son outil : cinq contrôles, vingt points chacun.

## Ce que ce lab note : la suite de tests de l'apprenant

Une suite de tests ne se juge pas à son nombre de tests verts, mais à ce
qu'elle attrape. On la joue donc sur deux sortes d'outil :

- la RÉFÉRENCE (`reference/security_check.py`, la solution du lab 4) : une
  bonne suite y passe entièrement ;
- quatre MUTANTS (`mutants/`, produits par `scripts/generer_mutants.py`) : la
  référence avec un seul défaut réaliste chacun. Une bonne suite échoue sur
  chacun d'eux ; on dit qu'elle « tue » le mutant.

Chaque passage se fait dans une copie du projet, où seul `security_check.py`
est remplacé : les tests de l'apprenant ne sont jamais modifiés, et son propre
outil n'est jamais touché.

## Pourquoi chaque mutant exige aussi la référence verte

Une suite qui échoue partout « tue » tous les mutants. Elle ne prouve rien :
chaque contrôle de mutant exige donc d'abord que la suite passe sur la
référence. Sans cette condition, le point de départ, dont pytest n'est pas
encore installé, aurait rendu 80 points sur 100 sans le moindre travail.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import pytest

from conftest import exiger_workdir, workdir_lab

WORKDIR = workdir_lab(__file__)
LAB_ID = "automatisation-tester-son-outil"
ICI = Path(__file__).resolve().parent
REFERENCE = ICI / "reference" / "security_check.py"
MUTANTS = ICI / "mutants"
MINIMUM_DE_TESTS = 5
EXCLUS = (".venv", "__pycache__", ".pytest_cache", ".ruff_cache")


@dataclass
class Passage:
    code: int
    sortie: str
    reussis: int
    echoues: int

    def resume(self) -> str:
        return f"pytest a rendu le code {self.code} :\n{self.sortie.strip()[-1500:]}"


@cache
def jouer_la_suite(outil: str) -> Passage:
    """La suite de l'apprenant, jouée sur une copie du projet où l'outil est remplacé."""
    exiger_workdir(WORKDIR, LAB_ID)
    uv = shutil.which("uv")
    if uv is None:
        pytest.fail("uv est introuvable sur le PATH. Lancez `mise install`.", pytrace=False)
    copie = Path(tempfile.mkdtemp(prefix="security-check-")) / "projet"
    shutil.copytree(WORKDIR, copie, ignore=shutil.ignore_patterns(*EXCLUS))
    shutil.copy2(outil, copie / "security_check.py")
    res = subprocess.run(
        [uv, "run", "--quiet", "--directory", str(copie), "pytest", "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, timeout=300, check=False,
    )
    sortie = res.stdout + res.stderr

    def nombre(mot: str) -> int:
        m = re.search(rf"(\d+) {mot}", sortie)
        return int(m.group(1)) if m else 0

    shutil.rmtree(copie.parent, ignore_errors=True)
    return Passage(res.returncode, sortie, nombre("passed"), nombre("failed") + nombre("error"))


def _exiger_reference_verte() -> Passage:
    ref = jouer_la_suite(str(REFERENCE))
    if "Failed to spawn" in ref.sortie and "pytest" in ref.sortie:
        pytest.fail(
            "pytest n'est pas installé dans le projet : `uv add --dev pytest` le "
            "déclare comme dépendance de développement.\n" + ref.resume(),
            pytrace=False,
        )
    assert ref.code == 0, (
        "Votre suite échoue sur l'outil de RÉFÉRENCE, qui est juste : un test "
        "attend autre chose que le comportement demandé par les labs précédents.\n"
        + ref.resume()
    )
    return ref


def test_la_suite_passe_sur_l_outil_juste_et_compte_assez_de_tests() -> None:
    ref = _exiger_reference_verte()
    assert ref.reussis >= MINIMUM_DE_TESTS, (
        f"{ref.reussis} test(s) seulement : il en faut au moins {MINIMUM_DE_TESTS}. "
        "L'exemple livré ne vérifie qu'une constante ; une suite utile exerce "
        "la lecture, le compte, le dédoublonnage et les codes de sortie.\n"
        + ref.resume()
    )


def _exiger_mutant_tue(nom: str, defaut: str, piste: str) -> None:
    _exiger_reference_verte()
    passage = jouer_la_suite(str(MUTANTS / f"{nom}.py"))
    assert passage.code != 0 and passage.echoues > 0, (
        f"Le mutant « {nom} » survit : votre suite passe sur un outil où {defaut}.\n"
        f"Ajoutez un test qui l'attrape : {piste}\n" + passage.resume()
    )


def test_la_suite_attrape_un_seuil_exclusif() -> None:
    _exiger_mutant_tue(
        "seuil_exclusif",
        "`--fail-on HIGH` ne compte plus les HIGH (seuil exclusif)",
        "un rapport qui ne contient QU'UN HIGH, avec `--fail-on HIGH`, doit rendre 1.",
    )


def test_la_suite_attrape_une_casse_non_normalisee() -> None:
    _exiger_mutant_tue(
        "casse_ignoree",
        "« high » en minuscules compte en UNKNOWN",
        "une sévérité en minuscules doit compter dans sa sévérité.",
    )


def test_la_suite_attrape_des_doublons_trivy() -> None:
    _exiger_mutant_tue(
        "doublons_comptes",
        "une faille répétée dans deux cibles Trivy compte deux fois",
        "un rapport Trivy dont deux cibles portent la même vulnérabilité.",
    )


def test_la_suite_attrape_un_rapport_absent_qui_rend_1() -> None:
    _exiger_mutant_tue(
        "erreur_en_code_1",
        "un rapport illisible rend le code 1, celui de « seuil atteint »",
        "un rapport absent doit rendre 2, même avec `--fail-on`.",
    )
