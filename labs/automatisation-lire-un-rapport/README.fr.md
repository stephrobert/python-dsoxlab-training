# Lire le rapport d'un scanner

Premier lab du fil rouge de la piste **Automatisation** de la formation
Python, jumelé à la leçon « Manipuler du JSON ». Il pose la version 1 de
`security_check.py`, l'outil que les quatre labs suivants font grandir :
lire un export JSON de findings, les compter par sévérité, et refuser une
entrée invalide comme le fait un outil de pipeline, en une ligne et avec un
code de sortie.

| | |
|---|---|
| Cible | votre poste : Python et uv (`mise install`), aucun Docker |
| Durée | environ 30 minutes |
| Leçon jumelée | [Manipuler du JSON](https://blog.stephane-robert.info/docs/developper/programmation/python/json/) |
| Suite | `automatisation-interroger-osv` part de votre solution |

```bash
mise install                                    # uv et Python
dsoxlab run   automatisation-lire-un-rapport    # pose le projet dans challenge/work
cd labs/automatisation-lire-un-rapport/challenge/work
uv run python security_check.py exemples/findings.json
dsoxlab check automatisation-lire-un-rapport    # lance l'outil et note
```

Les tests lancent l'outil exactement comme vous, avec `uv run`, sur des
rapports qu'ils écrivent eux-mêmes, dont deux tirés au hasard. Ils lisent le
résumé affiché, la sortie d'erreur et le code de sortie, jamais le code
source.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable, répertoire de travail retiré par
`dsoxlab clean`. Le verdict est dans `validation-labs.json`.
