# Changelog

**Language:** [English](./CHANGELOG.md) · [Français](./CHANGELOG.fr.md)

All notable changes to this project are recorded in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/).

This repository is a **content catalog**, not a library: it is not versioned and
publishes no releases. The entries below date changes to the catalog, and the
unit that matters is the lab.

## [Unreleased]

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
