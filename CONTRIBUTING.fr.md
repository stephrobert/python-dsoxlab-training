# Contribuer à python-dsoxlab-training

**Langue :** [English](./CONTRIBUTING.md) · [Français](./CONTRIBUTING.fr.md)

Ce dépôt est un **catalogue de labs** consommé par la CLI
[`dsoxlab`](https://github.com/stephrobert/dsoxlab). Les contributions sont de
nouveaux labs, des corrections et des traductions. La CLI vit dans son propre
dépôt : n'ajoutez pas de code de moteur ici.

## Installation

```bash
uv tool install dsoxlab        # la CLI (outil externe)
git clone https://github.com/stephrobert/python-dsoxlab-training.git
cd python-dsoxlab-training
mise install                   # uv et Python épinglés
dsoxlab validate-structure     # vérifier le contrat
```

Ni VM, ni Docker, ni `dsoxlab provision` : tous les labs sont en
`runtime: shell`, et l'outil de l'apprenant tourne sur son poste, dans son
propre projet uv.

## Le fil rouge

Les labs de la section `automatisation` construisent **un seul outil**,
`security_check.py`, version après version. Le point de départ d'un lab est
la solution de référence du précédent : une correction d'une solution se
reporte dans les `fixtures/` du lab suivant. L'ordre de `meta.yml` est celui
dans lequel les labs se jouent, et il ne se réordonne pas.

C'est aussi pourquoi les solutions **ne sont pas chiffrées**, contrairement
aux catalogues Linux, Terraform et Ansible : chaque solution est livrée en
clair comme point de départ du lab suivant, et la référence du dernier lab est
la solution du quatrième. Le chiffrement ne cacherait rien et ajouterait une
clé à ne pas perdre.

## La règle d'or : un lab s'éprouve dans les deux sens

Un test qui passe ne prouve rien tant qu'on n'a pas vu échouer ce qui doit
**échouer** :

```bash
uv run scripts/valider-labs.py --lab <id>
```

joue `dsoxlab run`, `check` (doit rendre 0), la solution de référence,
`check` (doit rendre 100), puis `clean`, `run`, `check` (0 à nouveau), et
consigne le verdict dans `validation-labs.json`. Un lab absent de ce fichier
est livrable, pas validé.

Pour chaque test, demandez-vous : **serait-il vert si l'apprenant ne faisait
rien ?** Avec un fil rouge, le piège est fréquent : la version précédente de
l'outil fait déjà la moitié du lab. Chaque test doit exiger ce que le lab
ajoute.

## Ce que les tests doivent lire

Ce que l'outil **fait** : sa sortie, sa sortie d'erreur, son code de sortie,
et ce qu'il a envoyé à l'API OSV factice. Jamais son code source. Les tests
lancent l'outil comme l'apprenant, avec `uv run` dans son projet
(`conftest.py::lancer_outil`) : `dsoxlab check` lance pytest dans
l'environnement de dsoxlab, qui n'a ni `requests` ni `click`.

Ce qui est attendu se **calcule**, il ne s'écrit pas : les rapports sont
tirés au hasard, et la graine s'affiche en cas d'échec.

## Anatomie d'un lab

```text
labs/<lab>/
├── lab.yaml            # le contrat (id, niveau, runtime, fixtures, validation…)
├── lab.fr.yaml         # surcharge française de title/description SEULEMENT
├── README.md / README.fr.md        # la présentation
├── scenario.md / scenario.fr.md    # la situation, l'état visé, la preuve
├── fixtures/           # le point de départ, copié dans challenge/work
├── solution/           # la solution de référence, posée sur challenge/work
└── challenge/
    ├── README.md / README.fr.md    # la mission, en exigences numérotées
    ├── hints.yaml                  # indices en base64, quatre niveaux de coût
    └── tests/test_functional.py    # la preuve
```

Les indices s'écrivent en clair dans `challenge/hints.source.yaml` (non
versionné), puis `uv run python scripts/ecrire_indices.py labs/<id>` les
encode.

Le dernier lab juge la suite de tests de l'apprenant sur des **mutants**
générés par `scripts/generer_mutants.py` depuis `challenge/tests/reference/`.

## Contrôles locaux avant une PR

```bash
dsoxlab validate-structure          # le contrat meta.yml + lab.yaml
uv run scripts/valider-labs.py      # chaque lab, dans les deux sens
uv run pytest tests/ -q             # les méta-tests du dépôt
uv run python scripts/gen_catalog.py --check   # le catalogue des README
```

## Conventions

- **Identifiant de lab :** `<section>-<sujet>`, identique au nom du
  répertoire.
- **Commits :** en français, un sujet factuel qui dit **ce qui a changé et
  pourquoi**, sans préfixe conventionnel.
- **i18n :** le fichier sans suffixe est en anglais (langue officielle du
  dépôt), `*.fr.md` est la traduction française. Les deux disent la même
  chose.
- **Style :** ni emoji ni tiret cadratin dans ce que lit l'apprenant. Les
  messages d'assertion enseignent : ils disent ce qui ne va pas, et pourquoi.

## Pull requests

Travaillez sur une branche dédiée, gardez `dsoxlab validate-structure` et
`valider-labs.py` au vert, et reliez la capacité ou l'issue traitée.
