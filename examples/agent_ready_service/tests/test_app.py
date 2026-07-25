import pytest
from src.app import LedgerEngine, PaymentRequest, TransactionStatus, process_payment


def test_process_payment_valid():
    res = process_payment(PaymentRequest(idempotency_key="pay-001", amount_cents=5000))
    assert res["status"] == "success"
    assert res["amount_cents"] == 5000
    assert res["idempotency_key"] == "pay-001"
    assert "transaction_id" in res


def test_process_payment_invalid():
    with pytest.raises(ValueError, match="greater than zero"):
        process_payment(PaymentRequest(amount_cents=-100))


def test_idempotent_deduplication():
    engine = LedgerEngine()
    req = PaymentRequest(idempotency_key="tx-unique-99", amount_cents=2500)

    first = engine.process(req)
    second = engine.process(req)

    assert first.transaction_id == second.transaction_id
    assert first.status == TransactionStatus.SETTLED
    assert second.status == TransactionStatus.SETTLED
    assert len(engine._records) == 1


def test_zero_amount_rejection():
    engine = LedgerEngine()
    with pytest.raises(ValueError, match="greater than zero"):
        engine.process(PaymentRequest(amount_cents=0))
