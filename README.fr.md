# Formation Python : les labs vérifiables

**Langue :** [English](./README.md) · [Français](./README.fr.md)

[![CI](https://github.com/stephrobert/python-dsoxlab-training/actions/workflows/ci.yml/badge.svg)](https://github.com/stephrobert/python-dsoxlab-training/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/python-dsoxlab-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/python-dsoxlab-training)
[![Plumber compliance](https://score.getplumber.io/github.com/stephrobert/python-dsoxlab-training.svg)](https://score.getplumber.io/github.com/stephrobert/python-dsoxlab-training)
[![SLSA 3](https://slsa.dev/images/gh-badge-level3.svg)](https://slsa.dev)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

Les labs de la piste **Automatisation** de la
[formation Python](https://blog.stephane-robert.info/docs/developper/programmation/python/)
du blog, joués avec [dsoxlab](https://github.com/stephrobert/dsoxlab). Un seul
outil, `security_check.py`, construit lab après lab : lire le rapport d'un
scanner, interroger la base OSV, analyser un vrai rapport Trivy, rendre un
code de sortie qu'un pipeline sait exploiter, et le tester.

Chaque lab a un point de départ (la solution du précédent), une vérification
qui exécute votre code, une solution de référence, et a été éprouvé dans les
deux sens : 0 avant le travail, 100 après. Le verdict de chaque lab est dans
`validation-labs.json`.

```bash
mise install                                     # uv et Python
export LAB_HOME=$PWD
dsoxlab list-labs
dsoxlab run   automatisation-lire-un-rapport
dsoxlab check automatisation-lire-un-rapport
```

Aucune VM, aucun Docker : l'outil tourne sur votre poste, dans son propre
projet uv.

<!-- LABS:START -->
### Automatisation : un outil de sécurité, pas à pas

| Lab (id) | Titre | Niveau | Certif | Runtime | Guide compagnon |
|---|---|---|---|---|---|
| `automatisation-lire-un-rapport` | Lire le rapport d'un scanner : compter les vulnérabilités par sévérité | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/programmation/python/json/) |
| `automatisation-interroger-osv` | Interroger l'API OSV : ce qu'on sait de chaque paquet du rapport | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/programmation/python/requests/) |
| `automatisation-rapport-trivy` | Lire un vrai rapport Trivy : résultats imbriqués, clés absentes et doublons | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/programmation/python/dictionnaire/) |
| `automatisation-code-de-sortie` | Un code de sortie qu'un pipeline sait exploiter : --fail-on avec Click | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/programmation/python/click/) |
| `automatisation-tester-son-outil` | Tester son outil : une suite pytest qui attrape quatre vrais bugs | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/programmation/python/tests/pytest/) |

_5 labs, table générée par `scripts/gen_catalog.py`._
<!-- LABS:END -->
