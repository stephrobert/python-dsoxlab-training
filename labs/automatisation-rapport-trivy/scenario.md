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
