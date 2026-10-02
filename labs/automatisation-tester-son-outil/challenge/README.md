# Challenge: the test suite of security_check.py

5 tasks, 100 points, 45 minutes.

The project is in `challenge/work`. You write `tests/`, and you do not touch
`security_check.py`: the checks replace it in a copy of the project, with
the reference then with each of the four mutants.

### Task 1: the suite passes on the correct tool (20 pts)

`uv run pytest` fully passes on the reference tool, with at least five
tests.

### Task 2: the suite catches an exclusive threshold (20 pts)

It fails on a mutant where `--fail-on HIGH` no longer counts HIGH.

### Task 3: the suite catches an unnormalised case (20 pts)

It fails on a mutant where a lower-case severity counts as UNKNOWN.

### Task 4: the suite catches Trivy duplicates (20 pts)

It fails on a mutant where a flaw repeated in two targets of a Trivy report
counts twice.

### Task 5: the suite catches a missing report returning 1 (20 pts)

It fails on a mutant where an unreadable report returns code 1, the one
meaning "threshold reached", instead of 2.

Tasks 2 to 5 also require task 1: a suite that fails everywhere "catches"
every mutant and proves nothing.
