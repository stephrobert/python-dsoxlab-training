# The real Trivy report

## Situation

The team replaces its home-made scanner with Trivy. Its JSON report is no
longer a list of findings: it is an object whose `Results` key lists the
scanned **targets** (each `requirements.txt`, each image layer), and each
target stores its vulnerabilities under `Vulnerabilities`, with the fields
`VulnerabilityID`, `PkgName`, `InstalledVersion` and `Severity`.

The `challenge/work` directory holds your solution of the previous lab, and
`exemples/trivy.json`, the real output of `trivy fs --format json`
(Trivy 0.74.0) on a project with three dependency files. Run your version 2
on it: it refuses it, since it expects a list.

This report carries two traps found on every real project. A clean target
has **no** `Vulnerabilities` key at all. And `requests 2.25.0`, declared in
two files, has its flaws appear in two targets: 26 occurrences, but 22
vulnerabilities to fix.

## Goal

`uv run python security_check.py exemples/trivy.json` prints the summary by
severity of the **distinct vulnerabilities**, one per (identifier, package,
version) triple. The list export of the previous labs stays readable, and
`--osv` queries the packages of a Trivy report like those of a list.

## Pointers

- `isinstance(data, dict)` tells Trivy's object from the list.
- `dict.get("Vulnerabilities")` returns `None` on a missing key, and
  `... or []` turns it into an empty list a loop goes through without error.
- A dictionary keyed by an `(id, package, version)` tuple keeps one entry
  per vulnerability.
- Translating each Trivy vulnerability into the tool's internal format
  (`id`, `package`, `version`, `severity`) leaves the rest of the code
  unchanged.

## Check

```bash
dsoxlab check automatisation-rapport-trivy
```

Five checks, twenty points each, on the real report and on Trivy reports
generated at random.

## Version 3 of security_check.py

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
