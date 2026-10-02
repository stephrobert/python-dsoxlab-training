# Challenge : la porte de sécurité du pipeline

5 tâches, 100 points, 40 minutes.

Le projet est dans `challenge/work`. Tout se passe dans
`.github/workflows/`, que vous créez. Les tests jouent votre workflow avec act
et lisent ce qu'il produit ; ils ne lisent pas vos commandes.

### Tâche 1 : un rapport propre laisse passer (20 pts)

Sur un rapport sans vulnérabilité, `act push` joue un seul job, vert, où les
tests de l'outil passent et où l'outil résume `rapports/trivy.json`.

### Tâche 2 : un CRITICAL arrête le pipeline (20 pts)

Sur le rapport livré, le job échoue sur le seuil : l'outil écrit sa ligne
`FAILED: ...`.

### Tâche 3 : le seuil est CRITICAL, pas plus bas (20 pts)

Un rapport qui ne porte que des HIGH et des MEDIUM laisse passer.

### Tâche 4 : un outil cassé ne décide de rien (20 pts)

Avec un outil cassé, le job échoue sur ses tests, et le seuil ne s'applique
pas.

### Tâche 5 : les pull requests passent la porte, avec des droits minimaux (20 pts)

`act pull_request` joue le même job, vert sur un rapport propre. Le workflow
déclare `permissions: contents: read`, et chaque action est épinglée sur le
SHA complet de son commit.
