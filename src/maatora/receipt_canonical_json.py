import json


def canonicalize(obj: dict) -> bytes:
    """
    Converts a dictionary into a deterministic UTF-8 byte string.

    The serialization ensures:
    - Keys are sorted alphabetically.
    - No whitespace between separators (separators=(',', ':')).
    - Nested structures (dicts, lists) are handled recursively.
    - UTF-8 encoding without BOM.
    - Floats are represented consistently (avoiding exponential notation where possible
      via the default json.dumps behavior for standard floats).
    """
    # json.dumps with sort_keys=True and separators=(',', ':') provides
    # a deterministic representation of the JSON structure.
    # ensure_ascii=False allows non-ASCII characters to be represented as UTF-8
    # rather than \uXXXX escapes, which is standard for canonical byte representations.
    json_string = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return json_string.encode("utf-8")


def decanonicalize(data: bytes) -> dict:
    """
    Reconstructs the original dictionary from the bytes produced by canonicalize.
    """
    # Decode the UTF-8 bytes back to a string and parse as JSON.
    json_string = data.decode("utf-8")
    result: dict = json.loads(json_string)
    return result
