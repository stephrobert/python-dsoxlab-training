# Challenge : la version 1 de security_check.py

5 tâches, 100 points, 30 minutes.

Le projet est dans `challenge/work`. Vous écrivez `lire_findings` et
`compter` dans `security_check.py`, et vous ajustez `main` pour les erreurs.
Les tests lancent l'outil comme vous, avec `uv run python security_check.py`,
et lisent ce qu'il affiche et le code qu'il rend.

### Tâche 1 : le résumé compte chaque sévérité (20 pts)

Pour un rapport quelconque, l'outil affiche six lignes, `CRITICAL: n`,
`HIGH: n`, `MEDIUM: n`, `LOW: n`, `UNKNOWN: n` puis `TOTAL: n`, et sort en 0.

### Tâche 2 : les sévérités inconnues comptent en UNKNOWN (20 pts)

`critical` et `High` comptent comme `CRITICAL` et `HIGH`. Une sévérité
absente, vide, nulle ou hors de la liste compte en `UNKNOWN`.

### Tâche 3 : un rapport vide rend des zéros (20 pts)

`[]` est un scan propre, pas une erreur : six lignes à zéro, code 0.

### Tâche 4 : un fichier absent se dit sans trace (20 pts)

Code de sortie 2, une ligne sur la sortie d'erreur qui nomme le fichier,
aucune trace Python, aucun résumé.

### Tâche 5 : un JSON invalide se dit sans trace (20 pts)

Même exigence pour un fichier dont le JSON est tronqué.
