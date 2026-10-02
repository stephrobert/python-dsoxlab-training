#!/usr/bin/env python3
"""Fabrique les mutants du lab automatisation-tester-son-outil.

Un mutant est l'outil de référence avec UN défaut réaliste, celui qu'un
développeur introduit en retouchant le code. La suite de tests de l'apprenant
doit passer sur la référence et échouer sur chacun d'eux.

Les mutants se GÉNÈRENT depuis la référence, ils ne s'écrivent pas à la main :
quand la référence évolue, `python3 scripts/generer_mutants.py` les refait, et
chaque remplacement est vérifié (exactement une occurrence) pour qu'un mutant
ne soit jamais, en silence, identique à l'original.
"""

from __future__ import annotations

import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent / "labs" / "automatisation-tester-son-outil"
REFERENCE = LAB / "challenge" / "tests" / "reference" / "security_check.py"
SORTIE = LAB / "challenge" / "tests" / "mutants"

MUTANTS = {
    # `--fail-on HIGH` ne compte plus les HIGH : seuil exclusif.
    "seuil_exclusif": (
        "return sum(compte[s] for s in SEUILS[: SEUILS.index(seuil) + 1])",
        "return sum(compte[s] for s in SEUILS[: SEUILS.index(seuil)])",
    ),
    # La casse n'est plus normalisée : « high » devient UNKNOWN.
    "casse_ignoree": (
        'valeur = str(finding.get("severity") or "").upper()',
        'valeur = str(finding.get("severity") or "")',
    ),
    # Plus de dédoublonnage : une faille répétée dans deux cibles compte deux fois.
    "doublons_comptes": (
        'vus.setdefault((finding["id"], finding["package"], finding["version"]), finding)',
        'vus[(finding["id"], finding["package"], finding["version"], len(vus))] = finding',
    ),
    # Un rapport illisible rend 1, le code qui dit « seuil atteint ».
    "erreur_en_code_1": (
        '        click.echo(f"error: {e}", err=True)\n        sys.exit(2)',
        '        click.echo(f"error: {e}", err=True)\n        sys.exit(1)',
    ),
}


def main() -> int:
    source = REFERENCE.read_text(encoding="utf-8")
    SORTIE.mkdir(parents=True, exist_ok=True)
    for nom, (avant, apres) in MUTANTS.items():
        n = source.count(avant)
        if n != 1:
            print(f"{nom} : {n} occurrence(s) de la ligne visée, 1 attendue. "
                  "La référence a changé : mettez MUTANTS à jour.", file=sys.stderr)
            return 1
        mutant = source.replace(avant, apres)
        cible = SORTIE / f"{nom}.py"
        cible.write_text(mutant, encoding="utf-8")
        assert cible.read_text(encoding="utf-8") != source
        print(f"{cible.relative_to(LAB)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
