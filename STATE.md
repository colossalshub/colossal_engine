# STATE.md — Colossal Quant Current Execution State

> **Authoritative live state.** This file answers WHERE the project is. It does not redefine the project specification.
>
> Agents MUST read this file before planning or implementing work.
> Do not infer current state from memory, chat history, commit messages, README text, or old audit reports.

---

## 1. Current State

```yaml
current_phase: 15
current_phase_status: IN_PROGRESS
current_task: 15.1
current_task_status: READY
next_task: 15.2
last_completed_task: 14.4
last_completed_phase: 14
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
- **Phase 12 — COMPLETE (all 4 tasks)**
- **Phase 12.5 — PARTIAL; U.0–U.3.1 COMPLETE; U.3.2 and U.4 pending after Phase 14–16**
- **Phase 13 — COMPLETE**
- **Phase 14 — COMPLETE (14.1–14.4)**
- **Phase 15 — IN_PROGRESS; 15.1 is the current task**
- Phase 16 — NOT STARTED (research-integrity foundation; commit to
  this before Phase 17+)
- Phase 17–29 — BACKLOG (research-platform ambitions; scope to be
  explicitly committed or deferred after Phase 16)

> Phase 0–11 status above is the recorded project state from the latest research-integrity audit context. If repository evidence contradicts this state, STOP and report the conflict rather than silently changing this file.

---

## 2. Current Objective

### Phase 15 — Execution Assumptions

**Goal:** Make the execution assumptions the engine already uses explicit, before anyone treats a result as realistic execution.

### Tasks

- [ ] **15.1 — Pin current assumptions** — READY
- [ ] **15.2 — Return assumptions on run metadata** — NOT STARTED
- [ ] **15.3 — Show assumptions on the tear sheet** — NOT STARTED
- [ ] **15.4 — Future-bar mutation** — NOT STARTED

Do not implement a custom matcher. Do not change fill behavior in this phase. Record what the runner already does.

### Current task

**15.1 — Pin current assumptions** — READY

Add one module and one test that state the assumptions `runner.py` already uses: bar `ts` is open time, the strategy submits from `on_bar` using that bar's close, maker and taker fees default to `0.001`, and `add_venue` passes no custom fill model, latency, spread, queue, or partial-fill model. The test must fail if the runner's call stops matching that record. No API field, no tear-sheet UI, and no change to order matching.

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

### 12.4 completion evidence

```yaml
task_id: 12.4
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/src/quant/api/routers/runs.py
  - backend/tests/api/test_runs_create.py
  - frontend/src/pages/TearSheet/index.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_added:
  - backend/tests/api/test_runs_create.py::test_multi_symbol_universe_rejected
  - backend/tests/api/test_runs_create.py::test_single_symbol_universe_accepted
  - frontend/src/pages/TearSheet/index.test.tsx (multi-symbol header note)
tests_modified:
  - backend/tests/api/test_runs_create.py::test_default_name_generation_multi_symbol_rejected (renamed from _multi_symbol; now expects 422)
  - backend/tests/api/test_runs_create.py::test_universe_round_trip_preserves_order (universe reduced to single symbol)
  - frontend/src/pages/TearSheet/index.test.tsx::renders the universe and formatted date range (updated header assertion)
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
tree_state: uncommitted_12.4_diff
acceptance_output:
  pytest: "388 passed"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 26 source files"
  tsc: "exit 0"
  vitest: "166 passed"
  build: "exit 0"
git_commit_sha: 839ca1f
next_task: 13.1
```

### U.2 completion evidence

```yaml
task_id: U.2
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/components/charts/chartOptions.ts (new)
  - frontend/src/components/charts/chartOptions.test.ts (new)
  - frontend/src/components/charts/BaseChart.tsx
  - frontend/src/components/charts/BaseChart.test.tsx
  - frontend/src/lib/theme.ts
  - frontend/src/lib/theme.test.ts
  - frontend/src/components/grid/agGridTheme.css
  - frontend/src/pages/CommandCenter/RunHistoryTable.tsx
  - frontend/src/pages/TearSheet/TradeLedger.tsx
tests_added:
  - chartOptions.test.ts (4)
  - theme.test.ts (+4)
  - BaseChart.test.tsx (+1)
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
tree_state: uncommitted_U.2_diff
acceptance_output:
  tsc: "exit 0"
  vitest: "26 files, 185 passed"
  build: "exit 0"
git_commit_sha: 2b0bb35
next_task: null
notes: |
  Live check (zoom preservation across theme toggle) not run by agent.
  Requires human confirmation before Phase 13 begins.
```

### U.3.1 completion evidence

```yaml
task_id: U.3.1
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/App.tsx
  - frontend/src/pages/TearSheet/index.tsx
  - frontend/src/pages/TearSheet/TearSheetNav.tsx (new)
  - frontend/src/pages/TearSheet/tearSheetNav.css (new)
  - frontend/src/pages/TearSheet/tearSheet.css
  - frontend/src/pages/TearSheet/tabs/ (new: OverviewTab, PerformanceTab,
    TradesTab, DataTab, PlaceholderTab)
  - frontend/src/pages/TearSheet/index.test.tsx
deviations_accepted:
  - Removed the "Widgets" picker from the header. It had no purpose
    without the drag layout. Back button, name, badges, and meta line
    unchanged.
tests_removed: 5 (drag-layout specific)
tests_added: 8 (tab rendering, nav rail, active state, redirect)
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
tree_state: uncommitted_U.3.1_diff
acceptance_output:
  tsc: "exit 0"
  vitest: "188 passed"
  build: "exit 0"
git_commit_sha: 15eebc2
next_task: null
notes: |
  Live check not run by agent. Requires human confirmation of tab
  switching, deep links, and per-tab chart rendering before Phase 13.
```

### 13.1 completion evidence

```yaml
task_id: 13.1
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/src/quant/extract/metrics.py
  - backend/src/quant/engine/orchestrator.py
  - backend/tests/extract/test_metrics.py
  - backend/tests/engine/test_orchestrator.py
tests_added:
  - backend/tests/extract/test_metrics.py (+4 closed-trade cases)
  - backend/tests/engine/test_orchestrator.py (+1 full-path test)
tests_updated:
  - Multiple TradeSummary constructions gained the closed=True flag
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
tree_state: uncommitted_13.1_diff
acceptance_output:
  pytest: "393 passed"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 26 source files"
git_commit_sha: db6729f
next_task: 14.1
notes: |
  ts_closed is Python None on open BuyHold positions (not pd.NaT).
  pd.notna covers both. Frontend KpiCards renders null as "—".
```

### 14.3 completion evidence

```yaml
task_id: 14.3
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/src/quant/api/main.py
  - backend/src/quant/strategies/registry.py (new)
  - backend/src/quant/strategies/buy_hold.py
  - backend/src/quant/strategies/ema_cross.py
  - backend/src/quant/engine/orchestrator.py
  - backend/src/quant/data/runs_store.py
  - backend/src/quant/api/schemas.py
  - backend/src/quant/api/routers/runs.py
  - backend/tests/data/test_runs_store.py
  - backend/tests/api/test_runs_create.py
  - backend/tests/api/test_schemas.py
  - backend/tests/engine/test_orchestrator.py
  - frontend/src/api/types.ts
  - frontend/src/pages/CommandCenter/RunHistoryTable.test.tsx
  - frontend/src/pages/CommandCenter/StrategyForm.test.tsx
  - frontend/src/pages/Compare/index.test.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - cd frontend && npx tsc -b
tree_state: uncommitted_14.3_diff
acceptance_output:
  pytest: "418 passed"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 29 source files"
  tsc: "exit 0"
git_commit_sha: b0243a0
next_task: 14.4
notes: |
  Lifespan handler added to api/main.py runs init_runs_schema at startup.
  experiment_id column added via ALTER TABLE migration. Seed semantics
  honest: deterministic strategies get None, non-deterministic read
  params["seed"].
```

### 14.4 completion evidence

```yaml
task_id: 14.4
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/src/quant/data/runs_store.py
  - scripts/run_worker.py
  - scripts/run_backtest.py
  - backend/tests/engine/test_cross_process_repro.py
  - backend/tests/data/test_runs_store.py
tests_added:
  - backend/tests/engine/test_cross_process_repro.py::test_cli_and_worker_produce_identical_snapshot_and_equity
  - backend/tests/data/test_runs_store.py::test_update_run_status_data_snapshot_optional
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
acceptance_output:
  pytest: "420 passed, 67 warnings in 53.79s"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 29 source files"
git_commit_sha: 3bc970a
next_task: 15.1
notes: |
  Reviewer re-ran acceptance. Worker success path persists data_snapshot.
  CLI and API-plus-worker produced the same snapshot and byte-identical
  equity.parquet. Accepted deviation: subprocess stdout uses utf-8 with
  errors=replace so Nautilus log bytes do not crash capture on Windows.
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

- Non-BTC symbols can be settled as BTC because the runner hardcodes the BTC/USDT account currency path. ADDRESSED by task 12.1 (commit ccadbfc); the audit text is unchanged.
- OHLCV data is not sufficiently validated.
- Ingestion can reach its page cap and still report success. ADDRESSED
  by task 12.3 (commit 8d54b19) (fail-closed on truncated range).
- Trade KPIs can treat an open position as a losing trade/fee result.
  ADDRESSED by Phase 13 (commit db6729f).

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
