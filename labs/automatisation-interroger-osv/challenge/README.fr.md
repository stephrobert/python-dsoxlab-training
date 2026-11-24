# Ce que la base OSV sait de vos paquets

## Situation

La version 1 de `security_check.py` résume ce que le scanner a trouvé. Mais un
scanner n'est jamais plus à jour que sa propre base : en relevant ce lab, la
base de Trivy ignorait encore une faille de `click` 8.3.1 que la base
publique OSV (Open Source Vulnerabilities) connaissait déjà. Votre équipe veut
une seconde source, interrogée à la demande.

Le répertoire `challenge/work` contient votre solution du lab précédent. OSV
expose une API HTTP : `POST https://api.osv.dev/v1/query`, avec un corps JSON
qui nomme le paquet, son écosystème et sa version, et une réponse qui liste
les vulnérabilités connues dans `vulns`.

## Objectif

`uv run python security_check.py <rapport> --osv` affiche le résumé habituel,
puis une ligne par couple (paquet, version) distinct du rapport, triés :

```text
OSV jinja2==2.11.2: none
OSV requests==2.25.0: GHSA-j8r2-6x86-q33q, PYSEC-2023-74
```

Chaque couple ne s'interroge qu'une fois, et seulement avec `--osv` : sans
l'option, l'outil ne fait aucun appel réseau. L'adresse de l'API se lit dans
la variable d'environnement `OSV_API_URL` (`https://api.osv.dev` par défaut),
et le délai maximal d'un appel, en secondes, dans `OSV_TIMEOUT` (10 par
défaut).

Une API en panne ou muette ne bloque pas le pipeline et ne produit pas de
trace : l'outil le dit en une ligne et sort avec le code 2.

## Repères

- `requests` n'est pas dans la bibliothèque standard : `uv add requests` le
  déclare dans `pyproject.toml` et l'installe dans le projet.
- `requests.post(url, json=corps, timeout=...)` envoie du JSON ; sans
  `timeout`, un serveur muet bloque l'appel indéfiniment.
- `raise_for_status()` transforme une réponse 500 en exception, et
  `requests.Timeout` et `requests.RequestException` s'attrapent.
- Un ensemble (`set`) de tuples élimine les doublons ; `sorted` les ordonne.

## Vérifier

```bash
dsoxlab check automatisation-interroger-osv
```

Cinq contrôles, vingt points chacun. Une API factice remplace OSV : elle
enregistre chaque requête reçue, ce qui permet de vérifier ce que l'outil a
réellement demandé.

## La version 2 de security_check.py

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
