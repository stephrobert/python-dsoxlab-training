# Ce que contient vraiment ce que vous livrez

## Situation

La porte du pipeline lit le rapport de Trivy. Mais le client exige désormais,
à chaque livraison, un **SBOM** (Software Bill of Materials) : l'inventaire de
tous les composants du logiciel, au format CycloneDX. Et un inventaire n'est
pas un rapport : il dit **ce qui est là**, jamais **ce qui est vulnérable**.
Pour le savoir, il faut croiser chaque composant avec une base de
vulnérabilités, ce que `security_check.py` sait déjà faire avec OSV.

Le répertoire `challenge/work` contient le projet tel que le lab précédent l'a
laissé, workflow compris, et `sbom/tableau-de-bord.cdx.json` : la sortie
réelle de syft 1.51.1 (CycloneDX 1.7) sur un projet Python doublé d'une
petite interface npm. Lancez-y votre version 4 : elle le refuse.

## Objectif

`uv run python security_check.py sbom/tableau-de-bord.cdx.json --osv` :

- reconnaît un SBOM CycloneDX à sa clé `bomFormat` ;
- interroge OSV une fois par composant **PyPI** distinct, lu dans son `purl`
  (`pkg:pypi/requests@2.25.0`) ; les composants npm ne sont pas des paquets
  PyPI ;
- fait de chaque vulnérabilité qu'OSV rend un finding, avec la sévérité de
  l'avis GitHub (`database_specific.severity`) : `MODERATE` y désigne ce que
  le résumé appelle MEDIUM, et un avis sans sévérité compte en UNKNOWN ;
- affiche le résumé habituel, les lignes OSV, et applique `--fail-on`.

Sans `--osv`, un SBOM n'a rien à compter : l'outil le dit en une ligne qui
nomme l'option, avec le code 2. Les rapports des labs précédents restent
lisibles, et la suite de tests du lab 5 doit continuer de passer.

Sur la vraie base, ce SBOM rend une quarantaine de vulnérabilités, dont une
vingtaine d'avis PYSEC sans sévérité. Beaucoup recoupent un avis GitHub déjà
compté : rapprocher ces doublons par leurs `aliases` est une suite possible,
hors de ce lab. OSV y voit aussi la faille de `click` 8.3.1 (CVE-2026-7246)
que la base de Trivy ignorait le même jour.

## Repères

- `isinstance(donnees, dict) and donnees.get("bomFormat") == "CycloneDX"`.
- `str.startswith`, `removeprefix` et `partition("@")` découpent un `purl`.
- Un ensemble de tuples dédoublonne les composants, `sorted` les ordonne.
- Un petit dictionnaire de traduction règle `MODERATE`.

## Vérifier

```bash
dsoxlab check automatisation-lire-un-sbom
```

Cinq contrôles, vingt points chacun, sur le SBOM réel et une API OSV factice
qui rend de vrais identifiants avec des sévérités choisies.

## La version 5 de security_check.py

5 tâches, 100 points, 45 minutes.

Le projet est dans `challenge/work`, avec votre version 4. Vous apprenez à
l'outil à lire un SBOM CycloneDX et à le croiser avec OSV. Les tests
remplacent OSV par une API factice, désignée par `OSV_API_URL`.

### Tâche 1 : chaque composant PyPI est interrogé une fois (20 pts)

Avec `--osv`, une requête par composant PyPI distinct du SBOM, écosystème
`PyPI`. Les composants npm ne sont pas interrogés.

### Tâche 2 : le résumé compte les vulnérabilités connues d'OSV (20 pts)

Chaque vulnérabilité rendue par OSV est un finding. Sa sévérité est celle de
l'avis GitHub : `MODERATE` compte en MEDIUM, un avis sans sévérité en
UNKNOWN.

### Tâche 3 : un SBOM sans --osv est une entrée inexploitable (20 pts)

Code 2, une ligne d'erreur qui nomme `--osv`, aucune trace Python, aucun
résumé à zéro.

### Tâche 4 : le seuil s'applique à un SBOM (20 pts)

`--fail-on HIGH` rend 1 si OSV connaît un HIGH ou un CRITICAL, 0 si les avis
ne dépassent pas MODERATE.

### Tâche 5 : les rapports restent lisibles, les composants npm ignorés (20 pts)

Le rapport Trivy des labs précédents donne toujours ses 22 failles, et un
SBOM sans composant PyPI ne déclenche aucune requête.
