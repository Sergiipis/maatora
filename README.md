# Maatora

> Cryptographic, tamper-evident audit log for AI agents.
> Built for EU AI Act Article 12, SOC 2, and HIPAA — open-source under MIT.

<!--
Badges will be enabled after the first public release. Reserved slots:
[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](.)
[![PyPI](https://img.shields.io/pypi/v/maatora.svg)](.)
[![Python](https://img.shields.io/pypi/pyversions/maatora.svg)](.)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/maatora/month)](.)
-->

<!--
HERO GIF: A 90-second demo (sign → verify → tamper → verification fails)
will be added before the public launch. Tooling: `vhs` or `asciinema`.
-->

## Why this exists

AI agents take real actions in production: they call APIs, move money,
update records, send messages. When something goes wrong — a regulator
asks "what did the agent do?", a customer asks "did your agent really
authorize this?", or an engineer asks "why did it call that tool with
those arguments?" — you need a forensic chain you can prove, not just a
dashboard you can show.

Most observability tools for agents (LangSmith, Langfuse, Helicone) provide
*tamper-resistant* audit logs: the data is hard to modify because access is
controlled. This SDK provides *tamper-EVIDENT* records: any modification
breaks a cryptographic chain and is publicly detectable by anyone holding
the public key.

This is the difference between "trust our SaaS" and "verify it yourself."

## 30-second quickstart

```bash
pip install maatora
```

```python
from maatora import receipt


class InMemoryStore:
    def __init__(self): self.receipts = []
    def append(self, r): self.receipts.append(r)


store = InMemoryStore()


@receipt(action="transfer_funds", store=store)
def transfer_funds(actor_id: str, amount: float, to: str) -> dict:
    return {"transferred": amount, "to": to}


transfer_funds(actor_id="agent-alpha", amount=100.0, to="alice")

print(store.receipts[0])
# {'action': 'transfer_funds', 'actor_id': 'agent-alpha',
#  'timestamp': 1716000000.0, 'input_hash': '...', 'output_hash': '...',
#  'status': 'success', 'error': None}
```

For Ed25519 signing and external verification, see
[`examples/04_verify_externally.py`](examples/04_verify_externally.py).

## What you get

- **Tamper-evident** — Ed25519 signatures on every action, append-only
  Merkle log over SHA-256
- **EU AI Act ready** — full reconstructability, parent/child call trees,
  retention controls. See [COMPLIANCE.md](COMPLIANCE.md) for a clause-by-
  clause mapping
- **Framework-agnostic** — works with LangGraph, AutoGen, CrewAI,
  LlamaIndex, or any Python callable
- **Drop-in** — one decorator on your tool functions, or one middleware
  wrap on your graph nodes
- **Self-host or embed** — minimal FastAPI ingest server included, or
  store receipts directly in your own database
- **MIT forever** — core SDK will never be relicensed. See
  [LICENSING.md](LICENSING.md) for the full layered model

## How it compares

| | This SDK | LangSmith | Langfuse | Helicone |
|---|---|---|---|---|
| Cryptographic action signatures | ✅ | ❌ | ❌ | ❌ |
| Tamper-evident Merkle log | ✅ | ❌ | ❌ | ❌ |
| Verifiable proof for compliance | ✅ | ❌ | ❌ | ❌ |
| Open-source self-host | ✅ MIT | ❌ | ✅ MIT | partial |
| Observability dashboards | minimal | ✅ | ✅ | ✅ |
| Cost tracking | ❌ | ✅ | ✅ | ✅ |

Different tools for different jobs. Use this SDK alongside an observability
tool, not instead of one.

## Modules

| Module | Purpose |
|---|---|
| `receipt_canonical_json` | Deterministic JSON serialization (RFC 8785 style) |
| `ed25519_signer` | Keypair generation, signing, verification |
| `receipt_models` | Pydantic v2 models for receipts |
| `receipt_decorator` | `@receipt` wrapper for any function |
| `langgraph_middleware` | Drop-in middleware for LangGraph / agent frameworks |
| `merkle_log` | Tamper-evident append-only log |
| `fastapi_ingest` | Minimal HTTP endpoint to receive receipts |
| `postgres_store` | Persistence to PostgreSQL |
| `cli_viewer` | Local CLI for browsing receipts |
| `html_summary_renderer` | Human-readable audit reports |

## Examples

Runnable examples live in [`examples/`](examples/):

- [`01_simple_decorator.py`](examples/01_simple_decorator.py) — minimal
  integration
- [`02_langgraph_middleware.py`](examples/02_langgraph_middleware.py) —
  agent-framework integration
- [`03_fastapi_ingest.py`](examples/03_fastapi_ingest.py) — centralized
  ingest endpoint
- [`04_verify_externally.py`](examples/04_verify_externally.py) — Ed25519
  sign, verify, tamper detection

## CLI

```bash
maatora list
maatora show <receipt-id>
```

## Compliance

This SDK is designed to help satisfy:

- **EU AI Act Article 12** — record-keeping for high-risk AI systems
  (deadline August 2026)
- **SOC 2 CC7.2** — tamper-evident audit logs of who accessed what data
- **HIPAA Security Rule** — integrity controls for audit records of PHI
  access
- **GDPR Article 30** — records of processing activities

See [COMPLIANCE.md](COMPLIANCE.md) for the clause-by-clause mapping. This
document is informational, not legal advice. For your specific deployment,
hire an auditor.

## Roadmap

The roadmap reflects an audience-first phase. Cloud and enterprise modules
are planned as separate repositories under a different license (see
[LICENSING.md](LICENSING.md)) and are not on the current core roadmap.

Core SDK (this repository, MIT forever):

- [ ] Multi-agent call tree examples and helpers
- [ ] SIEM-export formats (Splunk HEC, Datadog Logs, Elastic ECS)
- [ ] HTML audit report polish
- [ ] LlamaIndex and CrewAI native integrations
- [ ] Documentation site (mkdocs-material)
- [ ] Reproducible benchmarks (signature throughput, Merkle proof size)

## Contributing

Contributions are welcome under the Developer Certificate of Origin (DCO).
Sign off your commits with `git commit -s`. A `CONTRIBUTING.md` with
detailed guidelines will be added before the public launch.

Good first contributions:

- additional examples for your favorite agent framework
- additional storage backends (DuckDB, SQLite WAL mode, ClickHouse)
- documentation improvements
- SIEM exporters

## Community

Community channels (Discord, Twitter/X, newsletter) will be announced
before the public launch. For now, please open a GitHub issue for
questions, bug reports, or feature requests.

## License

MIT — free for any use including commercial. See [LICENSE](LICENSE).

The full layered licensing model (core MIT forever, planned BSL for
premium modules, planned proprietary cloud service) is documented in
[LICENSING.md](LICENSING.md).

## Security

To report a concern about the integrity of receipts, the signing
process, or anything that could mislead a downstream auditor, please
follow the process in [SECURITY.md](SECURITY.md) — open a private
GitHub Security Advisory rather than a public issue.
