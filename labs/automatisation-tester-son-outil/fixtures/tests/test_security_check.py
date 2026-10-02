"""Les tests de security_check.py.

Un exemple pour démarrer : il importe l'outil comme un module et vérifie une
de ses constantes. Il passe, et il ne prouve presque rien. L'énoncé dit ce
que votre suite doit attraper (`dsoxlab challenge`).

    uv add --dev pytest
    uv run pytest -v
"""

import security_check


def test_les_severites_vont_de_la_plus_grave_a_la_moins_grave():
    assert security_check.SEVERITES[0] == "CRITICAL"
    assert security_check.SEVERITES[-1] == "UNKNOWN"
