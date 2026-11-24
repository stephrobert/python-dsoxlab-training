# What you really ship

## Situation

The pipeline gate reads Trivy's report. But the customer now requires, with
every delivery, an **SBOM** (Software Bill of Materials): the inventory of
every component of the software, in CycloneDX format. And an inventory is
not a report: it says **what is there**, never **what is vulnerable**. To
know that, each component must be crossed with a vulnerability database,
which `security_check.py` already does with OSV.

The `challenge/work` directory holds the project as the previous lab left
it, workflow included, and `sbom/tableau-de-bord.cdx.json`: the real output
of syft 1.51.1 (CycloneDX 1.7) on a Python project with a small npm front
end. Run your version 4 on it: it refuses it.

## Goal

`uv run python security_check.py sbom/tableau-de-bord.cdx.json --osv`:

- recognises a CycloneDX SBOM by its `bomFormat` key;
- queries OSV once per distinct **PyPI** component, read from its `purl`
  (`pkg:pypi/requests@2.25.0`); npm components are not PyPI packages;
- turns every vulnerability OSV returns into a finding, with the severity of
  the GitHub advisory (`database_specific.severity`): `MODERATE` there means
  what the summary calls MEDIUM, and an advisory with no severity counts as
  UNKNOWN;
- prints the usual summary, the OSV lines, and applies `--fail-on`.

Without `--osv`, an SBOM has nothing to count: the tool says so in one line
naming the option, with code 2. The reports of the previous labs stay
readable, and the test suite of lab 5 must keep passing.

On the real database, this SBOM returns some forty vulnerabilities,
including about twenty PYSEC advisories with no severity. Many overlap a
GitHub advisory already counted: matching those duplicates by their
`aliases` is a possible next step, outside this lab. OSV also sees the flaw
in `click` 8.3.1 (CVE-2026-7246) that Trivy's database ignored the same day.

## Pointers

- `isinstance(data, dict) and data.get("bomFormat") == "CycloneDX"`.
- `str.startswith`, `removeprefix` and `partition("@")` split a `purl`.
- A set of tuples deduplicates the components, `sorted` orders them.
- A small translation dictionary settles `MODERATE`.

## Check

```bash
dsoxlab check automatisation-lire-un-sbom
```

Five checks, twenty points each, on the real SBOM and a fake OSV API that
returns real identifiers with chosen severities.

## Version 5 of security_check.py

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
