# A tool allowed to stop a pipeline

## Situation

`security_check.py` can read Trivy's report and query OSV, but it decides
nothing: it always exits with 0. The CI job that calls it therefore goes
green, even on two critical flaws. A pipeline does not read what a tool
prints, it reads its **exit code**: 0 lets it continue, any other code stops
the job.

The team also wants a sturdier command line than argparse's, with help that
reads at a glance: the course teaches **Click**. The `challenge/work`
directory holds your solution of the previous lab.

## Goal

The tool moves to Click, with the same arguments as before, and gains the
`--fail-on SEVERITY` option (CRITICAL, HIGH, MEDIUM or LOW, upper or lower
case). Three exit codes, and only three:

| Code | Meaning |
|---|---|
| 0 | nothing reaches the threshold, or no threshold requested |
| 1 | at least one vulnerability reaches the threshold |
| 2 | unusable input: missing or unreadable report, API down, invalid option |

The threshold is inclusive and counts everything at least as severe:
`--fail-on HIGH` fails on a CRITICAL. UNKNOWN reaches no threshold. When the
threshold is reached, the summary stays printed, and one line on standard
error says how many vulnerabilities exceed it.

## Pointers

- `uv add click` declares the dependency. `@click.command()`,
  `@click.argument()` and `@click.option()` replace argparse's parser.
- `type=click.Choice([...], case_sensitive=False)` refuses a value outside
  the list, with a message listing the choices and code 2.
- `sys.exit(1)` sets the exit code; `click.echo(..., err=True)` writes to
  standard error.
- The order of `SEVERITES` already gives the rank of each threshold.

## Check

```bash
dsoxlab check automatisation-code-de-sortie
```

Five checks, twenty points each. The second tries all four thresholds on a
report drawn at random.

## Version 4 of security_check.py

5 tasks, 100 points, 40 minutes.

The project is in `challenge/work`, with your version 3. The command line
moves to Click, and the `--fail-on` option gives the tool the right to stop
a pipeline.

### Task 1: a critical stops the pipeline (20 pts)

With `--fail-on CRITICAL` and a CRITICAL vulnerability: exit code 1, the
summary stays printed, and one line on standard error says how many
vulnerabilities reach the threshold.

### Task 2: the threshold counts everything above (20 pts)

On a report drawn at random, each of the four thresholds returns 1 if a
vulnerability at least as severe exists, 0 otherwise. UNKNOWN reaches no
threshold.

### Task 3: below the threshold or without one, the pipeline goes on (20 pts)

`--fail-on high` (lower case) on a report with no HIGH or CRITICAL returns
0. Without `--fail-on`, the tool returns 0 even on a CRITICAL.

### Task 4: invalid input stays a code 2 (20 pts)

`--fail-on SEVERE` returns 2, with a message listing the accepted
thresholds. A missing report returns 2, even with `--fail-on`, never 1.

### Task 5: the help is Click's (20 pts)

`--help` prints Click's help (it starts with `Usage:`), and mentions
`--fail-on` and `--osv`.
