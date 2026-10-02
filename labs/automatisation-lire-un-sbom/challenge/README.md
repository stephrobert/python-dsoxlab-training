# Challenge: version 5 of security_check.py

5 tasks, 100 points, 45 minutes.

The project is in `challenge/work`, with your version 4. You teach the tool
to read a CycloneDX SBOM and cross it with OSV. The tests replace OSV with a
fake API, given by `OSV_API_URL`.

### Task 1: each PyPI component is queried once (20 pts)

With `--osv`, one request per distinct PyPI component of the SBOM, ecosystem
`PyPI`. npm components are not queried.

### Task 2: the summary counts the vulnerabilities known to OSV (20 pts)

Each vulnerability returned by OSV is a finding. Its severity is that of the
GitHub advisory: `MODERATE` counts as MEDIUM, an advisory with no severity
as UNKNOWN.

### Task 3: an SBOM without --osv is unusable input (20 pts)

Exit code 2, one error line naming `--osv`, no Python traceback, no summary
at zero.

### Task 4: the threshold applies to an SBOM (20 pts)

`--fail-on HIGH` returns 1 if OSV knows a HIGH or a CRITICAL, 0 if the
advisories do not go beyond MODERATE.

### Task 5: reports stay readable, npm components are ignored (20 pts)

The Trivy report of the previous labs still gives its 22 flaws, and an SBOM
with no PyPI component triggers no request.
