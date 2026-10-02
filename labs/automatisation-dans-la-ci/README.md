# A security gate in the pipeline

Sixth and last lab of the running thread of the Python course's
**Automation** track, paired with the GitHub Actions lesson "Hardened CI
pipeline". The tool built lab after lab becomes a **gate**: a workflow runs
its tests, then has it judge the scanner report, and stops the branch as
soon as a CRITICAL vulnerability appears.

| | |
|---|---|
| Target | your machine: uv, Python and act (`mise install`), a running **Docker** |
| Duration | about 40 minutes |
| Paired lesson | [Hardened CI pipeline](https://blog.stephane-robert.info/docs/pipeline-cicd/github/securite/lab/pipeline-ci/) (in French) |
| Previous | `automatisation-tester-son-outil` |

```bash
mise install                                   # uv, Python and act
dsoxlab run   automatisation-dans-la-ci
cd labs/automatisation-dans-la-ci/challenge/work
act push                                       # plays your workflow
dsoxlab check automatisation-dans-la-ci
```

This is the only lab of the catalog that needs Docker: act plays the
workflow in the `ubuntu-24.04` runner image, pinned by digest in `.actrc`.
The tests replay your workflow on copies of the project, report and tool
replaced, and read the job result and the lines written.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
