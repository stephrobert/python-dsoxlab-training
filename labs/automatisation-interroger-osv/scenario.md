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
