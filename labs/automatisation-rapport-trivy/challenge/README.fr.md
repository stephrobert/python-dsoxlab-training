# Le vrai rapport de Trivy

## Situation

L'équipe remplace son scanner maison par Trivy. Son rapport JSON n'est plus
une liste de findings : c'est un objet dont la clé `Results` liste les
**cibles** analysées (chaque `requirements.txt`, chaque couche d'image), et
chaque cible range ses vulnérabilités sous `Vulnerabilities`, avec les champs
`VulnerabilityID`, `PkgName`, `InstalledVersion` et `Severity`.

Le répertoire `challenge/work` contient votre solution du lab précédent, et
`exemples/trivy.json`, la sortie réelle de `trivy fs --format json`
(Trivy 0.74.0) sur un projet à trois fichiers de dépendances. Lancez-y
votre version 2 : elle le refuse, puisqu'elle attend une liste.

Ce rapport porte deux pièges, qu'on rencontre sur tout projet réel. Une cible
saine n'a **pas** de clé `Vulnerabilities` du tout. Et `requests 2.25.0`,
déclaré dans deux fichiers, voit ses failles apparaître dans deux cibles :
26 occurrences, mais 22 vulnérabilités à corriger.

## Objectif

`uv run python security_check.py exemples/trivy.json` affiche le résumé par
sévérité des **vulnérabilités distinctes**, une par couple (identifiant,
paquet, version). L'export en liste des labs précédents reste lisible, et
`--osv` interroge les paquets d'un rapport Trivy comme ceux d'une liste.

## Repères

- `isinstance(donnees, dict)` distingue l'objet de Trivy de la liste.
- `dict.get("Vulnerabilities")` rend `None` sur une clé absente, et
  `... or []` en fait une liste vide qu'une boucle traverse sans erreur.
- Un dictionnaire dont la clé est un tuple `(id, paquet, version)` ne garde
  qu'une entrée par vulnérabilité.
- Traduire chaque vulnérabilité Trivy vers le format interne de l'outil
  (`id`, `package`, `version`, `severity`) laisse le reste du code inchangé.

## Vérifier

```bash
dsoxlab check automatisation-rapport-trivy
```

Cinq contrôles, vingt points chacun, sur le rapport réel et sur des rapports
Trivy générés au hasard.

## La version 3 de security_check.py

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
