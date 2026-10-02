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
