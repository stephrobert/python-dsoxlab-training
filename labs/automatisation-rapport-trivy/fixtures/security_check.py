"""security_check : résumer un rapport de vulnérabilités par sévérité.

Version 2 : avec `--osv`, l'outil interroge aussi la base OSV pour chaque
paquet du rapport, et affiche les vulnérabilités qu'elle connaît.

    uv run python security_check.py exemples/findings.json
    uv run python security_check.py exemples/findings.json --osv

La version 3 lit aussi le vrai rapport de Trivy (exemples/trivy.json) :
l'énoncé est dans challenge/README.md (`dsoxlab challenge`).

L'adresse de l'API se règle par OSV_API_URL (https://api.osv.dev par
défaut), le délai maximal d'un appel par OSV_TIMEOUT, en secondes.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests

# Du plus grave au moins grave : c'est l'ordre d'affichage.
SEVERITES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN")
OSV_PAR_DEFAUT = "https://api.osv.dev"


class ErreurRapport(Exception):
    """Une entrée inexploitable : l'outil le dit et sort en 2, sans trace Python."""


def lire_findings(chemin: Path) -> list[dict]:
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ErreurRapport(f"report not found: {chemin}") from None
    except json.JSONDecodeError as e:
        raise ErreurRapport(f"invalid JSON in {chemin}: line {e.lineno}, column {e.colno}") from None
    if not isinstance(donnees, list):
        raise ErreurRapport(f"{chemin} must contain a JSON list of findings")
    return [f for f in donnees if isinstance(f, dict)]


def severite(finding: dict) -> str:
    """La sévérité normalisée : en majuscules, UNKNOWN si absente ou inconnue."""
    valeur = str(finding.get("severity") or "").upper()
    return valeur if valeur in SEVERITES else "UNKNOWN"


def compter(findings: list[dict]) -> dict[str, int]:
    compte = dict.fromkeys(SEVERITES, 0)
    for f in findings:
        compte[severite(f)] += 1
    return compte


def paquets(findings: list[dict]) -> list[tuple[str, str]]:
    """Chaque couple (paquet, version) une seule fois, trié : un appel chacun."""
    return sorted({(str(f["package"]), str(f["version"]))
                   for f in findings if f.get("package") and f.get("version")})


def interroger_osv(paquet: str, version: str) -> list[str]:
    """Les identifiants des vulnérabilités qu'OSV connaît pour ce paquet PyPI."""
    url = os.environ.get("OSV_API_URL", OSV_PAR_DEFAUT).rstrip("/") + "/v1/query"
    delai = float(os.environ.get("OSV_TIMEOUT", "10"))
    corps = {"package": {"name": paquet, "ecosystem": "PyPI"}, "version": version}
    try:
        reponse = requests.post(url, json=corps, timeout=delai)
        reponse.raise_for_status()
    except requests.Timeout:
        raise ErreurRapport(f"OSV API did not answer within {delai:g} s ({url})") from None
    except requests.HTTPError:
        raise ErreurRapport(f"OSV API returned HTTP {reponse.status_code} for {paquet}=={version}") from None
    except requests.RequestException as e:
        raise ErreurRapport(f"cannot reach the OSV API at {url}: {e.__class__.__name__}") from None
    return sorted(v["id"] for v in reponse.json().get("vulns", []))


def main(argv: list[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(description="Summarise a vulnerability report by severity.")
    parseur.add_argument("rapport", type=Path, help="JSON report to read")
    parseur.add_argument("--osv", action="store_true", help="also query the OSV database for each package")
    args = parseur.parse_args(argv)
    try:
        findings = lire_findings(args.rapport)
        connues = {p: interroger_osv(*p) for p in paquets(findings)} if args.osv else {}
    except ErreurRapport as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    compte = compter(findings)
    for sev in SEVERITES:
        print(f"{sev}: {compte[sev]}")
    print(f"TOTAL: {sum(compte.values())}")
    for (paquet, version), ids in connues.items():
        print(f"OSV {paquet}=={version}: {', '.join(ids) if ids else 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
