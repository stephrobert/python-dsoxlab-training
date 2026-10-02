# Une porte de sécurité dans le pipeline

Sixième et dernier lab du fil rouge de la piste **Automatisation** de la
formation Python, jumelé à la leçon GitHub Actions « Pipeline CI durci ».
L'outil construit lab après lab devient une **porte** : un workflow lance ses
tests, puis le fait juger le rapport du scanner, et arrête la branche dès
qu'une vulnérabilité CRITICAL apparaît.

| | |
|---|---|
| Cible | votre poste : uv, Python et act (`mise install`), **Docker** qui répond |
| Durée | environ 40 minutes |
| Leçon jumelée | [Pipeline CI durci](https://blog.stephane-robert.info/docs/pipeline-cicd/github/securite/lab/pipeline-ci/) |
| Précédent | `automatisation-tester-son-outil` |

```bash
mise install                                   # uv, Python et act
dsoxlab run   automatisation-dans-la-ci
cd labs/automatisation-dans-la-ci/challenge/work
act push                                       # joue votre workflow
dsoxlab check automatisation-dans-la-ci
```

C'est le seul lab du catalogue qui demande Docker : act joue le workflow dans
l'image du runner `ubuntu-24.04`, épinglée par digest dans `.actrc`. Les
tests rejouent votre workflow sur des copies du projet, rapport et outil
remplacés, et lisent le résultat du job et les lignes écrites.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
