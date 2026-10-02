# An exit code a pipeline can act on

Fourth lab of the running thread of the Python course's **Automation**
track, paired with the lesson "Click: command-line tools in Python". It
starts from your `security_check.py` of the previous lab, moves its command
line to Click and adds `--fail-on`: the tool stops merely describing, it
decides, and says so in the only language a pipeline understands, its exit
code.

| | |
|---|---|
| Target | your machine: Python and uv (`mise install`), no Docker |
| Duration | about 40 minutes |
| Paired lesson | [Click: command-line tools in Python](https://blog.stephane-robert.info/docs/developper/programmation/python/click/) (in French) |
| Previous | `automatisation-rapport-trivy` |
| Next | `automatisation-tester-son-outil` starts from your solution |

```bash
dsoxlab run   automatisation-code-de-sortie
cd labs/automatisation-code-de-sortie/challenge/work
uv add click
uv run python security_check.py exemples/trivy.json --fail-on CRITICAL; echo "code: $?"
dsoxlab check automatisation-code-de-sortie
```

Three codes, and the confusion they prevent: 0 nothing reaches the
threshold, 1 the threshold is reached, 2 the input is unusable. A missing
report returning 1 would stop a deployment for a flaw that does not exist.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
