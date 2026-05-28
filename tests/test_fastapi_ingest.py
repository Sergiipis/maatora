from fastapi.testclient import TestClient

from maatora.fastapi_ingest import app, receipts_db

client = TestClient(app)


def test_post_get_roundtrip() -> None:
    """Tests round-trip of POST and GET for receipts."""
    # Clear the in-memory DB to ensure a clean state for the test
    receipts_db.clear()

    payload = {
        "action": "test_action_123",
        "actor_id": "agent_001",
        "principal_id": "user_999",
        "inputs_hash": "abc123hash",
        "outputs_hash": "def456hash",
        "timestamp": 1625097600.0,
        "cost": 0.05,
        "parent_trace_id": "trace_xyz",
        "signature": "sig_valid_123",
    }

    # Test POST
    post_response = client.post("/receipts", json=payload)
    assert post_response.status_code == 200
    assert post_response.json() == payload

    # Test GET all
    get_all_response = client.get("/receipts")
    assert get_all_response.status_code == 200
    assert len(get_all_response.json()) == 1
    assert get_all_response.json()[0]["action"] == "test_action_123"

    # Test GET by ID
    get_one_response = client.get("/receipts/test_action_123")
    assert get_one_response.status_code == 200
    assert get_one_response.json() == payload


def test_get_nonexistent_id() -> None:
    """Verifies 404 response for non-existent receipt ID."""
    # Ensure DB is empty or doesn't contain this specific ID
    receipts_db.clear()

    response = client.get("/receipts/non_existent_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Receipt not found"


def test_invalid_payload() -> None:
    """Ensures invalid payloads return a 422 status code."""
    # Missing required fields (e.g., action, actor_id)
    invalid_payload = {
        "action": "test_action",
        "cost": "not_a_float",  # Invalid type
    }

    response = client.post("/receipts", json=invalid_payload)
    assert response.status_code == 422
