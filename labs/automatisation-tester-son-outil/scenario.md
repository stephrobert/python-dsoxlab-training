# Tests that really catch something

## Situation

`security_check.py` now runs in the team's pipelines: it reads Trivy
reports, queries OSV and stops the job when a flaw reaches the threshold. A
tool with that power must not change behaviour silently. Yet it has no
tests: the next edit can make the threshold exclusive, forget an upper-case
letter or count the same flaw twice, and nobody will notice before a
CRITICAL reaches production.

The `challenge/work` directory holds your solution of the previous lab, and
`tests/test_security_check.py`, which only holds an example: it imports the
tool and checks a constant. It passes, and it proves almost nothing.

## Goal

Write the tool's test suite, run by `uv run pytest`. It is graded on **what
it catches**, not on the number of green tests. The checks run it in a copy
of your project where only `security_check.py` is replaced:

- by the **reference** tool, which is correct: your suite must pass, with at
  least five tests;
- by four **mutants** of that tool, each carrying one realistic bug: your
  suite must fail on each.

Your tests cover the behaviour required by the previous labs, never internal
details the reference could write differently: the names `SEVERITES`,
`severite`, `compter`, `depuis_trivy`, `lire_findings` and `main` exist in
it, the rest does not.

## Pointers

- `uv add --dev pytest` installs pytest as a development dependency; the
  provided `pyproject.toml` already tells pytest where to find the tool.
- A function is tested by calling it: `security_check.compter([...])`.
- The command line is tested with `CliRunner` from `click.testing`:
  `CliRunner().invoke(security_check.main, [path, "--fail-on", "HIGH"])`
  returns a result carrying `exit_code` and `output`.
- pytest's `tmp_path` fixture gives a temporary directory to write a report
  in; `@pytest.mark.parametrize` runs one test on several cases.
- For each rule of a previous lab, ask which bug would break it, then write
  the test that would see it.

## Check

```bash
dsoxlab check automatisation-tester-son-outil
```

Five checks, twenty points each: the suite passes on the reference, then it
kills each of the four mutants. The failure message names the bug of the
mutant that survives.
