import datetime
import hashlib
from collections.abc import Callable
from typing import Any


class ReceiptMiddleware:
    """
    Middleware wrapper for LangGraph step functions that creates a
    cryptographic audit trail of inputs and outputs.
    """

    def __init__(self, store: Any, actor_id: str, principal_id: str) -> None:
        """
        Initializes the middleware with a persistence store and identity identifiers.

        Args:
            store: An object providing a .save(receipt: dict) method.
            actor_id: Identifier for the actor performing the action.
            principal_id: Identifier for the principal authorizing the action.
        """
        self.store = store
        self.actor_id = actor_id
        self.principal_id = principal_id

    def _calculate_hash(self, data: Any) -> str:
        """
        Calculates a SHA-256 hash of the given data using its repr() string.
        """
        data_repr = repr(data).encode("utf-8")
        return hashlib.sha256(data_repr).hexdigest()

    def wrap(self, graph_step_fn: Callable[..., Any]) -> Callable[..., Any]:
        """
        Returns a wrapped version of graph_step_fn that calculates SHA-256 hashes
        of inputs and outputs using repr(), saves a receipt dictionary containing
        action, actor_id, principal_id, hashes, and ISO 8601 timestamp to store.save(),
        and returns the original result. Propagates exceptions without saving receipts.
        """

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Capture inputs for hashing
            input_payload = (args, kwargs)
            input_hash = self._calculate_hash(input_payload)

            try:
                # Execute the original function
                result = graph_step_fn(*args, **kwargs)

                # Capture output hash
                if result is not None:
                    output_hash = self._calculate_hash(result)

                    # Create the receipt
                    receipt = {
                        "action": graph_step_fn.__name__,
                        "actor_id": self.actor_id,
                        "principal_id": self.principal_id,
                        "input_hash": input_hash,
                        "output_hash": output_hash,
                        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                    }

                    # Persist the receipt
                    self.store.save(receipt)
                else:
                    pass  # Handle case where result is None
            except Exception as e:
                # Propagate exceptions without saving receipts
                raise e

            return result

        return wrapper
