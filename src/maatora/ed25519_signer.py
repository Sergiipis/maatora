from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


def generate_keypair() -> tuple[bytes, bytes]:
    """
    Generates a new Ed25519 private and public key pair.
    Returns them as a tuple of bytes (private_pem, public_pem) using standard PEM encoding.
    """
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem


def sign(priv_pem: bytes, payload: bytes) -> bytes:
    """
    Takes a PEM-encoded private key and a byte payload.
    Returns a 64-byte Ed25519 signature.
    Raises ValueError if the private key is invalid or cannot be loaded.
    """
    try:
        private_key = serialization.load_pem_private_key(priv_pem, password=None)
        if not isinstance(private_key, ed25519.Ed25519PrivateKey):
            raise ValueError("The provided PEM key is not an Ed25519 private key.")

        return private_key.sign(payload)
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Invalid private key: {e!s}") from e


def verify(pub_pem: bytes, payload: bytes, sig: bytes) -> bool:
    """
    Takes a PEM-encoded public key, the original byte payload, and the signature.
    Returns True if the signature is valid for the payload and key, False otherwise.
    """
    try:
        public_key = serialization.load_pem_public_key(pub_pem)
        if not isinstance(public_key, ed25519.Ed25519PublicKey):
            return False

        public_key.verify(sig, payload)
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False
