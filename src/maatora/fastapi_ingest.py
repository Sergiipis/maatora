from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class ReceiptSchema(BaseModel):
    action: str
    actor_id: str
    principal_id: str
    inputs_hash: str
    outputs_hash: str
    timestamp: float
    cost: float
    parent_trace_id: str | None = None
    signature: str


# In-memory storage for receipts
receipts_db: list[ReceiptSchema] = []


@app.get("/healthz")
async def health_check() -> dict[str, str]:
    """Returns {'status': 'ok'} for the /healthz endpoint."""
    return {"status": "ok"}


@app.post("/receipts", response_model=ReceiptSchema)
async def create_receipt(receipt: ReceiptSchema) -> ReceiptSchema:
    """Validates and stores a new receipt in memory. Returns the created receipt."""
    receipts_db.append(receipt)
    return receipt


@app.get("/receipts")
async def get_all_receipts() -> list[ReceiptSchema]:
    """Retrieves all stored receipts from memory."""
    return receipts_db


@app.get("/receipts/{action_id}")
async def get_receipt_by_action(action_id: str) -> ReceiptSchema:
    """Finds a receipt by action field. Raises HTTPException(404) if not found."""
    for receipt in receipts_db:
        if receipt.action == action_id:
            return receipt
    raise HTTPException(status_code=404, detail="Receipt not found")
