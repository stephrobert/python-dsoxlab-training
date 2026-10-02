# Tester son outil

Cinquième et dernier lab du fil rouge de la piste **Automatisation** de la
formation Python, jumelé à la leçon « pytest en pratique ». L'outil est
fini ; il lui manque des tests. Votre suite est notée sur ce qu'elle attrape :
elle doit passer sur l'outil juste et échouer sur quatre mutants, chacun
porteur d'un bug réaliste. C'est ce qu'on appelle le test par mutation, et
c'est la seule façon de savoir si une suite verte protège de quelque chose.

| | |
|---|---|
| Cible | votre poste : Python et uv (`mise install`), aucun Docker |
| Durée | environ 45 minutes |
| Leçon jumelée | [pytest en pratique](https://blog.stephane-robert.info/docs/developper/programmation/python/tests/pytest/) |
| Précédent | `automatisation-code-de-sortie` |

```bash
dsoxlab run   automatisation-tester-son-outil
cd labs/automatisation-tester-son-outil/challenge/work
uv add --dev pytest
uv run pytest -v
dsoxlab check automatisation-tester-son-outil
```

Les mutants vivent dans `challenge/tests/mutants/`. Ils se génèrent depuis
l'outil de référence par `scripts/generer_mutants.py`, qui vérifie que
chacun diffère réellement de l'original.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
