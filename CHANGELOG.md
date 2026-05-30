# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Nothing yet.

## [0.1.0] - 2026-05-29

First public release, published to PyPI.

### Added

- Cryptographic receipt model (`receipt_models`) for AI-agent actions, with
  canonical-JSON serialization (`receipt_canonical_json`) following RFC 8785
  style.
- Ed25519 keypair generation, signing, and verification (`ed25519_signer`).
- `@receipt` decorator for any Python callable (`receipt_decorator`).
- `ReceiptMiddleware` for LangGraph / AutoGen / CrewAI / any agent framework
  with a callable step function (`langgraph_middleware`).
- Append-only Merkle log over SHA-256 (`merkle_log`).
- Minimal FastAPI ingest server with `POST /receipts`, `GET /receipts`,
  `GET /receipts/{action_id}` (`fastapi_ingest`).
- PostgreSQL persistence backend (`postgres_store`).
- Local CLI for listing and showing receipts (`cli_viewer`, entry point `maatora`).
- HTML summary renderer for human-readable audit reports
  (`html_summary_renderer`).
- Multi-receipt audit report renderer (`audit_report.render_audit_report`):
  self-contained HTML with inline signature verification (VERIFIED /
  TAMPERED badges), Merkle root display, configurable brand + title,
  optional QR-coded footer pointing to a verification URL, print-friendly
  layout. QR code requires the optional `qrcode` dependency
  (`pip install maatora[audit]`).
- Five runnable examples in `examples/`:
  `01_simple_decorator.py`, `02_langgraph_middleware.py`,
  `03_fastapi_ingest.py`, `04_verify_externally.py`,
  `05_audit_report.py`.
- Documentation: `README.md`, `COMPLIANCE.md` (EU AI Act Article 12, SOC 2,
  HIPAA, GDPR mapping), `LICENSING.md` (layered licensing model),
  `CONTRIBUTING.md`.
- GitHub Actions CI: ruff lint + format check, mypy, pytest with coverage,
  matrix 3.11 / 3.12.
- GitHub Actions release workflow: tag-triggered publish to PyPI via OIDC
  trusted publishing.

### Notes

- This project was previously developed under the working name
  `agent-action-receipts-sdk`. It was renamed to `maatora` on 2026-05-25
  before the first public release. The Python module, PyPI package, and
  CLI entry point all use the new name. No external users existed before
  the rename, so no compatibility shim is provided.

[Unreleased]: https://github.com/Sergiipis/maatora/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Sergiipis/maatora/releases/tag/v0.1.0
