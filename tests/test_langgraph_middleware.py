import pytest

from maatora.langgraph_middleware import ReceiptMiddleware


class MockStore:
    """A simple mock store to capture saved receipts."""

    def __init__(self) -> None:
        self.saved_receipts: list[dict] = []

    def save(self, receipt: dict) -> None:
        self.saved_receipts.append(receipt)


def test_middleware_saves_receipt() -> None:
    """
    Verifies that a successful function call results in a receipt being saved
    to the store with correct metadata.
    """
    store = MockStore()
    actor_id = "user_123"
    principal_id = "admin_456"
    middleware = ReceiptMiddleware(store, actor_id, principal_id)

    def sample_step(x: int, y: int) -> int:
        return x + y

    wrapped_fn = middleware.wrap(sample_step)
    result = wrapped_fn(10, 20)

    # Verify function result is preserved
    assert result == 30
    # Verify one receipt was saved
    assert len(store.saved_receipts) == 1

    receipt = store.saved_receipts[0]
    assert receipt["action"] == "sample_step"
    assert receipt["actor_id"] == actor_id
    assert receipt["principal_id"] == principal_id
    assert "input_hash" in receipt
    assert "output_hash" in receipt
    assert "timestamp" in receipt


def test_middleware_preserves_exception() -> None:
    """
    Verifies that if the wrapped function raises an exception, the exception
    is propagated and no receipt is saved.
    """
    store = MockStore()
    middleware = ReceiptMiddleware(store, "actor", "principal")

    def failing_step():
        raise ValueError("Step failed")

    wrapped_fn = middleware.wrap(failing_step)

    # Verify exception propagates
    with pytest.raises(ValueError, match="Step failed"):
        wrapped_fn()

    # Verify no receipt was saved on failure
    assert len(store.saved_receipts) == 0


def test_middleware_handles_complex_types() -> None:
    """
    Verifies that inputs containing lists and dictionaries are correctly
    hashed and recorded.
    """
    store = MockStore()
    middleware = ReceiptMiddleware(store, "actor", "principal")

    def complex_step(data: dict) -> list:
        return [val for val in data.values()]

    wrapped_fn = middleware.wrap(complex_step)

    input_data = {"a": 1, "b": [2, 3], "c": {"d": 4}}
    result = wrapped_fn(input_data)

    assert result == [1, [2, 3], {"d": 4}]
    assert len(store.saved_receipts) == 1

    receipt = store.saved_receipts[0]

    # Verify that the same input produces the same hash (stability)
    input_hash_1 = receipt["input_hash"]

    # Run again with same input
    store.saved_receipts.clear()
    wrapped_fn(input_data)
    input_hash_2 = store.saved_receipts[0]["input_hash"]

    assert input_hash_1 == input_hash_2
