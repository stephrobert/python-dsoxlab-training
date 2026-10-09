# Journal des modifications

**Langue :** [English](./CHANGELOG.md) · [Français](./CHANGELOG.fr.md)

Toutes les modifications notables de ce projet sont consignées dans ce fichier.
Le format suit [Keep a Changelog](https://keepachangelog.com/fr/).

Ce dépôt est un **catalogue de contenu**, pas une bibliothèque : il n'est pas
versionné et ne publie aucune release. Les entrées ci-dessous datent les
modifications du catalogue, et l'unité qui compte est le lab.

## [0.1.0] - 2026-10-09

### Ajouté

- **La section `automatisation`**, sept labs qui construisent un seul outil,
  `security_check.py`, pour la piste Automatisation de la formation Python du
  blog (2026-10-02). Chaque lab part de la solution du précédent :
  - `automatisation-lire-un-rapport` lit un export JSON de findings et les
    compte par sévérité, avec le code 2 sur une entrée inexploitable ;
  - `automatisation-interroger-osv` interroge l'API OSV avec un délai
    maximal, vérifié contre une API factice locale qui enregistre chaque
    requête ;
  - `automatisation-rapport-trivy` lit un vrai rapport Trivy 0.74.0 :
    26 occurrences, 22 vulnérabilités distinctes, une cible sans clé
    `Vulnerabilities` ;
  - `automatisation-code-de-sortie` passe sous Click et ajoute `--fail-on` :
    0, 1 ou 2, les codes qu'un pipeline exploite ;
  - `automatisation-tester-son-outil` note la suite pytest de l'apprenant sur
    quatre mutants de l'outil de référence ;
  - `automatisation-dans-la-ci` fait de l'outil une porte dans GitHub
    Actions : les tests d'abord, puis le seuil CRITICAL, joué avec act. Le
    seul lab qui demande Docker ;
  - `automatisation-lire-un-sbom` croise un vrai SBOM CycloneDX (syft
    1.51.1) avec OSV : chaque vulnérabilité connue devient un finding, avec
    la sévérité de son avis GitHub (MODERATE en MEDIUM).
- La table anglaise des README signale les guides qui n'existent qu'en
  français.
- Les labs éprouvés dans les deux sens par `scripts/valider-labs.py` :
  0 avant le travail, 100 après la solution, 0 à nouveau après `clean` et
  `run`. Verdicts dans `validation-labs.json`.

[Non publié]: https://github.com/stephrobert/python-dsoxlab-training/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/stephrobert/python-dsoxlab-training/releases/tag/v0.1.0
