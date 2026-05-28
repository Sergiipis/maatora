"""
Example 04: External verification — tamper-evidence in action.

This is the core differentiator of the SDK. Anyone holding the public key
of the agent operator can verify a receipt without contacting the operator,
without trusting a SaaS dashboard, and without trusting the storage layer.

If the receipt is modified in any way after signing — by an attacker, by a
buggy data pipeline, or by a curious admin — verification fails and the
modification is detectable.

Run:
    python examples/04_verify_externally.py
"""

from maatora import generate_keypair, sign, verify


def main() -> None:
    # The agent operator generates a keypair. The public key is published
    # (or shared with auditors). The private key stays with the operator.
    private_pem, public_pem = generate_keypair()
    print("Generated Ed25519 keypair.")

    # The canonical bytes of a receipt are signed. In production, this is
    # the canonical-JSON serialization of an AgentReceipt model.
    receipt_canonical = (
        b'{"action":"transfer","actor_id":"agent-alpha",'
        b'"amount":100,"to":"alice","timestamp":1716000000}'
    )

    signature = sign(private_pem, receipt_canonical)
    print(f"Signed {len(receipt_canonical)} bytes, signature length: {len(signature)}")

    # An auditor or customer verifies. They only need the public key.
    is_valid = verify(public_pem, receipt_canonical, signature)
    print(f"Verification of unmodified receipt: {is_valid}")
    assert is_valid

    # An attacker (or buggy pipeline) modifies a single byte: "100" -> "999".
    tampered = receipt_canonical.replace(b'"amount":100', b'"amount":999')
    is_tampered_valid = verify(public_pem, tampered, signature)
    print(f"Verification of tampered receipt:   {is_tampered_valid}")
    assert not is_tampered_valid

    # Verification also fails if a different public key is used.
    _, wrong_public_pem = generate_keypair()
    is_wrong_key_valid = verify(wrong_public_pem, receipt_canonical, signature)
    print(f"Verification with wrong public key: {is_wrong_key_valid}")
    assert not is_wrong_key_valid

    print()
    print("This is what tamper-EVIDENT means: not 'unauthorized people")
    print("cannot modify the log', but 'any modification — authorized or")
    print("not — is publicly detectable by anyone with the public key.'")


if __name__ == "__main__":
    main()
