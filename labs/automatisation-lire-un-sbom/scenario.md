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
