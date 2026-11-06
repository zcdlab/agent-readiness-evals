# agent-readiness

> Zero-Config Repository Readiness Scanner & Auto-Onboarder for Autonomous AI Coding Agents.

[![CI](https://github.com/zcdlab/agent-readiness-evals/actions/workflows/ci.yaml/badge.svg)](https://github.com/zcdlab/agent-readiness-evals/actions/workflows/ci.yaml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/pytest-passing-brightgreen.svg)](tests/)
[![Live Demo](https://img.shields.io/badge/demo-GitHub%20Pages-blue.svg)](https://zcdlab.github.io/agent-readiness-evals/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Overview

`agent-readiness` evaluates whether a codebase is safe and prepared for autonomous AI coding agents (Claude Code, Devin, Cursor, GitHub Copilot Workspace).

### 🧠 The Harness Engineering Philosophy: First-Principles Architecture

In the era of autonomous coding, **the LLM is a reasoning engine; the harness is its operating system, sensorium, and guardrail.** Without a deterministic execution harness:
- Models operate open-loop without sensory feedback.
- Stochastic token predictions cascade into unverified regressions and production outages.
- Iteration costs multiply exponentially as agents wander across directories.

`agent-readiness` evaluates and auto-synthesizes the four foundational harness components:
1. **Deterministic Verification Loop:** Red &rarr; Green &rarr; Refactor with strict test execution budgets (&lt; 5s).
2. **Zero-Trust Blast Radius Isolation:** Machine-enforced boundary policies protecting production infrastructure (`infra/prod/`) and secrets (`.env`).
3. **Structured Operating Contracts (`AGENTS.md`):** Clear runtime constraints, tooling matrices, and systematic debugging protocols.
4. **Reproducible Build Environments:** Pinned package manifests preventing dependency drift and unvetted installs.

### 📁 Real-World Sample Targets

Explore the three comparative reference repositories under `examples/`:
- [`examples/unprepared_service/`](examples/unprepared_service/): **Score 0/100 [Grade F]** — Exposed `.env`, unprotected Terraform `infra/prod/`, no test harness.
- [`examples/unconfigured_service/`](examples/unconfigured_service/): **Score 50/100 [Grade C]** — Has Bazel and pytest, but lacks zero-trust policies and operating contracts.
- [`examples/agent_ready_service/`](examples/agent_ready_service/): **Score 100/100 [Grade A]** — Certified high-assurance harness with zero-trust `.agent-policy.yaml`, deep `AGENTS.md` contract, idempotent `LedgerEngine`, and 100% test coverage.

### 🌐 Live Interactive Demo
Try the interactive control plane in your browser:  
👉 **[https://zcdlab.github.io/agent-readiness-evals/](https://zcdlab.github.io/agent-readiness-evals/)**

---

## 🏛️ The 4 Core Readiness Pillars

| Pillar | Weight | Verification Criteria | Risk if Missing |
|---|---|---|---|
| ⚙️ **Reproducible Build & Dependencies** | **25 pts** | Detects `BUILD.bazel`, `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod` | Agent hallucinates build targets or installs unvetted dependencies |
| 🧪 **Deterministic Verification Harness** | **25 pts** | Detects automated test suites (`tests/`, `test/`) | Agent cannot verify its own code changes, causing regressions |
| 🛡️ **Blast-Radius Policy Boundary** | **25 pts** | Enforces `.agent-policy.yaml` quarantining `infra/prod/`, `security/`, `db/migrations/`, `.env` | Agent modifies production infrastructure or database schemas |
| 🤖 **Agent Operating Guidelines** | **25 pts** | Enforces `AGENTS.md` defining stack, permissions, and tool rules | Agent violates repo conventions and wanders across packages |

---

## 💻 Standalone CLI Usage

The package installs the standalone binary `readiness`:

```bash
# 1. Scan any repository and output readiness score & rubric breakdown
readiness scan examples/unconfigured_service

# 2. Output machine-readable JSON for CI/CD gates
readiness scan examples/unconfigured_service --json

# 3. Auto-onboard repository (synthesizes .agent-policy.yaml & AGENTS.md, raising score to 100/100)
readiness fix examples/unconfigured_service

# 4. Auto-onboard with live LLM contract synthesis (OpenAI, Gemini, Anthropic)
readiness fix examples/unconfigured_service --llm

# 5. Open interactive Web Control Plane
readiness ui
```

---

## ⚙️ Execution Modes: Production LLM Workflow vs. Browser Demo

`agent-readiness` is built with a clean separation of concerns:

1. **Production / CLI Workflow (Dynamic LLM Calls)**:
   In normal operation, the onboarding engine can call state-of-the-art LLMs (Gemini, OpenAI, Anthropic, or local Ollama) to synthesize bespoke, contextual policies and operating guidelines tailored to your repository:
   ```bash
   cp .env.example .env
   # Set OPENAI_API_KEY, GEMINI_API_KEY, or custom LLM_API_BASE
   readiness fix . --llm
   ```

2. **Interactive Browser Demo (Pre-Calculated Golden Fixtures)**:
   The web control plane (`docs/index.html` on GitHub Pages) operates 100% client-side with pre-calculated golden fixtures and zero external API dependencies, ensuring instant, deterministic, and safe evaluation without exposing credentials.

---

## 🐍 Python Library Usage

```python
from pathlib import Path
from src.scanner import scan_repository
from src.onboarder import onboard_repository

# 1. Scan repository
report = scan_repository("examples/unconfigured_service")
print(f"Score: {report.score_before}/100 [{report.grade}]")
print(f"Stack: {report.detected_stack}")
print(f"Missing: {report.missing_safeguards}")

# 2. Auto-onboard to 100/100
onboarded = onboard_repository("examples/unconfigured_service", write_files=True)
print(f"Elevated Score: {onboarded.score_after}/100 [{onboarded.grade}]")
```

---

## 🧪 Testing & Verification

```bash
pytest -v
```

---

## 📄 License

MIT Licensed &copy; 2026 zcdlab.
