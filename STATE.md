# STATE.md — Colossal Quant Current Execution State

> **Authoritative live state.** This file answers WHERE the project is. It does not redefine the project specification.
>
> Agents MUST read this file before planning or implementing work.
> Do not infer current state from memory, chat history, commit messages, README text, or old audit reports.

---

## 1. Current State

```yaml
current_phase: 16.5
current_phase_status: IN_PROGRESS
current_task: 16.5.6
current_task_status: READY
next_task: null
last_completed_task: 16.5.5
last_completed_phase: 16
execution_mode: ONE_TASK_AT_A_TIME
human_transition_required: false
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
- **Phase 12.5 — COMPLETE (U.0–U.5)**
- **Phase 13 — COMPLETE**
- **Phase 14 — COMPLETE (14.1–14.4)**
- **Phase 15 — COMPLETE (15.1–15.4)**
- **Phase 16 — COMPLETE (16.1–16.4)** (research-integrity foundation; closed before Phase 17+)
- **Phase 16.5 — IN_PROGRESS (16.5.6 READY)** (tear-sheet research report UI; not Phase 17)
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
- [x] **16.3.1 — Equity grid keeps every daily close** — COMPLETE
- [x] **16.4 — Record the clock next to the execution assumptions** — COMPLETE

The human confirmed the target clock on 2026-10-01. For daily bars, the close of one bar and the open of the next bar are the same timestamp. The equity series keeps the account start on the first open and a point on every bar close, including the first close. The same-bar fill and that first close share one timestamp, and the equity point at that timestamp includes the fill. Do not edit `PROJECT.md` for this note. 16.4 records that clock after 16.3.1 lands.

### Current task

**16.5.6 — Honest unavailable sections** — READY

The human authorized Phase 16.5 on 2026-10-01 instead of opening Phase 17. Phase 17 is not started. Do not invent a Phase 17 task split. `PROJECT.md` §4.4 still omits `execution_assumptions`; that docs sync stays out of scope.

Phase 16.5 is a frontend-only tear-sheet report. It does not add metrics, engines, or API fields. One task at a time. The open task is 16.5.6 only. On 2026-10-01 the human authorized the same agent to review a task after re-running its acceptance commands, then continue.

**16.5.6 goal.** Regimes and Robustness stay empty of fabricated analysis. The Execution tab shows the assumption strings already on the tear sheet, not a cost breakdown.

Regimes copy: "Not available for this run. No regime classification is attached to this result."

Robustness copy: "No robustness analysis is attached to this run."

Do not add a classifier, sensitivity run, walk-forward, bootstrap, Monte Carlo, or a score.

Execution renders every string on `execution_assumptions`, verbatim, with these labels:

- Bar time, Nautilus bar event, Signal and order, Order type, Sizing price
- Maker fee, Taker fee, Default maker fee, Default taker fee
- Fill model, Latency, Spread, Queue, Partial fills
- Equity time, Fill time, Marker time, Fill included in equity

Do not sum fees. Do not invent gross P&L, net P&L, funding, or a slippage amount. When `execution_assumptions` is missing, show "Execution assumptions are not on this response." once. Leave the Data tab as it is.

**Deliverables**

- `frontend/src/pages/TearSheet/tabs/ExecutionTab.tsx`
- `frontend/src/pages/TearSheet/tabs/ExecutionTab.test.tsx`
- `frontend/src/App.tsx`
- `frontend/src/pages/TearSheet/tabs/PlaceholderTab.tsx` only if the regimes and robustness copy cannot be passed in as it stands
- `frontend/src/pages/TearSheet/index.test.tsx` (the regimes test currently expects the Phase 21 label)

**Acceptance**

- `cd frontend && npx tsc -b`
- `cd frontend && npx vitest run`
- `cd frontend && npm run build`

**Commit**

`git add frontend/src/pages/TearSheet/tabs/ExecutionTab.tsx frontend/src/pages/TearSheet/tabs/ExecutionTab.test.tsx frontend/src/App.tsx frontend/src/pages/TearSheet/tabs/PlaceholderTab.tsx frontend/src/pages/TearSheet/index.test.tsx`

Omit `PlaceholderTab.tsx` from that line if this task does not change it.

`feat(ui): show honest unavailable tear sheet sections (Phase 16.5.6)`

### Phase 16.5 tasks

- [x] **16.5.1 — Experiment identity header** — COMPLETE
- [x] **16.5.2 — Overview executive summary** — COMPLETE. Headline and secondary KPIs visible together, plus existing equity, drawdown, and monthly heatmap. No new metrics. No rolling series.
- [x] **16.5.3 — Performance investigation layout** — COMPLETE. Existing price, equity, and underwater charts, equity dominant. No rolling Sharpe or volatility unless a series already exists on the tear sheet.
- [x] **16.5.4 — Trades summary** — COMPLETE. Existing closed-trade KPIs above the current ledger. No MAE, MFE, or R-multiple charts.
- [x] **16.5.5 — Data methodology layout** — COMPLETE. Reorganize fields the Data tab already renders, including the recorded equity clock. No new identity fields.
- [ ] **16.5.6 — Honest unavailable sections** — READY. Regimes and Robustness stay empty of fabricated analysis. Execution shows assumptions already on the response, not a cost breakdown.

Record an accepted task in this file only after the reviewer re-runs that task's acceptance commands. Do not open the next task until that evidence block is committed.

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

### 16.3.1 completion evidence

```yaml
task_id: 16.3.1
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/src/quant/engine/runner.py
  - backend/src/quant/strategies/buy_hold.py
  - backend/tests/engine/test_clock.py
  - backend/tests/engine/test_runner.py
  - backend/tests/strategies/test_buy_hold.py
tests_added: []
tests_updated:
  - backend/tests/engine/test_clock.py::test_buy_hold_equity_keeps_every_daily_close
  - backend/tests/engine/test_runner.py (first return is the first close; equity length 11)
  - backend/tests/strategies/test_buy_hold.py::test_on_order_filled_sets_entered_flag
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
acceptance_output:
  pytest: "428 passed, 81 warnings in 68.17s"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
git_commit_sha: 53248c52891f6e475981f66108dec118fb1c3ddd
next_task: 16.4
notes: |
  Reviewer re-ran whole-tree pytest, ruff, and mypy in the project venv.
  Equity timestamps are the first open and then every daily close. Jan 2
  equity includes the fill because on_order_filled replaces that snapshot.
  Accepted deviations: a fill timestamp that does not match the last
  snapshot raises RuntimeError instead of appending a point. The fill-flag
  test runs the engine first because portfolio has no USDT balance until
  then, and wraps that run in capfd.disabled() so the rejected-order log
  test still captures output. The denied-order test passed in isolation.
```

### 16.4 completion evidence

```yaml
task_id: 16.4
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/src/quant/engine/assumptions.py
  - backend/src/quant/api/schemas.py
  - backend/src/quant/api/routers/runs.py
  - backend/tests/engine/test_assumptions.py
  - backend/tests/api/test_schemas.py
  - backend/tests/api/test_runs_tearsheet.py
  - frontend/src/api/types.ts
  - frontend/src/pages/TearSheet/tabs/DataTab.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
  - frontend/src/pages/CommandCenter/RunHistoryTable.test.tsx
  - frontend/src/pages/Compare/index.test.tsx
tests_added:
  - backend/tests/engine/test_assumptions.py::test_current_assumptions_record_the_confirmed_daily_clock
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  pytest: "429 passed, 81 warnings in 49.58s"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
  tsc: "exit 0"
  vitest: "25 files, 182 passed"
  build: "exit 0"
git_commit_sha: f31dd1aadfc45de570feb60cfb26b41790db8916
next_task: null
notes: |
  Reviewer re-ran whole-tree pytest, ruff, mypy, tsc -b, vitest, and
  the production build. The four clock labels are on CURRENT_ASSUMPTIONS,
  copied onto the tear-sheet payload, and shown on the Data tab. The new
  test asserts those literals only. No timestamp code changed. PROJECT.md
  §4.4 still omits execution_assumptions. Phase 17 is not started.
```

### U.3.2 completion evidence

```yaml
task_id: U.3.2
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/tabs/DataTab.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
  - frontend/src/pages/TearSheet/tearSheet.css
tests_added:
  - frontend/src/pages/TearSheet/index.test.tsx::data tab methodology header shows timeframe, benchmark, and dirty git
  - frontend/src/pages/TearSheet/index.test.tsx::data tab methodology header appends dirty when a git sha is present
  - frontend/src/pages/TearSheet/index.test.tsx::data tab stays up when the tear sheet omits execution assumptions
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "25 files, 187 passed"
  build: "exit 0"
git_commit_sha: f491dc96fc47072b4293ffb5d79651d6a0b42f0b
follow_up_commit_sha: 77744a6f2fed86220d7c6e9cfe481d60ef689919
next_task: U.4
deviations:
  - "Header shows Strategy, Git SHA, Timeframe, Fees, Benchmark, and Verification. It does not show Strategy version or Dataset identity. Phase 12.5 forbids API contract changes. data_snapshot is not on the tear sheet. There is no strategy-version field. Tests pin both labels as absent."
  - "77744a6 is a second commit. It keeps the Data tab up when execution_assumptions is missing: fees render as an em dash and the assumptions section says the block is not on the response."
notes: |
  Reviewer read both diffs and re-ran tsc -b, vitest, and the production
  build once, on HEAD 3573c85, which contains U.3.2, the follow-up, and
  U.4. No Python files changed, so pytest, ruff, and mypy were not re-run.
  A dirty flag with no git SHA renders as an em dash, not "(dirty)".
  Fee rates on this header come from execution_assumptions, not from a
  second reading of params.
```

### U.4 completion evidence

```yaml
task_id: U.4
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/components/ui/kpiCard.css
  - frontend/src/pages/TearSheet/kpiCards.css
  - frontend/src/pages/TearSheet/KpiCards.tsx
  - frontend/src/pages/TearSheet/KpiCards.test.tsx
  - frontend/src/pages/TearSheet/TradeLedger.tsx
  - frontend/src/pages/TearSheet/TradeLedger.test.tsx
tests_added:
  - frontend/src/pages/TearSheet/KpiCards.test.tsx::omits avg duration when the metric is null
  - frontend/src/pages/TearSheet/TradeLedger.test.tsx::renders zero as 0
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "25 files, 187 passed"
  build: "exit 0"
git_commit_sha: 3573c85ab64ed86e89d672fa8f3af14c38f87c5e
next_task: null
deviations:
  - "KPI number colors use --pos-text and --neg-text. PROJECT.md §9.2 requires those tokens for text. The previous CSS used the fill tokens."
  - "A null average duration removes the card. The task allows a computed value or removal. A duration of 0 still renders as 0.0d."
notes: |
  Same acceptance run as U.3.2, on this commit. Quantity 0 renders as
  "0"; a non-zero quantity still uses four decimal places. Hover is a
  120ms border and background transition. KPI values are unchanged.
  Phase 17 is not started.
```

### U.5 completion evidence

```yaml
task_id: U.5
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/KpiCards.tsx
  - frontend/src/pages/TearSheet/KpiCards.test.tsx
  - frontend/src/pages/TearSheet/kpiCards.css
  - frontend/src/pages/TearSheet/index.test.tsx
tests_added:
  - frontend/src/pages/TearSheet/KpiCards.test.tsx::opens Returns and shows one group at a time
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "25 files, 187 passed"
  build: "exit 0"
git_commit_sha: 6808426f38012f5f40cae01c831bf97c9ae05cee
next_task: 16.5.1
deviations:
  - "U.5 was committed before STATE.md had a task for it. This block is the reconciliation. Phase 12.5 had already been marked complete at U.4; it stays complete and now includes U.5."
  - "No Python files changed, so pytest, ruff, and mypy were not re-run."
notes: |
  Reviewer re-ran tsc -b, vitest, and the production build on 6808426.
  KPI formatters and values are unchanged. The cards render one group
  at a time, defaulting to Returns. Phase 17 is not started.
```

### 16.5.1 completion evidence

```yaml
task_id: 16.5.1
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/ExperimentHeader.tsx
  - frontend/src/pages/TearSheet/ExperimentHeader.test.tsx
  - frontend/src/pages/TearSheet/index.tsx
  - frontend/src/pages/TearSheet/tearSheet.css
tests_added:
  - frontend/src/pages/TearSheet/ExperimentHeader.test.tsx (5)
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "26 files, 192 passed"
  build: "exit 0"
git_commit_sha: d0dfd7ed6928d0e46f9be34d6000be11f8ca0536
next_task: 16.5.2
deviations:
  - "A whitespace-only timeframe is omitted. The task says omit anything that is not a non-empty string. The component trims before that check, and the test pins the omit."
  - "tearSheet.css adds flex-wrap on the meta row so the added identity fields can wrap. Header layout only."
  - "index.test.tsx was not modified. Existing header assertions still match the extracted header."
  - "No Python files changed, so pytest, ruff, and mypy were not re-run."
notes: |
  Reviewer re-ran tsc -b, vitest, and the production build on d0dfd7e.
  The header shows name, strategy, first symbol, the multi-symbol note,
  UTC dates, optional timeframe, fees from params.maker_fee, optional
  benchmark, a 7-character git SHA, status, and the verification badge.
  A null or empty git SHA is omitted, including when git_dirty is true.
  Data tab, KPI grouping, charts, and the nav rail are unchanged.
  Vite still prints the existing chunk-size warning. The build exits 0.
  Phase 17 is not started.
```

### 16.5.2 completion evidence

```yaml
task_id: 16.5.2
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/OverviewSummary.tsx
  - frontend/src/pages/TearSheet/OverviewSummary.test.tsx
  - frontend/src/pages/TearSheet/tabs/OverviewTab.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_added:
  - frontend/src/pages/TearSheet/OverviewSummary.test.tsx (3)
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "27 files, 195 passed"
  build: "exit 0"
git_commit_sha: f1770f8023a92c333b2f6655a532e73cd3ea20a3
next_task: 16.5.3
deviations:
  - "Formatters are copied into OverviewSummary. KpiCards is unchanged, so Compare keeps the one-group default."
  - "No new CSS file. The summary reuses the existing kpi-cards grid."
  - "The overview page test scopes KPI labels to their sections because the nav item Trades shares that word."
  - "No Python files changed, so pytest, ruff, and mypy were not re-run."
notes: |
  Reviewer re-ran tsc -b, vitest, and the production build on f1770f8.
  Headline shows CAGR, Sharpe, and Max DD. Secondary shows Sortino,
  volatility, Calmar, win rate, profit factor, trades, average duration
  when non-null, and turnover. Nulls are em dashes. Equity, underwater,
  and the monthly heatmap render from the tear sheet series. The
  Performance tab was not changed in this commit. The human authorized
  same-agent review on 2026-10-01. Vite still prints the existing
  chunk-size warning. The build exits 0. Phase 17 is not started.
```

### 16.5.3 completion evidence

```yaml
task_id: 16.5.3
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/tabs/PerformanceTab.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
  - frontend/src/pages/TearSheet/tearSheet.css
tests_added: []
tests_updated:
  - frontend/src/pages/TearSheet/index.test.tsx::performance tab renders price, then a dominant equity chart, then underwater
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "27 files, 195 passed"
  build: "exit 0"
git_commit_sha: f9a4add012410f9dce142c82dfa749373fbd0f7b
next_task: 16.5.4
deviations:
  - "The page test mocks BaseChart. Real lightweight-charts throws in jsdom when a canvas context is missing. The mock renders the height prop so the test can check 420, 420, and 280."
  - "Removed the unused tear-sheet-tab__grid-2 rule."
  - "No Python files changed, so pytest, ruff, and mypy were not re-run."
notes: |
  Reviewer re-ran tsc -b, vitest, and the production build on f9a4add.
  Performance order is price, equity, then underwater. Equity and
  underwater are full width. Equity and price are 420px. Underwater is
  280px. No rolling series was added. Overview was not changed.
  Vite still prints the existing chunk-size warning. The build exits 0.
  Phase 17 is not started.
```

### 16.5.4 completion evidence

```yaml
task_id: 16.5.4
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/TradesSummary.tsx
  - frontend/src/pages/TearSheet/TradesSummary.test.tsx
  - frontend/src/pages/TearSheet/tabs/TradesTab.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_added:
  - frontend/src/pages/TearSheet/TradesSummary.test.tsx (4)
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "28 files, 199 passed"
  build: "exit 0"
git_commit_sha: cac63f82366016979ecd04771fe172597ade69ca
next_task: 16.5.5
deviations:
  - "The summary has a Closed trades heading so it matches the other tear-sheet sections. The task did not name that heading."
  - "Formatters are copied from KpiCards. Trading tones stay neutral. A duration of 0 still renders as 0.0d."
  - "No Python files changed, so pytest, ruff, and mypy were not re-run."
notes: |
  Reviewer re-ran tsc -b, vitest, and the production build on cac63f8.
  The Trades tab shows Trades, Win Rate, Profit Factor, and Avg Duration
  above the existing ledger. A null duration omits that card. Null KPIs
  are em dashes. The ledger still uses server pagination. No MAE, MFE,
  or R-multiple was added. Vite still prints the existing chunk-size
  warning. The build exits 0. Phase 17 is not started.
```

### 16.5.5 completion evidence

```yaml
task_id: 16.5.5
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/tabs/DataTab.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_added: []
tests_updated:
  - frontend/src/pages/TearSheet/index.test.tsx::data tab shows execution assumptions from tear sheet
  - frontend/src/pages/TearSheet/index.test.tsx::data tab stays up when the tear sheet omits execution assumptions
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "28 files, 199 passed"
  build: "exit 0"
git_commit_sha: 2c6c05d8d69be24118cf1446faec241a25c99d48
next_task: 16.5.6
deviations:
  - "The clock and execution lists use the existing tear-sheet-tab__facts grid. The execution list previously used an unstyled dl. Labels and values are unchanged."
  - "The Clock section is omitted when execution assumptions are missing, so the missing sentence still appears once."
  - "No Python files changed, so pytest, ruff, and mypy were not re-run."
notes: |
  Reviewer re-ran tsc -b, vitest, and the production build on 2c6c05d.
  With assumptions present, the Data tab groups methodology, clock, and
  the remaining execution fields. Clock shows the four recorded strings
  verbatim. A missing assumptions object keeps Fees as an em dash and
  one missing sentence. No venue, strategy version, or dataset identity
  was added. Vite still prints the existing chunk-size warning. The
  build exits 0. Phase 17 is not started.
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
