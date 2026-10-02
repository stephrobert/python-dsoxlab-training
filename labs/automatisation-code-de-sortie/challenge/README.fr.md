# Challenge : la version 4 de security_check.py

5 tâches, 100 points, 40 minutes.

Le projet est dans `challenge/work`, avec votre version 3. La ligne de
commande passe sous Click, et l'option `--fail-on` donne à l'outil le droit
d'arrêter un pipeline.

### Tâche 1 : un critique arrête le pipeline (20 pts)

Avec `--fail-on CRITICAL` et une vulnérabilité CRITICAL : code 1, le résumé
reste affiché, et une ligne sur la sortie d'erreur dit combien de
vulnérabilités atteignent le seuil.

### Tâche 2 : le seuil compte tout ce qui est au-dessus (20 pts)

Sur un rapport tiré au hasard, chacun des quatre seuils rend 1 si une
vulnérabilité au moins aussi grave existe, 0 sinon. UNKNOWN n'atteint aucun
seuil.

### Tâche 3 : sous le seuil ou sans seuil, le pipeline continue (20 pts)

`--fail-on high` (en minuscules) sur un rapport sans HIGH ni CRITICAL rend 0.
Sans `--fail-on`, l'outil rend 0 même sur un CRITICAL.

### Tâche 4 : une entrée invalide reste un code 2 (20 pts)

`--fail-on SEVERE` rend 2, avec un message qui liste les seuils acceptés. Un
rapport absent rend 2, même avec `--fail-on`, jamais 1.

### Tâche 5 : l'aide est celle de Click (20 pts)

`--help` affiche l'aide de Click (elle commence par `Usage:`), et mentionne
`--fail-on` et `--osv`.
