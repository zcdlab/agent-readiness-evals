from enum import StrEnum
from pydantic import BaseModel, Field


class TransactionStatus(StrEnum):
    PENDING = "pending"
    SETTLED = "settled"
    FAILED = "failed"


class PaymentRequest(BaseModel):
    idempotency_key: str = Field(default="default-key", min_length=1)
    amount_cents: int
    currency: str = "USD"


class PaymentRecord(BaseModel):
    transaction_id: str
    idempotency_key: str
    amount_cents: int
    currency: str
    status: TransactionStatus


class LedgerEngine:
    def __init__(self) -> None:
        self._records: dict[str, PaymentRecord] = {}

    def process(self, req: PaymentRequest) -> PaymentRecord:
        if req.amount_cents <= 0:
            raise ValueError("Payment amount must be greater than zero")
        if req.idempotency_key in self._records:
            return self._records[req.idempotency_key]

        tx_id = f"tx_{len(self._records) + 1:04d}"
        record = PaymentRecord(
            transaction_id=tx_id,
            idempotency_key=req.idempotency_key,
            amount_cents=req.amount_cents,
            currency=req.currency,
            status=TransactionStatus.SETTLED,
        )
        self._records[req.idempotency_key] = record
        return record


_default_engine = LedgerEngine()


def process_payment(req: PaymentRequest) -> dict:
    rec = _default_engine.process(req)
    return {
        "status": "success" if rec.status == TransactionStatus.SETTLED else "failed",
        "transaction_id": rec.transaction_id,
        "amount_cents": rec.amount_cents,
        "currency": rec.currency,
        "idempotency_key": rec.idempotency_key,
    }
