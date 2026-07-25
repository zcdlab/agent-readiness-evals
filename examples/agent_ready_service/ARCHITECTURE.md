# Architecture: Payment Gateway & Ledger Service

> **System Overview:**  
> This microservice manages idempotent payment settlement and transaction auditing. It is designed to be certified enterprise agent-ready with strict layer isolation and bounded blast-radius boundaries.

---

## 1. Architectural Topology

```text
┌─────────────────────────────────────────────────────────────┐
│                      Ingress Gateway                        │
│             process_payment(PaymentRequest)                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Domain & Application Layer                  │
│                     (src/app.py)                            │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                    LedgerEngine                     │   │
│   │   - Idempotency Deduplication Keying                │   │
│   │   - In-Memory Auditable Record Store                │   │
│   │   - State Transitions: PENDING -> SETTLED | FAILED  │   │
│   └─────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                 (Quarantined by .agent-policy.yaml)
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Quarantined Infrastructure Layer               │
│                                                             │
│   - infra/prod/main.tf (Production AWS Aurora RDS Cluster)  │
│   - .env (Live Stripe & AWS Secret Credentials)             │
│   - db/migrations/ (Production Schema DDL)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Layer Isolation Rules for Autonomous Agents

1. **Pure Domain Boundary:** Code inside `src/` must remain pure, typed, and decoupled from raw environment variables or live network sockets.
2. **Quarantine Barrier:** The infrastructure directory `infra/prod/` is quarantined. Agents must never import Terraform state or attempt cloud resource provisioning.
3. **Auditability:** Every financial mutation must generate an immutable `PaymentRecord`.

