# Read an SBOM

Seventh lab of the running thread of the Python course's **Automation**
track, paired with the DevSecOps course lesson "SBOM: the inventory of what
you ship". An SBOM lists components, not flaws: the tool learns to cross a
real CycloneDX inventory with the OSV database, and to judge the result with
the same threshold as scanner reports.

| | |
|---|---|
| Target | your machine: Python and uv (`mise install`), no Docker |
| Duration | about 45 minutes |
| Paired lesson | [SBOM: the inventory of what you ship](https://blog.stephane-robert.info/docs/securiser/supply-chain/sbom/) (in French) |
| Previous | `automatisation-dans-la-ci` |

```bash
dsoxlab run   automatisation-lire-un-sbom
cd labs/automatisation-lire-un-sbom/challenge/work
uv run python security_check.py sbom/tableau-de-bord.cdx.json --osv   # the real OSV API
dsoxlab check automatisation-lire-un-sbom
```

The sample SBOM is a real syft 1.51.1 output (CycloneDX 1.7), captured on
2026-10-02 on a Python project with an npm front end, with no local path in
it. The tests reuse it, with a fake OSV API.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
