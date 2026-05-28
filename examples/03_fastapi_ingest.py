"""
Example 03: FastAPI ingest endpoint.

The SDK ships a minimal FastAPI app that accepts signed receipts via
POST /receipts and serves them back via GET /receipts and
GET /receipts/{action_id}. Use this to centralize receipts from many
agent instances into a single audit store.

Run the server:
    uvicorn maatora.fastapi_ingest:app --reload

Submit a receipt (in another shell):
    curl -X POST http://localhost:8000/receipts \\
      -H 'Content-Type: application/json' \\
      -d '{
        "action": "lookup_user",
        "actor_id": "agent-alpha",
        "principal_id": "user-1234",
        "inputs_hash": "abc",
        "outputs_hash": "def",
        "timestamp": 1716000000.0,
        "cost": 0.0001,
        "signature": "ed25519-signature-bytes-base64"
      }'

This module also demonstrates direct usage of the FastAPI TestClient if you
prefer to verify ingest behavior in tests without a running server.
"""

from fastapi.testclient import TestClient

from maatora.fastapi_ingest import app


def main() -> None:
    client = TestClient(app)

    payload = {
        "action": "lookup_user",
        "actor_id": "agent-alpha",
        "principal_id": "user-1234",
        "inputs_hash": "abc123",
        "outputs_hash": "def456",
        "timestamp": 1716000000.0,
        "cost": 0.0001,
        "signature": "stub-signature-bytes",
    }

    health = client.get("/healthz").json()
    print(f"Health check: {health}")

    created = client.post("/receipts", json=payload).json()
    print(f"Created receipt: action={created['action']} actor={created['actor_id']}")

    listed = client.get("/receipts").json()
    print(f"Stored receipts: {len(listed)}")

    fetched = client.get(f"/receipts/{payload['action']}").json()
    print(f"Fetched by action: {fetched['action']}")


if __name__ == "__main__":
    main()
