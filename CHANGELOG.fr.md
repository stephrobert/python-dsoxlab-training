# Journal des modifications

**Langue :** [English](./CHANGELOG.md) · [Français](./CHANGELOG.fr.md)

Toutes les modifications notables de ce projet sont consignées dans ce fichier.
Le format suit [Keep a Changelog](https://keepachangelog.com/fr/).

Ce dépôt est un **catalogue de contenu**, pas une bibliothèque : il n'est pas
versionné et ne publie aucune release. Les entrées ci-dessous datent les
modifications du catalogue, et l'unité qui compte est le lab.

## [0.2.0] - 2026-10-17

### Modifié

- **Le validateur lit le contrat, plus l'encadré du terminal.**
  `scripts/valider-labs.py` lisait le score dans ce que `dsoxlab check`
  *affiche*. Cet encadré est de l'interface : il a changé en dsoxlab 0.4.0 et
  la regex a cessé de trouver quoi que ce soit. Il lit désormais
  `check --json`, qui porte un `schema`, et cette lecture vit dans
  `scripts/verdict_check.py`, **identique dans les douze catalogues**.

- **Trois verdicts, pas deux.** Une exécution dont tous les tests collectés ont
  skippé n'a rien mesuré : elle est **SKIP**, ni verte ni rouge, et reste à
  mesurer. La peindre en rouge accuserait le lab de ce qui manque au poste.
  `--check` sort donc en `10` dans ce cas, contre `1` pour un ROUGE, à l'image
  de `dsoxlab doctor --strict` où 9 se répare et 10 se remesure.

- **Le README prend la structure de référence** commune aux douze catalogues :
  quatorze sections, dans les deux langues. Sept d'entre elles décrivent
  dsoxlab et non le sujet, et sont donc identiques partout.

### Exige

- **dsoxlab 0.4.1 ou plus récent**, qui a introduit le champ `status` de
  `check --json`. Sans lui, le validateur refuse de conclure plutôt que de
  deviner.

## [0.1.1] - 2026-10-14

### Modifié

- Les cinq labs du fil rouge rejoués après la modification du `conftest.py`.
- La procédure de release réatteste les labs modifiés depuis leur verdict.

### Corrigé

- Cinq actions GitHub remises à jour.

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

[Non publié]: https://github.com/stephrobert/python-dsoxlab-training/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/stephrobert/python-dsoxlab-training/releases/tag/v0.1.1
[0.1.0]: https://github.com/stephrobert/python-dsoxlab-training/releases/tag/v0.1.0
