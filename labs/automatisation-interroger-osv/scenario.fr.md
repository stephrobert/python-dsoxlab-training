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
