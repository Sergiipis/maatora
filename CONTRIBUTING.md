# Contributing

Thank you for considering a contribution. This project is small and audience-first
in its current phase, which means clear, well-scoped contributions move faster
than large refactors. Read this document before opening a pull request.

## Ways to contribute

- **Bug reports and reproductions** — open an issue with a minimal failing example.
- **Examples** — additional examples for new agent frameworks (CrewAI, AutoGen,
  LlamaIndex, etc.) are explicitly welcome. See [`examples/README.md`](examples/README.md)
  for the format we use.
- **Storage backends** — DuckDB, SQLite WAL, ClickHouse, S3 — additional
  `*_store.py` modules that conform to the existing store protocol.
- **SIEM exporters** — formatters for Splunk HEC, Datadog Logs, Elastic ECS, Sentinel.
- **Documentation** — clarifications, typo fixes, additional compliance mappings.
- **New features** — please open a discussion first; the scope of the core SDK
  is intentionally narrow (see "Out of scope" below).

## Developer Certificate of Origin (DCO)

This project uses DCO instead of a CLA. By signing off your commits, you
certify that you wrote the code (or have the right to submit it) under the
terms of the project's MIT license. The full text is at
[developercertificate.org](https://developercertificate.org/).

To sign off, add `-s` to every commit:

```bash
git commit -s -m "your message"
```

This appends a `Signed-off-by: Your Name <your@email>` trailer. Use your real
name; pseudonyms are not accepted for DCO.

If you forget the sign-off on a single commit:

```bash
git commit --amend -s --no-edit
```

For a branch with multiple unsigned commits:

```bash
git rebase HEAD~N --signoff
```

CI will reject pull requests with any commit missing a sign-off.

## Local development setup

Requirements: Python 3.11 or 3.12.

```bash
git clone https://github.com/Sergiipis/maatora.git
cd maatora
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run the full local check suite before pushing:

```bash
ruff check src tests examples
ruff format --check src tests examples
mypy src examples
pytest --cov=maatora --cov-report=term -q
```

All four must pass. CI will run the same checks on the matrix `3.11`/`3.12`.

For changes that touch packaging, runtime dependencies, or anything
documented in the README, also run the clean-room smoke install test —
it builds the wheel and installs it in a fresh `python:3.12-slim`
Docker container, then runs both README snippets end-to-end:

```bash
bash scripts/smoke_install_test.sh
```

This catches missing runtime deps and broken entry points that happen
to work in the dev venv but would fail for a first-time user.

## Pull request checklist

Before requesting review, confirm:

- [ ] All commits are signed off (`git commit -s`)
- [ ] `ruff check` and `ruff format --check` pass
- [ ] `mypy` passes
- [ ] `pytest` passes and overall coverage stays at or above the existing line
- [ ] New behavior has tests (unit tests for new modules; integration test if
  the change touches FastAPI ingest or the Merkle log)
- [ ] Public API changes are mentioned in `CHANGELOG.md` under `## [Unreleased]`
- [ ] Documentation reflects the change (README, examples, or module docstring)

Small PRs merge faster than large ones. A 200-line PR will get a thorough
review the same week; a 2000-line PR will get a thorough review in a
month — or never. Split when in doubt.

## Code style

- `ruff` enforces formatting and lint rules — see `pyproject.toml` for the
  exact configuration.
- `mypy` runs in strict-enough mode that `Any` returns are flagged. Type
  annotations are required on all public functions.
- Public modules expose their API through `src/maatora/__init__.py`.
  Add new public symbols there.
- Prefer composition over inheritance for store/sink/exporter abstractions.
- No new runtime dependencies without discussion. The current dependency
  surface is intentionally small: `pydantic`, `cryptography`, `fastapi`,
  `jinja2`, `psycopg`.

## Tests

- Unit tests live alongside their target module: `tests/test_<module>.py`.
- Integration tests for the FastAPI ingest use `httpx.AsyncClient` and the
  `TestClient` pattern. See `tests/test_fastapi_ingest.py`.
- Tests must be deterministic. If you need time, use `freezegun` or inject
  a clock. If you need randomness, seed it.
- New cryptographic code requires both a positive-path test and a
  tamper-detection test (modify one byte, assert verification fails).

## Out of scope (for the core SDK)

These are deliberate non-goals for this repository. Premium and cloud features
will live in separate repositories under a different license — see
[`LICENSING.md`](LICENSING.md):

- Hosted SaaS, multi-tenant ingest, billing.
- Web UI beyond the existing HTML summary renderer.
- Per-tenant retention policies, RBAC, audit-export dashboards.
- Telemetry that calls home from the SDK.
- Vendor-locked storage backends (e.g., a proprietary cloud storage tier).

If your change overlaps with any of the above, please open a discussion
first.

## Reporting security issues

**Do not open a public issue for security vulnerabilities.** See
[`SECURITY.md`](SECURITY.md) for the responsible-disclosure process.

## Code of Conduct

Participation in this project is governed by the
[Code of Conduct](CODE_OF_CONDUCT.md). By contributing, you agree to abide by it.

## License

By contributing, you agree that your contributions will be licensed under the
MIT license (the project's license). The full layered licensing model is
documented in [`LICENSING.md`](LICENSING.md); the core SDK in this repository
is, and will remain, MIT.
