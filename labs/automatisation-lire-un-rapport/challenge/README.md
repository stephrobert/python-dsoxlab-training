# A scanner report nobody reads

## Situation

Your team's vulnerability scanner runs on every build and drops its results
into a JSON file: a list of findings, each with an identifier, a package, a
version and a severity. The file is hundreds of lines long, nobody opens it,
and last week a critical flaw reached production although it was listed
there.

You are going to write the tool that reads this report instead of humans:
`security_check.py`. This lab lays down version 1; the next four labs grow
it into the tool a pipeline calls to decide whether to carry on. The
`challenge/work` directory holds the project: a `pyproject.toml` managed by
uv, a skeleton of the tool whose two functions to write raise
`NotImplementedError`, and a sample report in `exemples/findings.json`.

## Goal

`uv run python security_check.py <report>` prints, for each severity in the
order CRITICAL, HIGH, MEDIUM, LOW, UNKNOWN, the number of findings, then the
total. A real export is not always clean: the case varies, and a severity
can be missing or hold anything. Those findings count as UNKNOWN, they do
not disappear.

A missing file or broken JSON is not a failure of the tool: it says so in
one line on standard error, naming the file, and exits with code 2. Code 1
is reserved: lab 4 will make it mean "vulnerabilities exceed the threshold".

## Pointers

- `json.load` reads an open file, `json.loads` a string; `Path.read_text`
  gives the string in one line.
- Reading a missing file raises `FileNotFoundError`, invalid JSON
  `json.JSONDecodeError`. Both can be caught.
- `dict.fromkeys(SEVERITES, 0)` starts with a zero count for every severity.
- An error message goes to `sys.stderr`, and `main()` returns the exit code.

## Check

```bash
dsoxlab check automatisation-lire-un-rapport
```

Five checks, twenty points each. The reports of the first three are written
by the tests, two of them drawn at random: a summary printed as a constant
does not pass.

## Version 1 of security_check.py

5 tasks, 100 points, 30 minutes.

The project is in `challenge/work`. You write `lire_findings` and `compter`
in `security_check.py`, and adjust `main` for errors. The tests run the tool
the way you do, with `uv run python security_check.py`, and read what it
prints and the code it returns.

### Task 1: the summary counts each severity (20 pts)

For any report, the tool prints six lines, `CRITICAL: n`, `HIGH: n`,
`MEDIUM: n`, `LOW: n`, `UNKNOWN: n` then `TOTAL: n`, and exits with 0.

### Task 2: unknown severities count as UNKNOWN (20 pts)

`critical` and `High` count as `CRITICAL` and `HIGH`. A severity that is
missing, empty, null or outside the list counts as `UNKNOWN`.

### Task 3: an empty report gives zeros (20 pts)

`[]` is a clean scan, not an error: six lines at zero, exit code 0.

### Task 4: a missing file is reported without a traceback (20 pts)

Exit code 2, one line on standard error naming the file, no Python
traceback, no summary.

### Task 5: invalid JSON is reported without a traceback (20 pts)

Same requirement for a file whose JSON is truncated.
