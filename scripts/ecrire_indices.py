#!/usr/bin/env python3
"""Écrit `challenge/hints.yaml` d'un lab depuis un fichier source en clair.

Les indices sont stockés en base64 pour qu'un apprenant ne les lise pas en
ouvrant le fichier. C'est aussi ce qui les rend illisibles à la relecture :
on les écrit donc en clair dans `challenge/hints.source.yaml` (non distribué,
voir .gitignore), et ce script produit la forme encodée.

    python3 scripts/ecrire_indices.py labs/<id>
"""

from __future__ import annotations

import base64
import sys
from pathlib import Path

import yaml


def encoder(texte: str) -> str:
    return base64.b64encode(texte.strip().encode("utf-8")).decode("ascii")


def main() -> int:
    lab = Path(sys.argv[1])
    source = yaml.safe_load((lab / "challenge" / "hints.source.yaml").read_text(encoding="utf-8"))
    sortie = {
        "points": source.get("points", 100),
        "hints": [
            {"text_en": encoder(h["en"]), "text_fr": encoder(h["fr"]), "cost": h["cost"]}
            for h in source["hints"]
        ],
    }
    cible = lab / "challenge" / "hints.yaml"
    cible.write_text(yaml.safe_dump(sortie, sort_keys=False, allow_unicode=True, width=10**6), encoding="utf-8")
    relu = yaml.safe_load(cible.read_text(encoding="utf-8"))
    assert len(relu["hints"]) == len(source["hints"])
    for h, s in zip(relu["hints"], source["hints"], strict=True):
        assert base64.b64decode(h["text_fr"]).decode() == s["fr"].strip()
    print(f"{cible} : {len(relu['hints'])} indice(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
