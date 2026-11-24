# Un rapport de scanner que personne ne lit

## Situation

Le scanner de vulnérabilités de votre équipe tourne à chaque build et dépose
ses résultats dans un fichier JSON : une liste de findings, chacun avec un
identifiant, un paquet, une version et une sévérité. Le fichier fait des
centaines de lignes, personne ne l'ouvre, et la semaine dernière une faille
critique est passée en production alors qu'elle y figurait.

Vous allez écrire l'outil qui lit ce rapport à la place des humains :
`security_check.py`. Ce lab en pose la version 1 ; les quatre labs suivants
la font grandir, jusqu'à l'outil qu'un pipeline appelle pour décider s'il
continue. Le répertoire `challenge/work` contient le projet : un
`pyproject.toml` géré par uv, un squelette de l'outil dont les deux fonctions
à écrire lèvent `NotImplementedError`, et un rapport d'exemple dans
`exemples/findings.json`.

## Objectif

`uv run python security_check.py <rapport>` affiche, pour chaque sévérité
dans l'ordre CRITICAL, HIGH, MEDIUM, LOW, UNKNOWN, le nombre de findings, puis
le total. Un export réel n'est pas toujours propre : la casse varie, et une
sévérité peut manquer ou valoir n'importe quoi. Ces findings-là comptent en
UNKNOWN, ils ne disparaissent pas.

Un fichier absent ou un JSON cassé ne sont pas des pannes de l'outil : il le
dit en une ligne sur la sortie d'erreur, en nommant le fichier, et sort avec
le code 2. Le code 1 est réservé : le lab 4 lui fera dire « des
vulnérabilités dépassent le seuil ».

## Repères

- `json.load` lit un fichier ouvert, `json.loads` une chaîne ; `Path.read_text`
  donne la chaîne en une ligne.
- Lire un fichier absent lève `FileNotFoundError`, un JSON invalide
  `json.JSONDecodeError`. Les deux s'attrapent.
- `dict.fromkeys(SEVERITES, 0)` part d'un compte à zéro pour chaque sévérité.
- Un message d'erreur va sur `sys.stderr`, et `main()` rend le code de sortie.

## Vérifier

```bash
dsoxlab check automatisation-lire-un-rapport
```

Cinq contrôles, vingt points chacun. Les rapports des trois premiers sont
écrits par les tests, et deux d'entre eux tirés au hasard : un résumé imprimé
en dur ne passe pas.

## La version 1 de security_check.py

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
