"""Multi-receipt audit report renderer.

Renders a self-contained HTML audit report from a list of receipts. Optionally
verifies Ed25519 signatures, displays VERIFIED/TAMPERED badges, and includes a
QR code in the footer for verifiable provenance.

Example:
    from maatora import render_audit_report

    html = render_audit_report(
        receipts=store.receipts,
        run_id="20260528_195346",
        model="llama3.1:8b-instruct-q4_K_M",
        public_key_pem=public_pem,
        qr_target_url="https://github.com/Sergiipis/maatora",
    )
    Path("report.html").write_text(html, encoding="utf-8")

The output is a single HTML document with inline CSS and inline SVG (no
external resources). Print-friendly via @media print; the Print button in the
toolbar hides when printing.

QR code rendering requires the optional `qrcode` package
(install with: `pip install maatora[audit]`).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from maatora.ed25519_signer import verify
from maatora.receipt_canonical_json import canonicalize


def _generate_qr_svg(url: str) -> str:
    """Return inline SVG markup for a QR code encoding url.

    Raises ImportError if the optional `qrcode` package is not installed.
    """
    try:
        import io

        import qrcode
        import qrcode.image.svg
    except ImportError as e:  # pragma: no cover - exercised only when qrcode missing
        raise ImportError(
            "qrcode package required for QR footer. Install with: pip install maatora[audit]"
        ) from e

    qr = qrcode.QRCode(
        box_size=4,
        border=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
    buf = io.BytesIO()
    img.save(buf)
    return buf.getvalue().decode("utf-8")


def _format_ts(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


_RECEIPT_BLOCK = """<div class="receipt {css_status}">
  <div class="status-bar {css_status}"><span class="status-bar-text">{status_label}</span></div>
  <div class="action">#{idx}. {action}</div>
  <div class="kv">
    <span>actor</span><span>{actor_id}</span>
    <span>timestamp</span><span class="date">{when}</span>
    <span>input hash</span><span><code>{input_hash}</code></span>
    <span>output hash</span><span><code>{output_hash}</code></span>
    <span>signature (Ed25519)</span><span class="sig"><code>{sig_short}</code></span>
    <span>Merkle root after</span><span class="sig"><code>{root_short}</code></span>
    {verification_row}
  </div>
</div>"""

_VERIFICATION_ROW = (
    '<span>verification</span><span class="badge {css_verify_badge}">{verify_label}</span>'
)


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{brand} {title} {run_id_suffix}</title>
<style>
body {{ font-family: -apple-system, system-ui, sans-serif; max-width: 1100px; margin: 2em auto; padding: 0 1em; color: #222; }}
.report-header {{
  border-bottom: 2px solid #1a4a8a;
  padding-bottom: 0.7em;
  margin-bottom: 1.5em;
}}
.report-header .brand {{
  font-size: 2.4em;
  font-weight: 800;
  color: #1a4a8a;
  letter-spacing: -0.02em;
  line-height: 1.05;
}}
.report-header .doc-type {{
  font-size: 1.25em;
  color: #555;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  margin-top: 0.55em;
}}
.meta {{ background: #f3f3f3; padding: 1em; border-radius: 4px; margin: 1em 0; font-size: 0.9em; line-height: 1.7; }}
.date {{ font-size: 1.2em; font-weight: 600; color: #1a4a8a; font-variant-numeric: tabular-nums; }}
.final {{ background: #e8f4ea; padding: 1em; border-left: 4px solid #2a7a3a; margin: 1em 0; }}
.receipt {{
  position: relative;
  border: 1px solid #ddd; border-radius: 6px;
  padding: 1.2em 1.2em 1.2em 2.5em;
  margin: 1.2em 0;
  overflow: hidden;
}}
.receipt.err {{ background: #fdf2f2; }}
.status-bar {{
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 1.3em;
  display: flex; align-items: center; justify-content: center;
}}
.status-bar.ok {{ background: #2a7a3a; }}
.status-bar.err {{ background: #c33; }}
.status-bar-text {{
  transform: rotate(-90deg);
  white-space: nowrap;
  color: white;
  font-weight: 700;
  font-size: 0.7em;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}}
.action {{
  font-weight: bold; font-size: 1.1em; color: #1a4a8a;
  margin-bottom: 0.5em;
}}
.kv {{ display: grid; grid-template-columns: 180px 1fr; gap: 0.3em 1em; margin-top: 0.5em; align-items: center; }}
.kv > span:nth-child(odd) {{ color: #666; }}
.kv > .badge {{ justify-self: start; }}
code {{ font-family: monospace; font-size: 0.85em; word-break: break-all; }}
.sig {{ color: #888; }}
.badge {{
  display: inline-flex; align-items: center; gap: 0.3em;
  padding: 0.35em 0.95em;
  border-radius: 14px;
  font-size: 0.78em; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.05em;
  color: white;
  white-space: nowrap;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}}
.badge.verified {{ background: #2a7a3a; }}
.badge.tampered {{ background: #c33; }}
.badge.unsigned {{ background: #888; }}
.toolbar {{
  position: fixed; top: 1.5em; right: 1.5em;
  display: flex; flex-direction: column; gap: 0.6em;
  z-index: 1000;
}}
.toolbar button {{
  background: #1a4a8a; color: white;
  border: none; padding: 0.85em 1.5em;
  font-size: 1em; font-weight: 600;
  border-radius: 8px; cursor: pointer;
  box-shadow: 0 3px 10px rgba(0,0,0,0.18);
  display: flex; align-items: center; gap: 0.55em;
  transition: all 0.15s;
  min-width: 13em;
  justify-content: center;
}}
.toolbar button:hover {{ background: #154075; transform: translateY(-2px); box-shadow: 0 5px 14px rgba(0,0,0,0.25); }}
.toolbar button:active {{ transform: translateY(0); box-shadow: 0 2px 6px rgba(0,0,0,0.2); }}
.toolbar button .icon {{ font-size: 1.25em; line-height: 1; }}
.report-footer {{
  margin-top: 3em;
  padding-top: 1.5em;
  border-top: 1px solid #ccc;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 1.5em;
  align-items: center;
  font-size: 0.85em;
  color: #555;
}}
.report-footer .qr svg {{ width: 90px; height: 90px; display: block; }}
.report-footer .qr {{ background: white; padding: 4px; border: 1px solid #ddd; border-radius: 4px; }}
.report-footer .footer-text {{ line-height: 1.5; }}
.report-footer .footer-text strong {{ color: #1a4a8a; font-size: 1.05em; }}
.report-footer .footer-right {{ text-align: right; font-size: 0.85em; color: #888; }}
@media print {{
  .toolbar {{ display: none !important; }}
  body {{ background: white; max-width: 100%; margin: 0; padding: 1em; }}
  .meta, .final, .receipt {{ box-shadow: none; }}
  .receipt {{ break-inside: avoid; page-break-inside: avoid; }}
  .meta {{ break-inside: avoid; }}
  .final {{ break-inside: avoid; }}
  h1, h2 {{ break-after: avoid; }}
  code {{ font-size: 0.75em; }}
  .report-footer {{ break-inside: avoid; page-break-inside: avoid; }}
  @page {{ margin: 1.5cm; }}
}}
</style></head><body>
<div class="toolbar">
  <button class="btn-print" onclick="window.print()" title="Print or save as PDF (Ctrl+P)">
    <span class="icon">&#128424;</span>
    <span>Print / Save as PDF</span>
  </button>
</div>
<header class="report-header">
  <div class="brand">{brand}</div>
  <div class="doc-type">{title}</div>
</header>
<div class="meta">
{meta_rows}
</div>
{final_block}
<h2>Receipts ({count})</h2>
{receipts_html}
{footer_html}
</body></html>
"""


def render_audit_report(
    receipts: list[dict[str, Any]],
    *,
    run_id: str | None = None,
    model: str | None = None,
    generated_at: datetime | None = None,
    merkle_root_hex: str | None = None,
    public_key_pem: bytes | None = None,
    final_answer: str | None = None,
    qr_target_url: str | None = None,
    title: str = "Audit Report",
    brand: str = "Maatora",
    version: str | None = None,
) -> str:
    """Render a multi-receipt audit report as self-contained HTML.

    Args:
        receipts: List of receipt dicts (as produced by the @receipt decorator).
            May optionally include `signature_hex` and `merkle_root_after`
            fields if the caller has signed each receipt externally.
        run_id: Identifier for this run/batch (shown in header).
        model: Name of the LLM/agent that produced these receipts.
        generated_at: When this report was generated. Defaults to now UTC.
        merkle_root_hex: Final Merkle root after all receipts (hex string).
        public_key_pem: Ed25519 public key in PEM bytes. If supplied AND a
            receipt has `signature_hex`, the receipt is verified and shown
            with a VERIFIED or TAMPERED badge. If not supplied (or no
            signature on the receipt), the verification row is omitted.
        final_answer: Optional textual final answer (highlighted block).
        qr_target_url: URL to encode in the footer QR code. If None, no QR
            is shown and the footer is omitted. Requires the optional
            `qrcode` package (install with: `pip install maatora[audit]`).
        title: Document type label (default "Audit Report").
        brand: Brand name shown in the header (default "Maatora").
        version: Optional version string shown in the footer (e.g. "v0.1.0").

    Returns:
        Self-contained HTML string with inline CSS and inline SVG.
    """
    if generated_at is None:
        generated_at = datetime.now(tz=UTC)

    # Render meta block
    meta_lines = []
    if run_id:
        meta_lines.append(f"  <strong>Run ID:</strong> {run_id}<br>")
    meta_lines.append(
        f'  <strong>Generated:</strong> <span class="date">'
        f"{generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</span><br>"
    )
    if model:
        meta_lines.append(f"  <strong>Model:</strong> <code>{model}</code><br>")
    meta_lines.append(f"  <strong>Receipts captured:</strong> {len(receipts)}<br>")
    if merkle_root_hex:
        meta_lines.append(
            f"  <strong>Merkle root (final):</strong> <code>{merkle_root_hex}</code><br>"
        )
    if public_key_pem:
        pub_first_line = public_key_pem.decode("ascii", errors="replace").split("\n")[1]
        meta_lines.append(
            f"  <strong>Public key (for auditor):</strong> <code>{pub_first_line[:48]}&hellip;</code>"
        )

    # Final answer block (optional)
    if final_answer:
        final_block = (
            f'<div class="final"><strong>Final LLM answer:</strong><br>'
            f"{final_answer.replace(chr(10), '<br>')}</div>"
        )
    else:
        final_block = ""

    # Receipts
    blocks = []
    for i, e in enumerate(receipts, 1):
        is_ok = e.get("status") == "success"
        sig_hex = e.get("signature_hex")
        root_hex = e.get("merkle_root_after")

        verification_row = ""
        if sig_hex and public_key_pem:
            sig_bytes = bytes.fromhex(sig_hex)
            canon = canonicalize(
                {k: v for k, v in e.items() if k not in ("signature_hex", "merkle_root_after")}
            )
            verified = verify(public_key_pem, canon, sig_bytes)
            verification_row = _VERIFICATION_ROW.format(
                css_verify_badge="verified" if verified else "tampered",
                verify_label="&#10003; VERIFIED" if verified else "&#10007; TAMPERED",
            )
        elif sig_hex and not public_key_pem:
            verification_row = _VERIFICATION_ROW.format(
                css_verify_badge="unsigned",
                verify_label="SIGNATURE PRESENT",
            )

        ts = e.get("timestamp", 0.0)
        blocks.append(
            _RECEIPT_BLOCK.format(
                idx=i,
                action=e.get("action", "(unknown)"),
                css_status="ok" if is_ok else "err",
                status_label="SUCCESS" if is_ok else "ERROR",
                actor_id=e.get("actor_id", "unknown"),
                when=_format_ts(ts) if ts else "(none)",
                input_hash=e.get("input_hash", "(none)"),
                output_hash=e.get("output_hash") or "(none)",
                sig_short=(sig_hex[:32] + "&hellip;") if sig_hex else "(unsigned)",
                root_short=(root_hex[:32] + "&hellip;") if root_hex else "(none)",
                verification_row=verification_row,
            )
        )

    receipts_html = "\n".join(blocks) if blocks else "<p>No receipts.</p>"

    # Footer with QR (optional)
    if qr_target_url:
        version_suffix = f"<br>{brand} {version}" if version else f"<br>{brand}"
        footer_html = (
            '<footer class="report-footer">\n'
            f'  <div class="qr">{_generate_qr_svg(qr_target_url)}</div>\n'
            '  <div class="footer-text">\n'
            f"    <strong>{brand}</strong> &mdash; open-source SDK for tamper-evident "
            "agent action receipts.<br>\n"
            "    Scan to learn how to verify this report and get the SDK.\n"
            "  </div>\n"
            f'  <div class="footer-right">Report generated by{version_suffix}</div>\n'
            "</footer>"
        )
    else:
        footer_html = ""

    run_id_suffix = f"&mdash; {run_id}" if run_id else ""

    return _HTML_TEMPLATE.format(
        brand=brand,
        title=title,
        run_id_suffix=run_id_suffix,
        meta_rows="\n".join(meta_lines),
        final_block=final_block,
        count=len(receipts),
        receipts_html=receipts_html,
        footer_html=footer_html,
    )
