"""security_check : résumer un rapport de vulnérabilités, et décider.

Version 5 : l'outil lit aussi un SBOM CycloneDX. Un SBOM liste des
composants, pas des vulnérabilités : avec `--osv`, chaque composant PyPI est
croisé avec la base OSV, et chaque vulnérabilité connue devient un finding,
avec la sévérité que l'avis GitHub lui donne. Les codes de sortie :

    0  rien n'atteint le seuil (ou aucun seuil demandé)
    1  au moins une vulnérabilité atteint le seuil
    2  entrée inexploitable : rapport absent ou illisible, API OSV en panne,
       option invalide

    uv run python security_check.py rapports/trivy.json --fail-on CRITICAL
    uv run python security_check.py sbom/tableau-de-bord.cdx.json --osv --fail-on HIGH

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


def charger(chemin: Path) -> object:
    """Le JSON du fichier, ou une ErreurRapport qui dit pourquoi il est illisible."""
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ErreurRapport(f"report not found: {chemin}") from None
    except json.JSONDecodeError as e:
        raise ErreurRapport(f"invalid JSON in {chemin}: line {e.lineno}, column {e.colno}") from None


def est_sbom(donnees: object) -> bool:
    return isinstance(donnees, dict) and donnees.get("bomFormat") == "CycloneDX"


def composants_pypi(sbom: dict) -> list[tuple[str, str]]:
    """Les couples (paquet, version) PyPI d'un SBOM CycloneDX, une fois chacun.

    Le `purl` (Package URL) dit l'écosystème : `pkg:pypi/requests@2.25.0`.
    Les autres écosystèmes (npm, Go...) ne sont pas interrogés comme PyPI.
    CycloneDX autorise des composants imbriqués : on les parcourt aussi.
    """
    couples: set[tuple[str, str]] = set()
    pile = list(sbom.get("components") or [])
    while pile:
        composant = pile.pop()
        if not isinstance(composant, dict):
            continue
        pile.extend(composant.get("components") or [])
        purl = str(composant.get("purl") or "")
        if not purl.startswith("pkg:pypi/"):
            continue
        nom, _, version = purl.removeprefix("pkg:pypi/").split("?")[0].split("#")[0].partition("@")
        if nom and version:
            couples.add((nom, version))
    return sorted(couples)


def lire_findings(chemin: Path) -> list[dict]:
    donnees = charger(chemin)
    if est_sbom(donnees):
        raise ErreurRapport(f"{chemin} is a CycloneDX SBOM: it lists components, not vulnerabilities; add --osv")
    if isinstance(donnees, dict) and "Results" in donnees:
        return depuis_trivy(donnees)
    if not isinstance(donnees, list):
        raise ErreurRapport(f"{chemin}: unsupported report format (a findings list or a Trivy JSON report)")
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


# GitHub nomme MODERATE ce que Trivy et ce résumé appellent MEDIUM.
SEVERITE_GITHUB = {"CRITICAL": "CRITICAL", "HIGH": "HIGH", "MODERATE": "MEDIUM", "LOW": "LOW"}


def severite_osv(vulnerabilite: dict) -> str:
    """La sévérité d'un avis OSV : celle de GitHub quand elle existe, UNKNOWN sinon."""
    brute = str((vulnerabilite.get("database_specific") or {}).get("severity") or "").upper()
    return SEVERITE_GITHUB.get(brute, "UNKNOWN")


def au_dessus(compte: dict[str, int], seuil: str) -> int:
    """Combien de vulnérabilités atteignent le seuil. UNKNOWN n'en atteint aucun."""
    return sum(compte[s] for s in SEUILS[: SEUILS.index(seuil) + 1])


def paquets(findings: list[dict]) -> list[tuple[str, str]]:
    """Chaque couple (paquet, version) une seule fois, trié : un appel chacun."""
    return sorted({(str(f["package"]), str(f["version"]))
                   for f in findings if f.get("package") and f.get("version")})


def interroger_osv(paquet: str, version: str) -> list[dict]:
    """Les vulnérabilités qu'OSV connaît pour ce paquet PyPI, triées par identifiant."""
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
    return sorted(reponse.json().get("vulns", []), key=lambda v: v["id"])


@click.command()
@click.argument("rapport", type=click.Path(path_type=Path))
@click.option("--osv", is_flag=True, help="Also query the OSV database for each package.")
@click.option("--fail-on", "seuil", type=click.Choice(SEUILS, case_sensitive=False),
              help="Exit with code 1 if a vulnerability reaches this severity.")
def main(rapport: Path, osv: bool, seuil: str | None) -> None:
    """Summarise a vulnerability report (findings list, Trivy JSON, or a CycloneDX SBOM with --osv) by severity.

    Exit codes: 0 nothing reaches the threshold, 1 the threshold is reached,
    2 unusable input.
    """
    try:
        donnees = charger(rapport)
        if est_sbom(donnees) and osv:
            # Le SBOM ne porte aucune vulnérabilité : OSV les fournit, et
            # chacune devient un finding, sévérité comprise.
            connues = {p: interroger_osv(*p) for p in composants_pypi(donnees)}
            findings = [{"id": v["id"], "package": p[0], "version": p[1], "severity": severite_osv(v)}
                        for p, vulns in connues.items() for v in vulns]
        else:
            findings = lire_findings(rapport)
            connues = {p: interroger_osv(*p) for p in paquets(findings)} if osv else {}
    except ErreurRapport as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(2)
    compte = compter(findings)
    for sev in SEVERITES:
        click.echo(f"{sev}: {compte[sev]}")
    click.echo(f"TOTAL: {sum(compte.values())}")
    for (paquet, version), vulns in connues.items():
        ids = [v["id"] for v in vulns]
        click.echo(f"OSV {paquet}=={version}: {', '.join(ids) if ids else 'none'}")
    if seuil:
        seuil = seuil.upper()
        nombre = au_dessus(compte, seuil)
        if nombre:
            click.echo(f"FAILED: {nombre} vulnerabilities at {seuil} or above", err=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
