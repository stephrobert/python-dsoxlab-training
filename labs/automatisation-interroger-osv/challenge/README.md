# What the OSV database knows about your packages

## Situation

Version 1 of `security_check.py` summarises what the scanner found. But a
scanner is never more up to date than its own database: when this lab was
written, Trivy's database still ignored a flaw in `click` 8.3.1 that the
public OSV (Open Source Vulnerabilities) database already knew. Your team
wants a second source, queried on demand.

The `challenge/work` directory holds your solution of the previous lab. OSV
exposes an HTTP API: `POST https://api.osv.dev/v1/query`, with a JSON body
naming the package, its ecosystem and its version, and a response listing
the known vulnerabilities in `vulns`.

## Goal

`uv run python security_check.py <report> --osv` prints the usual summary,
then one line per distinct (package, version) pair of the report, sorted:

```text
OSV jinja2==2.11.2: none
OSV requests==2.25.0: GHSA-j8r2-6x86-q33q, PYSEC-2023-74
```

Each pair is queried once, and only with `--osv`: without the option, the
tool makes no network call. The API address is read from the `OSV_API_URL`
environment variable (`https://api.osv.dev` by default), and the maximum
delay of a call, in seconds, from `OSV_TIMEOUT` (10 by default).

An API that is down or silent does not block the pipeline and produces no
traceback: the tool says so in one line and exits with code 2.

## Pointers

- `requests` is not in the standard library: `uv add requests` declares it
  in `pyproject.toml` and installs it in the project.
- `requests.post(url, json=body, timeout=...)` sends JSON; without
  `timeout`, a silent server blocks the call forever.
- `raise_for_status()` turns a 500 response into an exception, and
  `requests.Timeout` and `requests.RequestException` can be caught.
- A `set` of tuples removes duplicates; `sorted` orders them.

## Check

```bash
dsoxlab check automatisation-interroger-osv
```

Five checks, twenty points each. A fake API replaces OSV: it records every
request it receives, which makes it possible to check what the tool really
asked.

## Version 2 of security_check.py

5 tasks, 100 points, 40 minutes.

The project is in `challenge/work`, with your version 1. You add the
`--osv` option. The tests replace OSV with a fake API, given by
`OSV_API_URL`, which records what the tool asks it.

### Task 1: each package is queried only once (20 pts)

One `POST /v1/query` request per distinct (package, version) pair, with
`"ecosystem": "PyPI"` in `package`. A pair present twice in the report is
queried once.

### Task 2: known vulnerabilities are printed per package (20 pts)

After the summary, one `OSV package==version: ID, ID` line per pair, pairs
sorted by package then version, identifiers sorted, `none` if there are
none.

### Task 3: the summary stays, and without --osv no call (20 pts)

With `--osv`, the summary by severity does not change. Without `--osv`, the
tool does not contact the API.

### Task 4: an API outage is reported without a traceback (20 pts)

If the API answers HTTP 500: exit code 2, one error line containing `500`,
no Python traceback.

### Task 5: a silent API does not block the pipeline (20 pts)

With `OSV_TIMEOUT=1` and an API that takes 6 seconds to answer: exit code 2,
one error line containing `OSV`, and the tool returns within 5 seconds.
