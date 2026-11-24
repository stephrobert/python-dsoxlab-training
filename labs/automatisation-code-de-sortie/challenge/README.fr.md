# Un outil qui a le droit d'arrêter un pipeline

## Situation

`security_check.py` sait lire le rapport de Trivy et interroger OSV, mais il
ne décide de rien : il sort toujours en 0. Le job de CI qui l'appelle passe
donc au vert, même sur deux failles critiques. Un pipeline ne lit pas ce
qu'un outil affiche, il lit son **code de sortie** : 0 laisse continuer, tout
autre code arrête le job.

L'équipe veut aussi une ligne de commande plus solide que celle d'argparse,
dont l'aide se lit d'un coup d'œil : la formation enseigne **Click**. Le
répertoire `challenge/work` contient votre solution du lab précédent.

## Objectif

L'outil passe sous Click, avec les mêmes arguments qu'avant, et gagne
l'option `--fail-on SEVERITE` (CRITICAL, HIGH, MEDIUM ou LOW, en majuscules
comme en minuscules). Trois codes de sortie, et trois seulement :

| Code | Sens |
|---|---|
| 0 | rien n'atteint le seuil, ou aucun seuil demandé |
| 1 | au moins une vulnérabilité atteint le seuil |
| 2 | entrée inexploitable : rapport absent ou illisible, API en panne, option invalide |

Le seuil est inclusif et compte tout ce qui est au moins aussi grave :
`--fail-on HIGH` échoue sur un CRITICAL. UNKNOWN n'atteint aucun seuil. Quand
le seuil est atteint, le résumé reste affiché, et une ligne sur la sortie
d'erreur dit combien de vulnérabilités le dépassent.

## Repères

- `uv add click` déclare la dépendance. `@click.command()`,
  `@click.argument()` et `@click.option()` remplacent l'analyseur d'argparse.
- `type=click.Choice([...], case_sensitive=False)` refuse une valeur hors
  liste, avec un message qui liste les choix et le code 2.
- `sys.exit(1)` fixe le code de sortie ; `click.echo(..., err=True)` écrit
  sur la sortie d'erreur.
- L'ordre de `SEVERITES` donne déjà le rang de chaque seuil.

## Vérifier

```bash
dsoxlab check automatisation-code-de-sortie
```

Cinq contrôles, vingt points chacun. Le deuxième essaie les quatre seuils sur
un rapport tiré au hasard.

## La version 4 de security_check.py

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
