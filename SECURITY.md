# Security policy

**Language:** [English](./SECURITY.md) · [Français](./SECURITY.fr.md)

## Supported versions

`python-dsoxlab-training` is under active development. Security fixes
are applied to the latest version of the `main` branch.

| Version | Supported |
| --- | --- |
| latest (`main`) | yes |
| older | no |

## Reporting a vulnerability

**Do not open a public issue for a security vulnerability.**

If you believe you have found one, report it privately:

- Preferred: open a
  [private security advisory](https://github.com/stephrobert/python-dsoxlab-training/security/advisories/new)
  on GitHub.
- Otherwise, use the contact details published on
  <https://blog.stephane-robert.info>.

Please include:

- a description of the vulnerability and its impact,
- the steps to reproduce it (command, environment, `uv --version`, `python --version`,
  `dsoxlab --version`),
- any relevant logs or proof of concept.

We will keep you posted on the fix and credit you in the release notes if you
wish.

## Disclosure policy

We practise coordinated disclosure and commit to the following timelines,
counted from the moment we receive your report:

| Step | Target |
| --- | --- |
| Acknowledging your report | within **48 hours** |
| Initial assessment and severity triage | within **5 days** |
| Fix released, or a written remediation plan | within **30 days** |
| Public disclosure of the vulnerability | within **90 days** |

We publish the advisory as soon as a fix is available, or at the **90-day** mark
at the latest, whichever comes first. If a vulnerability is being actively
exploited, we may disclose sooner to protect users. If a complex fix needs more
time, we tell you before the deadline and agree a new date with you, rather than
letting it lapse in silence.

## Scope

This repository ships **lab content**: Python projects used as starting
points, reference solutions, fixtures and pytest tests, executed by the
external `dsoxlab` CLI on the learner's own machine. The labs build a
security tool that reads vulnerability reports and queries the public OSV
API.

In scope:

- dangerous or malicious lab material, in particular code that would send the
  learner's data anywhere but the OSV API the lab names;
- a leaked secret, private key or API token committed by mistake;
- a pinned dependency with a known vulnerability in a starting point or a
  solution (for instance `click` below 8.3.3, CVE-2026-7246).

Out of scope:

- vulnerabilities in the `dsoxlab` engine itself, which belong to
  [its own repository](https://github.com/stephrobert/dsoxlab);
- those of `requests`, `click`, uv, Trivy, the OSV service or any third-party
  dependency, to be reported to their respective projects;
- the vulnerabilities listed in the sample Trivy report: they are the
  subject of the labs, captured on purpose from outdated packages;
- a lab that fails or scores badly: that is a defect, and it goes in a public
  issue.

## What this repository will never ask of you

No lab requires a secret, an account or a token. The OSV API is public and
anonymous, and the tests replace it with a local fake server.
