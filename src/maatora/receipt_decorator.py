import functools
import hashlib
import json
import time
from collections.abc import Callable
from typing import Any, Protocol


class ReceiptStore(Protocol):
    def append(self, receipt: dict[str, Any]) -> None: ...


def _hash_data(data: Any) -> str:
    """
    Creates a deterministic SHA-256 hash of the provided data.
    Handles basic types and converts dictionaries/lists to sorted JSON strings.
    """
    try:
        # Ensure deterministic serialization for dicts/lists
        serialized = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
    except Exception:
        # Fallback for non-serializable objects
        serialized = str(data).encode("utf-8")

    return hashlib.sha256(serialized).hexdigest()


def receipt(action: str, store: ReceiptStore) -> Callable:
    """
    A decorator that creates a cryptographic audit trail of function calls.
    Logs input hashes, output hashes, actor identification, timestamp, and status.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Identify actor: priority is kwargs['actor_id'] -> args[0] (if it's a string) -> 'unknown'
            actor_id = "unknown"
            if "actor_id" in kwargs:
                actor_id = kwargs["actor_id"]
            elif args and isinstance(args[0], str) and "actor" in args[0].lower():
                # Heuristic: if first arg looks like an actor ID/name
                actor_id = args[0]

            # Prepare input data for hashing
            input_payload = {"args": args, "kwargs": kwargs}
            input_hash = _hash_data(input_payload)

            timestamp = time.time()
            status = "success"
            output_hash = None
            error_msg = None

            try:
                result = func(*args, **kwargs)
                output_hash = _hash_data(result)
                return result
            except Exception as e:
                status = "error"
                error_msg = str(e)
                raise e
            finally:
                # Construct the audit receipt
                receipt_entry = {
                    "action": action,
                    "actor_id": actor_id,
                    "timestamp": timestamp,
                    "input_hash": input_hash,
                    "output_hash": output_hash,
                    "status": status,
                    "error": error_msg,
                }
                store.append(receipt_entry)

        return wrapper

    return decorator
