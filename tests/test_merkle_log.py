from maatora.merkle_log import MerkleLog


def test_empty_root():
    log = MerkleLog()
    import hashlib

    assert log.root() == hashlib.sha256(b"").digest()


def test_single_element():
    log = MerkleLog()
    entry = b"action_1"
    idx = log.append(entry)
    import hashlib

    expected_root = hashlib.sha256(entry).digest()
    assert idx == 0
    assert log.root() == expected_root


def test_proof_verification():
    log = MerkleLog()
    entries = [b"a", b"b", b"c", b"d", b"e"]
    for e in entries:
        log.append(e)

    root = log.root()
    for i in range(len(entries)):
        p = log.proof(i)
        assert MerkleLog.verify_proof(entries[i], i, p, root) is True


def test_invalid_proof():
    log = MerkleLog()
    log.append(b"a")
    log.append(b"b")
    root = log.root()
    p = log.proof(0)
    # Tamper with entry
    assert MerkleLog.verify_proof(b"tampered", 0, p, root) is False
    # Tamper with proof
    p[0] = b"wrong_hash" * 4  # 40 bytes
    assert MerkleLog.verify_proof(b"a", 0, p, root) is False


def test_large_append():
    log = MerkleLog()
    for i in range(100):
        log.append(f"entry_{i}".encode())
    root = log.root()
    for i in range(100):
        p = log.proof(i)
        assert MerkleLog.verify_proof(f"entry_{i}".encode(), i, p, root) is True
