# Design Specification: Payment Gateway & Ledger Service

> **Design Pattern & State Machine Specifications**  
> Autonomous agents modifying this service must preserve the financial invariants and state transitions documented here.

---

## 1. Idempotent Settlement Pattern

To ensure network retries do not trigger duplicate charges:

$$\text{process}(\text{req}) = \begin{cases} \text{store}[\text{req.idempotency\_key}], & \text{if key exists} \\ \text{create\_settled\_record}(\text{req}), & \text{otherwise} \end{cases}$$

- **Key Constraint:** Idempotency keys must be at least 1 character in length.
- **Deduplication Invariant:** Calling `process()` $N$ times with identical `idempotency_key` creates exactly 1 record in `LedgerEngine` and returns the identical `transaction_id`.

---

## 2. Finite State Machine (FSM)

```text
               ┌─────────────┐
               │   PENDING   │
               └──────┬──────┘
                      │
            ┌─────────┴─────────┐
            │ Validate Amount   │
            │ (amount_cents > 0)│
            └─────────┬─────────┘
                      │
           ┌──────────┴──────────┐
           ▼                     ▼
     [Validation OK]       [Validation Error]
           │                     │
           ▼                     ▼
    ┌─────────────┐       ┌─────────────┐
    │   SETTLED   │       │   FAILED    │
    │(tx_id gen)  │       │(ValueError) │
    └─────────────┘       └─────────────┘
```

---

## 3. Financial Invariants
1. **Strict Positive Value:** Any transaction with `amount_cents <= 0` must raise `ValueError("Payment amount must be greater than zero")`.
2. **Immutable Audit Trail:** Once a transaction transitions to `SETTLED`, its fields (`transaction_id`, `amount_cents`, `currency`) are immutable.
3. **No Unhandled Exceptions:** Domain validation errors must be explicit and typed.

