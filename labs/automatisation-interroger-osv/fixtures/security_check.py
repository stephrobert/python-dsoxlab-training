"""security_check : résumer un rapport de vulnérabilités par sévérité.

Version 1 : lit un export JSON de findings (une liste d'objets portant au
moins `severity`) et affiche combien il y en a par sévérité.

    uv run python security_check.py exemples/findings.json

La version 2 ajoute l'option --osv : l'énoncé est dans challenge/README.md
(`dsoxlab challenge`).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Du plus grave au moins grave : c'est l'ordre d'affichage.
SEVERITES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN")


class ErreurRapport(Exception):
    """Un rapport illisible : l'outil le dit et sort en 2, sans trace Python."""


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


def main(argv: list[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(description="Summarise a vulnerability report by severity.")
    parseur.add_argument("rapport", type=Path, help="JSON report to read")
    args = parseur.parse_args(argv)
    try:
        findings = lire_findings(args.rapport)
    except ErreurRapport as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    compte = compter(findings)
    for sev in SEVERITES:
        print(f"{sev}: {compte[sev]}")
    print(f"TOTAL: {sum(compte.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
