# STATE.md — Colossal Quant Current Execution State

> **Authoritative live state.** This file answers WHERE the project is. It does not redefine the project specification.
>
> Agents MUST read this file before planning or implementing work.
> Do not infer current state from memory, chat history, commit messages, README text, or old audit reports.

---

## 1. Current State

```yaml
current_phase: 16
current_phase_status: IN_PROGRESS
current_task: 16.3.1
current_task_status: READY
next_task: 16.4
last_completed_task: 16.3
last_completed_phase: 15
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
- **Phase 15 — COMPLETE (15.1–15.4)**
- **Phase 16 — IN_PROGRESS; 16.3.1 is the current task** (research-integrity foundation; commit to
  this before Phase 17+)
- Phase 17–29 — BACKLOG (research-platform ambitions; scope to be
  explicitly committed or deferred after Phase 16)

> Phase 0–11 status above is the recorded project state from the latest research-integrity audit context. If repository evidence contradicts this state, STOP and report the conflict rather than silently changing this file.

---

## 2. Current Objective

### Phase 15 — Execution Assumptions

**Goal:** Make the execution assumptions the engine already uses explicit, before anyone treats a result as realistic execution.

### Tasks

- [x] **15.1 — Pin current assumptions** — COMPLETE
- [x] **15.2 — Return assumptions on run metadata** — COMPLETE
- [x] **15.3 — Show assumptions on the tear sheet** — COMPLETE
- [x] **15.4 — Future-bar mutation** — COMPLETE

Do not implement a custom matcher. Do not change fill behavior in this phase. Record what the runner already does.

### Phase 16 — Clock and Artifact Alignment

**Goal:** Every research artifact uses an explicit and coherent timestamp contract. Pin the current clock before moving any timestamp.

### Tasks

- [x] **16.1 — Pin the current equity clock** — COMPLETE
- [x] **16.2 — Benchmark timestamps cover the equity clock** — COMPLETE
- [x] **16.3 — Marker time is not earlier than the fill** — COMPLETE
- [ ] **16.3.1 — Equity grid keeps every daily close** — READY
- [ ] **16.4 — Record the clock next to the execution assumptions** — NOT STARTED

The human confirmed the target clock on 2026-10-01. For daily bars, the close of one bar and the open of the next bar are the same timestamp. The equity series keeps the account start on the first open and a point on every bar close, including the first close. The same-bar fill and that first close share one timestamp, and the equity point at that timestamp includes the fill. Do not edit `PROJECT.md` for this note. 16.4 records that clock after 16.3.1 lands.

### Current task

**16.3.1 — Equity grid keeps every daily close** — READY

`run_backtest` publishes the configured starting cash at the first open and a return at every equity snapshot, including the first close. The market fill is not visible at the end of `on_bar`. BuyHold replaces that bar's snapshot inside `on_order_filled`, at the fill timestamp, so the Jan 2 point includes the fill. Do not append a second point at that timestamp. Update the 16.1 clock test and the runner tests that pinned the skipped day. Do not edit `PROJECT.md`.

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

### 15.1 completion evidence

```yaml
task_id: 15.1
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/src/quant/engine/assumptions.py
  - backend/tests/engine/test_assumptions.py
tests_added:
  - backend/tests/engine/test_assumptions.py::test_current_assumptions_match_runner_behavior
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
acceptance_output:
  pytest: "421 passed, 69 warnings in 50.92s"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
git_commit_sha: 5cda495
next_task: 15.2
notes: |
  Reviewer re-ran acceptance. Spies confirmed add_venue kwargs, fee
  decimals, first bar ts_event at the next open, and one market order
  submitted inside on_bar. Accepted deviation: BacktestEngine is
  immutable, so the test proxies the class. Two test-only type ignores
  annotate the Nautilus method spies. Sizing-at-bar.close is recorded
  on the dataclass and was not exercised, because the run used the
  default deploy_pct of "0".
```

### 15.2 completion evidence

```yaml
task_id: 15.2
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/src/quant/api/schemas.py
  - backend/src/quant/api/routers/runs.py
  - backend/tests/api/test_schemas.py
  - backend/tests/api/test_runs_tearsheet.py
tests_added:
  - backend/tests/api/test_schemas.py::test_execution_assumptions_extra_field_forbidden_raises
  - backend/tests/api/test_runs_tearsheet.py::test_done_run_reports_custom_fees_in_execution_assumptions
  - backend/tests/api/test_runs_tearsheet.py::test_queued_run_with_no_fee_params_defaults_and_does_not_500
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
acceptance_output:
  pytest: "1 failed, 423 passed, 69 warnings in 58.87s"
  pytest_failure: "test_on_order_rejected_warns_and_resets_entered (I-005 capfd); isolated rerun passed in 1.64s"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
git_commit_sha: c7dd5ff
next_task: 15.3
notes: |
  Tear sheet JSON includes execution_assumptions. Structural fields come
  from CURRENT_ASSUMPTIONS. Non-empty string fee params are used; other
  types fall back to the default without coercion. Reviewer whole-tree
  pytest hit the pre-existing I-005 log-capture failure once. That test
  is not part of this diff. The three new tests passed in that run.
```

### 15.3 completion evidence

```yaml
task_id: 15.3
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/api/types.ts
  - frontend/src/pages/TearSheet/tabs/DataTab.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
  - frontend/src/pages/Compare/index.test.tsx
  - frontend/src/pages/CommandCenter/RunHistoryTable.test.tsx
tests_added:
  - frontend/src/pages/TearSheet/index.test.tsx::data tab shows execution assumptions from tear sheet
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "25 files, 182 passed"
  build: "exit 0"
git_commit_sha: b775da2feb3b7558295d48af41166530f1134ac9
next_task: 15.4
notes: |
  Reviewer re-ran tsc -b, vitest, and the production build. Data tab
  renders maker fee, taker fee, bar time, order type, and fill model
  from execution_assumptions. The test uses maker_fee 0.009 against
  params.maker_fee 0.002, and the header still shows fees 0.20%.
  U.3.2 placeholder remains. PROJECT.md §4.4 still omits
  execution_assumptions; that docs sync is not part of this task.
```

### 15.4 completion evidence

```yaml
task_id: 15.4
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/tests/engine/test_future_bar.py
tests_added:
  - backend/tests/engine/test_future_bar.py::test_mutating_last_bar_leaves_earlier_buy_hold_results_unchanged
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
acceptance_output:
  pytest: "425 passed, 73 warnings in 64.58s"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
git_commit_sha: 56e4e0369ce74d440e8d6e63f5f2d6281c051c4a
next_task: 16.1
notes: |
  Reviewer re-ran whole-tree pytest, ruff, and mypy. Mutating the last
  bar leaves the two fill rows and portfolio_returns[:-1] unchanged.
  Both ending balances move. With volume 1.0 and trade_size 1, Nautilus
  1.231.0 emits two fills on one order at the first bar close: 0.25 at
  100.00 and 0.75 at 100.01. The first prompt's len == 1 assertion was
  wrong; the test pins those two rows. No production code changed.
  The I-005 denied-order test did not fail on this run.
```

### 16.1 completion evidence

```yaml
task_id: 16.1
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/tests/engine/test_clock.py
tests_added:
  - backend/tests/engine/test_clock.py::test_buy_hold_fill_lands_between_the_first_two_equity_points
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
acceptance_output:
  pytest: "426 passed, 75 warnings in 70.34s"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
git_commit_sha: ac2fe880edfdb2221a53e34166845ff9586d9f97
next_task: 16.2
notes: |
  Reviewer re-ran whole-tree pytest, ruff, and mypy. Both fills convert
  to 1735776000000. Equity starts at 1735689600000. The next equity
  point is 1735862400000, equal to portfolio_returns[0][0]. The fill
  timestamp is not an equity point. No production code changed.
```

### 16.2 completion evidence

```yaml
task_id: 16.2
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/tests/engine/test_benchmark_clock.py
tests_added:
  - backend/tests/engine/test_benchmark_clock.py::test_benchmark_last_point_is_last_close_on_the_equity_clock
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
acceptance_output:
  pytest: "427 passed, 77 warnings in 59.62s"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
git_commit_sha: e873f85d3bb0e556f1fc75da2a8197a12073f9d6
next_task: 16.3
notes: |
  Reviewer re-ran whole-tree pytest, ruff, and mypy in the project venv.
  Stored benchmark timestamps are the five candle opens. The last equity
  point is one day after the last stored open, and its benchmark equals
  the first equity point times the last stored close over the first
  stored close. deploy_pct is "0"; the default "1.0" on volume-1 bars
  buys 999 and the account goes negative before any equity series exists.
  No production code changed.
```

### 16.3 completion evidence

```yaml
task_id: 16.3
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/tests/engine/test_marker_clock.py
tests_added:
  - backend/tests/engine/test_marker_clock.py::test_buy_marker_is_not_earlier_than_the_fill
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
acceptance_output:
  pytest: "428 passed, 79 warnings in 47.74s"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
git_commit_sha: e8eb2a5afc862789a738c2a81e880b1b82c8f83d
next_task: 16.4
notes: |
  Reviewer re-ran whole-tree pytest, ruff, and mypy in the project venv.
  The buy marker from _map_position_row and _build_markers is
  1735776000000, equal to both fills and later than the stored bar open.
  The position stays open, so there is no exit marker. No production
  code changed. 16.4 is blocked until the human confirms the target clock.
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
