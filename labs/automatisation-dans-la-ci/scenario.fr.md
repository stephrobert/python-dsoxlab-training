# La porte de sécurité de la branche principale

## Situation

`security_check.py` lit les rapports de Trivy, interroge OSV, rend un code de
sortie qui a du sens, et sa suite de tests attrape les régressions. Mais il ne
tourne que quand quelqu'un pense à le lancer. L'équipe veut qu'il **garde la
branche `main`** : aucun code ne doit y arriver tant que le rapport du scanner
porte une vulnérabilité CRITICAL.

Le répertoire `challenge/work` contient le projet tel que le lab précédent l'a
laissé : l'outil, `tests/`, un `uv.lock`, et `rapports/trivy.json`, le rapport
que le job de scan dépose (la sortie réelle de Trivy 0.74.0, deux CRITICAL).
Aucun workflow. Le fichier `.actrc` désigne l'image du runner pour act.

## Objectif

Un workflow GitHub Actions qui, à chaque **push** et à chaque **pull request**
vers `main`, dans un seul job :

1. installe uv et les dépendances **verrouillées** du projet ;
2. lance les **tests de l'outil** : un outil cassé ne doit rien décider ;
3. applique `security_check.py rapports/trivy.json --fail-on CRITICAL`.

Le job ne réclame que le droit de **lire le code**, et chaque action est
épinglée sur le **SHA complet** de son commit, version en commentaire.

## Repères

- Un step qui échoue arrête les suivants : l'ordre des steps est la garantie.
- `astral-sh/setup-uv` installe uv ; `uv sync --locked` refuse un `uv.lock`
  qui ne correspond plus au `pyproject.toml`.
- `act push` et `act pull_request` jouent le workflow sur votre poste ;
  `act -l` liste ce qu'act a compris de vos fichiers.
- `git ls-remote --tags <dépôt> <tag>` donne le SHA d'un tag.

## Vérifier

```bash
dsoxlab check automatisation-dans-la-ci
```

Cinq contrôles, vingt points chacun. Ils jouent votre workflow avec act sur
des copies du projet, où le rapport et l'outil sont remplacés : rapport
propre, rapport livré, rapport sans CRITICAL, outil cassé, pull request.
Docker doit répondre (`docker info`).
