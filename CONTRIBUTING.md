# Contributing to python-dsoxlab-training

**Language:** [English](./CONTRIBUTING.md) · [Français](./CONTRIBUTING.fr.md)

This repository is a **lab catalog** consumed by the
[`dsoxlab`](https://github.com/stephrobert/dsoxlab) CLI. Contributions are new
labs, fixes and translations. The CLI lives in its own repository: do not add
engine code here.

## Setup

```bash
uv tool install dsoxlab        # the CLI (external tool)
git clone https://github.com/stephrobert/python-dsoxlab-training.git
cd python-dsoxlab-training
mise install                   # the pinned uv and Python
dsoxlab validate-structure     # check the contract
```

No VM, no Docker, no `dsoxlab provision`: every lab is `runtime: shell`, and
the learner's tool runs on their own machine, in its own uv project.

## The running thread

The labs of the `automatisation` section build **one tool**,
`security_check.py`, version after version. The starting point of a lab is
the reference solution of the previous one: a fix to a solution must be
carried over to the next lab's `fixtures/`. The order of `meta.yml` is the
order in which the labs are played, and it is not reordered.

This is also why the solutions are **not encrypted**, unlike the Linux,
Terraform and Ansible catalogs: each solution is shipped in clear as the next
lab's starting point, and the reference of the last lab is the solution of
the fourth. Encryption would hide nothing and add a key to lose.

## The golden rule: a lab is proven in both directions

A passing test proves nothing until you have seen the right thing **fail**:

```bash
uv run scripts/valider-labs.py --lab <id>
```

plays `dsoxlab run`, `check` (must be 0), the reference solution, `check`
(must be 100), then `clean`, `run`, `check` (0 again), and records the
verdict in `validation-labs.json`. A lab absent from that file is
deliverable, not validated.

Ask yourself, for every test: **would it be green if the learner did
nothing?** With a running thread the trap is frequent: the previous version
of the tool already does half of the lab. Every test must require what the
lab adds.

## What the tests must read

What the tool **does**: its output, its standard error, its exit code, and
what it sent to the fake OSV API. Never its source code. The tests run the
tool the way the learner does, with `uv run` in the learner's project
(`conftest.py::lancer_outil`): `dsoxlab check` runs pytest in dsoxlab's own
environment, which has neither `requests` nor `click`.

Expected results are **computed**, not written: reports are drawn at random,
and the seed is printed on failure.

## Anatomy of a lab

```text
labs/<lab>/
├── lab.yaml            # the contract (id, level, runtime, fixtures, validation…)
├── lab.fr.yaml         # French override of title/description ONLY
├── README.md / README.fr.md        # the presentation
├── scenario.md / scenario.fr.md    # the situation, the target state, the proof
├── fixtures/           # the starting material, copied into challenge/work
├── solution/           # the reference solution, laid over challenge/work
└── challenge/
    ├── README.md / README.fr.md    # the mission, numbered requirements
    ├── hints.yaml                  # base64 hints, four cost levels
    └── tests/test_functional.py    # the proof
```

Hints are written in clear in `challenge/hints.source.yaml` (not committed),
then `uv run python scripts/ecrire_indices.py labs/<id>` encodes them.

The last lab grades the learner's test suite against **mutants** generated
by `scripts/generer_mutants.py` from `challenge/tests/reference/`.

## Local checks before opening a PR

```bash
dsoxlab validate-structure          # the meta.yml + lab.yaml contract
uv run scripts/valider-labs.py      # every lab, both directions
uv run pytest tests/ -q             # the repository's meta-tests
uv run python scripts/gen_catalog.py --check   # the README catalog
```

## Conventions

- **Lab id:** `<section>-<slug>`, matching the directory name.
- **Commits:** in French, a factual subject saying **what changed and why**,
  no conventional prefix.
- **i18n:** the unsuffixed file is English (the repository's official
  language), `*.fr.md` is the French translation. Both must say the same
  thing.
- **Style:** no emoji and no em dash in what the learner reads. Assertion
  messages teach: they say what is wrong and why.

## Pull requests

Work on a dedicated branch, keep `dsoxlab validate-structure` and
`valider-labs.py` green, and link the capability or issue it addresses.
