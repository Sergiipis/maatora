import pytest

from maatora.ed25519_signer import generate_keypair, sign, verify


@pytest.fixture
def keys():
    """Fixture to provide a fresh Ed25519 keypair for tests."""
    return generate_keypair()


def test_roundtrip_sign_verify(keys):
    """
    Tests that a payload can be signed and verified correctly with the generated keys.
    Asserts signature length and successful verification.
    """
    priv_pem, pub_pem = keys
    payload = b"Hello, Ed25519 world!"

    signature = sign(priv_pem, payload)

    # Ed25519 signatures are exactly 64 bytes
    assert len(signature) == 64
    assert verify(pub_pem, payload, signature) is True


def test_verify_wrong_payload(keys):
    """Tests verification failure when the payload is tampered after signing."""
    priv_pem, pub_pem = keys
    payload = b"Original message"
    tampered_payload = b"Tampered message"

    signature = sign(priv_pem, payload)
    assert verify(pub_pem, tampered_payload, signature) is False


def test_verify_wrong_signature(keys):
    """Tests verification failure when the signature is altered."""
    priv_pem, pub_pem = keys
    payload = b"Secure data"

    signature = bytearray(sign(priv_pem, payload))
    # Flip a bit in the signature to make it invalid
    signature[0] ^= 0xFF

    assert verify(pub_pem, payload, bytes(signature)) is False


def test_verify_wrong_key():
    """Tests verification failure when using a different public key than the one used for signing."""
    priv_pem1, _pub_pem1 = generate_keypair()
    _priv_pem2, pub_pem2 = generate_keypair()
    payload = b"Secret message"

    # Sign with key 1
    signature = sign(priv_pem1, payload)

    # Verify with key 2
    assert verify(pub_pem2, payload, signature) is False


def test_invalid_private_key_format():
    """Tests that an invalid private key format raises ValueError during signing."""
    invalid_pem = b"---BEGIN PRIVATE KEY---\nNotAKey\n---END PRIVATE KEY---"
    payload = b"Some data"

    with pytest.raises(ValueError):
        sign(invalid_pem, payload)
