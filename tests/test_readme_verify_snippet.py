"""README "Verify it yourself" snippet — must run exactly as documented.

If this test fails, the README example no longer works as written.
Either fix the API regression, or update README.md to match — but the
two must stay in lockstep.
"""

from maatora import generate_keypair, sign, verify


def test_readme_verify_it_yourself_snippet():
    priv, pub = generate_keypair()
    canonical = b'{"action":"transfer","actor_id":"agent-alpha","amount":100}'
    sig = sign(priv, canonical)

    assert verify(pub, canonical, sig) is True
    assert verify(pub, canonical.replace(b"100", b"999"), sig) is False
