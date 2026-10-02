# Challenge : la version 5 de security_check.py

5 tâches, 100 points, 45 minutes.

Le projet est dans `challenge/work`, avec votre version 4. Vous apprenez à
l'outil à lire un SBOM CycloneDX et à le croiser avec OSV. Les tests
remplacent OSV par une API factice, désignée par `OSV_API_URL`.

### Tâche 1 : chaque composant PyPI est interrogé une fois (20 pts)

Avec `--osv`, une requête par composant PyPI distinct du SBOM, écosystème
`PyPI`. Les composants npm ne sont pas interrogés.

### Tâche 2 : le résumé compte les vulnérabilités connues d'OSV (20 pts)

Chaque vulnérabilité rendue par OSV est un finding. Sa sévérité est celle de
l'avis GitHub : `MODERATE` compte en MEDIUM, un avis sans sévérité en
UNKNOWN.

### Tâche 3 : un SBOM sans --osv est une entrée inexploitable (20 pts)

Code 2, une ligne d'erreur qui nomme `--osv`, aucune trace Python, aucun
résumé à zéro.

### Tâche 4 : le seuil s'applique à un SBOM (20 pts)

`--fail-on HIGH` rend 1 si OSV connaît un HIGH ou un CRITICAL, 0 si les avis
ne dépassent pas MODERATE.

### Tâche 5 : les rapports restent lisibles, les composants npm ignorés (20 pts)

Le rapport Trivy des labs précédents donne toujours ses 22 failles, et un
SBOM sans composant PyPI ne déclenche aucune requête.
