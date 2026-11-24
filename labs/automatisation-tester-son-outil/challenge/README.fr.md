# Des tests qui attrapent vraiment quelque chose

## Situation

`security_check.py` tourne désormais dans les pipelines de l'équipe : il lit
les rapports de Trivy, interroge OSV et arrête le job quand une faille
atteint le seuil. Un outil qui a ce pouvoir ne doit pas changer de
comportement en silence. Or il n'a aucun test : la prochaine retouche peut
rendre le seuil exclusif, oublier une majuscule ou compter deux fois la même
faille, et personne ne le verra avant qu'un CRITICAL passe en production.

Le répertoire `challenge/work` contient votre solution du lab précédent, et
`tests/test_security_check.py`, qui ne contient qu'un exemple : il importe
l'outil et vérifie une constante. Il passe, et il ne prouve presque rien.

## Objectif

Écrire la suite de tests de l'outil, lancée par `uv run pytest`. Elle est
notée sur **ce qu'elle attrape**, pas sur le nombre de tests verts. Les
contrôles la jouent dans une copie de votre projet où seul
`security_check.py` est remplacé :

- par l'outil de **référence**, juste : votre suite doit passer, avec au
  moins cinq tests ;
- par quatre **mutants** de cet outil, portant chacun un bug réaliste : votre
  suite doit échouer sur chacun.

Vos tests portent sur le comportement demandé par les labs précédents, jamais
sur des détails internes que la référence pourrait écrire autrement : les
noms `SEVERITES`, `severite`, `compter`, `depuis_trivy`, `lire_findings` et
`main` y existent, le reste non.

## Repères

- `uv add --dev pytest` installe pytest comme dépendance de développement ;
  le `pyproject.toml` fourni dit déjà à pytest où trouver l'outil.
- Une fonction se teste en l'appelant : `security_check.compter([...])`.
- La ligne de commande se teste avec `CliRunner` de `click.testing` :
  `CliRunner().invoke(security_check.main, [chemin, "--fail-on", "HIGH"])`
  rend un résultat qui porte `exit_code` et `output`.
- La fixture `tmp_path` de pytest donne un répertoire temporaire où écrire un
  rapport ; `@pytest.mark.parametrize` joue un test sur plusieurs cas.
- Pour chaque règle d'un lab précédent, demandez-vous quel bug la casserait,
  puis écrivez le test qui le verrait.

## Vérifier

```bash
dsoxlab check automatisation-tester-son-outil
```

Cinq contrôles, vingt points chacun : la suite passe sur la référence, puis
elle tue chacun des quatre mutants. Le message d'échec nomme le bug du mutant
qui survit.

## La suite de tests de security_check.py

5 tâches, 100 points, 45 minutes.

Le projet est dans `challenge/work`. Vous écrivez `tests/`, et vous ne
touchez pas à `security_check.py` : les contrôles le remplacent dans une
copie du projet, par la référence puis par chacun des quatre mutants.

### Tâche 1 : la suite passe sur l'outil juste (20 pts)

`uv run pytest` passe entièrement sur l'outil de référence, avec au moins
cinq tests.

### Tâche 2 : la suite attrape un seuil exclusif (20 pts)

Elle échoue sur un mutant où `--fail-on HIGH` ne compte plus les HIGH.

### Tâche 3 : la suite attrape une casse non normalisée (20 pts)

Elle échoue sur un mutant où une sévérité en minuscules compte en UNKNOWN.

### Tâche 4 : la suite attrape des doublons Trivy (20 pts)

Elle échoue sur un mutant où une faille répétée dans deux cibles d'un rapport
Trivy compte deux fois.

### Tâche 5 : la suite attrape un rapport absent qui rend 1 (20 pts)

Elle échoue sur un mutant où un rapport illisible rend le code 1, celui qui
signifie « seuil atteint », au lieu de 2.

Les tâches 2 à 5 exigent aussi la tâche 1 : une suite qui échoue partout
« attrape » tous les mutants et ne prouve rien.
