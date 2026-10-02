# Challenge : la version 3 de security_check.py

5 tâches, 100 points, 40 minutes.

Le projet est dans `challenge/work`, avec votre version 2. Vous apprenez à
l'outil le format JSON de Trivy, sans perdre ce qu'il savait déjà faire.

### Tâche 1 : le vrai rapport compte 22 failles distinctes (20 pts)

Sur le rapport réel de Trivy livré avec les tests, le résumé compte chaque
vulnérabilité une fois par couple (identifiant, paquet, version) : 22, pas
les 26 occurrences.

### Tâche 2 : un rapport Trivy généré est dédoublonné (20 pts)

Même exigence sur des rapports à plusieurs cibles tirés au hasard, où une
même faille se répète d'une cible à l'autre.

### Tâche 3 : des cibles sans vulnérabilité ne cassent rien (20 pts)

Une cible sans clé `Vulnerabilities`, avec `null` ou une liste vide, et un
`Results` à `null` : le résumé est à zéro, code 0.

### Tâche 4 : les deux formats restent lisibles (20 pts)

L'export en liste des labs précédents donne toujours le bon résumé, et le
rapport Trivy aussi.

### Tâche 5 : --osv interroge les paquets du rapport Trivy (20 pts)

Avec `--osv`, une requête par couple (`PkgName`, `InstalledVersion`)
distinct du rapport.
