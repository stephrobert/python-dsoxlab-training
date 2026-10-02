# Query the OSV API

Second lab of the running thread of the Python course's **Automation**
track, paired with the lesson "Calling APIs with requests". It starts from
your `security_check.py` of the previous lab and makes it query the public
OSV database for each package of the report: a dependency declared with uv,
an HTTP call bounded in time, and network failures handled the way a
pipeline tool does.

| | |
|---|---|
| Target | your machine: Python and uv (`mise install`), no Docker |
| Duration | about 40 minutes |
| Paired lesson | [Calling APIs with requests](https://blog.stephane-robert.info/docs/developper/programmation/python/requests/) (in French) |
| Previous | `automatisation-lire-un-rapport` |
| Next | `automatisation-rapport-trivy` starts from your solution |

```bash
dsoxlab run   automatisation-interroger-osv
cd labs/automatisation-interroger-osv/challenge/work
uv add requests
uv run python security_check.py exemples/findings.json --osv   # the real OSV API
dsoxlab check automatisation-interroger-osv
```

The tests do not touch the real database, whose answers change every week:
a local fake API answers like OSV and records every request. They check
what the tool asked, what it prints, and that an API that is down or silent
produces neither a traceback nor a hang.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
