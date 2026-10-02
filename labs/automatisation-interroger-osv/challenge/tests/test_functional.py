"""Interroger OSV : cinq contrôles, vingt points chacun.

## Une API factice, et pourquoi

Les tests ne touchent pas la vraie base OSV : ses réponses changent chaque
semaine, et un test qui dépend du réseau échoue pour de mauvaises raisons. Un
serveur local répond comme `POST /v1/query`, et il ENREGISTRE ce qu'il reçoit :
c'est ce qui permet de vérifier ce que l'outil a vraiment demandé, et combien
de fois. L'outil le trouve par la variable OSV_API_URL, que l'énoncé impose.

## Les deux derniers contrôles sont ceux d'un outil de pipeline

Une API en panne ou muette ne doit ni produire une trace Python, ni bloquer
le job jusqu'à son délai maximal : l'outil dit le problème et sort en 2.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from conftest import (
    compter,
    ecrire_json,
    exiger_workdir,
    lancer_outil,
    lire_resume,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "automatisation-interroger-osv"

FINDINGS = [
    {"id": "CVE-A", "package": "requests", "version": "2.25.0", "severity": "HIGH"},
    {"id": "CVE-B", "package": "requests", "version": "2.25.0", "severity": "MEDIUM"},
    {"id": "CVE-C", "package": "urllib3", "version": "1.26.4", "severity": "critical"},
    {"id": "CVE-D", "package": "jinja2", "version": "2.11.2", "severity": "LOW"},
    {"id": "CVE-E", "package": "requests", "version": "2.31.0", "severity": "HIGH"},
]
ATTENDUS = {("jinja2", "2.11.2"), ("requests", "2.25.0"), ("requests", "2.31.0"), ("urllib3", "1.26.4")}


@pytest.fixture(scope="module")
def projet() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    return WORKDIR


@pytest.fixture
def rapport(tmp_path: Path) -> Path:
    return ecrire_json(tmp_path / "findings.json", FINDINGS)


def _osv(projet: Path, rapport: Path, serveur, **env: str):
    return lancer_outil(projet, str(rapport), "--osv", env={"OSV_API_URL": serveur.url, **env})


def _exiger_succes(execution) -> None:
    assert execution.code == 0, (
        "`--osv` devait réussir (code 0). Si la sortie parle de `requests` "
        "introuvable, la bibliothèque n'est pas une dépendance du projet : "
        "`uv add requests` l'y déclare.\n"
        f"  {execution.resume()}"
    )


def test_chaque_paquet_est_interroge_une_seule_fois(projet: Path, rapport: Path, serveur_osv) -> None:
    """Quatre couples (paquet, version) distincts : quatre requêtes, bien formées."""
    _exiger_succes(_osv(projet, rapport, serveur_osv))
    recus = []
    for r in serveur_osv.requetes:
        corps = r["corps"]
        assert r["chemin"] == "/v1/query", (
            f"Requête reçue sur {r['chemin']} : OSV répond sur `/v1/query`, "
            "au bout de l'adresse donnée par OSV_API_URL."
        )
        paquet = corps.get("package") or {}
        assert paquet.get("ecosystem") == "PyPI", (
            f"Corps reçu : {corps}. OSV doit savoir dans quel écosystème "
            "chercher : `\"ecosystem\": \"PyPI\"` dans `package`."
        )
        recus.append((paquet.get("name"), corps.get("version")))
    assert sorted(recus) == sorted(ATTENDUS), (
        f"Requêtes reçues : {sorted(recus)}\n  attendues : {sorted(ATTENDUS)}\n\n"
        "Une requête par couple (paquet, version) distinct du rapport : "
        "`requests 2.25.0` y figure deux fois, il ne s'interroge qu'une fois, "
        "et `requests 2.31.0` est un autre couple."
    )


def test_les_vulnerabilites_connues_s_affichent_par_paquet(projet: Path, rapport: Path, serveur_osv) -> None:
    serveur_osv.reponses = {
        "requests": ["PYSEC-2023-74", "GHSA-j8r2-6x86-q33q"],
        "urllib3": ["GHSA-v845-jxx5-vc9f"],
    }
    execution = _osv(projet, rapport, serveur_osv)
    _exiger_succes(execution)
    lignes = [ligne for ligne in execution.sortie.splitlines() if ligne.startswith("OSV ")]
    attendu = [
        "OSV jinja2==2.11.2: none",
        "OSV requests==2.25.0: GHSA-j8r2-6x86-q33q, PYSEC-2023-74",
        "OSV requests==2.31.0: GHSA-j8r2-6x86-q33q, PYSEC-2023-74",
        "OSV urllib3==1.26.4: GHSA-v845-jxx5-vc9f",
    ]
    assert lignes == attendu, (
        "Les lignes OSV ne sont pas celles attendues.\n"
        f"  attendu : {attendu}\n  obtenu  : {lignes}\n\n"
        "Une ligne par couple, triés par paquet puis version, au format "
        "`OSV paquet==version: ID, ID` (identifiants triés) ou `: none`.\n"
        f"  {execution.resume()}"
    )


def test_le_resume_reste_et_sans_osv_aucun_appel(projet: Path, rapport: Path, serveur_osv) -> None:
    """`--osv` ajoute des lignes, il ne retire rien ; sans lui, pas de réseau."""
    attendu = compter([f["severity"] for f in FINDINGS])
    avec = _osv(projet, rapport, serveur_osv)
    _exiger_succes(avec)
    assert lire_resume(avec.sortie) == attendu, (
        f"Avec `--osv`, le résumé par sévérité doit rester le même.\n  attendu : {attendu}\n"
        f"  {avec.resume()}"
    )
    avant = len(serveur_osv.requetes)
    sans = lancer_outil(projet, str(rapport), env={"OSV_API_URL": serveur_osv.url})
    assert sans.code == 0 and lire_resume(sans.sortie) == attendu, sans.resume()
    assert len(serveur_osv.requetes) == avant, (
        "Sans `--osv`, l'outil ne doit faire aucun appel réseau : dans un "
        "pipeline hors ligne, le simple résumé doit continuer de marcher."
    )


def _exiger_refus_propre(execution, indice: str, cas: str) -> None:
    assert execution.code == 2, (
        f"{cas} : l'outil doit sortir en 2, comme pour toute entrée inexploitable.\n"
        f"  {execution.resume()}"
    )
    assert "Traceback" not in execution.erreurs, (
        f"{cas} : une trace Python remonte. Les exceptions de `requests` "
        "s'attrapent, et le problème se dit en une ligne.\n"
        f"  {execution.resume()}"
    )
    assert indice in execution.erreurs, (
        f"{cas} : le message doit dire ce qui s'est passé (il doit contenir « {indice} »).\n"
        f"  {execution.resume()}"
    )


def test_une_api_en_panne_se_dit_sans_trace(projet: Path, rapport: Path, serveur_osv) -> None:
    serveur_osv.statut = 500
    _exiger_refus_propre(_osv(projet, rapport, serveur_osv), "500", "API qui répond HTTP 500")


def test_une_api_muette_ne_bloque_pas_le_pipeline(projet: Path, rapport: Path, serveur_osv) -> None:
    """Un serveur qui met 6 s à répondre, un délai maximal de 1 s."""
    serveur_osv.delai = 6
    debut = time.monotonic()
    execution = _osv(projet, rapport, serveur_osv, OSV_TIMEOUT="1")
    duree = time.monotonic() - debut
    _exiger_refus_propre(execution, "OSV", "API qui ne répond pas")
    # uv et Python démarrent en moins de 2 s ; une seule requête attendue.
    assert duree < 5, (
        f"L'outil a attendu {duree:.1f} s : le délai maximal OSV_TIMEOUT=1 "
        "n'est pas appliqué. Sans `timeout=`, `requests` attend indéfiniment.\n"
        f"  {execution.resume()}"
    )
