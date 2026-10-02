"""security_check : résumer un rapport de vulnérabilités par sévérité.

Version 1 : lit un export JSON de findings (une liste d'objets portant au
moins `severity`) et affiche combien il y en a par sévérité.

    uv run python security_check.py exemples/findings.json

L'énoncé est dans challenge/README.md (`dsoxlab challenge`).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Du plus grave au moins grave : c'est l'ordre d'affichage.
SEVERITES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN")


def lire_findings(chemin: Path) -> list[dict]:
    """Lit le rapport et rend la liste des findings."""
    raise NotImplementedError("à écrire")


def compter(findings: list[dict]) -> dict[str, int]:
    """Rend le nombre de findings par sévérité, pour chaque clé de SEVERITES."""
    raise NotImplementedError("à écrire")


def main(argv: list[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(description="Summarise a vulnerability report by severity.")
    parseur.add_argument("rapport", type=Path, help="JSON report to read")
    args = parseur.parse_args(argv)
    findings = lire_findings(args.rapport)
    compte = compter(findings)
    for sev in SEVERITES:
        print(f"{sev}: {compte[sev]}")
    print(f"TOTAL: {sum(compte.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
