# Challenge: version 2 of security_check.py

5 tasks, 100 points, 40 minutes.

The project is in `challenge/work`, with your version 1. You add the
`--osv` option. The tests replace OSV with a fake API, given by
`OSV_API_URL`, which records what the tool asks it.

### Task 1: each package is queried only once (20 pts)

One `POST /v1/query` request per distinct (package, version) pair, with
`"ecosystem": "PyPI"` in `package`. A pair present twice in the report is
queried once.

### Task 2: known vulnerabilities are printed per package (20 pts)

After the summary, one `OSV package==version: ID, ID` line per pair, pairs
sorted by package then version, identifiers sorted, `none` if there are
none.

### Task 3: the summary stays, and without --osv no call (20 pts)

With `--osv`, the summary by severity does not change. Without `--osv`, the
tool does not contact the API.

### Task 4: an API outage is reported without a traceback (20 pts)

If the API answers HTTP 500: exit code 2, one error line containing `500`,
no Python traceback.

### Task 5: a silent API does not block the pipeline (20 pts)

With `OSV_TIMEOUT=1` and an API that takes 6 seconds to answer: exit code 2,
one error line containing `OSV`, and the tool returns within 5 seconds.
