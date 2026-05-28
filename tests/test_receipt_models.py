from maatora.receipt_models import AgentReceipt, receipt_canonical_json


def test_receipt_validation():
    """
    Validates fields of a fully populated AgentReceipt instance.
    """
    data = {
        "id": "receipt-123",
        "action": "web_search",
        "actor_id": "agent-007",
        "principal_id": "user-456",
        "inputs_hash": "abc123hash",
        "outputs_hash": "def456hash",
        "timestamp": 1625097600.0,
        "cost_usd": 0.0025,
        "parent_trace_id": "trace-789",
        "model_version": "gpt-4-turbo",
        "signature": "sig_xyz_789",
    }
    receipt = AgentReceipt(**data)

    assert receipt.id == "receipt-123"
    assert receipt.action == "web_search"
    assert receipt.actor_id == "agent-007"
    assert receipt.principal_id == "user-456"
    assert receipt.inputs_hash == "abc123hash"
    assert receipt.outputs_hash == "def456hash"
    assert receipt.timestamp == 1625097600.0
    assert receipt.cost_usd == 0.0025
    assert receipt.parent_trace_id == "trace-789"
    assert receipt.model_version == "gpt-4-turbo"
    assert receipt.signature == "sig_xyz_789"


def test_receipt_defaults():
    """
    Tests default values in AgentReceipt when not all fields are provided.
    """
    data = {
        "id": "receipt-123",
        "action": "web_search",
        "actor_id": "agent-007",
        "principal_id": "user-456",
        "inputs_hash": "abc123hash",
        "outputs_hash": "def456hash",
        "timestamp": 1625097600.0,
        "cost_usd": 0.0025,
        "model_version": "gpt-4-turbo",
    }
    # parent_trace_id and signature are Optional and should default to None
    receipt = AgentReceipt(**data)

    assert receipt.parent_trace_id is None
    assert receipt.signature is None


def test_canonical_serialization():
    """
    Ensures receipt_canonical_json excludes 'signature' and returns sorted keys,
    and model_dump_canonical returns bytes.
    """
    data = {
        "id": "r1",
        "action": "act1",
        "actor_id": "a1",
        "principal_id": "p1",
        "inputs_hash": "ih1",
        "outputs_hash": "oh1",
        "timestamp": 100.0,
        "cost_usd": 0.1,
        "model_version": "v1",
        "signature": "secret_sig",
        "parent_trace_id": "t1",
    }
    receipt = AgentReceipt(**data)

    # Test receipt_canonical_json
    json_str = receipt_canonical_json(receipt).encode("utf-8")
    assert (
        json_str
        == b'{"action":"act1","actor_id":"a1","cost_usd":0.1,"id":"r1","inputs_hash":"ih1","model_version":"v1","outputs_hash":"oh1","parent_trace_id":"t1","principal_id":"p1","timestamp":100.0}'
    )

    # Test model_dump_canonical
    bytes = receipt.model_dump_canonical()
    assert bytes == json_str
