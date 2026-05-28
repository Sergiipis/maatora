from maatora.receipt_canonical_json import canonicalize, decanonicalize


def test_determinism():
    """
    Verifies that different orderings of the same dictionary produce
    identical byte strings when canonicalized.
    """
    dict1 = {"a": 1, "b": 2, "c": 3}
    dict2 = {"c": 3, "a": 1, "b": 2}

    assert canonicalize(dict1) == canonicalize(dict2)


def test_symmetry():
    """
    Ensures that a dictionary can be serialized and deserialized back
    to its original form without loss or alteration.
    """
    original = {"id": 123, "name": "Test Item", "active": True, "value": 45.67, "meta": None}
    serialized = canonicalize(original)
    deserialized = decanonicalize(serialized)

    assert original == deserialized


def test_no_whitespace():
    """
    Confirms there is no whitespace in the serialized output,
    ensuring consistency for cryptographic purposes.
    """
    data = {"key": "value", "list": [1, 2, 3]}
    serialized = canonicalize(data).decode("utf-8")

    # Standard JSON dumps with default separators adds spaces after ',' and ':'
    # Canonical JSON must not have them.
    assert " " not in serialized
    assert ": " not in serialized
    assert ", " not in serialized
    assert serialized == '{"key":"value","list":[1,2,3]}'


def test_unicode_handling():
    """
    Checks correct handling of Unicode characters during
    serialization and deserialization.
    """
    # Testing emojis and non-Latin scripts
    original = {"greeting": "Hello 🌍", "language": "日本語"}
    serialized = canonicalize(original)

    # Verify it's encoded as UTF-8 bytes
    assert isinstance(serialized, bytes)

    deserialized = decanonicalize(serialized)
    assert original == deserialized


def test_nested_structures():
    """
    Validates that nested dictionaries and lists are correctly
    handled by both functions.
    """
    original = {
        "user": {
            "id": 1,
            "details": {"email": "test@example.com", "tags": ["admin", "beta-tester"]},
        },
        "items": [{"sku": "A1", "qty": 2}, {"sku": "B2", "qty": 5}],
        "version": "1.0",
    }

    # Test symmetry
    serialized = canonicalize(original)
    deserialized = decanonicalize(serialized)
    assert original == deserialized

    # Test determinism of nested keys
    nested_alt = {
        "version": "1.0",
        "items": [{"sku": "A1", "qty": 2}, {"sku": "B2", "qty": 5}],
        "user": {
            "details": {"tags": ["admin", "beta-tester"], "email": "test@example.com"},
            "id": 1,
        },
    }
    assert canonicalize(original) == canonicalize(nested_alt)
