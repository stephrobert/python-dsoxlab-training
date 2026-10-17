# Formation Python : les labs vérifiables

**Langue :** [English](./README.md) · [Français](./README.fr.md)

[![CI](https://github.com/stephrobert/python-dsoxlab-training/actions/workflows/ci.yml/badge.svg)](https://github.com/stephrobert/python-dsoxlab-training/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/python-dsoxlab-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/python-dsoxlab-training)
[![Plumber compliance](https://score.getplumber.io/github.com/stephrobert/python-dsoxlab-training.svg)](https://score.getplumber.io/github.com/stephrobert/python-dsoxlab-training)
[![SLSA 3](https://slsa.dev/images/gh-badge-level3.svg)](https://slsa.dev)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

Les labs de la piste **Automatisation** de la
[formation Python](https://blog.stephane-robert.info/docs/developper/programmation/python/)
du blog, joués avec [dsoxlab](https://github.com/stephrobert/dsoxlab).

## Ce que c'est

**Sept labs, un seul outil.** Vous n'écrivez pas sept exercices : vous
construisez `security_check.py` lab après lab, et chaque lab part du résultat
du précédent. Lire le rapport d'un scanner, interroger la base OSV, analyser un
vrai rapport Trivy avec ses résultats imbriqués et ses clés absentes, rendre un
code de sortie qu'un pipeline sait exploiter, tester son propre outil, puis le
brancher dans un job de CI.

Cet enchaînement est le sujet. Un outil qui lit un seul JSON bien formé est un
exercice ; un outil qui survit à un vrai rapport Trivy, rend un code qu'un
pipeline lit, et porte des tests qui attrapent ses propres bugs, est quelque
chose dont vous vous servirez le lendemain.

## Prérequis

- **`mise`** : il installe `uv` et Python aux versions épinglées dans
  [`mise.toml`](./mise.toml), sans curl d'archive ni gestionnaire de paquets
  système.
- **`git`**
- **`dsoxlab`**, le moteur, installé en outil autonome (voir plus bas).
- **Docker**, pour le **dernier lab seulement**
  (`automatisation-dans-la-ci`), qui rejoue un job GitHub Actions en local avec
  `act`. Les six autres ne demandent que Python.

**Aucune VM, aucun `dsoxlab provision`.** Ce catalogue ne déclare aucun bloc
`infra:` : tous ses labs sont `runtime: shell` et tournent sur votre poste,
dans leur propre projet `uv`.

## Installation

`dsoxlab` est publié sur [PyPI](https://pypi.org/project/dsoxlab/).
Installez-le en outil autonome, pour qu'il reste hors de ce dépôt :

```bash
# 1. La CLI dsoxlab (outil externe, hors de ce dépôt)
uv tool install dsoxlab

# 2. Ce catalogue de labs
git clone https://github.com/stephrobert/python-dsoxlab-training.git
cd python-dsoxlab-training

# 3. Les outils, aux versions épinglées
mise install

# 4. Vérifier que le contrat est valide
dsoxlab validate-structure
```

### Votre premier lab, en cinq minutes

```bash
export LAB_HOME=$PWD
dsoxlab list-labs                                  # les sept labs, dans l'ordre
dsoxlab run       automatisation-lire-un-rapport   # poser l'état de départ
dsoxlab challenge automatisation-lire-un-rapport   # lire la mission
# ... vous travaillez dans challenge/work ...
dsoxlab check     automatisation-lire-un-rapport   # lancer les tests, enregistrer le score
```

C'est `run` qui prépare `challenge/work` et copie les fixtures que le lab
déclare. Un `check` joué sur un lab jamais démarré ne mesure rien, et le dit
au lieu d'enregistrer un 0.

### Garder à jour

```bash
uv tool upgrade dsoxlab        # le moteur, publié sur PyPI
git -C <ce dépôt> pull         # le catalogue
```

Le moteur et le catalogue avancent indépendamment : un nouveau `dsoxlab` ne
demande jamais de recloner les labs, et de nouveaux labs ne demandent jamais de
mettre l'outil à jour, tant que la version du contrat correspond. `dsoxlab
doctor` dit ce dont ce dépôt a besoin, et ce dont il n'a pas besoin.

## Comment ça marche

### Le contrat déclaratif, à deux niveaux

Le catalogue est décrit par des données, pas par du code, et c'est ce qui garde
le moteur `dsoxlab` indépendant du domaine :

- **`meta.yml`** à la racine déclare l'identité du dépôt et l'**ordre** des
  sections affichées par `list-labs` ;
- **`lab.yaml`** par lab déclare ses `skills`, son `level`, son `runtime`
  (type, fixtures, services), ses `distros`, son `doc_url` et un bloc
  `validation`. Un `lab.fr.yaml` surcharge `title` et `description` en
  français, et rien d'autre.

`dsoxlab validate-structure` contrôle tout le contrat : `meta.yml` bien formé,
chaque lab référencé présent avec un `lab.yaml` valide, chaque fichier de test
et de fixture déclaré réellement là, et chaque lien relatif d'un README qui
mène quelque part.

### Le cycle de vie d'un lab

```bash
dsoxlab list-labs              # parcourir le catalogue
dsoxlab show      <id>         # métadonnées et état d'un lab
dsoxlab run       <id>         # poser l'état de départ
dsoxlab challenge <id>         # lire la mission, sans pas-à-pas
dsoxlab hint      <id>         # révéler un indice (déduit du score)
dsoxlab check     <id>         # lancer les tests, calculer et enregistrer le score
dsoxlab clean     <id>         # retirer le répertoire de travail
dsoxlab progress               # avancement par section, score moyen
```

### Les runtimes

| Runtime | Ce que le lab demande |
|---|---|
| `shell` | un terminal, `uv` et Python. Votre outil tourne dans **son propre** projet `uv`, avec ses dépendances. |
| `shell` + Docker | le dernier lab seulement, qui rejoue un job GitHub Actions avec `act`. |

La séparation des environnements compte ici : votre outil a besoin de
`requests` et de `click`, et les tests de dsoxlab tournent dans
l'environnement de dsoxlab, qui n'a ni l'un ni l'autre. C'est pourquoi les labs
appellent `uv run` au lieu d'importer votre code.

### Le modèle de validation

La validation **prouve le comportement, elle ne fait pas confiance à
l'apprenant**. Chaque lab porte des tests `pytest` sous `challenge/tests/` qui
lancent votre outil en sous-processus et lisent ce qu'il écrit et ce qu'il
rend : jamais ce qu'un fichier contient.

Et un lab est prouvé **dans les deux sens** : les tests doivent échouer avant
le travail et passer après. Un test vert avant le travail n'est pas un test,
c'est une hypothèse sur le setup. `scripts/valider-labs.py` joue ce cycle
entier sur chaque lab et écrit son verdict dans
[`validation-labs.json`](./validation-labs.json), qui est versionné : un lab
livré sans verdict ne prouve rien.

Les solutions de référence vivent sous `labs/<lab>/solution/`, **en clair**, et
c'est délibéré ici : le point de départ de chaque lab *est* la solution du
précédent, donc le fichier doit pouvoir être copié comme fixture. Le lire, c'est
vous gâcher le lab.

### Score, indices, avancement

`check` enregistre un score (tests réussis sur total, moins le coût des indices
révélés). Les indices sont **en base64** dans `challenge/hints.yaml`, pour qu'on
n'y accède pas en ouvrant le fichier, et leur coût croît avec leur précision.
L'historique vit dans une base SQLite **locale à ce dépôt**.

Une exécution qui n'a rien mesuré n'est ni une réussite ni un échec : si tous
les tests collectés skippent, `check` n'enregistre aucune note et dit pourquoi.
Un 0 accuserait le lab de ce qui manque au poste.

## Catalogue

<!-- LABS:START -->
### Automatisation : un outil de sécurité, pas à pas

| Lab (id) | Titre | Niveau | Certif | Runtime | Guide compagnon |
|---|---|---|---|---|---|
| `automatisation-lire-un-rapport` | Lire le rapport d'un scanner : compter les vulnérabilités par sévérité | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/programmation/python/json/) |
| `automatisation-interroger-osv` | Interroger l'API OSV : ce qu'on sait de chaque paquet du rapport | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/programmation/python/requests/) |
| `automatisation-rapport-trivy` | Lire un vrai rapport Trivy : résultats imbriqués, clés absentes et doublons | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/programmation/python/dictionnaire/) |
| `automatisation-code-de-sortie` | Un code de sortie qu'un pipeline sait exploiter : --fail-on avec Click | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/programmation/python/click/) |
| `automatisation-tester-son-outil` | Tester son outil : une suite pytest qui attrape quatre vrais bugs | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/programmation/python/tests/pytest/) |
| `automatisation-dans-la-ci` | Une porte de sécurité dans le pipeline : security_check.py dans GitHub Actions | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/pipeline-cicd/github/securite/lab/pipeline-ci/) |
| `automatisation-lire-un-sbom` | Lire un SBOM : croiser un inventaire CycloneDX avec la base OSV | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/securiser/supply-chain/sbom/) |

_7 labs, table générée par `scripts/gen_catalog.py`._
<!-- LABS:END -->

## Contribuer

Lisez [`CONTRIBUTING.fr.md`](./CONTRIBUTING.fr.md). En bref : un lab est prouvé
**dans les deux sens** avant d'être fusionné, `dsoxlab validate-structure` est
vert, et l'énoncé existe en anglais et en français.

Tout ce qui s'affiche est bilingue. Un document traduit d'un seul côté est
signalé par le validateur, et non laissé à la bonne volonté.

## Licence

Voir [`LICENSE`](./LICENSE).
