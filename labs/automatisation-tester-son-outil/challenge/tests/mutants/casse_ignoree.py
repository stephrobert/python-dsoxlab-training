"""security_check : résumer un rapport de vulnérabilités, et décider.

Version 4 : la ligne de commande passe sous Click, et `--fail-on` donne à
l'outil le droit d'arrêter un pipeline. Les codes de sortie :

    0  rien n'atteint le seuil (ou aucun seuil demandé)
    1  au moins une vulnérabilité atteint le seuil
    2  entrée inexploitable : rapport absent ou illisible, API OSV en panne,
       option invalide

    uv run python security_check.py exemples/trivy.json --fail-on CRITICAL

L'adresse de l'API OSV se règle par OSV_API_URL (https://api.osv.dev par
défaut), le délai maximal d'un appel par OSV_TIMEOUT, en secondes.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import click
import requests

# Du plus grave au moins grave : c'est l'ordre d'affichage ET celui des seuils.
SEVERITES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN")
SEUILS = SEVERITES[:-1]
OSV_PAR_DEFAUT = "https://api.osv.dev"


class ErreurRapport(Exception):
    """Une entrée inexploitable : l'outil le dit et sort en 2, sans trace Python."""


def depuis_trivy(rapport: dict) -> list[dict]:
    """Les findings d'un rapport Trivy, une fois par (identifiant, paquet, version)."""
    vus: dict[tuple[str, str, str], dict] = {}
    for resultat in rapport.get("Results") or []:
        for v in resultat.get("Vulnerabilities") or []:
            finding = {
                "id": v.get("VulnerabilityID", ""),
                "package": v.get("PkgName", ""),
                "version": v.get("InstalledVersion", ""),
                "severity": v.get("Severity"),
            }
            vus.setdefault((finding["id"], finding["package"], finding["version"]), finding)
    return list(vus.values())


def lire_findings(chemin: Path) -> list[dict]:
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ErreurRapport(f"report not found: {chemin}") from None
    except json.JSONDecodeError as e:
        raise ErreurRapport(f"invalid JSON in {chemin}: line {e.lineno}, column {e.colno}") from None
    if isinstance(donnees, dict) and "Results" in donnees:
        return depuis_trivy(donnees)
    if not isinstance(donnees, list):
        raise ErreurRapport(f"{chemin}: unsupported report format (a findings list or a Trivy JSON report)")
    return [f for f in donnees if isinstance(f, dict)]


def severite(finding: dict) -> str:
    """La sévérité normalisée : en majuscules, UNKNOWN si absente ou inconnue."""
    valeur = str(finding.get("severity") or "")
    return valeur if valeur in SEVERITES else "UNKNOWN"


def compter(findings: list[dict]) -> dict[str, int]:
    compte = dict.fromkeys(SEVERITES, 0)
    for f in findings:
        compte[severite(f)] += 1
    return compte


def au_dessus(compte: dict[str, int], seuil: str) -> int:
    """Combien de vulnérabilités atteignent le seuil. UNKNOWN n'en atteint aucun."""
    return sum(compte[s] for s in SEUILS[: SEUILS.index(seuil) + 1])


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


@click.command()
@click.argument("rapport", type=click.Path(path_type=Path))
@click.option("--osv", is_flag=True, help="Also query the OSV database for each package.")
@click.option("--fail-on", "seuil", type=click.Choice(SEUILS, case_sensitive=False),
              help="Exit with code 1 if a vulnerability reaches this severity.")
def main(rapport: Path, osv: bool, seuil: str | None) -> None:
    """Summarise a vulnerability report (findings list or Trivy JSON) by severity.

    Exit codes: 0 nothing reaches the threshold, 1 the threshold is reached,
    2 unusable input.
    """
    try:
        findings = lire_findings(rapport)
        connues = {p: interroger_osv(*p) for p in paquets(findings)} if osv else {}
    except ErreurRapport as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(2)
    compte = compter(findings)
    for sev in SEVERITES:
        click.echo(f"{sev}: {compte[sev]}")
    click.echo(f"TOTAL: {sum(compte.values())}")
    for (paquet, version), ids in connues.items():
        click.echo(f"OSV {paquet}=={version}: {', '.join(ids) if ids else 'none'}")
    if seuil:
        seuil = seuil.upper()
        nombre = au_dessus(compte, seuil)
        if nombre:
            click.echo(f"FAILED: {nombre} vulnerabilities at {seuil} or above", err=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
