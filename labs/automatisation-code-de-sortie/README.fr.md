# Un code de sortie qu'un pipeline sait exploiter

Quatrième lab du fil rouge de la piste **Automatisation** de la formation
Python, jumelé à la leçon « Click : des CLI en Python ». Il part de votre
`security_check.py` du lab précédent, passe sa ligne de commande sous Click
et lui ajoute `--fail-on` : l'outil cesse de seulement décrire, il décide, et
il le dit dans la seule langue qu'un pipeline comprend, son code de sortie.

| | |
|---|---|
| Cible | votre poste : Python et uv (`mise install`), aucun Docker |
| Durée | environ 40 minutes |
| Leçon jumelée | [Click : des CLI en Python](https://blog.stephane-robert.info/docs/developper/programmation/python/click/) |
| Précédent | `automatisation-rapport-trivy` |
| Suite | `automatisation-tester-son-outil` part de votre solution |

```bash
dsoxlab run   automatisation-code-de-sortie
cd labs/automatisation-code-de-sortie/challenge/work
uv add click
uv run python security_check.py exemples/trivy.json --fail-on CRITICAL; echo "code : $?"
dsoxlab check automatisation-code-de-sortie
```

Trois codes, et la confusion qu'ils évitent : 0 rien n'atteint le seuil,
1 le seuil est atteint, 2 l'entrée est inexploitable. Un rapport absent qui
rendrait 1 arrêterait un déploiement pour une faille qui n'existe pas.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
