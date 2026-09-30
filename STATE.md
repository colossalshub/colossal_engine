# STATE.md — Colossal Quant Current Execution State

> **Authoritative live state.** This file answers WHERE the project is. It does not redefine the project specification.
>
> Agents MUST read this file before planning or implementing work.
> Do not infer current state from memory, chat history, commit messages, README text, or old audit reports.

---

## 1. Current State

```yaml
current_phase: 12
current_phase_status: IN_PROGRESS
current_task: 12.4
current_task_status: READY
next_task: null
last_completed_task: 12.3
last_completed_phase: 11
execution_mode: ONE_TASK_AT_A_TIME
human_transition_required: true
```

### Phase status

- Phase 0 — COMPLETE
- Phase 1 — COMPLETE
- Phase 2 — COMPLETE
- Phase 3 — COMPLETE
- Phase 4 — COMPLETE
- Phase 5 — COMPLETE
- Phase 6 — COMPLETE
- Phase 7 — COMPLETE
- Phase 8 — COMPLETE
- Phase 9 — COMPLETE
- Phase 10 — COMPLETE
- Phase 11 — COMPLETE
- **Phase 12 — IN PROGRESS; 12.1–12.3 COMPLETE; 12.4 READY**
- Phase 13–16 — NOT STARTED (research-integrity foundation; commit to
  this before Phase 17+)
- Phase 17–29 — BACKLOG (research-platform ambitions; scope to be
  explicitly committed or deferred after Phase 16)

> Phase 0–11 status above is the recorded project state from the latest research-integrity audit context. If repository evidence contradicts this state, STOP and report the conflict rather than silently changing this file.

---

## 2. Current Objective

### Phase 12 — Fail Closed

**Goal:** Prevent apparently valid research from being produced when the data, instrument identity, ingestion completeness, or declared universe is invalid for the current execution architecture.

### Tasks

- [x] **12.1 — Instrument Identity** — COMPLETE
- [x] **12.2 — OHLCV Integrity** — COMPLETE
- [x] **12.3 — Ingestion Completeness** — COMPLETE
- [ ] **12.4 — Universe Contract** — READY

### Current task

**12.4 — Universe Contract** — READY

Current execution is single-instrument. Reject `len(universe) != 1`
until Phase 23 explicitly changes the architecture. Tear sheet metadata
must not claim symbols were traded when only the first symbol was
executed. Do not start this task until a human begins it.

### 12.1 completion evidence

```yaml
task_id: 12.1
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-09-30
files_changed:
  - backend/src/quant/engine/runner.py
  - backend/tests/engine/test_runner.py
tests_added:
  - backend/tests/engine/test_runner.py::test_unsupported_instrument_fails_before_engine
  - backend/tests/engine/test_runner.py::test_btc_usdt_instrument_maps_btc_base_and_usdt_quote
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
tree_state: uncommitted_12.1_diff  # acceptance was run on the working tree before the commit landed
acceptance_output:
  pytest: "365 passed, 52 warnings in 28.82s"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 26 source files"
git_commit_sha: ccadbfc
next_task: 12.2
```

### 12.2 completion evidence

```yaml
task_id: 12.2
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-09-30
files_changed:
  - backend/src/quant/data/store.py
  - backend/tests/data/test_store.py
  - backend/tests/data/test_read.py
  - backend/tests/api/test_data_coverage.py
tests_added:
  - backend/tests/data/test_store.py (12 new rejection + batch tests)
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
acceptance_output:
  pytest: "381 passed"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 26 source files"
git_commit_sha: 4567de9
next_task: 12.3
```

### 12.3 completion evidence

```yaml
task_id: 12.3
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - scripts/ingest_bars.py
  - backend/tests/test_ingest_completeness.py
tests_added:
  - backend/tests/test_ingest_completeness.py (5 tests)
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
tree_state: uncommitted_12.3_diff
acceptance_output:
  pytest: "386 passed (first run 384 passed + 2 flaky capfd; re-run green)"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 26 source files"
git_commit_sha: 8d54b19
next_task: 12.4
```

Phase 12.1 is committed as `ccadbfc`. The commit message follows the
Conventional Commits format defined in `WORKFLOW.md` §3.

Deviations accepted with the task: a non-BTC symbol can still be queued by the API. `run_backtest` rejects it before `BacktestEngine` is constructed. The worker records `failed` and does not write a successful run, artifacts, or verification. Universe length remains 12.4.

### Phase 12 non-goals

Do NOT implement:

- multi-asset execution;
- perpetual/futures mechanics;
- funding/liquidation;
- a custom matching engine;
- a custom portfolio/accounting engine;
- an optimizer;
- walk-forward validation;
- Monte Carlo validation;
- statistical-model expansion.

---

## 3. Known Research-Integrity Findings

From the latest Quant Research Integrity Audit:

### P0 / critical

- Non-BTC symbols can be settled as BTC because the runner hardcodes the BTC/USDT account currency path. Addressed by task 12.1; the audit text is unchanged.
- OHLCV data is not sufficiently validated.
- Ingestion can reach its page cap and still report success. Addressed
  by task 12.3 (fail-closed on truncated range).
- Trade KPIs can treat an open position as a losing trade/fee result.

### P1 / high

- Dataset identity is not a fingerprint of the exact ordered bars used.
- UI/worker execution does not reliably capture git SHA.
- Current execution assumptions include same-bar close behavior and zero slippage/default Nautilus fill behavior but are not sufficiently surfaced.
- The API/UI can accept a multi-symbol universe while the execution path trades only the first symbol.

### Important limitations

- A green test suite does not prove absence of future-bar influence.
- A self-consistent equity reconstruction is not an independent external account verification.
- Bar-close timestamps do not by themselves eliminate same-bar execution bias.
- Statistical metrics are not evidence of strategy validity until the research-design controls are implemented.

---

## 4. Last Audit Record

```yaml
type: Quant Research Integrity Audit
status: COMPLETE — AUDIT ONLY
commit: 5fffa3cbd618ca05e65620f2b26ddae260f122be
branch: main
date: 2026-09-30
scope: Phases 0–11
```

The audit recorded:

- backend acceptance: 361 passed;
- ruff: clean;
- mypy: clean;
- frontend acceptance: 165 passed;
- TypeScript: clean.

These are historical acceptance results and must not be reused as current results after code changes. Run the required acceptance commands for the current task.

---

## 5. Permanent Architecture Boundary

### Colossal Quant owns

- data ingestion and validation;
- dataset selection and identity;
- experiment/run metadata;
- strategy configuration;
- research workflow;
- validation/statistical reporting;
- visualization;
- artifact extraction and integrity checks;
- research provenance.

### NautilusTrader owns

- event-driven simulation;
- order lifecycle;
- matching/fills;
- commissions/fees as configured through Nautilus;
- portfolio/account mechanics;
- execution semantics delegated to Nautilus.

**Do not build a second implementation of a Nautilus responsibility.**

---

## 6. State-Transition Rules

A task may transition only through:

```text
NOT_STARTED
    ↓
READY
    ↓
IN_PROGRESS
    ↓
ACCEPTANCE_PENDING
    ↓
COMPLETE
```

Failure returns the task to `IN_PROGRESS` or `BLOCKED`.

A phase cannot become `COMPLETE` until:

1. every task is complete;
2. required tests exist and test the specified behavior;
3. whole-tree acceptance passes;
4. no unapproved scope changes remain;
5. required probe/approval rules were followed;
6. the reviewer accepts the work;
7. this file is updated with evidence.

No agent may skip a state transition merely because the change appears small.

---

## 7. Required Evidence Per Completed Task

Record:

- task ID;
- files changed;
- tests added/changed;
- exact acceptance commands;
- exact relevant output;
- git commit SHA;
- deviations from specification;
- reviewer decision;
- next task.

Do not record “done” as the only evidence.

---

## 8. Conflict Protocol

If any of the following disagree:

- `STATE.md`;
- `PROJECT.md`;
- `WORKFLOW.md`;
- `REVIEWER.md`;
- repository code;
- tests;
- git history;
- a third-party API probe;

STOP.

Report:

```text
STATE CONFLICT

Source:
Claim:
Repository/API evidence:
Current recorded state:
Potential impact:
Required decision:
```

Do not silently choose which source is “probably right.”

---

## 9. Update Rule

`STATE.md` is intentionally short and mutable.

It must be updated whenever a task or phase changes state.

Do not copy the complete roadmap into this file. The permanent roadmap belongs in `PROJECT.md`.

Do not put implementation details here unless they are necessary to describe current state or a blocker.
