# Interroger l'API OSV

Deuxième lab du fil rouge de la piste **Automatisation** de la formation
Python, jumelé à la leçon « Appeler des API avec requests ». Il part de votre
`security_check.py` du lab précédent et lui fait interroger la base publique
OSV pour chaque paquet du rapport : une dépendance déclarée avec uv, un appel
HTTP borné dans le temps, et des pannes réseau traitées comme le fait un
outil de pipeline.

| | |
|---|---|
| Cible | votre poste : Python et uv (`mise install`), aucun Docker |
| Durée | environ 40 minutes |
| Leçon jumelée | [Appeler des API avec requests](https://blog.stephane-robert.info/docs/developper/programmation/python/requests/) |
| Précédent | `automatisation-lire-un-rapport` |
| Suite | `automatisation-rapport-trivy` part de votre solution |

```bash
dsoxlab run   automatisation-interroger-osv
cd labs/automatisation-interroger-osv/challenge/work
uv add requests
uv run python security_check.py exemples/findings.json --osv   # la vraie API OSV
dsoxlab check automatisation-interroger-osv
```

Les tests ne touchent pas la vraie base, dont les réponses changent chaque
semaine : une API factice locale répond comme OSV et enregistre chaque
requête. Ils vérifient ce que l'outil a demandé, ce qu'il affiche, et qu'une
API en panne ou muette ne produit ni trace ni blocage.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
