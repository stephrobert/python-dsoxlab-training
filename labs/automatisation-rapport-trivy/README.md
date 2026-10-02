# Read a real Trivy report

Third lab of the running thread of the Python course's **Automation**
track, paired with the lesson "Dictionaries". It starts from your
`security_check.py` of the previous lab and teaches it Trivy's real format:
results nested by target, a key missing when a target is clean, and flaws
repeated from one target to another, to be counted once.

| | |
|---|---|
| Target | your machine: Python and uv (`mise install`), no Docker |
| Duration | about 40 minutes |
| Paired lesson | [Dictionaries](https://blog.stephane-robert.info/docs/developper/programmation/python/dictionnaire/) (in French) |
| Previous | `automatisation-interroger-osv` |
| Next | `automatisation-code-de-sortie` starts from your solution |

```bash
dsoxlab run   automatisation-rapport-trivy
cd labs/automatisation-rapport-trivy/challenge/work
uv run python security_check.py exemples/trivy.json
dsoxlab check automatisation-rapport-trivy
```

The sample report is a real Trivy 0.74.0 output, captured on 2026-10-02 on
a project with three `requirements.txt` files: 26 occurrences, 22 distinct
vulnerabilities. The tests reuse it and add Trivy reports generated at
random.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
