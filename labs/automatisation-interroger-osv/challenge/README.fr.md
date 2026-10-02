# Challenge : la version 2 de security_check.py

5 tâches, 100 points, 40 minutes.

Le projet est dans `challenge/work`, avec votre version 1. Vous ajoutez
l'option `--osv`. Les tests remplacent OSV par une API factice, désignée par
`OSV_API_URL`, qui enregistre ce que l'outil lui demande.

### Tâche 1 : chaque paquet est interrogé une seule fois (20 pts)

Une requête `POST /v1/query` par couple (paquet, version) distinct, avec
`"ecosystem": "PyPI"` dans `package`. Un couple présent deux fois dans le
rapport ne s'interroge qu'une fois.

### Tâche 2 : les vulnérabilités connues s'affichent par paquet (20 pts)

Après le résumé, une ligne `OSV paquet==version: ID, ID` par couple, couples
triés par paquet puis version, identifiants triés, `none` s'il n'y en a pas.

### Tâche 3 : le résumé reste, et sans --osv aucun appel (20 pts)

Avec `--osv`, le résumé par sévérité ne change pas. Sans `--osv`, l'outil ne
contacte pas l'API.

### Tâche 4 : une API en panne se dit sans trace (20 pts)

Si l'API répond HTTP 500 : code 2, une ligne d'erreur qui contient `500`,
aucune trace Python.

### Tâche 5 : une API muette ne bloque pas le pipeline (20 pts)

Avec `OSV_TIMEOUT=1` et une API qui met 6 secondes à répondre : code 2, une
ligne d'erreur qui contient `OSV`, et l'outil rend la main en moins de
5 secondes.
