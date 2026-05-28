# Examples

Runnable examples for `maatora`. Each example is a single
self-contained Python file with no external services required.

| File | What it shows |
|------|---------------|
| `01_simple_decorator.py` | The `@receipt` decorator on a regular Python function — the simplest way to add an audit trail to any callable |
| `02_langgraph_middleware.py` | `ReceiptMiddleware` wrapping a graph step function (works with LangGraph, AutoGen, CrewAI, or any callable) |
| `03_fastapi_ingest.py` | The built-in FastAPI ingest endpoint — POST /receipts, GET /receipts, GET /receipts/{action_id} |
| `04_verify_externally.py` | Ed25519 sign and verify — the core tamper-EVIDENT differentiator. Demonstrates that any modification breaks verification |
| `05_audit_report.py` | `render_audit_report` — multi-receipt HTML report with inline signature verification and a QR-coded footer (requires `pip install -e ".[audit]"` for the QR feature) |

## Running

Install the SDK in editable mode (from the repo root) and then run any
example directly:

```bash
pip install -e ".[test]"
python examples/01_simple_decorator.py
python examples/02_langgraph_middleware.py
python examples/03_fastapi_ingest.py
python examples/04_verify_externally.py
```

For example `03_fastapi_ingest.py`, you can also run the server standalone:

```bash
uvicorn maatora.fastapi_ingest:app --reload
```

## Reading order

If you are new to the SDK, read in this order:

1. **04_verify_externally.py** first — this shows *what makes this SDK
   different* (tamper-EVIDENT vs tamper-resistant), independent of any
   framework.
2. **01_simple_decorator.py** — the minimal integration path for any Python
   function.
3. **02_langgraph_middleware.py** — for agent frameworks.
4. **03_fastapi_ingest.py** — for centralizing receipts from multiple
   agents.
5. **05_audit_report.py** — once you have receipts flowing, render a
   human-readable report for auditors.

## Planned examples (not yet written)

- `06_merkle_log.py` — append-only Merkle log with tamper detection across
  the entire chain (not just individual receipts).
- `07_postgres_store.py` — persisting receipts to PostgreSQL.
- `08_multi_agent_call_tree.py` — using `parent_trace_id` to reconstruct
  multi-agent call trees as required by EU AI Act Article 12.
- `09_compliance_export.py` — exporting receipts in a format suitable for
  SIEM ingestion (Splunk, Datadog, Sentinel).

Contributions of additional examples (especially for new agent frameworks)
are welcome. See `CONTRIBUTING.md` (when added) for the contribution flow.
