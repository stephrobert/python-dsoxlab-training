# The security gate of the main branch

## Situation

`security_check.py` reads Trivy reports, queries OSV, returns a meaningful
exit code, and its test suite catches regressions. But it only runs when
someone remembers to launch it. The team wants it to **guard the `main`
branch**: no code may reach it while the scanner report carries a CRITICAL
vulnerability.

The `challenge/work` directory holds the project as the previous lab left
it: the tool, `tests/`, a `uv.lock`, and `rapports/trivy.json`, the report
the scan job drops (the real output of Trivy 0.74.0, two CRITICAL). No
workflow. The `.actrc` file names the runner image for act.

## Goal

A GitHub Actions workflow that, on every **push** and every **pull request**
to `main`, in a single job:

1. installs uv and the project's **locked** dependencies;
2. runs the **tool's tests**: a broken tool must decide nothing;
3. applies `security_check.py rapports/trivy.json --fail-on CRITICAL`.

The job only asks for the right to **read the code**, and every action is
pinned to the **full SHA** of its commit, version in a comment.

## Pointers

- A failing step stops the following ones: the order of the steps is the
  guarantee.
- `astral-sh/setup-uv` installs uv; `uv sync --locked` refuses a `uv.lock`
  that no longer matches `pyproject.toml`.
- `act push` and `act pull_request` play the workflow on your machine;
  `act -l` lists what act understood from your files.
- `git ls-remote --tags <repository> <tag>` gives the SHA of a tag.

## Check

```bash
dsoxlab check automatisation-dans-la-ci
```

Five checks, twenty points each. They play your workflow with act on copies
of the project, where the report and the tool are replaced: clean report,
shipped report, report without CRITICAL, broken tool, pull request. Docker
must answer (`docker info`).
