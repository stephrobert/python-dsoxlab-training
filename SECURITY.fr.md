# Politique de sécurité

**Langue :** [English](./SECURITY.md) · [Français](./SECURITY.fr.md)

## Versions supportées

`python-dsoxlab-training` est en développement actif. Les correctifs de
sécurité sont appliqués à la dernière version de la branche `main`.

| Version | Supportée |
| --- | --- |
| dernière (`main`) | oui |
| plus anciennes | non |

## Signaler une vulnérabilité

**N'ouvrez pas d'issue publique pour une vulnérabilité de sécurité.**

Si vous pensez avoir trouvé une vulnérabilité, signalez-la en privé :

- De préférence : ouvrez un
  [avis de sécurité privé](https://github.com/stephrobert/python-dsoxlab-training/security/advisories/new)
  sur GitHub.
- Sinon, utilisez les coordonnées publiées sur
  <https://blog.stephane-robert.info>.

Merci d'inclure :

- une description de la vulnérabilité et de son impact,
- les étapes pour la reproduire (commande, environnement, `uv --version`, `python --version`,
  `dsoxlab --version`),
- tout journal ou preuve de concept pertinent.

Nous vous tiendrons informé de l'avancement du correctif et vous créditerons
dans les notes de version si vous le souhaitez.

## Politique de divulgation

Nous pratiquons la divulgation coordonnée et nous engageons sur les délais
suivants, décomptés à partir de la réception de votre signalement :

| Étape | Délai visé |
| --- | --- |
| Accusé de réception de votre signalement | sous **48 heures** |
| Évaluation initiale et qualification de la sévérité | sous **5 jours** |
| Correctif publié, ou plan de remédiation écrit | sous **30 jours** |
| Divulgation publique de la vulnérabilité | sous **90 jours** |

Nous publions l'avis de sécurité dès qu'un correctif est disponible, ou au plus
tard à l'échéance des **90 jours**, selon ce qui arrive en premier. Si une
vulnérabilité est activement exploitée, nous pouvons la divulguer plus tôt pour
protéger les utilisateurs. Si un correctif complexe demande plus de temps, nous
vous prévenons avant l'échéance et convenons d'une nouvelle date avec vous,
plutôt que de la laisser expirer sans rien dire.

## Périmètre

Ce dépôt livre du **contenu de lab** : des projets Python servant de points
de départ, des solutions de référence, des fixtures et des tests pytest,
exécutés par la CLI externe `dsoxlab` sur le poste de l'apprenant. Les labs
construisent un outil de sécurité qui lit des rapports de vulnérabilités et
interroge l'API publique OSV.

Dans le périmètre :

- un contenu de lab dangereux ou malveillant, en particulier du code qui
  enverrait les données de l'apprenant ailleurs qu'à l'API OSV que le lab
  nomme ;
- un secret, une clé privée ou un jeton d'API commité par erreur ;
- une dépendance épinglée porteuse d'une vulnérabilité connue dans un point de
  départ ou une solution (par exemple `click` avant 8.3.3, CVE-2026-7246).

Hors périmètre :

- les vulnérabilités du moteur `dsoxlab` lui-même, qui relèvent de
  [son propre dépôt](https://github.com/stephrobert/dsoxlab) ;
- celles de `requests`, `click`, uv, Trivy, du service OSV ou de toute
  dépendance tierce, à signaler à leurs projets respectifs ;
- les vulnérabilités listées dans le rapport Trivy d'exemple : elles sont le
  sujet des labs, relevées à dessein sur des paquets anciens ;
- un lab qui échoue ou note mal : c'est un défaut, il va dans une issue
  publique.

## Ce que ce dépôt ne vous demandera jamais

Aucun lab ne demande de secret, de compte ni de jeton. L'API OSV est publique
et anonyme, et les tests la remplacent par un faux serveur local.
