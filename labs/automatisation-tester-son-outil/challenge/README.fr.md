# Challenge : la suite de tests de security_check.py

5 tâches, 100 points, 45 minutes.

Le projet est dans `challenge/work`. Vous écrivez `tests/`, et vous ne
touchez pas à `security_check.py` : les contrôles le remplacent dans une
copie du projet, par la référence puis par chacun des quatre mutants.

### Tâche 1 : la suite passe sur l'outil juste (20 pts)

`uv run pytest` passe entièrement sur l'outil de référence, avec au moins
cinq tests.

### Tâche 2 : la suite attrape un seuil exclusif (20 pts)

Elle échoue sur un mutant où `--fail-on HIGH` ne compte plus les HIGH.

### Tâche 3 : la suite attrape une casse non normalisée (20 pts)

Elle échoue sur un mutant où une sévérité en minuscules compte en UNKNOWN.

### Tâche 4 : la suite attrape des doublons Trivy (20 pts)

Elle échoue sur un mutant où une faille répétée dans deux cibles d'un rapport
Trivy compte deux fois.

### Tâche 5 : la suite attrape un rapport absent qui rend 1 (20 pts)

Elle échoue sur un mutant où un rapport illisible rend le code 1, celui qui
signifie « seuil atteint », au lieu de 2.

Les tâches 2 à 5 exigent aussi la tâche 1 : une suite qui échoue partout
« attrape » tous les mutants et ne prouve rien.
