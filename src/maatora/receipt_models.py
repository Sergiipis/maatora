import json

from pydantic import BaseModel


class AgentReceipt(BaseModel):
    """
    Pydantic model for an Agent Action Receipt.
    """

    id: str
    action: str
    actor_id: str
    principal_id: str
    inputs_hash: str
    outputs_hash: str
    timestamp: float
    cost_usd: float
    parent_trace_id: str | None = None
    model_version: str
    signature: str | None = None

    def model_dump_canonical(self) -> bytes:
        """
        Returns the canonical JSON representation of the receipt as UTF-8 encoded bytes.
        """
        return receipt_canonical_json(self).encode("utf-8")


def receipt_canonical_json(receipt: AgentReceipt) -> str:
    """
    Returns a deterministic, sorted JSON string of the receipt excluding the 'signature' field.
    """
    # Convert model to dict (excluding signature, which is computed over canonical form)
    data = receipt.model_dump(exclude={"signature"})

    # sort_keys=True ensures deterministic ordering of keys
    # separators=(',', ':') removes whitespace for a compact, canonical form
    return json.dumps(data, sort_keys=True, separators=(",", ":"))
