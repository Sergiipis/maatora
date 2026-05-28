"""
Example 05: Multi-receipt audit report renderer.

Produces a self-contained HTML audit report from a list of receipts, with
Ed25519 signature verification (when keys are supplied) and an optional QR
code in the footer.

This is the production-grade renderer for compliance use cases: one HTML
document per audit window, printable, contains everything an auditor needs
to verify the receipts externally — without running any code.

Run:
    pip install -e ".[audit]"        # to get the qrcode dependency
    python examples/05_audit_report.py

Writes `audit_report.html` next to this file. Open in a browser; use the
Print button (top-right) to save as PDF or print on paper.
"""

from __future__ import annotations

from pathlib import Path

from maatora import (
    canonicalize,
    generate_keypair,
    render_audit_report,
    sign,
)


def main() -> None:
    # The agent operator generates a keypair once. The public key is shared
    # with auditors; the private key stays with the operator.
    private_pem, public_pem = generate_keypair()

    # Simulate three agent actions captured by the @receipt decorator (or
    # the LangGraph middleware). In production these come from a real run.
    raw_receipts = [
        {
            "action": "transfer_funds",
            "actor_id": "agent-alpha",
            "timestamp": 1716000000.0,
            "input_hash": "a" * 64,
            "output_hash": "b" * 64,
            "status": "success",
            "error": None,
        },
        {
            "action": "send_email",
            "actor_id": "agent-alpha",
            "timestamp": 1716000060.0,
            "input_hash": "c" * 64,
            "output_hash": "d" * 64,
            "status": "success",
            "error": None,
        },
        {
            "action": "call_external_api",
            "actor_id": "agent-alpha",
            "timestamp": 1716000120.0,
            "input_hash": "e" * 64,
            "output_hash": None,
            "status": "error",
            "error": "HTTP 503 from upstream",
        },
    ]

    # Sign each receipt with the operator's private key. Each signature is
    # over the canonical bytes of the receipt fields (sorted JSON keys, no
    # whitespace). The auditor will replay the same canonicalization to
    # verify externally.
    for r in raw_receipts:
        sig = sign(private_pem, canonicalize(r))
        r["signature_hex"] = sig.hex()

    # Render the report. The renderer verifies each signature against the
    # supplied public key and shows a VERIFIED or TAMPERED badge per
    # receipt. The QR code in the footer encodes a URL where readers can
    # learn how to verify the report and how to install Maatora themselves.
    html = render_audit_report(
        raw_receipts,
        run_id="example-run-001",
        model="example-llm-v1",
        public_key_pem=public_pem,
        final_answer=(
            "Agent attempted three actions. Two succeeded; one failed due to an upstream HTTP 503."
        ),
        qr_target_url="https://github.com/sergiipis/maatora",
        version="v0.1.0",
    )

    out = Path(__file__).parent / "audit_report.html"
    out.write_text(html, encoding="utf-8")

    print(f"Audit report written to: {out}")
    print(f"  Receipts:    {len(raw_receipts)}")
    print(f"  Bytes:       {len(html)}")
    print("  Open in a browser; use the Print button (top-right) to save as PDF.")


if __name__ == "__main__":
    main()
