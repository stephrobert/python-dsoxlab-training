# Lire un SBOM

Septième lab du fil rouge de la piste **Automatisation** de la formation
Python, jumelé à la leçon « SBOM : l'inventaire de ce qu'on livre » de la
formation DevSecOps. Un SBOM liste des composants, pas des failles : l'outil
apprend à croiser un inventaire CycloneDX réel avec la base OSV, et à juger
le résultat avec le même seuil que les rapports de scanner.

| | |
|---|---|
| Cible | votre poste : Python et uv (`mise install`), aucun Docker |
| Durée | environ 45 minutes |
| Leçon jumelée | [SBOM : l'inventaire de ce qu'on livre](https://blog.stephane-robert.info/docs/securiser/supply-chain/sbom/) |
| Précédent | `automatisation-dans-la-ci` |

```bash
dsoxlab run   automatisation-lire-un-sbom
cd labs/automatisation-lire-un-sbom/challenge/work
uv run python security_check.py sbom/tableau-de-bord.cdx.json --osv   # la vraie API OSV
dsoxlab check automatisation-lire-un-sbom
```

Le SBOM d'exemple est une sortie réelle de syft 1.51.1 (CycloneDX 1.7),
relevée le 2026-10-02 sur un projet Python doublé d'une interface npm, sans
aucun chemin local. Les tests le reprennent, avec une API OSV factice.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
