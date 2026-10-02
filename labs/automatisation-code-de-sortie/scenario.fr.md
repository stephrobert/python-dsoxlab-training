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
