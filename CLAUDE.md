# Instructions Claude Code : `python-dsoxlab-training`

Catalogue de **labs vérifiables** pour la formation Python du blog
`blog.stephane-robert.info`, joué par la CLI **dsoxlab** (`~/Projets/dsoxlab`).
Ce dépôt n'est qu'un **fournisseur de contenu** : `meta.yml`, `labs/**`, les
tests du catalogue, la documentation. Modèle et doctrine repris de
`github-actions-training`, dont on garde les règles sans les recopier ici
quand elles valent telles quelles.

## Pourquoi ce dépôt existe

Décision de Stéphane du 2026-10-02, après une revue externe du parcours
métier DevSecOps : Python passe **avant la CI**, en piste courte
`automatisation`, et l'apprenant y construit **un seul outil**,
`security_check.py`, lab après lab. La formation Python avait alors 55 quiz
et **aucun lab** : rien ne prouvait qu'un apprenant sache écrire l'outil
qu'un pipeline appelle.

Plan et état côté site : `~/Projets/test-astro-5/todo/fil-rouge-security-check.md`.

## Le fil rouge

Le point de départ d'un lab est la **solution du précédent**. L'ordre de
`meta.yml` est donc celui du jeu, et une correction de la solution d'un lab
se reporte dans les `fixtures/` du suivant.

| Lab | Version de l'outil |
|---|---|
| `automatisation-lire-un-rapport` | lire un export JSON, compter par sévérité, code 2 sur entrée invalide |
| `automatisation-interroger-osv` | `--osv` : l'API OSV, délai maximal, pannes dites en une ligne |
| `automatisation-rapport-trivy` | le vrai format Trivy : cibles imbriquées, clé absente, doublons |
| `automatisation-code-de-sortie` | Click, `--fail-on` : 0, 1 ou 2 |
| `automatisation-tester-son-outil` | la suite pytest de l'apprenant, jugée par mutation |

## L'architecture : l'outil tourne dans SON projet

`dsoxlab check` lance pytest dans l'environnement de dsoxlab
(`dsoxlab/services/lab_service.py::resolve_pytest_cmd`), qui n'a ni
`requests` ni `click`. Les tests lancent donc l'outil par
`uv run --directory <work>` (`conftest.py::lancer_outil`), dans le projet de
l'apprenant et avec ses dépendances. Une dépendance oubliée y échoue comme
chez lui, et `uv add` fait partie de ce qui s'apprend.

- Aucun bloc `infra:`, aucune VM, aucun Docker : tous les labs sont
  `runtime.type: shell`.
- `mise.toml` épingle uv et Python ; `.python-version` force uv sur ce
  Python. `scripts/valider-labs.py` refuse de jouer avec d'autres versions.
- Les tests n'appellent **jamais** la vraie API OSV : `conftest.py::serveur_osv`
  répond comme `POST /v1/query` et enregistre les requêtes. L'outil le trouve
  par `OSV_API_URL`.

## Règles reprises du modèle, qui valent ici

1. **Un lab s'éprouve dans les deux sens** : 0 avant, 100 avec `solution/`,
   0 au rejeu, poste rendu intact. `uv run scripts/valider-labs.py`, verdict
   dans `validation-labs.json`. Un lab absent de ce fichier est livrable, pas
   validé.
2. **Les tests lisent ce que l'outil fait** (sortie, sortie d'erreur, code),
   jamais son code source.
3. **Un test vrai avant le travail n'est pas un test.** Le fil rouge rend le
   piège fréquent : la version précédente sait déjà faire la moitié du lab.
   Chaque test exige donc la nouveauté du lab (une option, un format).
4. **Ce qui est attendu se calcule** : rapports tirés au hasard, graine
   affichée en cas d'échec.
5. **Fichiers canoniques en anglais**, doublés en français ; on rédige en
   français d'abord.

## Écrire un lab

```bash
export LAB_HOME=$PWD
dsoxlab new lab automatisation-<sujet>
rmdir labs/automatisation-<sujet>/challenge/work   # voir le piège ci-dessous
```

Les indices s'écrivent **en clair** dans `challenge/hints.source.yaml` (exclu
du dépôt : le publier rendrait l'encodage vain), puis
`uv run python scripts/ecrire_indices.py labs/<id>` produit `hints.yaml` en
base64 et vérifie qu'il se relit.

Le dernier lab juge la suite de l'apprenant sur des **mutants** générés par
`scripts/generer_mutants.py` depuis `challenge/tests/reference/`. Quand la
référence change, on régénère : le script refuse un mutant identique à
l'original.

## Pièges mesurés

- **`dsoxlab new lab` crée un `challenge/work/` vide** (constaté le
  2026-10-02 sur les cinq labs). `find -type f` ne le montre pas, et
  `valider-labs.py` refuse alors de partir, puis le nettoie en sortant : le
  second passage réussit, ce qui a l'air d'un comportement aléatoire.
  `rmdir` après la création.
- **zsh ne découpe pas une variable** : `$args` passe en un seul argument.
  Les boucles de test vont dans un script `bash`.
- **Le `python` de `uv run`** est celui du venv : sans `.python-version`, uv
  prenait un autre 3.14 que celui de mise.

## Ne pas pousser

Le dépôt est **local**. Créer `stephrobert/python-dsoxlab-training` et pousser
sont une décision de Stéphane.
