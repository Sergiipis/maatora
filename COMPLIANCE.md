# Compliance — how maatora maps to regulatory requirements

This document explains how `maatora` addresses concrete
regulatory requirements for AI agent audit logging. It is intended for
compliance officers, security engineers, and AI engineers in regulated
industries (fintech, healthtech, legal-tech, govtech).

It is informational, not legal advice.

## EU AI Act — Article 12 (Record-keeping)

EU AI Act, Article 12, applies to high-risk AI systems with progressive
applicability culminating in **August 2026**. It requires:

| Requirement | How the SDK addresses it |
|-------------|--------------------------|
| Automatic recording of events across the lifecycle | `@action_receipt` decorator captures every tool-call action automatically |
| Full reconstructability of algorithmic decisions | Each receipt stores input arguments, output, timestamp, agent identity, and parent receipt ID |
| Complete audit trail of every relevant interaction | `merkle_log` provides append-only, tamper-evident chain |
| Parent/child IDs for multi-agent call trees | `receipt_models` exposes `parent_id` and `correlation_id` fields |
| Retention of at least 6 months | `postgres_store` retains receipts indefinitely; rotation policy configurable |
| Audit layer integrated into core design, not bolted on | The SDK is the core design — receipts are produced at the moment of action, not reconstructed after the fact |

## SOC 2 — Tamper-evident audit trail

SOC 2 requires "complete, tamper-evident logs of who accessed what data,
when, and how". For AI agents, this means logging the agent identity, the
LLM reasoning context, the parameters passed to tools, and the results
returned.

| Requirement | How the SDK addresses it |
|-------------|--------------------------|
| Tamper-evident logs | Ed25519 signature on every receipt + Merkle hash chain |
| Who performed the action | `receipt_models.agent_id` field, signed |
| What data was accessed | Action name + canonical-JSON-serialized arguments |
| When | RFC 3339 timestamp, included in signature |
| How | Tool name, version, and result, included in signature |
| Append-only storage | `merkle_log` is append-only by construction |
| Centralized log management | `fastapi_ingest` provides POST `/receipts` endpoint for centralization |

Unlike LangSmith and Langfuse audit logs (which are tamper-RESISTANT through
access controls), this SDK provides tamper-EVIDENT records: any modification
breaks the cryptographic chain and is detectable by anyone holding the
public key.

## HIPAA — Integrity controls for audit logs

HIPAA Security Rule requires integrity controls to protect audit logs from
unauthorized alteration or deletion. The January 2025 HIPAA Security Rule
NPRM, expected to be finalized in mid-2026, makes explicit that AI software
which creates, receives, maintains, or transmits ePHI must be inventoried
as a technology asset and subject to mandatory compliance audits.

| Requirement | How the SDK addresses it |
|-------------|--------------------------|
| Integrity controls protecting logs from alteration | Ed25519 cryptographic signature on every receipt |
| Detection of unauthorized modification | Merkle hash chain breaks on any modification |
| 6-year retention | `postgres_store` supports indefinite retention; rotation policy configurable |
| Audit of who accessed PHI | Receipts capture agent identity and action; PHI handling is the user's responsibility |
| Inventory as a technology asset | The SDK is a single Python package with explicit version (`pyproject.toml`) |

Note: this SDK provides the audit-log infrastructure, not the access-control
or encryption-at-rest layers. Those are the responsibility of the deploying
organization.

## GDPR — Article 30 records of processing activities

GDPR Article 30 requires records of processing activities. While not the
primary use-case, the SDK can complement Article 30 records by providing
provable evidence of when an AI agent processed personal data.

| Requirement | How the SDK addresses it |
|-------------|--------------------------|
| Records of processing activities | Each receipt is a record of one processing activity |
| Categories of data processed | Action name + arguments capture the data categories |
| Recipients of the data | Tool name + target captures recipients |
| Time of processing | RFC 3339 timestamp |

For GDPR data-subject requests (right to access, right to erasure), the
deploying organization must implement its own retrieval and deletion logic
on top of receipts.

## Verifying receipts externally

Any third party (auditor, customer, regulator) holding the public key of
the agent operator can verify a receipt without contacting the operator:

```python
from maatora import ed25519_signer, receipt_models

public_key = ed25519_signer.PublicKey.from_pem("...")
receipt = receipt_models.Receipt.from_json(open("receipt.json").read())

assert ed25519_signer.verify(receipt, public_key)
```

This is the property that distinguishes tamper-evident (verifiable proof)
from tamper-resistant (trust-based).

## What the SDK does NOT provide

To be transparent about scope:

- access control or authentication (use your existing IAM)
- encryption at rest (use your existing storage encryption)
- PHI/PII redaction (you must implement before passing arguments to tools)
- dashboards, alerting, or SIEM integration (use `fastapi_ingest` output
  with your SIEM)
- legal certification (this is an open-source library, not a SOC 2 auditor)

## Getting an opinion letter

For B2B sales into regulated industries, customers often request an opinion
letter from a third-party auditor or law firm confirming that a particular
technical implementation satisfies a specific requirement. The SDK author
does not provide this letter, but the architecture is straightforward to
review:

- canonical JSON serialization (RFC 8785 style) — deterministic, no ambiguity
- Ed25519 signing — NIST-recommended, widely audited
- Merkle log over SHA-256 — standard tamper-evident construction
- PostgreSQL append-only — well-understood storage

If you need a letter for your specific deployment, hire an auditor and point
them at this document plus the source code.

## Related external resources

- EU AI Act Article 12 official text: <https://eur-lex.europa.eu/eli/reg/2024/1689>
- NIST SP 800-92 (Guide to Computer Security Log Management)
- RFC 8785 (JSON Canonicalization Scheme)
- RFC 8032 (Edwards-Curve Digital Signature Algorithm, Ed25519)
