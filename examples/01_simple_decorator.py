"""
Example 01: Basic @receipt decorator on a regular function.

The simplest way to add an audit trail to any Python function: wrap it with
the @receipt decorator and provide a store. Every call writes a receipt with
input hash, output hash, actor, timestamp, and status.

Run:
    python examples/01_simple_decorator.py
"""

from maatora import receipt


class InMemoryStore:
    """Minimal ReceiptStore implementation that keeps receipts in a list."""

    def __init__(self) -> None:
        self.receipts: list[dict] = []

    def append(self, receipt: dict) -> None:
        self.receipts.append(receipt)


store = InMemoryStore()


@receipt(action="transfer_funds", store=store)
def transfer_funds(actor_id: str, amount: float, to_account: str) -> dict:
    """A toy banking action that an AI agent might call as a tool."""
    return {"transferred": amount, "to": to_account, "status": "ok"}


def main() -> None:
    transfer_funds(actor_id="agent-alpha", amount=100.0, to_account="alice")
    transfer_funds(actor_id="agent-alpha", amount=50.0, to_account="bob")

    print(f"Captured {len(store.receipts)} receipts:")
    for r in store.receipts:
        print(f"  action={r['action']} actor={r['actor_id']} status={r['status']}")
        print(f"    input_hash={r['input_hash'][:16]}...")
        print(f"    output_hash={r['output_hash'][:16]}...")


if __name__ == "__main__":
    main()
