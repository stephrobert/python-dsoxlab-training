# Challenge: version 3 of security_check.py

5 tasks, 100 points, 40 minutes.

The project is in `challenge/work`, with your version 2. You teach the tool
Trivy's JSON format, without losing what it could already do.

### Task 1: the real report counts 22 distinct flaws (20 pts)

On the real Trivy report shipped with the tests, the summary counts each
vulnerability once per (identifier, package, version) triple: 22, not the
26 occurrences.

### Task 2: a generated Trivy report is deduplicated (20 pts)

Same requirement on multi-target reports drawn at random, where the same
flaw repeats from one target to another.

### Task 3: targets without vulnerabilities break nothing (20 pts)

A target with no `Vulnerabilities` key, with `null` or an empty list, and a
`Results` set to `null`: the summary is at zero, exit code 0.

### Task 4: both formats stay readable (20 pts)

The list export of the previous labs still gives the right summary, and so
does the Trivy report.

### Task 5: --osv queries the packages of the Trivy report (20 pts)

With `--osv`, one request per distinct (`PkgName`, `InstalledVersion`) pair
of the report.
