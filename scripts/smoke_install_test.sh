#!/usr/bin/env bash
#
# Clean-room smoke install test.
#
# Builds the wheel and installs it inside a fresh python:3.12-slim
# container with no shared state from the developer's machine. Verifies
# the two snippets the README promises will work: the @receipt quickstart
# and the verify-it-yourself path. Then installs the [audit] extra and
# checks render_audit_report produces non-empty HTML.
#
# Run from the SDK root:
#     bash scripts/smoke_install_test.sh
#
# Useful as a final gate before publishing to PyPI: catches missing
# runtime deps, broken entry points, and platform-specific wheels that
# happen to work on the dev machine but not on a fresh slim image.

set -euo pipefail

SDK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SDK_DIR"

echo "==> Building wheel from $SDK_DIR"
rm -rf dist build ./*.egg-info
.venv/bin/python -m build --wheel >/dev/null
WHEEL="$(ls dist/maatora-*.whl)"
echo "    Built: $WHEEL"

echo "==> Running clean-room install test in python:3.12-slim"
docker run --rm \
    --network host \
    -v "$SDK_DIR:/work:ro" \
    -w /work \
    python:3.12-slim \
    bash -c '
        set -euo pipefail
        echo "--- python version ---"
        python --version

        echo "--- pip install wheel ---"
        pip install --quiet "$(ls dist/maatora-*.whl)"

        echo "--- import smoke ---"
        python -c "import maatora; print(\"maatora\", maatora.__name__, \"OK\")"

        echo "--- README quickstart snippet ---"
        python - <<PY
from maatora import receipt
class S:
    def __init__(self): self.r=[]
    def append(self,x): self.r.append(x)
s = S()
@receipt(action="transfer_funds", store=s)
def t(actor_id, amount, to):
    return {"transferred": amount, "to": to}
t(actor_id="agent-alpha", amount=100.0, to="alice")
r = s.r[0]
assert r["action"] == "transfer_funds"
assert r["status"] == "success"
assert len(r["input_hash"]) == 64
assert len(r["output_hash"]) == 64
print("quickstart receipt OK:", r["action"], r["status"])
PY

        echo "--- README Verify it yourself snippet ---"
        python - <<PY
from maatora import generate_keypair, sign, verify
priv, pub = generate_keypair()
canonical = b"{\"action\":\"transfer\",\"actor_id\":\"agent-alpha\",\"amount\":100}"
sig = sign(priv, canonical)
assert verify(pub, canonical, sig) is True
assert verify(pub, canonical.replace(b"100", b"999"), sig) is False
print("tamper-evidence OK")
PY

        echo "--- CLI entry point ---"
        maatora --help | head -1

        echo "--- audit extra ---"
        pip install --quiet "$(ls dist/maatora-*.whl)[audit]"
        python - <<PY
from maatora import canonicalize, generate_keypair, render_audit_report, sign
priv, pub = generate_keypair()
r = {"action":"a","actor_id":"x","timestamp":1.0,"input_hash":"a"*64,"output_hash":"b"*64,"status":"success","error":None}
r["signature_hex"] = sign(priv, canonicalize(r)).hex()
html = render_audit_report([r], public_key_pem=pub, qr_target_url="https://example.com")
assert "<!DOCTYPE html>" in html
assert "VERIFIED" in html
assert "<svg" in html
print("audit report renders OK,", len(html), "bytes")
PY

        echo "--- all smoke checks passed ---"
    '

echo "==> Smoke install test passed."
