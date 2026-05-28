from typing import Any

import pytest

from maatora.receipt_decorator import ReceiptStore, receipt


class MockStore(ReceiptStore):
    def __init__(self):
        self.receipts: list[dict[str, Any]] = []

    def append(self, receipt: dict[str, Any]) -> None:
        self.receipts.append(receipt)


def test_receipt_captures_success() -> None:
    """verifies that a successful function call generates a receipt with status 'success' and contains input/output hashes."""
    store = MockStore()

    @receipt(action="test_action", store=store)
    def add(a, b):
        return a + b

    result = add(10, 20)

    assert result == 30
    assert len(store.receipts) == 1
    receipt_entry = store.receipts[0]
    assert receipt_entry["action"] == "test_action"
    assert receipt_entry["status"] == "success"
    assert "input_hash" in receipt_entry
    assert "output_hash" in receipt_entry
    assert receipt_entry["error"] is None


def test_receipt_deterministic_hashing() -> None:
    """verifies that identical inputs produce identical input hashes."""
    store = MockStore()

    @receipt(action="hash_test", store=store)
    def identity(x, **kwargs):
        return x

    # Call with same inputs twice
    identity(1, actor_id="user1")
    identity(1, actor_id="user1")

    assert len(store.receipts) == 2
    assert store.receipts[0]["input_hash"] == store.receipts[1]["input_hash"]


def test_receipt_captures_error() -> None:
    """verifies that a function raising an exception results in a receipt with status 'error' and that the exception is re-raised."""
    store = MockStore()

    @receipt(action="error_test", store=store)
    def fail_func():
        raise ValueError("Something went wrong")

    with pytest.raises(ValueError, match="Something went wrong"):
        fail_func()

    assert len(store.receipts) == 1
    receipt_entry = store.receipts[0]
    assert receipt_entry["status"] == "error"
    assert receipt_entry["error"] == "Something went wrong"
    assert receipt_entry["output_hash"] is None


def test_receipt_actor_id_priority() -> None:
    """verifies that actor_id passed in kwargs takes priority over environment variables or defaults."""
    store = MockStore()

    @receipt(action="actor_test", store=store)
    def process(data, **kwargs):
        return True

    # Case 1: actor_id in kwargs (Highest priority)
    process("some_data", actor_id="admin_user")
    assert store.receipts[-1]["actor_id"] == "admin_user"

    # Case 2: First arg is a string containing 'actor' (Heuristic priority)
    process("Actor_John_Doe", some_other_param=1)
