# Test your own tool

Fifth and last lab of the running thread of the Python course's
**Automation** track, paired with the lesson "pytest in practice". The tool
is finished; it lacks tests. This suite is graded on what it catches: it
must pass on the correct tool and fail on four mutants, each carrying one
realistic bug. This is called mutation testing, and it is the only way to
know whether a green suite protects against anything.

| | |
|---|---|
| Target | your machine: Python and uv (`mise install`), no Docker |
| Duration | about 45 minutes |
| Paired lesson | [pytest in practice](https://blog.stephane-robert.info/docs/developper/programmation/python/tests/pytest/) (in French) |
| Previous | `automatisation-code-de-sortie` |

```bash
dsoxlab run   automatisation-tester-son-outil
cd labs/automatisation-tester-son-outil/challenge/work
uv add --dev pytest
uv run pytest -v
dsoxlab check automatisation-tester-son-outil
```

The mutants live in `challenge/tests/mutants/`. They are generated from the
reference tool by `scripts/generer_mutants.py`, which checks that each one
really differs from the original.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
