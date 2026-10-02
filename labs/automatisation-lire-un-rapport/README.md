# Read a scanner report

First lab of the running thread of the Python course's **Automation** track,
paired with the lesson "Working with JSON". It lays down version 1 of
`security_check.py`, the tool the next four labs grow: read a JSON export of
findings, count them by severity, and refuse invalid input the way a
pipeline tool does, in one line and with an exit code.

| | |
|---|---|
| Target | your machine: Python and uv (`mise install`), no Docker |
| Duration | about 30 minutes |
| Paired lesson | [Working with JSON](https://blog.stephane-robert.info/docs/developper/programmation/python/json/) (in French) |
| Next | `automatisation-interroger-osv` starts from your solution |

```bash
mise install                                    # uv and Python
dsoxlab run   automatisation-lire-un-rapport    # lays the project in challenge/work
cd labs/automatisation-lire-un-rapport/challenge/work
uv run python security_check.py exemples/findings.json
dsoxlab check automatisation-lire-un-rapport    # runs the tool and grades
```

The tests run the tool exactly as you do, with `uv run`, on reports they
write themselves, two of them drawn at random. They read the printed
summary, standard error and the exit code, never the source code.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable, working directory removed by
`dsoxlab clean`. The verdict is in `validation-labs.json`.
