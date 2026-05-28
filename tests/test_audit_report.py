"""Tests for maatora.audit_report.render_audit_report."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from maatora import (
    canonicalize,
    generate_keypair,
    render_audit_report,
    sign,
)


def _sample_receipts(signer_pem: bytes | None = None) -> list[dict]:
    """Build a small list of receipts; sign each if a private key is given."""
    raw = [
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
            "output_hash": None,
            "status": "error",
            "error": "SMTP timeout",
        },
    ]
    if signer_pem is not None:
        for r in raw:
            sig = sign(signer_pem, canonicalize(r))
            r["signature_hex"] = sig.hex()
    return raw


def test_render_minimal_no_signatures():
    """With no signatures and no QR, render plain HTML."""
    html = render_audit_report(_sample_receipts())
    assert "<!DOCTYPE html>" in html
    assert "Maatora" in html
    assert "Audit Report" in html
    assert "transfer_funds" in html
    assert "send_email" in html
    assert "SUCCESS" in html
    assert "ERROR" in html
    # No verification badge if neither signature nor public key
    assert "VERIFIED" not in html
    assert "TAMPERED" not in html
    # No footer element if no QR url (CSS classes for footer exist in <style>,
    # so check for the rendered <footer> element specifically)
    assert "<footer" not in html


def test_render_with_metadata():
    """Run ID, model, generated_at appear in the meta block."""
    when = datetime(2026, 5, 28, 12, 0, 0, tzinfo=UTC)
    html = render_audit_report(
        _sample_receipts(),
        run_id="20260528_120000",
        model="llama3.1:8b",
        generated_at=when,
        merkle_root_hex="abcd1234",
    )
    assert "20260528_120000" in html
    assert "llama3.1:8b" in html
    assert "2026-05-28 12:00:00 UTC" in html
    assert "abcd1234" in html


def test_render_signatures_verified():
    """With valid signatures and matching public key, all show VERIFIED."""
    priv, pub = generate_keypair()
    receipts = _sample_receipts(signer_pem=priv)
    html = render_audit_report(receipts, public_key_pem=pub)
    assert html.count("VERIFIED") == 2
    assert "TAMPERED" not in html


def test_render_signatures_tampered():
    """With valid signatures but wrong public key, all show TAMPERED."""
    priv, _ = generate_keypair()
    _, wrong_pub = generate_keypair()
    receipts = _sample_receipts(signer_pem=priv)
    html = render_audit_report(receipts, public_key_pem=wrong_pub)
    assert html.count("TAMPERED") == 2
    assert "VERIFIED" not in html


def test_render_mixed_signatures():
    """If only some receipts have signature_hex, only those get verification."""
    priv, pub = generate_keypair()
    receipts = _sample_receipts(signer_pem=priv)
    # Strip signature from second receipt
    del receipts[1]["signature_hex"]
    html = render_audit_report(receipts, public_key_pem=pub)
    assert html.count("VERIFIED") == 1
    assert html.count("TAMPERED") == 0


def test_render_signature_present_without_key():
    """If receipts have signatures but caller did not supply a public key,
    the badge says SIGNATURE PRESENT (not VERIFIED, not TAMPERED)."""
    priv, _ = generate_keypair()
    receipts = _sample_receipts(signer_pem=priv)
    html = render_audit_report(receipts)
    assert "SIGNATURE PRESENT" in html
    assert "VERIFIED" not in html
    assert "TAMPERED" not in html


def test_render_with_qr_url():
    """QR URL produces an inline SVG QR code in the footer."""
    html = render_audit_report(
        _sample_receipts(),
        qr_target_url="https://example.com/maatora",
    )
    assert "<footer" in html
    assert "<svg" in html
    assert "Scan to learn how to verify" in html


def test_render_without_qr_url():
    """Without a QR URL, the footer is omitted entirely."""
    html = render_audit_report(_sample_receipts())
    assert "<footer" not in html
    assert "<svg" not in html


def test_render_custom_brand_and_title():
    """Brand and title are configurable for white-label use."""
    html = render_audit_report(
        _sample_receipts(),
        brand="AcmeCorp",
        title="Compliance Log",
    )
    assert "AcmeCorp" in html
    assert "Compliance Log" in html
    # The default brand should not leak through
    assert "<title>AcmeCorp Compliance Log" in html


def test_render_with_final_answer():
    """Final answer text appears in its highlighted block."""
    html = render_audit_report(
        _sample_receipts(),
        final_answer="The agent transferred funds and attempted to send confirmation.",
    )
    assert "Final LLM answer:" in html
    assert "transferred funds" in html


def test_render_without_final_answer():
    """Without a final_answer, the highlighted block is absent."""
    html = render_audit_report(_sample_receipts())
    assert "Final LLM answer:" not in html


def test_render_with_version_in_footer():
    """Version string is reflected in the footer when QR is present."""
    html = render_audit_report(
        _sample_receipts(),
        qr_target_url="https://example.com",
        version="v0.1.0",
    )
    assert "v0.1.0" in html


def test_render_empty_receipts():
    """An empty receipt list still renders valid HTML with a placeholder."""
    html = render_audit_report([])
    assert "<!DOCTYPE html>" in html
    assert "No receipts." in html
    assert "Receipts (0)" in html


def test_render_handles_missing_optional_fields():
    """Receipts without optional fields (signature, merkle root) render OK."""
    minimal = [
        {
            "action": "ping",
            "actor_id": "agent-x",
            "timestamp": 1716000000.0,
            "input_hash": "a" * 64,
            "output_hash": "b" * 64,
            "status": "success",
            "error": None,
        },
    ]
    html = render_audit_report(minimal)
    assert "ping" in html
    assert "(unsigned)" in html  # signature placeholder
    assert "(none)" in html  # merkle root placeholder


def test_qr_svg_inline_no_external_resources():
    """QR is embedded as inline SVG, the HTML has no external requests."""
    html = render_audit_report(
        _sample_receipts(),
        qr_target_url="https://example.com/x",
    )
    assert "<svg" in html
    # No external script or stylesheet references
    assert "<script src=" not in html
    assert "<link rel=" not in html
    assert 'src="http' not in html


def test_qrcode_missing_raises_clear_error(monkeypatch):
    """If qrcode package is missing, a clear ImportError is raised."""
    import maatora.audit_report as ar

    def _raise(*args, **kwargs):
        raise ImportError("simulated missing qrcode")

    monkeypatch.setattr(ar, "_generate_qr_svg", _raise)

    with pytest.raises(ImportError, match="simulated"):
        render_audit_report(
            _sample_receipts(),
            qr_target_url="https://example.com",
        )
