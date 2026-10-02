# Challenge: version 1 of security_check.py

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
