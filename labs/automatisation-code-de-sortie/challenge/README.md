# Challenge: version 4 of security_check.py

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
