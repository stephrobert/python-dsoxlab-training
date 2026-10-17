# Python Training: verifiable labs

**Language:** [English](./README.md) · [Français](./README.fr.md)

[![CI](https://github.com/stephrobert/python-dsoxlab-training/actions/workflows/ci.yml/badge.svg)](https://github.com/stephrobert/python-dsoxlab-training/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/python-dsoxlab-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/python-dsoxlab-training)
[![Plumber compliance](https://score.getplumber.io/github.com/stephrobert/python-dsoxlab-training.svg)](https://score.getplumber.io/github.com/stephrobert/python-dsoxlab-training)
[![SLSA 3](https://slsa.dev/images/gh-badge-level3.svg)](https://slsa.dev)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

The labs of the **Automation** track of the blog's
[Python course](https://blog.stephane-robert.info/docs/developper/programmation/python/)
(in French), played with [dsoxlab](https://github.com/stephrobert/dsoxlab).

## What it is

**Seven labs, one tool.** You do not write seven exercises: you build
`security_check.py` lab after lab, and each lab starts from the previous one's
result. Read a scanner report, query the OSV database, parse a real Trivy
report with its nested results and missing keys, return an exit code a pipeline
can act on, test your own tool, then wire it into a CI job.

That chaining is the point. A tool that reads one well-formed JSON file is an
exercise; a tool that survives a real Trivy report, returns a code a pipeline
reads, and has tests that catch its own bugs, is something you can use the next
day.

## Requirements

- **`mise`**: it installs `uv` and Python at the versions pinned in
  [`mise.toml`](./mise.toml), without curling an archive or touching the system
  package manager.
- **`git`**
- **`dsoxlab`**, the engine, installed as a standalone tool (see below).
- **Docker**, for the **last lab only** (`automatisation-dans-la-ci`), which
  replays a GitHub Actions job locally with `act`. The six others need nothing
  but Python.

**No VM, no `dsoxlab provision`.** This catalog declares no `infra:` block at
all: every lab is `runtime: shell` and runs on your own machine, in its own
`uv` project.

## Install

`dsoxlab` is published on [PyPI](https://pypi.org/project/dsoxlab/). Install it
as a standalone tool, so it stays out of this repository:

```bash
# 1. The dsoxlab CLI (external tool, stays out of this repo)
uv tool install dsoxlab

# 2. This lab catalog
git clone https://github.com/stephrobert/python-dsoxlab-training.git
cd python-dsoxlab-training

# 3. The toolchain, at the pinned versions
mise install

# 4. Check the contract is valid
dsoxlab validate-structure
```

### Your first lab, in five minutes

```bash
export LAB_HOME=$PWD
dsoxlab list-labs                                  # the seven labs, in order
dsoxlab run       automatisation-lire-un-rapport   # set the starting state
dsoxlab challenge automatisation-lire-un-rapport   # read the mission
# ... you work in challenge/work ...
dsoxlab check     automatisation-lire-un-rapport   # run the tests, record the score
```

`run` is what prepares `challenge/work` and copies the fixtures the lab
declares. Running `check` on a lab you never started measures nothing, and says
so rather than recording a 0.

### Keeping it up to date

```bash
uv tool upgrade dsoxlab        # the engine, published on PyPI
git -C <this repo> pull        # the catalog
```

The engine and the catalog move independently: a new `dsoxlab` never requires
re-cloning the labs, and new labs never require upgrading the tool, as long as
the contract version matches. `dsoxlab doctor` says what this repository needs
and what it does not.

## How it works

### The declarative contract (two levels)

The catalog is described by data, not code, which is what keeps the `dsoxlab`
engine domain-agnostic:

- **`meta.yml`** at the root declares the repository identity and the **order**
  of the sections shown by `list-labs`;
- **`lab.yaml`** per lab declares its `skills`, `level`, `runtime` (type,
  fixtures, services), `distros`, `doc_url` and a `validation` block. A
  `lab.fr.yaml` overrides `title` and `description` in French, and nothing else.

`dsoxlab validate-structure` checks the whole contract: `meta.yml` is well
formed, every referenced lab exists with a valid `lab.yaml`, every declared test
and fixture file is really there, and every relative link in a README leads
somewhere.

### The lab lifecycle

```bash
dsoxlab list-labs              # browse the catalog
dsoxlab show      <id>         # metadata and status of one lab
dsoxlab run       <id>         # set the starting state
dsoxlab challenge <id>         # read the mission, no step-by-step
dsoxlab hint      <id>         # reveal a hint (deducted from the score)
dsoxlab check     <id>         # run the tests, compute and record the score
dsoxlab clean     <id>         # remove the work directory
dsoxlab progress               # per-section progress, average score
```

### Runtimes

| Runtime | What the lab asks for |
|---|---|
| `shell` | a terminal, `uv` and Python. Your tool runs in **its own** `uv` project, with its own dependencies. |
| `shell` + Docker | the last lab only, which replays a GitHub Actions job with `act`. |

The separation of environments matters here: your tool needs `requests` and
`click`, and the dsoxlab tests run in dsoxlab's own environment, which has
neither. That is why the labs call `uv run` rather than importing your code.

### The validation model

Validation **proves the behaviour, it does not trust the learner**. Each lab
ships `pytest` tests under `challenge/tests/` that run your tool as a
subprocess and read what it writes and what it returns: never what a file
contains.

And a lab is proven **in both directions**: the tests must fail before the work
and pass after it. A test that is green before the work is not a test, it is an
assumption about the setup. `scripts/valider-labs.py` plays that whole cycle on
every lab and writes its verdict to
[`validation-labs.json`](./validation-labs.json), which is versioned: a lab
shipped without a verdict proves nothing.

Reference solutions live under `labs/<lab>/solution/`, **in clear text**, and
that is deliberate here: each lab's starting point *is* the previous lab's
solution, so the file has to be copyable as a fixture. Read it and you spoil
the lab for yourself.

### Scoring, hints, progress

`check` records a score (tests passed out of total, minus the cost of any hints
revealed). Hints are **base64-encoded** in `challenge/hints.yaml`, so that
opening the file does not give them away, and their cost grows with their
precision. History lives in a SQLite database **local to this repository**.

A run that measured nothing is neither a pass nor a failure: if every collected
test skips, `check` records no score and says why. A score of 0 would accuse the
lab of what is missing from the machine.

## Catalog

<!-- LABS:START -->
### Automation: a security tool, step by step

| Lab (id) | Title | Level | Certif | Runtime | Companion guide |
|---|---|---|---|---|---|
| `automatisation-lire-un-rapport` | Read a scanner report: count the vulnerabilities by severity | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/programmation/python/json/) (in French) |
| `automatisation-interroger-osv` | Query the OSV API: what is known about each package of the report | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/programmation/python/requests/) (in French) |
| `automatisation-rapport-trivy` | Read a real Trivy report: nested results, missing keys and duplicates | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/programmation/python/dictionnaire/) (in French) |
| `automatisation-code-de-sortie` | An exit code a pipeline can act on: --fail-on with Click | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/programmation/python/click/) (in French) |
| `automatisation-tester-son-outil` | Test your own tool: a pytest suite that catches four real bugs | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/programmation/python/tests/pytest/) (in French) |
| `automatisation-dans-la-ci` | A security gate in the pipeline: security_check.py in GitHub Actions | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/pipeline-cicd/github/securite/lab/pipeline-ci/) (in French) |
| `automatisation-lire-un-sbom` | Read an SBOM: cross a CycloneDX inventory with the OSV database | automatisation | - | shell | [guide](https://blog.stephane-robert.info/docs/securiser/supply-chain/sbom/) (in French) |

_7 labs, table generated by `scripts/gen_catalog.py`._
<!-- LABS:END -->

## Contributing

Read [`CONTRIBUTING.md`](./CONTRIBUTING.md). In short: a lab is proven **in both
directions** before it is merged, `dsoxlab validate-structure` is green, and the
statement exists in English and in French.

Anything user-facing is bilingual. A document translated on one side only is
reported by the validator, not left to goodwill.

## License

See [`LICENSE`](./LICENSE).
