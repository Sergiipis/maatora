"""
Example 02: ReceiptMiddleware for graph step functions.

Use ReceiptMiddleware to wrap any callable that represents an agent step —
including LangGraph nodes. Each invocation produces a receipt linking the
actor (the agent) to the principal (the human or service on whose behalf
the agent acts).

Run:
    python examples/02_langgraph_middleware.py

LangGraph is not required to run this example: any Callable works.
"""

from maatora import ReceiptMiddleware


class InMemoryStore:
    """Store with the .save() interface expected by ReceiptMiddleware."""

    def __init__(self) -> None:
        self.receipts: list[dict] = []

    def save(self, receipt: dict) -> None:
        self.receipts.append(receipt)


def lookup_user(user_id: str) -> dict:
    """A toy agent step: look up a user by ID."""
    return {"id": user_id, "name": "Alice", "tier": "premium"}


def main() -> None:
    store = InMemoryStore()
    middleware = ReceiptMiddleware(
        store=store,
        actor_id="agent-customer-support",
        principal_id="user-1234",
    )

    wrapped_lookup = middleware.wrap(lookup_user)

    _ = wrapped_lookup("user-1234")
    _ = wrapped_lookup("user-5678")

    print(f"Captured {len(store.receipts)} receipts:")
    for r in store.receipts:
        print(f"  action={r['action']} actor={r['actor_id']}")
        print(f"    principal={r['principal_id']}")
        print(f"    timestamp={r['timestamp']}")
        print(f"    input_hash={r['input_hash'][:16]}...")
        print(f"    output_hash={r['output_hash'][:16]}...")


if __name__ == "__main__":
    main()
