# Changelog

**Language:** [English](./CHANGELOG.md) · [Français](./CHANGELOG.fr.md)

All notable changes to this project are recorded in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/).

This repository is a **content catalog**, not a library: it is not versioned and
publishes no releases. The entries below date changes to the catalog, and the
unit that matters is the lab.

## [0.2.1] - 2026-10-19

### Changed

- **Every `doc_url` now points at `www.stephane-robert.info`.** The site moved
  from `blog.` to `www.`, and the old host redirects with a 301 to the same
  path. Nothing was broken: `validate-structure --check-urls` follows
  redirections, and this catalogue was green before a single line changed. The
  migration is housekeeping, not repair: a `doc_url` should point at the page
  rather than depend on a redirection that will be removed one day.

  The paths are identical between the two hosts, so only the host changed. The
  359 `doc_url` the catalogues declare were looked up in the site's own
  repository, offline: all of them exist there, including twenty-three pages
  the old host answered with a 404.

## [0.2.0] - 2026-10-17

### Changed

- **The validator reads the contract, not the terminal panel.**
  `scripts/valider-labs.py` parsed the score out of what `dsoxlab check`
  *displays*. That panel is interface: it changed in dsoxlab 0.4.0 and the
  regex stopped finding anything. It now reads `check --json`, which carries a
  `schema`, and the reading lives in `scripts/verdict_check.py`, **identical in
  all twelve catalogs**.

- **Three verdicts, not two.** A run where every collected test skipped
  measured nothing: it is **SKIP**, neither green nor red, and it stays to be
  measured. Painting it red would accuse the lab of what is missing from the
  machine. `--check` therefore exits `10` in that case, against `1` for a RED,
  mirroring `dsoxlab doctor --strict` where 9 is repaired and 10 is remeasured.

- **The README takes the reference structure** shared by the twelve catalogs:
  fourteen sections, in both languages. Seven of them describe dsoxlab rather
  than the subject, and are therefore identical everywhere.

### Requires

- **dsoxlab 0.4.1 or later**, which introduced the `status` field of
  `check --json`. Without it the validator refuses to conclude rather than
  guessing.

## [0.1.1] - 2026-10-14

### Changed

- The five labs of the common thread replayed after the `conftest.py`
  change.
- The release procedure re-attests labs modified since their verdict.

### Fixed

- Five GitHub actions brought up to date.

## [0.1.0] - 2026-10-09

### Added

- **The `automatisation` section**, seven labs that build one tool,
  `security_check.py`, for the Automation track of the blog's Python course
  (2026-10-02). Each lab starts from the previous lab's solution:
  - `automatisation-lire-un-rapport` reads a JSON export of findings and
    counts them by severity, with exit code 2 on unusable input;
  - `automatisation-interroger-osv` queries the OSV API with a maximum delay,
    checked against a local fake API that records every request;
  - `automatisation-rapport-trivy` parses a real Trivy 0.74.0 report: 26
    occurrences, 22 distinct vulnerabilities, a target with no
    `Vulnerabilities` key;
  - `automatisation-code-de-sortie` moves to Click and adds `--fail-on`:
    0, 1 or 2, the codes a pipeline acts on;
  - `automatisation-tester-son-outil` grades the learner's pytest suite on
    four mutants of the reference tool;
  - `automatisation-dans-la-ci` makes the tool a gate in GitHub Actions:
    tests first, then the CRITICAL threshold, played with act. The only lab
    that needs Docker;
  - `automatisation-lire-un-sbom` crosses a real CycloneDX SBOM (syft
    1.51.1) with OSV: each known vulnerability becomes a finding, with the
    severity of its GitHub advisory (MODERATE as MEDIUM).
- The README's English table marks guides that only exist in French.
- All labs proven in both directions by `scripts/valider-labs.py`:
  0 before the work, 100 after the solution, 0 again after `clean` and
  `run`. Verdicts in `validation-labs.json`.

[Unreleased]: https://github.com/stephrobert/python-dsoxlab-training/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/stephrobert/python-dsoxlab-training/releases/tag/v0.1.1
[0.1.0]: https://github.com/stephrobert/python-dsoxlab-training/releases/tag/v0.1.0
