# Lire un vrai rapport Trivy

Troisième lab du fil rouge de la piste **Automatisation** de la formation
Python, jumelé à la leçon « Les dictionnaires ». Il part de votre
`security_check.py` du lab précédent et lui apprend le format réel de Trivy :
des résultats imbriqués par cible, une clé absente quand une cible est saine,
et des failles répétées d'une cible à l'autre, à compter une seule fois.

| | |
|---|---|
| Cible | votre poste : Python et uv (`mise install`), aucun Docker |
| Durée | environ 40 minutes |
| Leçon jumelée | [Les dictionnaires](https://blog.stephane-robert.info/docs/developper/programmation/python/dictionnaire/) |
| Précédent | `automatisation-interroger-osv` |
| Suite | `automatisation-code-de-sortie` part de votre solution |

```bash
dsoxlab run   automatisation-rapport-trivy
cd labs/automatisation-rapport-trivy/challenge/work
uv run python security_check.py exemples/trivy.json
dsoxlab check automatisation-rapport-trivy
```

Le rapport d'exemple est une sortie réelle de Trivy 0.74.0, relevée le
2026-10-02 sur un projet à trois fichiers `requirements.txt` : 26
occurrences, 22 vulnérabilités distinctes. Les tests le reprennent, et y
ajoutent des rapports Trivy générés au hasard.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
