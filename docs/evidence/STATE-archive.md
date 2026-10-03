# STATE.md Evidence Archive

Historical task evidence blocks and audit records moved out of
`STATE.md` by DOCS.1 to cut the live file's size. Moved verbatim, in
their original order. This file is historical reference only — it is
not required reading before starting or reviewing current work.

---

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

### Human clock decision before 16.4

The following decision was recorded in the former `STATE.md` Current
Objective after 16.3.1 and before 16.4. It is preserved verbatim:

The human confirmed the target clock on 2026-10-01. For daily bars, the close of one bar and the open of the next bar are the same timestamp. The equity series keeps the account start on the first open and a point on every bar close, including the first close. The same-bar fill and that first close share one timestamp, and the equity point at that timestamp includes the fill. Do not edit `PROJECT.md` for this note. 16.4 records that clock after 16.3.1 lands.

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
Conventional Commits format defined in `docs/ai/WORKFLOW.md` §3.

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

## Phase 0–11 Audit Findings (historical)

Originally `STATE.md` §3 (the "P0 / critical" and "P1 / high" lists
only — "Important limitations" stays in `STATE.md`) and §4 (Last
Audit Record). Moved verbatim.

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


# Historical completed records moved on 2026-10-03 after combined 18.2g/g.1 acceptance

These records are preserved verbatim from STATE.md. Their READY/status prose
is historical; current execution state and latest acceptance live in STATE.md.

### 18.2g.1 blocking-fix readiness contract

Independent readiness opens only this mini-task under the existing explicit
post-probe approval and the user's delegated instruction, "make trustworthy
decisions and continue until this phase is done". Fixing observed violation of
the already approved no-rounding contract is within that authorization; no
new third-party API, dependency, unseen-probe approval or phase crossing.

**Observed blocker:** independent review of original implementation
`5a24edce407b4d3da75ee54c123ee14f0f928d3a` found admitted float volume
`1000000000000.0001` satisfies precision validation of `Decimal(str(value))`,
but binary float `.6f` serializes it to `1000000000000.000122`. Installed
Quantity accepts that changed value and the real public runner returns
BacktestResult. This violates "Formatting serializes accepted precision only,
never rounds source values." Reviewer reproduction evidence is retained in
`/tmp/phase18g-review-blocker.log` and `/tmp/phase18g-review-report.md`.
Original review Ruff and mypy passed; whole pytest was not started following
interruption and blocker discovery. That partial review is not completed
acceptance. Original doer lint failures and report remain preserved. No buggy
original SHA alone is accepted; do not amend or erase it.

**Exact scope:** modify only `backend/src/quant/engine/research_runner.py` and
`backend/tests/engine/test_research_runner.py`. In the five admitted Bar OHLCV
constructor arguments, format `Decimal(str(row[field]))` rather than the binary
float: `.2f` for open/high/low/close, `.6f` for volume, then existing
Price.from_str/Quantity.from_str. Use the identical decimal interpretation that
passed admission; precision predicates, accepted/rejected inputs, public
signature, clock selection/gating, lifecycle, results and ordinary runner stay
unchanged. No new helpers, APIs, dependencies, defaults, numeric coercion or
other behavior. Serialize initial cash with
`f"{Decimal(str(starting_balance_usdt)):.0f}"` for the same admitted-decimal
consistency; existing whole-float cash admission is unchanged. This authorizes
only these six formatting sites, no cash/size/fee redesign.

**Regression:** run the actual public research runner with real Nautilus engine
and admitted float volume `1000000000000.0001`; use existing delegating engine
watch to capture actual Bars, assert exact volume string
`1000000000000.000100` (or exact Decimal equality plus precision6), normal
actual fill/fee/results and unchanged input deep snapshot. Verify representative
normal OHLCV exact serializations and normal control results remain unchanged.
No factory mocks as the sole proof, weakened assertions or changes to existing
fixtures/expectations. The original failure must be exposed by this regression
on the original serialization and pass on the correction, retaining evidence.

**Acceptance:** existing Linux venv activated, repository root, both doer and
fresh independent combined reviewer run exactly:

```bash
python -m ruff check .
python -m mypy --strict backend/src
python -m pytest backend/tests -q
git diff --check
git status --short
```

Whole-tree checks, unchanged options/plugins/proxy/TLS, established command-only
local TestClient socket permission as needed. Preserve complete outputs,
failures/corrections under five-loop limit. No frontend files/checks. One
terminal fix commit, no amend:
`fix(engine): preserve admitted decimal formatting (Phase 18.2g.1)`.
Doer does not edit STATE or self-accept. Independent reviewer verifies the
combined original+fix tree against full 18.2g contract and this correction,
reruns all commands and then records separate STATE completion for g and g.1,
final combined accepted implementation SHA and original blocking evidence.
No completion is recorded by this readiness. Later integration/guarantees
retain separate gates; whole 18.2 and Phase 18 stay incomplete.

**Readiness evidence:** known unchanged startup/spec/probe/rules from the earlier
readiness review were retained; no new claim of complete historical reads. The
original acceptance reviewer disclosed truncated mandatory-document output;
fresh combined reviewer must complete unread portions in bounded chunks before
acceptance. Latest live STATE/current task, original
review report and actual five serialization sites/test watch inspected.
Clean same branch `phase18/18.2g-research-buy-hold` at original task SHA above;
accepted prerequisite main 8b519e0 is ancestor (exit 0). Independent live
`git ls-remote --heads origin main` returned
`8b519e04fe676ef2be6d58bb047a92990177fd5e`, exit 0. Network proxy/TLS unchanged.
Whole diff/staged scope/whitespace checks precede this separate STATE-only
readiness commit; no production edits, suites, installs, workers, push/merge
or amend. No Python files changed; pytest/Ruff/mypy skipped under WORKFLOW §5.
Serial original g READY -> implementation IN_PROGRESS -> committed
ACCEPTANCE_PENDING -> blocking review returns g to IN_PROGRESS is recorded
here; the earlier persisted READY snapshot was not completion evidence.
Only g.1 READY, next_task null, last_completed_task 18.2f and
human_transition_required false; historical approval/evidence preserved.
No other task/phase opened; never Phase 29.

### 18.2g readiness contract and post-probe approval

Independent readiness opens only **18.2g — Research-only fresh BuyHold adapter**.
Rule identity is `phase18-temporal-v1`; supplemental corrected plan is
`/tmp/phase18g-plan.md`. This durable contract stands independently.

**Human approval (2026-10-03):** after the accepted 18.2f probe and exact
bounded Stage 2 proposal were presented, the user replied directly:
"make trustworthy decisions and continue until this phase is done".
The coordinator and independent readiness reviewer record this as explicit
post-probe WORKFLOW §2 approval of the observed calls
`engine.cache.positions_open()` and
`engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))`,
and the bounded research-only BuyHold implementation below. It clears the
current human-transition gate. It approves no unseen future probe, unfamiliar
API, new dependency, automatic phase crossing or completed implementation.
Earlier 18.2f readiness/completion evidence remains historical and unchanged.

**Scope/interface:** create only `backend/src/quant/engine/research_runner.py`
and `backend/tests/engine/test_research_runner.py`. Doer never edits STATE.
No existing runner, BuyHold, helper, export, orchestrator, transport, storage,
API/CLI/worker/frontend/protected/dependency edits. Exact keyword-only public
signature, no defaults:

```text
run_research_buy_hold(*, active: ResearchInterval,
    warmup: ResearchInterval | None, required_warmup_observations: int,
    timeframe: str, calendar: str, anchor_ts: int,
    clocks: tuple[BarClock, ...], rows: Sequence[Mapping[str, object]],
    starting_balance_usdt: float, trade_size: str, deploy_pct: str,
    maker_fee: str, taker_fee: str) -> BacktestResult
```

Absolute imports of accepted interval/clock/coverage helper, BuyHold and existing
BacktestResult. Only BTCUSDT.BINANCE CASH NETTING, timeframe exactly `1d`,
calendar exactly `continuous_utc_fixed`, caller-supplied anchor. Unsupported
capabilities reject, no symbol/strategy inference or numeric defaults.

**Pre-engine admission:** validate all inputs before constructing BacktestEngine.
Recheck directly constructed interval/clock integer fields excluding bool.
Active start<end aligned to explicit daily grid. Required warmup count is
nonbool integer >=0; absent warmup requires zero; present warmup requires
positive count, valid aligned earlier [start,end), end<=active.start and complete
coverage at least that count. No inferred history; BuyHold has no indicator or
fitted state. A supplied gap is permitted without claiming 18.3 enforcement.

Join rows to clocks by unique row `ts` = clock `open_ts`, independently of
sequence order; reject duplicate keys and unequal keysets. Structural checks
on every row/clock: integer keys/clocks, grid alignment, close=open+86400000,
explicit available=close. Detached admitted snapshots sorted by unique open;
no caller mutation, coercion, deduplication or declaration repair. Select only
closes in active or explicitly declared warmup. Excluded earlier/sentinel/later
rows never reach engine; their OHLCV is ignored. Exact chronological admitted
active and warmup batches go to accepted validate_bar_coverage with explicit
`ts`, `close_ts`, `available_ts`; propagate helper errors/logs unchanged.

Admitted OHLCV must be finite int/float excluding bool, prices>0, volume>=0,
high>=max(open,close), low<=min(open,close), high>=low. Reject strings/Decimal
source prices. Reject prices not exactly representable at 2 decimal places and
volume not exactly representable at 6, checking decimal value via str(value);
trailing zeroes are harmless. Formatting serializes accepted precision only,
never rounds source values. Earliest admitted instrument open and all admitted
bar closes multiplied by 1000000 must fit [0,2**64-1] before engine creation;
pure accepted helpers retain signed/unbounded integer support. Cash is finite
positive float excluding bool and exactly whole USDT, an explicit capability
restriction matching copied Money construction, no rounding. Decimal-string
size/deploy/fees must be finite: size>0 exactly representable at 6 places,
deploy in [0,1], fees>=0; lexical errors become field-specific ValueError.
Adapter admission errors log once plus raise with precise field messages, no
payload dump; no wrapper logging for accepted helper errors.

**Runtime:** copy probed/existing builders and Bar API exactly, precision 2/6;
instrument timestamps earliest admitted open, bar ts_event=ts_init=verified
close*1000000. Only admitted Bars reach add_data. Existing engine.run() with
no boundary/streaming kwargs. Finally dispose across construction aftermath,
run and reports. Private _ResearchBuyHold retains inherited active action order.
At on_start and immediately before first active inherited on_bar, require empty
all-engine and instrument positions_open plus instrument orders_open/inflight
using exact proven expressions; query failure is unknown state and aborts.
Warmup returns without inherited trading/scoring. Unexpected callback membership
rejects; active inherited callback only [start,end). Check actual fill ts_event
inside active before inherited fill/snapshot replacement; no liquidation,
cancellation, new callback/query/accessor or engine lifecycle API.

Retain first callback Exception in private Python callback_error, re-raise;
later overridden callbacks must fail before action if retained. Wrap checks and
inherited on_start/on_bar/on_order_filled to retain failures, excluding
BaseException. Immediately after engine.run(), re-raise retained failure before
extraction even if engine dispatch logs/swallows. No successful fallback.
Installed actor.pyx handle_bar and strategy.pyx handle_event log then re-raise;
this inspection does not substitute for live public-run failure acceptance.
This guard uses Python state only and requires no new third-party API probe.
If implementation needs an unprobed call or documented runtime call fails,
STOP and report verbatim rather than adapt or assume this approval covers it.

**Result:** existing BacktestResult only, active snapshots/returns. Start returns
from exact configured cash at active.start, including first eligible close's
actual fill/fee effect. Ending balance is final scored snapshot. Independently
value latest account row per currency USDT cash+BTC*last eligible close; absent
required valuation rows fail loudly, no snapshot substitution. Preserve existing
raw fills/positions report patterns/timestamps, reset_index for IDs, last USDT
account_report shape. Disclose genuinely open residual positions, absent closure,
no fabricated liquidation or carry to next fresh call. Proven terminal queries
must reject nonzero open/inflight orders as unsupported; ending positions need
not be flat. No pending-order stop assumption or new result fields.

**Meaningful tests:** deterministic actual Nautilus engines/in-memory fixtures,
no data/DB/network. Shifted-anchor daily stage includes first prior-open bar,
start-inclusive/end-exclusive, no warmup and explicit complete/count warmup.
Spy actual add_data to assert sentinel/later never admitted. Different first/final
prices verify actual fill at active.start, first fee return, latest account cash
plus base valuation at last eligible price, genuine residual position and fresh
repeat calls. Radically vary excluded OHLC and warmup prices; independently
shuffle clock/row order; assert unchanged admitted results/event clocks, ignore
invalid excluded prices, inputs deep unchanged. Compare ordinary actual
run_backtest daily control clocks; existing tests untouched. Representative
pre-engine fail-if-called rejection cases cover missing/incomplete coverage,
join/duplicates, direct bool/invalid records, delay, malformed OHLCV, precision,
negative/overwide engine timestamps, unsupported tokens, fractional/nonfinite
cash and malformed/nonfinite size/deploy/fees; helper owns exhaustive matrices.

Inject nonempty/query failures during real on_start and first-active dispatch,
including warmup, and invalid fill time during actual fill dispatch. Assert
public function raises original failure, no submission after failed clean check,
no successful BacktestResult and disposal. Test terminal orders fail. A narrow
engine wrapper deliberately swallowing dispatched callback exception must still
fail via retained Python guard before extraction. These are mandatory acceptance
checks, not an already-observed successful propagation claim. No mock-only
success certification, hidden retries, weakened assertions or unused scaffolding.

**Implementation acceptance:** activate existing Linux venv, repository root:

```bash
python -m pytest backend/tests -q
python -m ruff check .
python -m mypy --strict backend/src
git diff --check
git status --short
```

Preserve complete outputs/failures/correction history, maximum five loops;
established command-only local TestClient socket permission, unchanged
options/plugins/proxy/TLS. No frontend changes/checks. One terminal two-file
implementation commit: `feat(engine): add bounded research buy-hold adapter (Phase 18.2g)`.
Fresh independent reviewer reruns every exact command before separate STATE
completion commit. Coordinator verifies authorized PR merge before fresh later
planning. This readiness changes only STATE, runs no implementation/suites,
installs/workers/fetch/push/merge/amend. No Python files changed;
pytest/ruff/mypy were not rerun under WORKFLOW §5.

**Readiness evidence:** AGENTS/STATE/WORKFLOW/REVIEWER/INCIDENTS, relevant
PROJECT §§1/2/4.1–4.3/4.5/5/6.0/Phases16–18/completion/AI rules, full approved
spec/probe and Nautilus/project/backend rules reviewed; actual runner/BuyHold
and installed callback error paths inspected. Clean branch
`phase18/18.2g-research-buy-hold`, baseline
`8b519e04fe676ef2be6d58bb047a92990177fd5e` (merged PR9). Independent live
`git ls-remote --heads origin main` returned that exact SHA, exit 0, inherited
proxy/TLS and command-only network permission preserved. Accepted probe
78250cd and completion 8b8c1c2 are ancestors (both exit 0). Runtime skill/network
policy inspected without credential values/configuration changes. Whole diff,
status and staged whitespace/scope checks precede separate STATE-only terminal
commit. Deviations from scratch draft: explicit no-rounding source precision,
engine UInt64 timestamp support and retained callback failure safeguard/tests,
all within delegated bounded scope; Linux commands replace historical Windows.

Only 18.2g is READY, next_task null, last_completed_task 18.2f,
human_transition_required false. Whole 18.2 remains incomplete, Phase 18
IN_PROGRESS, 18.3/18.4 NOT_STARTED. Supplied clock self-consistency/containment
cannot certify actual source availability/revision history, frozen selection,
dependency/gap eligibility, OOS contamination, realistic fills, provenance or
walk-forward guarantees. Source evidence transport/binding and caller integration
require later narrow contracts; none opened. No whole-phase claim; never Phase 29.

### 18.2f readiness contract and evidence

Independent readiness accepts only this Stage 1 contract. Baseline clean merged PR8 HEAD 7c8466f8ca3081b134022e9b28dc46c046c74893; remaining 18.2 NOT_STARTED. Only 18.2f is READY. Follow AGENTS/STATE/WORKFLOW, REVIEWER/INCIDENTS, approved phase-18 spec, relevant PROJECT contracts/Phases16–18, backend/project rules and Nautilus guide.

Goal: probe the NEW cache.positions_open call required for explicit clean research-stage state and trace actual bar/order/fill clocks with existing BuyHold construction. No production implementation, dependency changes, real-data writes, network download or eligibility claim. Sole repo deliverable docs/specs/phase-18-runtime-probe.md. Scratch source/logs under /tmp. orders_open/orders_inflight, engine.run(), strategy market/limit orders and reports already have repository patterns; copy them. Do not probe engine.run start/end/streaming or implement EMA/walk-forward behavior.

**Exact bounded probe**

Doer writes standalone /tmp/phase18f-runtime-probe.py. Print Python/Nautilus versions and baseline SHA; import success; inspect.signature and full docstring for actual live engine.cache.positions_open (print signature exception and docstring fallback for Cython). Print exact expressions/kwargs before live calls: positions_open() and positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE')). Query fresh engine before run, strategy.on_start and postrun before disposal. Alongside these, copy existing orders_open(instrument_id=...) and orders_inflight(instrument_id=...) to record clean and residual order state. Print return classes, counts, IDs and actual documented state/quantity fields. A query failure is not empty state; print full traceback and STOP new API path without silent substitution. No speculative additional filters.

Copy runner.py's existing engine/venue/CurrencyPair builder exactly: BTCUSDT.BINANCE NETTING CASH, explicit100000USDT, fees0.001, precision2/6. Existing Bar and Money/Price/Quantity APIs copied, not rediscovered. Four in-memory daily fixture bars: T=1735689600000 UTCms, D=86400000; closes T+D,T+2D,T+3D,T+4D, opens one D earlier, ts_event=ts_init=close*1000000, OHLC100/101/99/100, volume1000. Fixture active [T+2D,T+4D), first close warmup, last close end-exclusive sentinel. These numbers are scratch fixture choices, never experiment defaults.

Exactly two cases, fresh engine each, finally dispose:

1. Ordinary BuyHold control, all four bars, existing engine.run(). Scratch tracer subclasses BuyHold and preserves inherited action ordering. Trace monotonically numbered on_start, on_bar before/after, _submit_entry before/after, on_order_filled before/after and on_stop. Print bar/event ts_event/ts_init rawns and ms when present, order IDs where available, equity snapshot before/after. No new self.clock accessor or speculative event callbacks required. Record clean queries and terminal position/order queries. This observes unchanged same-bar fill/equity clocks and terminal residual position.
2. Scratch gated BuyHold: close<T+2D records warmup without inherited trading/snapshot; T+2D<=close<T+4D calls inherited on_bar; close>=T+4D records excluded sentinel without inherited trading/snapshot. Existing engine.run() still receives all fixture bars deliberately to expose callback gate capability. Record query state at active entry and terminal state, and assert zero warmup/sentinel entry submissions/scored snapshots and clean active-start state before first eligible order. Assert unchanged inherited active fill/snapshot clock. This is a scratch capability demonstration, not an approved runtime fix; sentinel reaching engine may still affect matching/valuation, and must be disclosed.

No third pending-limit case by default: orders queries and terminal market-order state are enough to establish clean-state call design. Only if two cases cannot reveal whether pending orders survive stop AND that behavior is necessary for proposed Stage2 disclosure, add one labeled passive limit case by copying EmaCross.order_factory.limit: quantity1, BUYprice1, post_onlyTrue, last eligible close submission, all lows99; print actual end state. Never cancel/liquidate or change fixture secretly to force outcome.

Dump full fixture, numbered traces, equity_snapshots, existing fills/positions/account report columns/types/index and full records for each case. Preserve original timestamps and guide conversions; absence is printed rather than inferred. Include terminal residual quantity and cash/base values with valuation at last eligible close; do not fabricate liquidation. No portfolio_returns reconstruction necessary. Unsupported findings and assertion failures remain verbatim; no claimed source-availability evidence.

**Execution, durable document and acceptance**

From repository root after existing venv activation:

```bash
source .venv/bin/activate
python /tmp/phase18f-runtime-probe.py > /tmp/phase18f-doer-probe.log 2>&1
```

Record exact exit code; no pipeline hides status. Doer creates durable doc containing complete fenced source and complete raw stdout/stderr verbatim (no truncation), command/version/baseline, all failures/corrections, observed state/event order and exact working positions_open calls. /tmp references are supplemental. Chat handoff is compact: paths, exit code, key findings, failures; do not print entire log into chat. No repo Python test added because sole repo artifact is documentation.

Document proposes only a concrete bounded future research-only interface: explicit active range + warmup declaration + verified clock rows; pre-engine filtering feeds permitted warmup/active rows and never an end-exclusive sentinel; scratch demonstrates strategy warmup gate suppressing submissions/scoring; new engine queries proven positions_open plus existing orders queries enforce fresh clean state; residual positions disclosed at last eligible price. Ordinary runner path and timestamps preserved. Exact Stage2 signatures/calls are recommendations, derived from observations; no approval invented. Source availability transport/policy remains a separate contract task. No numeric defaults or global guarantees.

Independent reviewer extracts the exact fenced source to /tmp/phase18f-review-runtime-probe.py and replays from root:

```bash
source .venv/bin/activate
python /tmp/phase18f-review-runtime-probe.py > /tmp/phase18f-review-probe.log 2>&1
git diff --check
git status --short
```

Record every exit and complete replay output; compare causal clocks, query counts/states and report outcomes, explicitly identifying variable IDs/durations without hiding raw logs. Verify only declared doc changed and probe produced no data/repo mutation. Replay failure returns to doer, no secret fixes; preserve correction history/five-loop limit. No backend/scripts/frontend changes: pytest/ruff/mypy/frontend checks skipped under WORKFLOW§5. Independent replay is mandatory.

One doer terminal commit: docs(engine): record research runtime probe (Phase 18.2f). After independent documentation acceptance reviewer commits STATE separately:18.2f COMPLETE, remaining18.2 NOT_STARTED, next_tasknull, human_transition_requiredtrue pending explicit post-probe approval. Coordinator may publish authorized docs PR; auto-merge authority does not approve unseen third-party implementation. WORKFLOW§2 'Report everything verbatim. STOP. Human approves.' applies to NEW positions_open call; REVIEWER§4 existing-pattern exception covers copied constructors/orders/reports/run(), not that new call. Present exact proven query call and bounded Stage2 proposal for human approval before implementation. No full18.2/Phase18 completion or later phase opened.

**Independent readiness evidence (2026-10-03):** full AGENTS, STATE,
WORKFLOW, REVIEWER, INCIDENTS and confirmed Phase 18 spec read; relevant
PROJECT architecture/data/extraction/execution/conventions, Phases 16–18,
completion and AI rules, project/backend rules and Nautilus guide inspected.
Actual runner/BuyHold and existing EmaCross instrument-filtered orders query
patterns inspected. Positions queries are NEW and unverified: no initial
capability, documented field, empty-state, fill ordering or terminal-state
outcome is claimed before the live probe. Missing fields are printed rather
than invented; expected assertions that fail are retained with traceback and
STOP, not repaired silently. Exactly two cases are authorized by default;
any necessary passive-case exception must first be explained to coordinator,
including why the two cases are insufficient. No new clock accessor.

Clean phase18/18.2f-runtime-probe at exact baseline above verified with
status and log. Accepted implementation c1eefaec202c0c5a7c0162dd786b4fc8ff14df99
and completion 9a94df6 are ancestors (each command exit 0). Independent live
`git ls-remote --heads origin main` returned exactly
`7c8466f8ca3081b134022e9b28dc46c046c74893 refs/heads/main`, exit 0,
with command-only network grant and inherited proxy/TLS preserved.
Cloud runtime skill and supported current enforced network policy inspected;
no credential values or configuration changes. This is point-in-time merged
prerequisite/connectivity evidence, not future publication or freshness.

Only STATE changes in this separate terminal readiness commit. Whole diff,
status and staged whitespace/scope checks run before commit. No Python files
changed; pytest/ruff/mypy were not re-run under WORKFLOW §5. No frontend
files changed, so no frontend checks. Mandatory independent exact-source
probe replay remains required for future documentation acceptance. No probe,
implementation, install, data write, worker, fetch, push, merge or amend by
readiness reviewer. Supplemental /tmp/phase18f-plan.md has a premerge local
baseline; this durable contract explicitly records the verified merged baseline.
No semantic deviation required. Last completed task remains 18.2e; current
18.2f READY only, next_task null, Phase 18 IN_PROGRESS and 18.3/18.4
NOT_STARTED. Existing evidence unchanged. Neither this readiness nor authorized
future PR auto-merge grants unseen Stage 2 approval. WORKFLOW §2 states:
"Report everything verbatim. STOP." and "Human approves. Adjust Stage 2
based on what the probe found." After independent probe acceptance, separate
completion STATE commit must set remaining 18.2 NOT_STARTED, next_task null,
human_transition_required true pending that explicit human approval. No full
runtime eligibility, availability, gaps, selection, provenance or walk-forward
claim is accepted; never begin Phase 29.

### 18.2f completion evidence

```yaml
task_id: 18.2f
status: COMPLETE
reviewer_decision: accepted_stage1_documentation_and_scratch_observations_only
reviewer_date: 2026-10-03
files_changed:
  - docs/specs/phase-18-runtime-probe.md
tests_added_or_updated:
  - exact standalone two-case scratch source with live clean-state and clock assertions
  - no repository Python test; sole implementation artifact is documentation
acceptance_commands:
  - source .venv/bin/activate
  - python /tmp/phase18f-review-runtime-probe.py > /tmp/phase18f-review-probe.log 2>&1
  - git diff --check
  - git status --short
  - git diff 59257d1 78250cd --check
  - git diff-tree --no-commit-id --name-only -r 78250cd
acceptance_output:
  probe: "CASE PASS (ordinary); CASE PASS (gated); PROBE PASS; exit 0"
  diff_check: "no output; exit 0 (clean working tree)"
  status: "no output; clean before STATE update; exit 0"
  committed_diff_check: "exit 2; 12 trailing-whitespace diagnostics, all inside verbatim raw-output fences; authorized exception, not green"
  changed_paths: "docs/specs/phase-18-runtime-probe.md; exit 0"
git_commit_sha: 78250cd5af871c065cf96c186f95432d9227d36e
readiness_commit_sha: 59257d113f1649138c6d768fb4ba392bfb6c7189
readiness_baseline_sha: 7c8466f8ca3081b134022e9b28dc46c046c74893
next_task: null
remaining_18_2_status: NOT_STARTED
human_transition_required: true
deviations:
  - "Authorized float representation correction only: math.isclose against independently reported cash plus base valuation, abs_tol=1e-8, rel_tol=0; original attempt 1 exit 1 retained."
  - "Authorized transcript-inherent trailing-space exception only for raw output fences; authored extra EOF blank line removed, initial diagnostics retained verbatim."
notes: |
  Independent reviewer inspected startup/state/workflow/reviewer/incidents,
  relevant PROJECT contracts and Phases 16–18, confirmed temporal spec,
  project/backend rules, Nautilus guide, bounded plan, committed document,
  actual BuyHold and runner construction/report patterns. Serial READY,
  doer IN_PROGRESS, committed ACCEPTANCE_PENDING and independent COMPLETE
  handoffs are recorded here; doer did not edit STATE or self-accept.
  Corrected source was extracted byte-for-byte from the complete replay-target
  fence to /tmp/phase18f-review-runtime-probe.py. Exactly one independent replay
  from repository root with existing venv passed, without source edits,
  substitution, retries, production fixes, dependency installs or data writes.
  Complete raw reviewer stdout/stderr remains /tmp/phase18f-review-probe.log
  (103501 bytes, 1301 lines). Baseline printed by this replay is doer commit
  78250cd5af871c065cf96c186f95432d9227d36e, versus readiness SHA in doer runs.
  Runtime UUIDs/event IDs, PID, wall-clock log timestamps, durations and memory
  observations vary; original raw logs are retained without normalization.
  124 causal/query/snapshot/outcome/report-timestamp lines match doer exactly.
  Both proven calls are engine.cache.positions_open() and
  engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE')).
  Live signature/docstring succeeds on Python 3.12.14/NautilusTrader 1.231.0.
  Fresh/on_start queries are all zero; gated active-start queries are all zero
  before the first eligible submission. Terminal positions calls each return
  one open LONG quantity 1 BTC; copied orders_open/orders_inflight return zero.
  Ordinary snapshots occupy all four closes; entry/fill is 1735776000000 ms.
  Gated snapshots occupy only 1735862400000 and 1735948800000 ms; entry/fill is
  1735862400000 ms. Numbered trace order and same-bar snapshot replacement
  match inherited BuyHold. Global exact timestamp/submission/fill assertions
  meaningfully check exclusions; the local unchanged-list guard is redundant
  and is not relied on as independent evidence. Latest USDT cash 99899.9 plus
  BTC 1.0 valued at last eligible price 100 equals 99999.9, independently from
  account rows; snapshot 99999.90000000001 agrees within absolute tolerance.
  Report columns/types/index/records preserve timestamps, IDs, fill commission
  0.10000000 USDT and genuinely open residual position without liquidation.
  Complete corrected source, original attempt1 source/log and attempt2 log
  each byte-match durable document fences and their retained /tmp originals.
  Original assertion failure is disclosed, not hidden by corrected success.
  Supplemental raw checks: /tmp/phase18f-review-diff-check.log,
  /tmp/phase18f-review-status-before.log and
  /tmp/phase18f-review-committed-diff-check.log. Committed whitespace flags are
  lines 958,990,1585,1617,2507,2539 (pandas header padding) and
  2661,2663,2665,2667,2669,2671 (retained diagnostic rows), exclusively inside
  verbatim text output fences. No source/prose trailing whitespace or EOF
  defect remains. Initial staged check exit 2 and its removed authored EOF
  defect remain disclosed; committed check exit 2 is not reported as passing.
  Only declared document changed in doer commit; checkout clean before STATE.
  No Python/frontend files changed; pytest/Ruff/mypy/frontend checks skipped
  under WORKFLOW §5; mandatory independent scratch replay was performed.
  Both scratch engines deliberately received all four bars including sentinel;
  gated callback suppression proves no pre-engine boundary enforcement or
  immunity to later matching/valuation. Flat prices conceal price effects.
  Pending-order survival is unproven and not required by the proposal. No
  actual source-availability, eligibility, realistic fills, causal EMA warmup,
  gap, selection, OOS contamination, provenance or walk-forward guarantee.
  Future explicit research-only interface/pre-engine filtering/clean-state
  query design remain recommendations, not production approval. WORKFLOW §2
  requires explicit post-probe human approval for NEW positions_open use.
  No Stage 2, push, PR, merge, worker or future readiness by this reviewer.
  Separate STATE-only completion preserves all prior readiness/evidence;
  remaining 18.2 NOT_STARTED, next_task null, human_transition_required true,
  18.3/18.4 NOT_STARTED, Phase 18 IN_PROGRESS. Never begin Phase 29.
```

### 18.2e readiness contract and evidence

Independent readiness reviewer accepts this exact bounded contract under
phase18-temporal-v1 ST-01, TW-03, EN-01/EN-02/EN-04/EN-05 and SC-03/SC-04.
Supplemental plan: /tmp/phase18e-plan.md; this durable contract stands alone.
Goal: recheck direct/queued execution declarations with the accepted raw
factory before any bar, engine or artifact action. Implementation changes only
backend/src/quant/engine/orchestrator.py and
backend/tests/engine/test_orchestrator.py. No helper, runner, worker, API, CLI,
storage, frontend, dependency, protected-file or STATE implementation edits.

Exact production change: add absolute import
quant.engine.temporal.validate_research_declaration. Immediately after the
execute_run docstring, before venue resolution, call the factory with this
explicit dictionary and discard its return:

```python
    validate_research_declaration({
        "research_stage": record.research_stage,
        "in_sample_start_ts": record.in_sample_start_ts,
        "in_sample_end_ts": record.in_sample_end_ts,
        "validation_start_ts": record.validation_start_ts,
        "validation_end_ts": record.validation_end_ts,
        "oos_start_ts": record.oos_start_ts,
        "oos_end_ts": record.oos_end_ts,
    })
```

Read exactly these seven existing top-level values without conversion. No
asdict, vars, params mapping, copied predicates, normalization, coercion,
active-range fallback, exception wrapping or extra logger call. Actual
RunRecord is a plain unslotted dataclass; explicit mapping is a scope choice
that avoids unrelated payload traversal, not a slots requirement. Coordinator
accepted correction of the temporary unapproved plan's mistaken slots rationale
before implementation; no production contract or authoritative spec changed.
Directly constructible invalid raw stages and bool/string endpoints must reach
the real factory unchanged. Invalid research declaration intentionally becomes
the first runtime failure, before venue/timeframe/universe validation. Factory
emits one quant.engine.temporal ERROR and its same ValueError propagates.
Valid and null-stage declarations retain subsequent existing failure priority
and ordinary execution behavior. No DB write or status transition is added;
callers retain existing failure handling.

Focused tests use dataclasses.replace on existing _make_record fixtures:

- Representative missing required IS/OOS, partial inactive pair, equal/reversed
  interval, chronological overlap, raw bool/string endpoint and invalid raw
  stage. Assert exact factory message, single temporal ERROR, unchanged input
  record and no artifact directory. Patch read_bars_json, fingerprint_bars,
  run_backtest, extract_equity, extract_metrics and write_artifacts with
  fail-if-called guards proving rejection precedes those actions.
- Competing invalid research plus venue/timeframe/universe proves declared
  first-failure priority. Valid and null declarations with existing invalid
  params/universe preserve the subsequent established venue/timeframe/universe
  priority. Use the real factory, not a mocked validation result.
- Actual execute_run integration through existing tmp_path DuckDB and
  Nautilus/artifact patterns: exploration without formal IS, validation,
  OOS with and without validation, touching endpoints. Exact top-level metadata,
  params and execution timestamps survive in returned RunRecord, all existing
  artifact files are produced, and input record remains unchanged. Deliberately
  distinct execution/research ranges prove no containment enforcement claim.
- Null-stage partial/reversed/overlapping metadata executes unchanged through
  actual engine/artifact path. Preserve all existing tests/assertions; avoid
  duplicating exhaustive 18.2a matrices, new dependencies or new third-party
  signatures. Raw malformed construction tests need no production typing change.

Probe: no new third-party API/signature/event behavior. Production adds only
an existing internal pure helper and explicit stdlib dict; integrations copy
existing test patterns. REVIEWER section 4 permits existing-pattern/stdlib
probe exclusion. New future Nautilus APIs require WORKFLOW section 2 Stage1
import/signature/docstring/live probes, verbatim report, STOP and post-probe
human approval before implementation.

Implementation acceptance: activate existing Linux venv and run from repo root
exactly:

```bash
python -m pytest backend/tests -q
python -m ruff check .
python -m mypy --strict backend/src
git diff --check
git status --short
```

Preserve verbatim failures and corrections, maximum five loops. Full pytest
uses established command-only permission for local TestClient sockets, leaving
options/plugins/proxy/TLS unchanged. No frontend change, so no frontend checks.
One terminal implementation commit:
feat(engine): recheck research declarations before execution (Phase 18.2e).
Doer never edits STATE or publishes/merges. Fresh independent acceptance
reviewer reruns every exact command and commits STATE separately, accepting
only runtime declaration recheck. Coordinator may publish the authorized task
PR/auto-merge after acceptance and verifies merged remote before fresh planning.
No following task is opened by this READY contract.

**Independent readiness evidence:** full AGENTS/STATE/WORKFLOW/REVIEWER/
INCIDENTS/spec, required PROJECT sections and applicable project/backend rules
reviewed; actual RunRecord, helper/helper tests, orchestrator/orchestrator tests
and routed Nautilus guide inspected. Clean branch
phase18/18.2e-runtime-declarations at
 aad2607fbb21c3de4c77e0c3b993dbe4e3764aeb agrees with accepted 18.2d.
Independent live git ls-remote --heads origin main returned exactly
 aad2607fbb21c3de4c77e0c3b993dbe4e3764aeb refs/heads/main, exit 0, using
command-only network grant with inherited proxy and TLS verification preserved.
Accepted CLI implementation fc0d2e2b6685e3c5627210042bde429583b683ba and
completion 22a30551a5d9de3482b06ce72bc541ebcb1e062d are ancestors (each exit 0);
accepted 73f81f0, b9a25ee and 9049d6a also are ancestors (each exit 0).
This verifies present merged prerequisites/connectivity, not future freshness.
Cloud runtime/network policy inspected without credential values or changes.

Only STATE changes in this separate terminal readiness commit. Whole diff,
status, staged whitespace/scope and exact baseline checked before commit.
No Python files changed; pytest/ruff/mypy were not rerun under WORKFLOW section
5 path-scoped acceptance. No implementation, installs, workers, fetch, push,
merge or amend occurred. Deviation: factual unapproved plan rationale corrected
as disclosed above; existing Linux Bash venv and command-only local socket
grant replace historical Windows examples without command/options changes.
Last completed task remains 18.2d; current_task is only 18.2e READY, next_task
null. All prior evidence remains unchanged. Whole 18.2 stays incomplete,
18.3/18.4 NOT_STARTED, Phase 18 IN_PROGRESS. No execution containment, coverage,
availability, causal warmup, boundary-state, gaps, selection freezing,
provenance, OOS contamination or walk-forward guarantee is accepted. A runtime
declaration check is not full runtime eligibility. Never begin Phase 29.

### 18.2e completion evidence

```yaml
task_id: 18.2e
status: COMPLETE
reviewer_decision: accepted_runtime_raw_declaration_recheck_only
reviewer_date: 2026-10-03
files_changed:
  - backend/src/quant/engine/orchestrator.py
  - backend/tests/engine/test_orchestrator.py
tests_added_or_updated:
  - 20 focused cases using the real declaration factory and existing fixtures
  - nine raw rejection cases with exact error and single temporal ERROR before six guarded actions
  - six valid/null-stage cases preserve existing venue/timeframe/universe failure priority
  - five actual DuckDB/Nautilus/artifact paths preserve metadata, params and execution clocks
acceptance_commands:
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - python -m pytest backend/tests -q
  - git diff --check
  - git status --short
acceptance_output:
  ruff: "All checks passed!; exit 0"
  mypy: "Success: no issues found in 32 source files; exit 0"
  pytest: "899 passed, 91 warnings in 36.27s; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer state update; exit 0"
git_commit_sha: c1eefaec202c0c5a7c0162dd786b4fc8ff14df99
readiness_commit_sha: 054186409fca12aa64d6f26579ea1eeefb9019e3
readiness_baseline_sha: aad2607fbb21c3de4c77e0c3b993dbe4e3764aeb
next_task: 18.2
next_task_status: NOT_STARTED
human_decisions: confirmed
human_transition_required: false
deviations:
  - "Existing Linux Bash venv activation and command-only local TestClient socket network grant replace Windows examples; exact options/plugins/proxy/TLS unchanged."
notes: |
  Serial READY proceeded through doer implementation (IN_PROGRESS), committed
  handoff (ACCEPTANCE_PENDING), and fresh independent acceptance (COMPLETE).
  Doer did not edit STATE or self-accept. Reviewer read full AGENTS/STATE,
  WORKFLOW/REVIEWER/INCIDENTS/spec, required PROJECT/rules and Nautilus guide,
  corrected /tmp/phase18e-plan.md and /tmp/phase18e-doer-report.md, actual
  complete two-file diff, factory, RunRecord and established engine clocks.
  Exact seven-field dict reads raw top-level values immediately after docstring
  and before params/venue; return discarded, no mutation/coercion/normalization,
  fallback, catch/rethrow or extra logging. Invalid declarations intentionally
  outrank venue/timeframe/universe; same factory ValueError propagates unchanged.
  Rejection guards cover bars, fingerprint, engine, equity, metrics and artifacts;
  no artifact directory/database appears and record remains unchanged.
  Actual integrations retain all five artifacts and independently enumerated
  inclusive execution price-open and equity-close sequences. Null-stage partial,
  reversed and overlapping metadata executes unchanged. Research bounds differ
  from execution bounds, expressly demonstrating absence of containment checks.
  Prior test assertions are unchanged; production adds exactly one absolute
  import and accepted raw call. No helper/runner/worker/API/CLI/storage/frontend,
  dependency or protected-file edits occurred. Existing-pattern/stdlib probe
  exclusion under REVIEWER section 4 applies; no new third-party signature.
  Every exact whole-tree command independently passed on first invocation.
  Raw logs remain /tmp/phase18e-review-ruff.log, -mypy.log, -pytest.log,
  -diff-check.log and -status-before.log (same phase18e-review prefix).
  Full pytest used command-only network permission for local TestClient sockets,
  inherited proxy/TLS/options/plugins preserved. Existing Starlette httpx and
  Pandas Timestamp.utcnow categories account for 91 warnings, including ten
  added warnings from five actual engine integrations. Doer likewise reported
  899 passed, 91 warnings on first invocation (40.42s); logs were inspected.
  No failed acceptance, retry, hidden fix, implementation/test edits, installs,
  workers, amend, push or merge by reviewer. Cloud runtime skill/policy inspected
  without secret values or configuration changes. No frontend checks because
  no frontend change. Branch phase18/18.2e-runtime-declarations, exact task and
  readiness parent, clean checkout and merged PR7 baseline ancestor verified.
  This is local acceptance; coordinator handles authorized PR publication and
  merge after GitHub checks, then independently verifies merged remote freshness.
  Inherited helper docstring still says no caller wired; actual callers were
  inspected and that already-recorded stale comment is outside two-file scope.
  Runtime declarations certify no actual eligibility, execution containment,
  availability/coverage, causal warmup, boundary state, gaps, frozen selection,
  provenance, OOS contamination or walk-forward guarantee. Whole 18.2 remains
  incomplete and current_task 18.2 NOT_STARTED identifies remaining planning
  only; next_task null, 18.3/18.4 NOT_STARTED, Phase 18 IN_PROGRESS. No other
  READY task, future split or phase crossing is opened; never begin Phase 29.
  All prior readiness and completion evidence is preserved unchanged.
```

### 18.2d readiness contract and evidence

Independent readiness reviewer accepts the following exact bounded contract.
The supplemental plan is `/tmp/phase18d-plan.md`; the durable contract here
stands independently of that temporary artifact.

Goal: EN-01 admission parity with accepted raw declaration factory, ST-01/TW-03/EN-02/SC-03/04. Only scripts/run_backtest.py and backend/tests/test_run_backtest.py change. No STATE/protected/dependency/storage/API/engine/helper changes. No runtime eligibility claim.

Exact production change:

- Add absolute import quant.engine.temporal.validate_research_declaration.
- In main(), immediately after the existing successful execution timestamp parse try/except and before symbol/name/path resolution, UUID, git capture, schema creation, RunRecord, execution or persistence, add a separate try: validate_research_declaration(vars(args)); except ValueError as exc: print(exc, file=sys.stderr) with existing noqa T201 convention; sys.exit(2). Discard factory return. Do not modify args, infer active execution bounds, normalize/reorder ranges or catch broad exceptions. vars(args) supplies the exact parsed Namespace mapping; argparse's established integer lexical conversion remains intact. Missing stage is None and factory returns early without inspecting endpoints.
- Change only the research-stage help text from misleading 'metadata only' to 'declaration checks only; runtime eligibility unverified'. All flags, choices, defaults, parser types and inclusive execution timestamp help remain unchanged.

Error behavior: argparse retains stage/lexical-int rejection and exit 2. Existing timeframe validation remains before execution timestamp validation, which remains before declaration validation; if these pass, helper's existing first-failure order/message is authoritative. Factory emits exactly one quant.engine.temporal ERROR; CLI writes that same message plus newline to stderr, exit 2, no CLI logging/rethrow/wrapper. No success run/artifact/metrics stdout on rejected declarations. No UUID/git/schema/execute/insert side effect. Configure_logging and config.repo_root already occur earlier and stay unchanged. Valid and ordinary paths otherwise retain existing persistence/output.

Focused meaningful CLI main() tests, using established importlib fixture, argv monkeypatch and tmp_path SQLite, real factory and argparse:

- Representative missing required IS/OOS, partial inactive range, equal/reversed range, chronological overlap, and one competing-invalid declaration proving exact helper precedence. Assert exact SystemExit(2), stderr factory message, one matching temporal ERROR, no success stdout, no created runs DB/artifact path; replace UUID generation, git capture, init_runs_schema, execute_run and insert_run with fail-if-called spies to prove early rejection. Keep configure_logging disabled for caplog.
- Valid exploration without formal IS, validation with IS/validation, OOS with and without validation, touching boundaries; verify actual main -> RunRecord -> isolated SQLite persistence with execute_run stub inspecting exact top-level metadata outside params and execution start/end preserved (not forcibly equal to active range). Existing metadata persistence test remains unchanged.
- Ordinary absent-stage partial/reversed/overlapping integer ranges continue through main and persist unchanged, without temporal error. Signed/zero/large integer fixture demonstrates no admission bounds added; choose SQLite-representable ints for persistence, since arbitrary huge ints are factory-only and SQLite limits are unchanged.
- Parser's existing three invalid-metadata tests stay unchanged; add one lexical fractional endpoint case if needed to show argparse rejects before admission. Add invalid-timeframe/invalid-execution-timestamp plus invalid-research combinations to verify established error priority and no database side effects. Avoid exhaustive endpoint type/stage/overlap matrices already owned by 18.2a, fabricated raw Python values impossible in argv, redundant mocks of factory, test weakening or new dependencies.

Probe: production adds only stdlib Namespace mapping access and an accepted internal pure helper call. No new third-party API calls or Nautilus behavior; existing test SQLite/pytest patterns copied. WORKFLOW §2 third-party Stage1 probe does not apply here. Future runner/extraction changes using new Nautilus APIs require Stage1 import/signature/docstring/live probes, verbatim report, STOP and human approval before implementation.

Acceptance: activate existing Linux venv, from repository root run exactly:

```bash
python -m pytest backend/tests -q
python -m ruff check .
python -m mypy --strict backend/src
git diff --check
git status --short
```

Preserve complete failures/correction history under five-loop limit. Full pytest requires established command-only network permission for local TestClient sockets, unchanged proxy/TLS/options/plugins. No frontend files change, so frontend checks not required. One terminal implementation commit: feat(cli): validate research declarations before execution (Phase 18.2d). Doer never edits STATE or publishes/merges. Fresh independent reviewer reruns every command, accepts only CLI declaration admission, commits STATE separately. Coordinator publishes task PR after acceptance and verifies merge before fresh next-task planning. User has authorized task PRs/auto-merge; repository setting availability is a separate publication constraint.

**Independent readiness evidence:** reviewed full AGENTS, STATE, WORKFLOW,
REVIEWER, INCIDENTS, confirmed phase-18 spec, relevant PROJECT sections and
applicable rules; inspected actual CLI/tests, accepted temporal helper/tests,
and relevant persistence/read/orchestrator/runner paths. Clean branch
`phase18/18.2d-cli-declarations` at
`812c059f320a395344005ffc4b5671c2b58b4f38` agrees with recorded accepted 18.2c.
Independent live `git ls-remote --heads origin main` returned exactly
`812c059f320a395344005ffc4b5671c2b58b4f38`, exit 0, with command-only network
grant and preserved proxy/TLS. Accepted task commits 73f81f0, b9a25ee and
9049d6a are ancestors. This verifies present merged prerequisites/connectivity,
not future freshness or publication. No fetch, dependency install, implementation,
worker, push, merge or amend occurs in this readiness review.

Only STATE changes in this separate terminal readiness commit. No Python files
changed; pytest/ruff/mypy were not rerun under WORKFLOW section 5. Whole diff,
status, staged whitespace/scope and exact baseline checks precede commit.
Deviation: existing Linux Bash venv and command-only local socket grant replace
historical Windows examples, preserving exact acceptance commands/options/plugins.
No semantic or production-scope deviation was required. Last completed task
remains 18.2c; current_task is only 18.2d READY and next_task null. Prior evidence
is preserved. 18.3/18.4 stay NOT_STARTED; whole 18.2 and Phase 18 remain incomplete.
No runtime eligibility, availability, coverage, warmup, gap, freezing, provenance,
OOS contamination or walk-forward guarantee is accepted; never begin Phase 29.

### 18.2d completion evidence

```yaml
task_id: 18.2d
status: COMPLETE
reviewer_decision: accepted_cli_declaration_admission_only
reviewer_date: 2026-10-03
files_changed:
  - scripts/run_backtest.py
  - backend/tests/test_run_backtest.py
tests_added_or_updated:
  - 19 focused CLI main admission, persistence, priority and help cases
  - exact exit 2, stderr and single temporal ERROR before UUID/git/schema/execute/insert
  - valid exploration/validation/OOS and touching signed/zero/large integer ranges
  - ordinary partial/reversed/overlapping ranges and unchanged execution timestamps
  - actual isolated SQLite top-level metadata, exact params and success output
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - git diff --check
  - git status --short
acceptance_output:
  pytest: "879 passed, 81 warnings in 40.46s; exit 0"
  ruff: "All checks passed!; exit 0"
  mypy: "Success: no issues found in 32 source files; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer state update; exit 0"
git_commit_sha: fc0d2e2b6685e3c5627210042bde429583b683ba
readiness_commit_sha: 911c2fd6d312eb01581412f65ccfbec65e5c6b47
readiness_baseline_sha: 812c059f320a395344005ffc4b5671c2b58b4f38
next_task: 18.2
next_task_status: NOT_STARTED
human_decisions: confirmed
human_transition_required: false
deviations:
  - "Existing Linux Bash venv activation and command-only TestClient socket network grant replace historical Windows examples; options/plugins/proxy/TLS unchanged."
notes: |
  Serial READY proceeded through doer implementation (IN_PROGRESS), committed
  handoff (ACCEPTANCE_PENDING), and fresh independent acceptance (COMPLETE).
  Doer did not edit STATE or self-accept. Reviewer read full AGENTS/STATE,
  WORKFLOW/REVIEWER/INCIDENTS/spec, relevant PROJECT/rules, exact supplemental
  /tmp/phase18d-plan.md and /tmp/phase18d-doer-report.md and actual two-file
  diff. Previous test assertions are unchanged. Exact accepted helper call
  validates vars(args) after execution timestamp parsing and before paths,
  UUID/git/schema/RunRecord/runtime/persistence. Return is discarded, only
  ValueError is caught; no mutation, extra log, normalization or active-bound
  inference. Existing timeframe/timestamp/parser priorities remain intact.
  Real factory/argparse tests guard rejected run side effects and ordinary
  null-stage persistence; admitted execution times remain independent of ranges.
  All exact whole-tree commands passed on first independent invocation.
  Full outputs remain /tmp/phase18d-review-pytest.log, -ruff.log, -mypy.log,
  -diff-check.log and -status-before.log (same phase18d-review prefix).
  Full pytest used command-only local TestClient socket network permission,
  preserving inherited proxy/TLS/options/plugins. Existing warnings concern
  Starlette httpx and Pandas Timestamp.utcnow. No reviewer implementation/test
  edits, retries, installs, workers, amend, push or merge. Doer initial Ruff
  E501 (99 > 88) is preserved in /tmp/phase18d-doer-ruff-1.log and inspected;
  help literal wrapping alone corrected it in two bounded cosmetic cycles.
  Doer startup reads first used incorrect cwd then succeeded before edits;
  no hidden behavioral correction or test failure is reported or observed.
  Verified exact task/readiness parent, branch phase18/18.2d-cli-declarations,
  clean checkout, two implementation paths and main baseline ancestor.
  This is local acceptance, not remote publication/merge or future freshness
  evidence. Coordinator handles authorized task PR publication and merge.
  CLI admission certifies no runtime eligibility, actual source availability
  or coverage, execution containment, causal warmup, gaps, frozen selection,
  provenance, OOS contamination or walk-forward guarantee. Earlier logging and
  config root lookup remain; no claim of zero startup activity is made.
  Accepted helper's stale unwired-caller docstring is inherited and outside
  this two-file task; actual API/CLI callers were inspected, not inferred from it.
  Whole 18.2 remains incomplete; current_task 18.2 NOT_STARTED identifies
  remaining planning only, next_task null, 18.3/18.4 NOT_STARTED and Phase 18
  IN_PROGRESS. No future READY split or phase crossing is opened; never begin
  Phase 29. All prior readiness and completion evidence is preserved.
```

### 18.2c readiness contract and evidence

Independent readiness review accepts this bounded contract under
`phase18-temporal-v1` ST-01, TW-01/TW-03, EN-01/EN-02/EN-04/EN-05 and
SC-03/SC-04. Only `backend/src/quant/api/schemas.py` and
`backend/tests/api/test_schemas.py` may change in implementation. No fields,
defaults, nullability, Literal values, extra-forbid policy, JSON schema shapes,
execution timestamps, transport, dependencies, protected files or other callers
change. Doer never edits STATE.

**Exact interface:** import `collections.abc.Mapping`, Pydantic
`model_validator`, and absolute `quant.engine.temporal.validate_research_declaration`.
At RunCreate's end, after trial_count and before KpiBlock, add only:

```python
    @model_validator(mode="before")
    @classmethod
    def validate_research_ranges(cls, data: Any) -> Any:
        """Check raw designated declarations before field coercion."""
        if isinstance(data, Mapping):
            validate_research_declaration(data)
        return data
```

Original mapping is passed/returned unchanged; factory result is discarded.
No RunSummary/base validator, normalization, catch/rethrow, added logging,
assignment validation, revalidation or from_attributes setting. Existing
18.2a messages and failure precedence remain authoritative: stage, supplied
IS/validation/OOS pairs/types/order, applicability, chronological nonoverlap.
Pydantic wraps helper ValueError as root loc (), type value_error and message
`Value error, ` plus exact factory message; temporal emits one matching ERROR.
Missing/null stage preserves ordinary field validation/coercion and permissive
range semantics; nonmapping inputs retain Pydantic handling. RunSummary remains
permissive historical metadata. Construction/copy bypasses and postcreation
mutation are outside admission guarantee.

**Focused tests:** retain existing assertions; valid all-stage applicability,
optional absent/null pairs, touching ranges and signed/zero/huge/subclass
integers. Across all six endpoint slots reject coercible bool/string/integral
float/Decimal before field conversion (24 cases). Representative stage,
required-range, pair, equal/reversed/order/inactive-range failures and precedence
exercise real models. Verify exact root error/log wrapping, clean successful
logs, constructor/mapping/JSON paths, JSON raw string/bool/float rejection,
unchanged dumps/top-level metadata and mapping/nested-params immutability.
Ordinary missing/null-stage partial/reversed/overlap and normal string/bool
coercion persist; noncoercible ordinary fields keep field errors. Historical
RunSummary incomplete/reversed/overlap acceptance, nonmapping errors and valid
model-instance defaults are explicit regressions. Existing factory suite owns
exhaustive payload/overlap matrices; do not duplicate it. Real POST tests in
this mirrored file copy established FastAPI/router/TestClient setup with
isolated tmp_path DB: invalid partial/order/string/bool declarations give 422
with existing default detail list and no row; valid designated and ordinary
null-stage cases give 201/queued with unchanged metadata. No weakened tests,
new dependencies, real data writes, random fixtures or redundant mock tests.

**Probe interpretation:** REVIEWER section 4 explicitly says
"It's a Pydantic model (schemas follow §4.4, no probing needed)"; this narrow
request-model validator qualifies for that specific exception to WORKFLOW
section 2's general third-party probe pattern. Existing FastAPI test patterns
are copied, with no new internals. Coordinator and independent reviewer accept
this interpretation under delegated routine choices; no post-probe human
approval is invented or required for this exempt model task. Supplemental
installed Pydantic 2.13.5 import/signature/docstring/live prototype succeeded
in /tmp/phase18c-pydantic-probe.py and .log; no installs.

**Evidence and limits:** reviewer inspected full startup/state/workflow/review/
incident/spec records, relevant project/rules, actual helper/schema/router/tests
and /tmp/phase18c-plan.md. Clean branch `phase18/18.2c-api-declarations` at
`7a1894db0166722e338c6d6edb2124f2f69a7ab4`; live
`git ls-remote --heads origin main` independently returned that same SHA,
exit 0, using command-only network permission and preserved proxy/TLS.
Accepted helper task commits 73f81f0 and b9a25ee are ancestors (exit 0).
This verifies merged prerequisite tree now, not future freshness/publication.
No Python/frontend files changed; acceptance suites are skipped for this
STATE-only readiness commit under WORKFLOW section 5. Whole diff/status/staged
whitespace/scope checks run before terminal commit. Prior evidence is preserved.
Request admission alone certifies no CLI/runtime enforcement, actual coverage,
availability, execution containment, warmup, gaps, freezing, provenance, OOS
contamination or walk-forward guarantees. Whole 18.2 and Phase 18 remain incomplete;
18.3/18.4 stay NOT_STARTED, no later task opens, never begin Phase 29.

**Implementation acceptance:** activate existing Linux venv; from repo root run
exactly `python -m pytest backend/tests -q`, `python -m ruff check .`,
`python -m mypy --strict backend/src`, `git diff --check`, `git status --short`.
Full pytest uses command-only network grant for local TestClient sockets with
options/plugins/proxy/TLS unchanged. Preserve full failures/correction history
under five-loop limit. One terminal task commit, only the two declared paths:
`feat(api): reject invalid raw research declarations (Phase 18.2c)`.
Independent reviewer reruns every exact command before separate completion
STATE commit. Coordinator creates task PR to main after acceptance; no doer or
readiness-reviewer push/amend/merge. Stop after this bounded task; subsequent
work waits for its PR merge and fresh readiness.

### 18.2c completion evidence

```yaml
task_id: 18.2c
status: COMPLETE
reviewer_decision: accepted_raw_api_declaration_admission_only
reviewer_date: 2026-10-02
files_changed:
  - backend/src/quant/api/schemas.py
  - backend/tests/api/test_schemas.py
tests_added_or_updated:
  - 68 focused raw request-model and real POST admission regressions
  - six endpoint slots reject bool/string/integral float/Decimal before coercion
  - exact root error and single temporal ERROR, precedence, applicability and immutable payloads
  - constructor/mapping/JSON paths, touching/signed/zero/huge/subclass integers
  - ordinary missing/null stage coercion and historical permissive summaries preserved
  - isolated POST 422 without inserted row and 201 queued metadata persistence
acceptance_commands:
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - python -m pytest backend/tests -q
  - git diff --check
  - git status --short
acceptance_output:
  ruff: "All checks passed!; exit 0"
  mypy: "Success: no issues found in 32 source files; exit 0"
  pytest: "860 passed, 81 warnings in 38.04s; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer state update; exit 0"
git_commit_sha: 9049d6af141b61785453443a3faaef8a811da751
readiness_commit_sha: d3827ca48595d47e84cce6e78c0cab1b8eeb776b
readiness_baseline_sha: 7a1894db0166722e338c6d6edb2124f2f69a7ab4
next_task: 18.2
next_task_status: NOT_STARTED
human_decisions: confirmed
human_transition_required: false
deviations:
  - "Existing Linux Bash venv activation and command-only socket grant replace historical Windows examples; acceptance options/plugins/proxy/TLS unchanged."
notes: |
  Serial READY task proceeded through doer implementation (IN_PROGRESS),
  committed handoff (ACCEPTANCE_PENDING), and fresh independent acceptance
  (COMPLETE). Doer did not edit STATE or self-accept. Reviewer read full
  startup/state/workflow/reviewer/incident/spec records, relevant PROJECT/rules,
  planner/readiness/doer reports, supplemental installed Pydantic probe and
  actual complete two-file commit. Exact Mapping before-validator passes and
  returns original data, discards factory result and adds no logging/rethrow.
  Existing fields/defaults/nullability/JSON schema shape and RunSummary are
  unchanged; no earlier test assertion was removed or weakened. REVIEWER4's
  explicit Pydantic model exception was independently accepted at readiness;
  copied established FastAPI test setup requires no new API internals.
  Every exact whole-tree command independently passed on its first invocation.
  Full outputs remain in /tmp/phase18c-review-ruff.log, -mypy.log, -pytest.log,
  -diff-check.log and -status-before.log (same phase18c-review prefix).
  Full pytest used required command-only network permission for TestClient
  sockets, with proxy/TLS/options/plugins preserved. Existing warnings concern
  Starlette httpx and Pandas Timestamp.utcnow. No installs, retries, code/test
  edits or hidden behavioral corrections by reviewer. Doer disclosed two
  precommit cosmetic Ruff failures (12 then 2 diagnostics); exact originals
  /tmp/phase18c-doer-ruff-1.log and -2.log remain preserved and were inspected.
  Verified clean phase18/18.2c-api-declarations at exact task/parent SHAs,
  only two declared changed paths and accepted helpers as ancestors. Live
  git ls-remote --heads origin main returned baseline 7a1894db0166722e338c6d6edb2124f2f69a7ab4,
  exit 0 before this separate STATE-only terminal commit. This is point-in-time
  prerequisite evidence, not publication, merge or future freshness evidence.
  Coordinator publishes the task PR to main after handoff; reviewer stops.
  Admission alone proves no CLI/runtime eligibility, actual coverage/source
  availability, execution containment, causal warmup, gaps, freezing, provenance,
  OOS contamination or walk-forward property. Model construction/copy bypasses
  and postcreation mutation are outside the admission guarantee. Whole 18.2
  remains incomplete; current_task 18.2 is NOT_STARTED remaining planning only,
  next_task null, 18.3/18.4 NOT_STARTED and Phase 18 IN_PROGRESS. No later READY
  split or phase crossing is opened. All readiness/prior evidence is preserved.
```

### 18.2b readiness contract and evidence

Fresh independent readiness review accepts only the following task contract.
Rule source: `docs/specs/phase-18.md`, `phase18-temporal-v1`, especially
TW-01/TW-02/TW-03/TW-05, IA-02 and EN-01/EN-02/EN-04/EN-05. The coordinator
accepted this conservative supported capability under the human's delegated
choices. Unsupported clocks fail closed rather than acquiring invented defaults.

**Scope:** create only `backend/src/quant/engine/bar_coverage.py` and
`backend/tests/engine/test_bar_coverage.py`. Production uses stdlib and an
absolute import of the accepted `quant.engine.temporal.ResearchInterval`.
No existing code, exports, schema, storage, ingestion, API, CLI, runner, worker,
frontend, fingerprint, protected file or dependency changes. Doer never edits
STATE. Direct record construction itself is unvalidated, as in 18.2a.

**Public interface:** frozen `BarClock(open_ts: int, close_ts: int,
available_ts: int)` and
`validate_bar_coverage(interval: ResearchInterval, *, timeframe: object,
calendar: object, anchor_ts: object, observations: Sequence[Mapping[str, object]])
-> tuple[BarClock, ...]`. Input containers obey their typed Sequence/Mapping
contracts; payloads are validated at runtime. Caller supplies the interval
explicitly, with no stage inference, active-range fallback or eligibility flag.

**Supported clock:** exact calendar token `continuous_utc_fixed` plus explicit
anchor; no venue/session/weekday/midnight/epoch-zero default. Exact canonical
fixed durations in UTC milliseconds: 1m=60000, 5m=300000, 15m=900000,
30m=1800000, 1h=3600000, 4h=14400000, 1d=86400000, 1w=604800000.
These established units match orchestrator.py; an identical local table avoids
importing its third-party execution dependencies. Session and calendar-month
clocks, 1mo/1M and all other unsupported tokens reject without normalization.
Week is an explicit elapsed duration anchored by the caller, not an exchange
weekday assumption. This is a helper input contract, not new persisted fields.

**Values and boundaries:** anchor and interval endpoints must be integers
excluding bool; benign int subclasses, signed/zero/unbounded integers are
preserved. No coercion, datetime bound or normalization. Revalidate interval
endpoints because ResearchInterval is directly constructible: start<end and
both endpoints congruent to anchor modulo duration. Each observation explicitly
supplies integer `ts` (established OPEN meaning), `close_ts`, `available_ts`;
missing/null evidence rejects. Open must align, close must equal open+duration,
and availability must explicitly equal close for this supported zero-delay
capability. Known delayed availability is unsupported, not silently shifted;
unknown availability cannot be inferred from opens, ingested_at or wall time.

**Exact coverage batch:** each close lies in [start,end), including start and
excluding end. Input contains exactly the active-stage batch, already ordered;
context/warmup/later observations reject, never filter/sort/deduplicate/repair.
All repeated opens reject, including equal records and conflicting extras;
strict chronological order is required. First close may have an open one
interval before start. Membership does not permit scoring earlier movement or
carrying exposure, positions, orders or returns. Empty batch rejects. With
expected_count=(end-start)//duration, require exact count after validating every
row. Aligned unique strictly ordered closes inside the aligned half-open grid
with exact count mathematically imply start,start+duration,...,end-duration.
Independent reviewer identified a redundant unreachable per-index mismatch
predicate in the draft plan; coordinator explicitly approved its removal before
implementation. No accepted inputs or observable errors change and no impossible
branch test is required. Use O(n) actual-row work/memory and arithmetic count,
never allocate or iterate a huge expected schedule or shorten an interval.
Return detached frozen records in a tuple; extra mapping values are ignored,
caller inputs untouched, repeated calls equal, later caller mutation harmless.

**Failure order:** calendar then timeframe; anchor/start/end types; strict
interval order; start then end alignment; each row in input order checks ts,
close_ts, available_ts types, open alignment, close equality, availability
equality, close membership, duplicate open, strict chronology. After all rows:
empty batch then complete count. A later malformed row outranks missing-count
failure; row-local types outrank duplicate/order. Every rejection logs exactly
one ERROR on this module's logger and raises ValueError with identical message;
valid calls emit no log. Do not serialize caller payloads or arbitrary objects.

Exact messages:

- `calendar must be continuous_utc_fixed`
- `timeframe must be one of 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w`
- `<field> must be an integer UTC epoch-millisecond timestamp (bool is not allowed)`
  for anchor_ts, interval.start_ts, interval.end_ts or observations[i].ts,
  observations[i].close_ts, observations[i].available_ts
- `interval.start_ts must be less than interval.end_ts`
- `interval.start_ts must align with the declared bar grid`
- `interval.end_ts must align with the declared bar grid`
- `observations[i].ts must align with the declared bar grid`
- `observations[i].close_ts must equal ts plus the declared timeframe duration`
- `observations[i].available_ts must equal close_ts for the supported clock`
- `observations[i].close_ts must be inside the half-open interval`
- `observations[i].ts duplicates an earlier observation`
- `observations must be strictly chronological`
- `observations must contain at least one stage observation`
- `observations do not provide complete expected bar coverage`

**Required tests:** independent fixtures for all eight durations with shifted
anchors and exact records; one-duration/start-inclusive/end-exclusive/shared
boundary membership; signed/zero/huge/subclass integers; unsupported tokens and
nonstrings; bool/float/string/Decimal/null/NaN/inf/object for all six timestamp
slots plus missing row fields; equal/reversed/misaligned intervals/opens;
incorrect/stretched closes; early/unknown/delayed availability; empty/missing
first/interior/last/partial batches; exact/conflicting duplicates, reversed order
and extra context rows; February/March monthly rejection; enormous interval
with small batch and no timing-based assertion; deterministic precedence,
single ERROR/value error and no payload leakage; mapping proxies/nested sentinels,
repeatability/caller mutation, tuple/frozen output. No random data, real data
writes, new dependencies, external services or weakened existing tests.
Every function needs meaningful public-path/direct coverage.

**Claim limits:** mechanically consistent supplied timestamps/calendar do not
certify source history, actual publication delays, point-in-time revisions,
realistic same-bar execution, preboundary exposure, causal warmup, fitting,
feature/outcome horizons, gaps, freezing, provenance, multi-instrument coverage,
OOS contamination or walk-forward properties. No caller integration is opened.
Stored bars contain opens only; read.py's inclusive open filter/deduplication
and runner.py's next-stored-open/monthly-30-day inference are insufficient
research evidence and remain unchanged. Whole 18.2 and Phase 18 remain incomplete.
No later task or phase is opened; never begin Phase 29.

Readiness baseline: clean branch `phase18/18.2b-bar-coverage` at
`4d3c8e84ca25974e78ee69952116b0211109fb7c`. Reviewer independently verified
live `git ls-remote --heads origin main` returned that SHA; accepted decision
commit 2bfe143 and helper commit 73f81f0 are ancestors (both exit 0). The user's
wait-for-PR-merge condition is fulfilled by the merged prerequisite tree on main.
Remote observation is current-check evidence, not guaranteed future freshness
or publication. Git used command-only network permission, preserving proxy/TLS.
Existing venv Python 3.12.14 imports pytest 9.1.1, ruff 0.16.10, mypy 2.4.0,
duckdb 1.5.6, pydantic 2.13.5 and NautilusTrader 1.231.0; no installs needed.
Readiness review read full AGENTS/STATE/WORKFLOW/REVIEWER/INCIDENTS/spec and
required PROJECT/rules, planner report and relevant actual code/tests.
Supplemental exact plan: /tmp/phase18b-plan.md; this durable contract does not
depend on that temporary file for the supported scope. No third-party call in
this task needs a Stage-1 probe. No Python files changed; pytest/ruff/mypy were
not rerun for this STATE-only readiness commit under WORKFLOW section 5.
Reviewer ran whole git diff/status/staged whitespace and scope checks before
terminal commit. This READY transition is separate from future implementation
and acceptance; last_completed_task remains 18.2a and next_task remains null.

**Implementation acceptance:** activate existing Linux venv, run from repo root
exactly `python -m pytest backend/tests -q`, `python -m ruff check .`,
`python -m mypy --strict backend/src`, `git diff --check`, `git status --short`.
Full pytest needs the previously evidenced command-only network grant for
local TestClient sockets, with options/plugins/proxy/TLS unchanged. Preserve
all failures and authorized correction history under the documented loop limit.
One terminal implementation commit:
`feat(engine): validate explicit bar clock coverage (Phase 18.2b)`.
Fresh independent acceptance reviewer reruns all exact commands, then records
accepted evidence in a separate STATE commit. Task-level PR targets main after
acceptance; coordinator confirms remote branch/PR before claiming publication.
Doer/readiness reviewer neither pushes nor merges. Further tasks require fresh
narrow planning/readiness; no automatic main mutation or phase crossing.

### 18.2b completion evidence

```yaml
task_id: 18.2b
status: COMPLETE
reviewer_decision: accepted_supplied_clock_consistency_and_batch_coverage_only
reviewer_date: 2026-10-03
files_changed:
  - backend/src/quant/engine/bar_coverage.py
  - backend/tests/engine/test_bar_coverage.py
tests_added_or_updated:
  - 164 deterministic cases with independent eight-duration fixtures and shifted anchors
  - exact explicit calendar and zero-delay availability; unsupported session/monthly/delayed clocks reject
  - six strict timestamp slots, signed/zero/unbounded/subclass integers, missing evidence and aligned half-open boundaries
  - exact complete ordered unique batch, missing/empty/duplicate/context rejection and enormous arithmetic-count fixture
  - deterministic precedence, one matching ERROR and ValueError, no payload serialization, immutable detached tuple and repeatability
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - git diff --check
  - git status --short
acceptance_output:
  pytest: "792 passed, 81 warnings in 41.30s; exit 0"
  ruff: "All checks passed!; exit 0"
  mypy: "Success: no issues found in 32 source files; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer state update; exit 0"
git_commit_sha: b9a25ee197b637e3f3a99ee693d6c13bc34cd5e0
readiness_commit_sha: 5c3d600564146d1bf287ed0427f0168a5e8dd77c
readiness_baseline_sha: 4d3c8e84ca25974e78ee69952116b0211109fb7c
next_task: 18.2
next_task_status: NOT_STARTED
human_decisions: confirmed
human_transition_required: false
deviations:
  - "Existing Linux Bash venv activation and command-only network grant instead of Windows examples; exact acceptance commands/options/plugins unchanged."
notes: |
  The authorized serial READY task proceeded through doer implementation
  (IN_PROGRESS), committed handoff (ACCEPTANCE_PENDING) and fresh independent
  reviewer acceptance (COMPLETE). These role handoffs are recorded here; doer
  neither advanced STATE nor self-accepted. Reviewer read full startup,
  workflow/reviewer/incident/spec records, required project/rules, corrected
  plan, readiness report, doer report and actual complete two-file commit.
  Public interface, ordered predicate/message precedence, no inferred evidence,
  no filtering/repair and exact detached frozen values match the durable
  readiness contract. Aligned unique strictly ordered closes inside the finite
  half-open grid plus exact arithmetic count prove complete expected coverage;
  no redundant impossible predicate or giant schedule is required.
  Every exact whole-tree acceptance command independently passed on its first
  reviewer invocation. Full raw output is supplemental in
  /tmp/phase18b-review-pytest.log, /tmp/phase18b-review-ruff.log and
  /tmp/phase18b-review-mypy.log. Full pytest used required command-only network
  permission for local TestClient sockets, preserving proxy/TLS and all options
  and plugins. No installs, retries or implementation/test changes by reviewer.
  Doer disclosed initial Ruff failure (three long lines, two B008 constructor
  defaults) before its authorized cosmetic correction. Original output is
  preserved in its report/logs; full final acceptance rerun passed. Review found
  no weakened assertion or hidden behavioral correction. Existing 81 warnings
  concern Starlette httpx and Pandas Timestamp.utcnow, not new helper code.
  Independently verified branch phase18/18.2b-bar-coverage, exact task parent
  and clean checkout, unchanged protected/dependency/existing files, and accepted
  decision/helper prerequisites as ancestors. Live git ls-remote --heads origin
  main returned 4d3c8e84ca25974e78ee69952116b0211109fb7c, exit 0, before this
  STATE-only terminal commit. This point-in-time check is not future freshness
  or publication evidence. Coordinator must confirm task remote branch/PR.
  Supplied timestamps/calendar consistency does not prove actual historical
  source publication, delays or point-in-time revisions. Zero-delay fixed grids
  are the supported capability; delayed/session/monthly clocks fail closed.
  No caller wiring, runtime eligibility, preboundary exposure/scoring, realistic
  same-bar execution, causal warmup, fitting, dependencies/gaps, frozen selection,
  provenance, multi-instrument coverage, OOS contamination or walk-forward
  property is accepted. Direct value-record construction remains unvalidated.
  Ordinary/historical behavior remains unchanged. Whole 18.2 is incomplete;
  current_task 18.2 identifies remaining narrow planning only and stays
  NOT_STARTED with next_task null. No further split or READY contract is
  invented, 18.3/18.4 remain NOT_STARTED, Phase 18 remains IN_PROGRESS, and no
  phase crossing is opened. Historical readiness/evidence blocks are unchanged.
```

### 18.2a completion evidence

```yaml
task_id: 18.2a
status: COMPLETE
reviewer_decision: accepted_declaration_contract_only
reviewer_date: 2026-10-03
files_changed:
  - backend/src/quant/engine/temporal.py
  - backend/tests/engine/test_temporal.py
tests_added_or_updated:
  - 184 deterministic parameterized declaration and point-membership cases
  - absent/null stage exits before endpoint reads and ignores malformed legacy ranges
  - exact stages, applicability, every complete optional/required pair and endpoint type
  - semantic chronology, overlap rejection, signed/zero/unbounded integers and shared boundaries
  - matching single ERROR and ValueError, first-failure precedence, caller immutability and frozen outputs
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - git diff --check
  - git status --short
acceptance_output:
  pytest: "628 passed, 81 warnings in 34.71s; exit 0"
  ruff: "All checks passed!; exit 0"
  mypy: "Success: no issues found in 31 source files; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer state update; exit 0"
git_commit_sha: 73f81f0636b6c715e07c3f01ba0ab03c8eb0251a
next_task: 18.2b
next_task_status: NOT_STARTED
human_decisions: confirmed
human_transition_required: false
deviations:
  - "Existing Linux venv/Bash activation and command-only network grant instead of documented Windows example; acceptance commands unchanged."
notes: |
  The authorized serial task moved from READY through planner contract/readiness,
  doer implementation (IN_PROGRESS), committed handoff (ACCEPTANCE_PENDING),
  and fresh independent reviewer acceptance (COMPLETE). The intervening role
  handoffs are recorded here; the doer did not advance STATE or self-accept.
  Reviewer read the full actual two-file commit, accepted narrow plan, doer
  report, full workflow/reviewer/incident/spec records and relevant project
  contracts. Stage requirements, every supplied inactive pair, fixed semantic
  order, half-open membership, immutable detached records, early ordinary exit
  and deterministic log-plus-raise behavior match the approved contract.
  All exact whole-tree acceptance commands independently passed on their first
  reviewer invocation using the existing venv; no installs or code changes.
  Full pytest used command-only network permission for local TestClient socket
  operation, preserving configured proxy/TLS and all command options/plugins.
  Doer's initial restricted pytest stalled without a result; only verified
  owned PID was terminated after the network-granted diagnostic succeeded.
  Its original shell exit was unavailable, not reported as a passed run.
  Two precommit cosmetic lint correction cycles (5 issues then one remaining
  long line) and all original failures remain in the doer report/logs.
  Reviewer found no hidden semantic correction or weakened test assertion.
  Independent output is preserved in /tmp/phase18a-review-pytest.log,
  /tmp/phase18a-review-ruff.log and /tmp/phase18a-review-mypy.log; temporary
  reports are supplemental, while this evidence and task commit are durable.
  Live git ls-remote --heads origin main work independently returned main
  81824f70aaeeb7efc07b8afc127a43a2b888bcd7 and work
  90c35911d95515fde0f25e856fd9858e99332a9f before this state commit.
  That observation verifies current connectivity, not publication of this task.
  This separate reviewer commit changes STATE only. No caller/API/CLI/runtime
  integration, bar/calendar coverage, warmup, gaps, frozen selection, provenance
  or walk-forward guarantee is accepted. API coercion cannot be undone here;
  missing versus null is intentionally equivalent, validation use cannot be
  inferred, and integer points/touching boundaries prove no availability/gap
  eligibility. 18.2b remains NOT_STARTED pending fresh narrow planning/readiness.
  Whole 18.2 remains incomplete, Phase 18 remains IN_PROGRESS, and no later
  task or phase is opened. Historical evidence below is preserved unchanged.
```

### 18.1.1 completion evidence

```yaml
task_id: 18.1.1
status: COMPLETE
reviewer_decision: accepted_confirmed_decision_record_only
reviewer_date: 2026-10-03
files_changed:
  - docs/specs/phase-18.md
tests_added_or_updated: []
acceptance_commands:
  - python /tmp/phase18-verify-decision-record.py
  - python /tmp/phase18-reviewer-compare.py
  - git diff --check
  - git status --short
  - git show --check 2bfe14315cb6c0152ad01e57068173e379a66f9e
  - git diff-tree --no-commit-id --name-only -r 2bfe14315cb6c0152ad01e57068173e379a66f9e
acceptance_output:
  source_comparison: "PASS: all 23 stable decision IDs match the source record exactly (whitespace normalized). PASS: all 15 stable scenario IDs match the source record exactly."
  provenance_scope: "PASS: approval/provenance, historical inventory acceptance, scope gates, stage applicability, and absence of decision placeholders verified."
  changed_paths: "PASS: only docs/specs/phase-18.md changed; protected/state/code/test/dependency files unchanged."
  independent_comparison: "All 23 unique IDs/decisions and 15 outcomes exact; original headings, scenarios, question links, established contract bullets/source links preserved; exit 0."
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer state update"
  commit_check: "commit header/message only; no whitespace errors; exit 0"
  file_list: "docs/specs/phase-18.md"
git_commit_sha: 2bfe14315cb6c0152ad01e57068173e379a66f9e
next_task: 18.2a
next_task_status: READY
human_decisions: confirmed
human_transition_required: false
deviations:
  - "Question prose replaced with confirmed answers; stable headings/IDs and original inventory commit preserve historical evidence. Coordinator explicitly accepted this approach; no amendment requested."
notes: |
  Fresh independent reviewer read the full spec and actual one-file task diff,
  applicable project/workflow/reviewer/rules and incident records, doer report,
  and independently supplied /tmp/phase18-confirmed-decisions.md. All 23
  decision paragraphs and 15 scenario outcomes match that approved source.
  Manual review confirmed stage applicability, approval provenance, scope gates,
  historical preservation, explicit experiment inputs and limited guarantees.
  The user approved seven initial decisions, delegated remaining choices, saw
  the complete record, and explicitly confirmed/authorized the first task with
  "just fix the git connectivity and start the first task auto now".
  Reviewer independently re-ran every documentation acceptance command.
  A supplemental comparison first failed at SC-01 because its temporary parser
  included the trailing table delimiter; the parser alone was corrected outside
  the checkout. Its full rerun passed; no specification correction was needed.
  Live git ls-remote origin refs/heads/main independently returned
  81824f70aaeeb7efc07b8afc127a43a2b888bcd7 using configured proxy/network permission.
  No backend, scripts, or frontend files changed; pytest, ruff, mypy, tsc,
  vitest and build were not rerun under WORKFLOW.md section 5.
  This separate reviewer state commit opens only 18.2a. 18.2b, 18.3 and 18.4
  remain NOT_STARTED. Phase 18 remains IN_PROGRESS; no phase crossing or
  runtime eligibility, warmup, gap/window, API/CLI or freeze enforcement is
  certified. Further narrow task planning and independent acceptance remain
  required. The original 18.1 evidence block below is historical and unchanged.
```

### 18.1 completion evidence

```yaml
task_id: 18.1
status: COMPLETE
reviewer_decision: accepted_question_inventory_only
reviewer_date: 2026-10-03
files_changed:
  - docs/specs/phase-18.md
tests_added_or_updated: []
acceptance_commands:
  - git diff --check
  - git status --short
  - git show --check f6060f8b97e2ed304e7c8a4618647d9dca725d09
  - git diff-tree --no-commit-id --name-only -r f6060f8b97e2ed304e7c8a4618647d9dca725d09
acceptance_output:
  diff_check: "no output; exit 0"
  status: "no output; clean before state evidence update"
  commit_check: "commit header only; no whitespace errors; exit 0"
  file_list: "docs/specs/phase-18.md"
git_commit_sha: f6060f8b97e2ed304e7c8a4618647d9dca725d09
next_task: 18.2
next_task_status: NOT_STARTED
human_transition_required: true
deviations: []
notes: |
  Fresh independent reviewer inspected the entire 364-line questions document
  and actual one-file commit, current metadata schemas/persistence/wire types,
  accepted Phase 17 evidence, and the Phase 16 clock contract and test evidence.
  Manual documentation acceptance verified all 23 question groups and 15
  scenario outcomes remain unresolved; all human approval fields remain blank.
  Coverage includes stage meaning, boundaries and membership, warmup and
  information access, boundary state, gaps, walk-forward identity and reselection,
  final holdout, enforcement, legacy records, provenance, and guarantee limits.
  No defaults, recommendations, numeric window sizes, implementation design,
  inferred human decisions, or authorization for 18.2 were introduced.
  No backend, scripts, or frontend files changed; pytest, ruff, mypy, tsc,
  vitest, and build were not rerun for this documentation-only task.
  Implementation and acceptance review of 18.1 have concluded; this separate
  reviewer evidence commit records completion. The next task is identified
  without opening it: 18.2 remains NOT_STARTED pending human decisions.
  Phase 18 remains IN_PROGRESS; 18.3 and 18.4 remain NOT_STARTED.
```

### 17.1 completion evidence

```yaml
task_id: 17.1
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/src/quant/data/runs_store.py
  - backend/tests/data/test_runs_store.py
tests_added_or_updated:
  - fresh meta_runs schemas contain all nullable research metadata columns
  - legacy schemas migrate in place with NULL research metadata
  - insert_run preserves every research metadata field
  - insert_run_with_connection preserves every research metadata field
  - claim_next_queued preserves every research metadata field
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - git diff --check
  - git status --short
acceptance_output:
  pytest: "431 passed, 81 warnings"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
  diff_check: "exit 0"
  status: "clean"
git_commit_sha: b0ad975
next_task: 17.2
deviations: []
notes: |
  Commit b0ad975 was cherry-picked into the primary checkout as
  1a925cc. Before final acceptance, separate commit 0c5d842 replaced
  the known I-005 Rust-bridge capfd polling tests with deterministic
  warning spies. The reviewer then re-ran every whole-tree acceptance
  command without retries. No API, frontend, optimizer, or Phase 18
  validation behavior is included.
```

### 17.2 completion evidence

```yaml
task_id: 17.2
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/src/quant/api/schemas.py
  - backend/tests/api/test_schemas.py
tests_added_or_updated:
  - RunSummary accepts and serializes all nullable research metadata
  - RunCreate accepts all nullable research metadata
  - omitted research metadata defaults to None
  - invalid research_stage values are rejected
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - git diff --check
  - git status --short
acceptance_output:
  pytest: "435 passed, 81 warnings"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
  diff_check: "exit 0"
  status: "clean"
git_commit_sha: 62a2365
next_task: 17.3
deviations: []
notes: |
  Reviewer independently re-ran every whole-tree acceptance command.
  The implementation changes only API schema contracts and their direct
  tests. No API transport wiring, frontend, optimizer, or Phase 18
  validation behavior is included.
```

### 17.3 completion evidence

```yaml
task_id: 17.3
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-02
files_changed:
  - backend/src/quant/api/routers/runs.py
  - backend/tests/api/test_runs_create.py
tests_added_or_updated:
  - research metadata round-trips through run creation and persistence
  - run-list responses preserve all research metadata
  - tear-sheet run summaries preserve all research metadata
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - git diff --check
  - git status --short
acceptance_output:
  pytest: "436 passed, 81 warnings"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
  diff_check: "exit 0"
  status: "clean"
git_commit_sha: fa311a4
next_task: 17.4
deviations: []
notes: |
  Reviewer independently re-ran every whole-tree acceptance command
  without retries. All eleven research metadata fields flow through the
  API create, list, and tear-sheet paths. No CLI, frontend, optimizer, or
  Phase 18 validation behavior is included.
```

### 17.4 completion evidence

```yaml
task_id: 17.4
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-02
files_changed:
  - scripts/run_backtest.py
  - backend/tests/test_run_backtest.py
tests_added_or_updated:
  - omitted CLI research metadata persists as NULL and remains outside params
  - all CLI research metadata inputs persist with their established names and types
  - exploration, validation, and oos research stages are accepted
  - invalid research stages and integer metadata inputs are rejected
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - git diff --check
  - git status --short
acceptance_output:
  pytest: "444 passed, 81 warnings"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
  diff_check: "exit 0"
  status: "clean"
git_commit_sha: 9b3fe3909116fe1eaf52d745b891489d8a6188e9
next_task: 17.5
deviations: []
notes: |
  Reviewer independently inspected the committed CLI and test diff and
  re-ran every whole-tree backend acceptance command. Research metadata
  remains separate from strategy params. The task adds metadata inputs only;
  it does not add frontend behavior or Phase 18 temporal enforcement.
```

### 17.5 completion evidence

```yaml
task_id: 17.5
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-02
files_changed:
  - frontend/src/api/types.ts
  - frontend/src/api/runs.test.ts
  - frontend/src/pages/CommandCenter/RunHistoryTable.test.tsx
  - frontend/src/pages/CommandCenter/StrategyForm.test.tsx
  - frontend/src/pages/Compare/index.test.tsx
  - frontend/src/pages/TearSheet/ExperimentHeader.test.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_added_or_updated:
  - populated and explicit-null metadata remains top-level in create requests
  - omitted request metadata is supported and response metadata is explicitly null
  - run-list and tear-sheet responses preserve populated and null research metadata
  - incomplete RunSummary metadata is rejected at compile time
  - exploration, validation, and oos typecheck while unsupported stage literals fail
  - five existing RunSummary fixtures explicitly provide all eleven nullable fields
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
  - git diff --check
  - git status --short
acceptance_output:
  tsc: "exit 0"
  vitest: "Test Files  30 passed (30); Tests  215 passed (215)"
  build: "142 modules transformed; built in 387ms; exit 0"
  diff_check: "exit 0"
  status: "clean"
git_commit_sha: e2ea48089cd63bd7a1115e49542b584bfe13d679
next_task: 17.6
deviations:
  - "Human approved amendment and expansion to five existing response fixture files so RunSummary fields remain required nullable."
notes: |
  Fresh independent reviewer inspected the full seven-file committed diff
  and re-ran every whole-tree frontend acceptance command from the repo
  root using PowerShell Push-Location/Pop-Location and preserved exit codes.
  The eleven new RunSummary fields are required nullable; RunCreate metadata
  is optional nullable. Existing API helpers are unchanged. No runtime
  component, dependency, optimizer, or Phase 18 temporal enforcement changed.
  The production build reported the existing large-chunk advisory. No backend
  or scripts files changed; pytest, ruff, and mypy were not re-run under
  WORKFLOW.md section 5 path-scoped acceptance.
```

### 17.6 completion evidence

```yaml
task_id: 17.6
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-02
files_changed:
  - frontend/src/pages/CommandCenter/StrategyForm.tsx
  - frontend/src/pages/CommandCenter/StrategyForm.test.tsx
tests_added_or_updated:
  - all twelve optional research controls are accessible and initially blank
  - all metadata submits at top level with trimmed strings and UTC epoch-ms dates
  - exploration, validation, and oos stages submit with their exact wire values
  - whitespace, cleared fields, and unset stage are omitted
  - each single date endpoint is accepted without requiring its paired endpoint
  - reversed and overlapping ranges and trial index greater than count are accepted
  - zero, signed integers, and safe-integer boundaries are accepted
  - invalid calendar dates and malformed, fractional, nonfinite, or unsafe integers block submission
  - existing strategy, timeframe, universe, fees, deployment, benchmark, navigation, error, and pending behavior remains covered
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
  - git diff --check
  - git status --short
acceptance_output:
  tsc: "npm notice run frontend@0.0.0 npx; npm notice run tsc -b; exit 0"
  vitest: "Test Files  30 passed (30); Tests  242 passed (242); Duration  7.97s; exit 0"
  build: "142 modules transformed; built in 713ms; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean"
git_commit_sha: 60aee99f550fcbf8139eb43dc0c0c910c5623833
next_task: 17.7
deviations: []
notes: |
  Fresh independent reviewer read the actual two-file committed diff,
  checked backend schemas and accepted frontend wire types, and reran all
  whole-tree frontend acceptance commands from the repository root using
  PowerShell Push-Location/Pop-Location with preserved exit codes. Tests
  exercise real form inputs and payload construction at the createRun
  boundary. No Phase 18 temporal or trial-relationship enforcement was
  added. The production build reported the existing large-chunk advisory.
  No backend or scripts files changed; pytest, ruff, and mypy were not
  rerun under WORKFLOW.md section 5 path-scoped acceptance. Phase 17
  remains IN_PROGRESS; task 17.7 is opened but not implemented.
```

### 17.7 completion evidence

```yaml
task_id: 17.7
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-02
files_changed:
  - frontend/src/pages/CommandCenter/RunHistoryTable.tsx
  - frontend/src/pages/CommandCenter/RunHistoryTable.test.tsx
tests_added_or_updated:
  - real grid renders exact column order and populated and null metadata
  - mixed experiments and all three stages remain in API order
  - strings preserve whitespace and UTC ranges preserve full milliseconds
  - partial endpoints, epoch zero, reversed and overlapping ranges remain visible
  - trial zero, negative values and index greater than count remain exact
  - all nine research columns sort through real grid header interactions
  - shared experiment and stage retain distinct selected run IDs
  - existing loading, empty, error, polling and double-click navigation tests remain
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
  - git diff --check
  - git status --short
acceptance_output:
  tsc: "npm notice run frontend@0.0.0 npx; npm notice run tsc -b; exit 0"
  vitest: "Test Files  30 passed (30); Tests  254 passed (254); Duration  14.08s; exit 0"
  build: "142 modules transformed; built in 379ms; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean"
git_commit_sha: a7dff301b1c008168ef29398bde4524109fc786c
next_task: 17.8
deviations:
  - "Supplementary whole-tree npx vitest run --retry=0 probe: 2 failed files, 28 passed; 2 failed tests, 252 passed; duration 13.46s; exit 1. This was not a required acceptance command."
notes: |
  Fresh independent reviewer inspected the full two-file committed diff
  against the task prompt, accepted wire types and backend schemas, then
  reran every required frontend acceptance command from the repository root
  using PowerShell Push-Location/Pop-Location with preserved exit codes.
  Required acceptance passed on its first invocation. No inferred research
  validity, filtering, grouping, Phase 18 enforcement or tear-sheet work was
  added. Existing query, navigation, theme and KPI behavior is unchanged.
  Earlier debugging attempts corrected grid header selectors and the blank
  selection-column header expectation; final assertions verify exact DOM
  values and real sorting rather than weakening the behavior checks.
  To audit I-013, the reviewer additionally disabled retries for one full
  suite probe. RunHistoryTable > renders rows when data loads and
  TradeLedger > renders rows when data loads timed out finding their row
  text; failure DOM showed hidden grid containers and empty headers. Both
  assertions predate this task and are unchanged. All metadata-specific
  tests passed. frontend-tooling.md and original commit dfaafcb explicitly
  authorize retry: 2 for parallel AG Grid jsdom layout timing; this task
  does not change that setting. The supplemental failures are retained here,
  not reported as green or hidden behind a rerun. Production build reported
  the existing large-chunk advisory. No backend or scripts files changed;
  pytest, ruff and mypy were not rerun under WORKFLOW.md section 5.
  Phase 17 remains IN_PROGRESS; task 17.8 is opened but not implemented.
```

### 17.8 completion evidence

```yaml
task_id: 17.8
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-02
files_changed:
  - frontend/src/pages/TearSheet/ExperimentHeader.tsx
  - frontend/src/pages/TearSheet/ExperimentHeader.test.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
  - frontend/src/pages/TearSheet/tearSheet.css
tests_added_or_updated:
  - null research metadata renders as em dashes in run-history label order
  - populated strings, all three stages, and full UTC ranges stay exact
  - partial endpoints, a reversed range, trial zero, and a negative trial count stay exact
  - the Data tab timeframe em dash assertion is scoped to that row
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
  - git diff --check
  - git status --short
acceptance_output:
  tsc: "exit 0"
  vitest: "Test Files  30 passed (30); Tests  256 passed (256); Duration  11.95s; exit 0"
  build: "142 modules transformed; built in 561ms; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean"
git_commit_sha: 77df5035d30446328ab45e63b3c52fec3b8bb590
next_task: 18.1
deviations:
  - "Display formatters live in ExperimentHeader instead of being shared with RunHistoryTable."
  - "The reversed-range test title also says overlapping; the asserted OOS case is reversed (1000 to 0), not a separate overlap fixture."
  - "Supplementary whole-tree npx vitest run --retry=0: 30 files passed, 256 tests passed, duration 11.88s, exit 0. This was not a required acceptance command."
notes: |
  Fresh reviewer read the four-file committed diff against the task,
  accepted wire types, and run-history display rules, then reran every
  required frontend acceptance command from the repository root.
  Required acceptance passed on its first invocation. The header shows
  all eleven persisted fields, including explicit nulls, without
  inferring validity or adding Phase 18 enforcement. The Data tab still
  omits a null experiment id. The production build reported the existing
  large-chunk advisory. No backend or scripts files changed; pytest,
  ruff, and mypy were not rerun under WORKFLOW.md section 5. Phase 17
  is complete. Phase 18.1 is opened as questions only because embargo,
  inclusivity, and walk-forward sizes are not specified.
```

### U.6.1 completion evidence

```yaml
task_id: U.6.1
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/tabs/RiskTab.tsx
  - frontend/src/pages/TearSheet/tabs/RiskTab.test.tsx
tests_added:
  - RiskTab shows the five supplied risk KPIs and drawdown series
  - RiskTab renders five null KPI values as em dashes
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "30 files, 205 passed"
  build: "exit 0"
git_commit_sha: bff113e37788b898172bfa10bae15d533bc71e84
next_task: U.6.2
deviations: []
notes: |
  Reviewer re-ran all frontend acceptance commands. No backend or
  scripts files changed, so pytest, ruff, and mypy were not re-run.
```

### U.6.2 completion evidence

```yaml
task_id: U.6.2
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/App.tsx
  - frontend/src/pages/TearSheet/TearSheetNav.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_updated:
  - nav renders eight items in the approved order with intended badges
  - Risk route renders and marks its navigation item active
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "30 files, 205 passed"
  build: "exit 0"
git_commit_sha: ffc277b
next_task: U.6.3
deviations: []
notes: |
  Reviewer re-ran all frontend acceptance commands. No backend or
  scripts files changed, so pytest, ruff, and mypy were not re-run.
```

### U.6.3 completion evidence

```yaml
task_id: U.6.3
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/OverviewSummary.tsx
  - frontend/src/pages/TearSheet/OverviewSummary.test.tsx
  - frontend/src/pages/TearSheet/tabs/OverviewTab.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_updated:
  - Overview keeps the approved headline and secondary KPI bands
  - Overview omits Win Rate, Trades, Avg Duration, and Underwater
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "30 files, 205 passed"
  build: "exit 0"
git_commit_sha: 290be85
next_task: U.6.4
deviations:
  - "The first full-suite run exposed an over-broad negative assertion that matched the permanent Trades nav item; the assertion was scoped to the KPI section before commit."
notes: |
  Reviewer re-ran all frontend acceptance commands after the test fix.
  No backend or scripts files changed, so pytest, ruff, and mypy were
  not re-run.
```

### U.6.4 completion evidence

```yaml
task_id: U.6.4
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/tabs/PerformanceTab.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_updated:
  - Performance keeps Price + Fills followed by dominant equity
  - Performance omits Underwater, whose route remains Risk
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "30 files, 205 passed"
  build: "exit 0"
git_commit_sha: 97cd298
next_task: U.6.5
deviations: []
notes: |
  Reviewer re-ran all frontend acceptance commands. No backend or
  scripts files changed, so pytest, ruff, and mypy were not re-run.
```

### U.6.5 completion evidence

```yaml
task_id: U.6.5
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/tabs/DataTab.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_updated:
  - Data renders a non-null experiment id
  - Data omits a null experiment id and shows the UTC date range
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "30 files, 206 passed"
  build: "exit 0"
git_commit_sha: 3928376
next_task: null
deviations: []
notes: |
  Reviewer re-ran all frontend acceptance commands. Compare and all
  existing frontend tests passed. No backend or scripts files changed,
  so pytest, ruff, and mypy were not re-run. U.6 is complete; Phase 17
  remains unopened.
```

### 16.5.6 completion evidence

```yaml
task_id: 16.5.6
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/tabs/ExecutionTab.tsx
  - frontend/src/pages/TearSheet/tabs/ExecutionTab.test.tsx
  - frontend/src/App.tsx
  - frontend/src/pages/TearSheet/tabs/PlaceholderTab.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_added:
  - frontend/src/pages/TearSheet/tabs/ExecutionTab.test.tsx (2)
  - frontend/src/pages/TearSheet/index.test.tsx::robustness tab says no analysis is attached
  - frontend/src/pages/TearSheet/index.test.tsx::execution tab shows assumption strings from the tear sheet
tests_updated:
  - frontend/src/pages/TearSheet/index.test.tsx::regimes tab says classification is not attached
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "29 files, 203 passed"
  build: "exit 0"
git_commit_sha: aa0aaff7c21011f3301d97c467f8e7f91dc2007f
next_task: null
deviations:
  - "PlaceholderTab now takes the unavailable sentence directly. The old phase template could not show the required copy."
  - "A non-object assumptions value, or one whose maker_fee is not a string, uses the same missing sentence as the Data tab."
  - "No Python files changed, so pytest, ruff, and mypy were not re-run."
notes: |
  Reviewer re-ran tsc -b, vitest, and the production build on aa0aaff.
  Regimes and Robustness show the unavailable sentences and no
  fabricated analysis. Execution lists every assumption string
  verbatim. Fees are not summed. A missing assumptions object shows
  the missing sentence once. The Data tab was not changed. Phase 17
  is not started.
```

End of verbatim records moved from STATE.md on 2026-10-03.

### 18.2g and 18.2g.1 combined completion evidence

```yaml
task_ids: [18.2g, 18.2g.1]
status: COMPLETE
reviewer_decision: accepted_supplied_daily_clock_consistency_and_runtime_containment_only
reviewer_date: 2026-10-03
files_changed:
  - backend/src/quant/engine/research_runner.py
  - backend/tests/engine/test_research_runner.py
tests_added_or_updated:
  - 61 original expanded admission, real-engine containment, callback-failure and compatibility cases
  - one actual-engine exact decimal-volume regression; 62 new cases combined
acceptance_commands:
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - python -m pytest backend/tests -q
  - git diff --check
  - git status --short
acceptance_output:
  ruff: "All checks passed!; exit 0"
  mypy: "Success: no issues found in 33 source files; exit 0"
  pytest: "961 passed, 121 warnings in 40.42s; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer state maintenance; exit 0"
git_commit_sha: 47fa7068077952fe9894483ee373ab5873f000df
original_unaccepted_implementation_sha: 5a24edce407b4d3da75ee54c123ee14f0f928d3a
readiness_commit_shas:
  - 568822e9adc6e96e9e8923ea2747875a8773e00f
  - 8154fdebdbde089a95b8b6839df3a94eb73dc1aa
next_task: null
remaining_18_2_status: NOT_STARTED
human_transition_required: false
deviations:
  - "Independent blocking precision finding required separate authorized g.1 repair; original g SHA preserved, never accepted alone or amended."
  - "One corrected-g task PR is the necessary publication unit for original unaccepted adapter plus blocking repair on the same branch; no buggy precursor merge or dependent PR."
  - "Authorized reviewer documentation maintenance includes STATE.md and docs/evidence/STATE-archive.md: completed historical records moved verbatim, original archive prefix and current rules preserved."
notes: |
  Serial g READY -> implementation IN_PROGRESS -> committed ACCEPTANCE_PENDING
  -> blocking review IN_PROGRESS; bounded g.1 READY -> implementation
  IN_PROGRESS -> committed ACCEPTANCE_PENDING -> fresh combined acceptance
  COMPLETE. Doer did not edit STATE or self-accept. Only the combined final
  tree at 47fa706 is accepted. Reviewer completed previously truncated mandatory
  reads in bounded chunks: full STATE/workflow/reviewer/incidents, relevant
  PROJECT/rules, approved spec, full runtime-probe source/evidence and Nautilus
  guide; exact original two-file implementation/tests and corrective diff read.
  Exact keyword-only signature/no defaults, key-based joined clocks, structural
  integer/grid/availability validation, admitted-only OHLCV and ns bounds,
  complete active/warmup coverage, warmup without exposure/scoring and explicit
  daily BTC capability match the contract. Excluded earlier/sentinel/later data
  never reaches engine; last eligible close alone values residual exposure.
  Live on_start and first-active clean queries fail on nonempty or unknown state.
  Actual fill membership checked before inherited snapshot replacement; first
  callback Exception retained, later callbacks abort and postrun guard prevents
  successful extraction even after deliberately swallowed dispatch. Finally
  disposes. Terminal open/inflight orders fail; genuine open positions remain
  disclosed without fabricated liquidation. Latest account rows independently
  value cash plus BTC; missing required currencies fail. Actual first fill/fee
  returns and ordinary daily runner control agree; ordinary source unchanged.
  Original volume 1000000000000.0001 was admitted but serialized to
  1000000000000.000122. Complete real public-run blocker evidence retained in
  /tmp/phase18g-review-blocker.log and /tmp/phase18g-review-report.md.
  Authorized g.1 changes only five OHLCV and initial-cash formatting sites to
  Decimal(str(value)); regression sees actual Quantity 1000000000000.000100,
  rejects observed original value, verifies all actual admitted OHLCV decimal
  equality, normal fill/fee/results and deep input immutability. No new API.
  Every exact final whole command independently passed. Single completed full
  pytest invocation used current enabled network permission with unchanged
  options/plugins/proxy/TLS; no dependency install or services. Earlier tool
  executions interrupted after cheap checks never started pytest and are not
  reported green. Original independent g pytest NOT RUN after confirmed blocker.
  Final raw logs: /tmp/phase18g1-review-ruff.log, -mypy.log, -pytest.log,
  -diff-check.log and -status-before.log. Full review report:
  /tmp/phase18g1-review-report.md. Original doer Ruff failures (25 then 2 E501)
  remain /tmp/phase18g-doer-ruff-1.log and -2.log; cosmetic wraps disclosed.
  Original doer 960-test pass is historical. Corrective doer first full suite
  961 passed,121 warnings in35.84s; no hidden test retry or weakened assertions.
  Current 121 warnings concern established Starlette httpx and Nautilus Pandas
  Timestamp.utcnow behavior, including added live-engine fixtures.
  Acceptance is local, not publication/merge. Coordinator verifies authorized
  corrected-g PR checks/merge before fresh next planning. Reviewer neither
  amends, pushes, creates PR, merges, launches workers nor edits implementation.
  Completed historical contract/evidence blocks are archived verbatim with a
  compact live reference table and explicit post-probe human approval retained.
  This supports mandatory full live-STATE reads without discarding evidence.
  Initial documentation diff check exited2 for a new blank line at archive EOF,
  inherited from the verbatim moved separator. Exact slice was preserved and
  an authored end-of-records marker appended; final diff check exit0. Raw
  /tmp/phase18g1-review-state-diff-check.log and -state-diff-check-final.log
  retain the initial diagnostic and final success. No historical bytes changed.
  Only supplied-clock consistency/runtime containment is accepted: no historical
  source availability/revision, frozen selection, evidence transport/binding,
  orchestrator/API/CLI/worker integration, research eligibility/OOS inspection,
  dependencies/gaps/windows or whole18.2/Phase18 completion. No future task is
  READY; remaining18.2 NOT_STARTED, next_task null, last_completed_task18.2g.1,
  human_transition_required false, Phase18 IN_PROGRESS. Never begin Phase29.
```

### 18.2h completion evidence

```yaml
task_id: 18.2h
status: COMPLETE
reviewer_decision: accepted_immutable_supplied_evidence_and_exact_content_identity_only
reviewer_date: 2026-10-04 Asia/Manila
git_commit_sha: a0d08e6aa2ff36ead2eac54dda698ea7ec5fb2a3
readiness_commit_sha: 2213ee19704c28514d1051a961f1a5b64cc76484
files_changed:
  - backend/src/quant/engine/research_input.py
  - backend/tests/engine/test_research_input.py
tests_added_or_updated: 173 new public-factory and detached-record cases
acceptance_commands:
  - .venv/bin/python -m ruff check .
  - .venv/bin/python -m mypy --strict backend/src
  - .venv/bin/python -m pytest backend/tests -q
  - git diff --check
  - git status --short
acceptance_output:
  ruff: "All checks passed!; exit 0"
  mypy: "Success: no issues found in 34 source files; exit 0"
  pytest: "1134 passed, 121 warnings in 38.53s; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer state maintenance; exit 0"
next_task: null
remaining_18_2_status: NOT_STARTED
human_transition_required: false
deviations: []
notes: |
  Serial READY -> implementation IN_PROGRESS -> committed ACCEPTANCE_PENDING
  -> independent acceptance COMPLETE. Doer never edited STATE or self-accepted.
  Reviewer read full live STATE/AGENTS/WORKFLOW/REVIEWER/INCIDENTS in bounded
  recovered reads, required PROJECT/spec/rules, actual two new files and relevant
  accepted clock/runner/read/store/fingerprint boundaries. Exact factory/interface,
  detached frozen slots/tuple/bytes, required fields/nulls, ordered fail/log behavior,
  signed unbounded clocks and finite numeric checks, claim-only provenance and raw
  chronological retention match the standalone contract. Independent manual typed
  fixture reconstruction agrees with complete hardcoded bytes; separate SHA-256
  matches df720d027a740232c362fc02a800b717083bc93c8144e219ebcb07ffc4d774f6.
  Int/float, negative zero, nearby floats, >4300-digit positive/negative clocks and
  OHLCV, Unicode and deep mutation isolation covered through actual public factory.
  One fresh full reviewer suite, no retries or implementation edits. Raw logs:
  /tmp/phase18h-review-ruff.log, -mypy.log, -pytest.log, -diff-check.log,
  -status-before.log and -independent.log. Reviewer report: /tmp/phase18h-review-report.md.
  Doer first full suite 1134 passed,121 warnings in38.72s is separate evidence.
  Doer retained Ruff failures (24 E501 then2) and one mypy literal-type failure
  in /tmp/phase18h-doer-*. Three corrective cycles preceded first full pytest;
  cosmetic wraps and explicit literal returns, no weakened tests or hidden retries.
  Warnings remain established Starlette httpx and Nautilus Pandas UTC deprecations.
  Acceptance certifies supplied consistency/content identity only: no authenticated
  publication/revision history, reproduced fixture capability, complete coverage,
  selection freeze/OOS inspection, runtime compatibility, evidence transport or
  orchestrator/API/CLI/worker integration, dependencies/gaps/windows, whole18.2 or
  Phase18 completion. Duplicate discarded JSON keys cannot be recovered by Mapping.
  Existing fingerprint and ordinary execution unchanged. No publication, merge,
  dependency install, worker launch or archive edits by reviewer. No future READY;
  current_task18.2 NOT_STARTED, last_completed_task18.2h, next_task null,
  human_transition_required false, Phase18 IN_PROGRESS. Never begin Phase29.
```

### 18.2h independent readiness contract — 2026-10-04 Asia/Manila

Independent plan review opens **ONLY 18.2h READY**. User's original post-probe
approval remains dated 2026-10-03; current delegation authorizes conservative
trustworthy choices within Phase 18, with independent gates and no phase crossing.
Baseline: clean `phase18/18.2h-input-snapshot`, refreshed main
`22da696ee3a1ed129a083acdb8945593595e0431`; origin main connectivity verified.
PR10 squash integrates the full accepted tracked tree: independent
`git diff --quiet a5be160 origin/main` exits 0. Original combined implementation
`47fa7068077952fe9894483ee373ab5873f000df` and reviewer
`a5be160409489991d1d2fecde7e807ad7cba0455` are not main ancestors (exit 1);
original published source branch/PR preserves their evidence history. No original
SHA ancestry is inferred from identical tree content. Coordinator verified PR10
merged with all three checks green and original remote branch at a5be160.

**Deliverables only:** new `backend/src/quant/engine/research_input.py` and
mirrored `backend/tests/engine/test_research_input.py`. Pure stdlib, no probe,
dependencies, caller/runtime/storage/API/CLI/UI/fingerprint changes. No exporter,
execution adapter, selection freeze, gaps/windows, source verification or eligibility
certification. Full live STATE, AGENTS, WORKFLOW, REVIEWER/INCIDENTS, required
PROJECT sections, confirmed spec, applicable rules and relevant accepted helpers,
runner/source/fingerprint code/tests reviewed. Detailed scratch plan is disposable;
this standalone contract governs implementation.

**Interface:** frozen slots dataclasses, direct construction unvalidated:
`InputProvenance(kind: Literal['controlled_fixture','researcher_attested','unknown'],
reference: str | None, declared_by: str | None)`;
`ResearchObservation(ts: int, close_ts: int, available_ts: int | None,
open: int | float, high: int | float, low: int | float, close: int | float,
volume: int | float, source_id: str, revision_id: str, provenance: InputProvenance)`;
`ResearchInputSnapshot(contract_version: str, rule_id: str, venue: str, symbol: str,
timeframe: str, calendar: str, anchor_ts: int,
observations: tuple[ResearchObservation,...], canonical_bytes: bytes, snapshot_id: str)`.
`create_research_input_snapshot(document: Mapping[str, object]) -> ResearchInputSnapshot`
is the sole validated factory; detached records/tuple/bytes have no mutable containers
or verified/eligible/frozen flags. Production docstring records wire and identity rules.

**Exact wire:** every declared field required; unknown keys rejected at document,
row and provenance levels. Top fields match snapshot metadata plus observations,
excluding canonical_bytes/snapshot_id. Fixed tokens in order: `research-input-v1`,
`phase18-temporal-v1`, `binance`, `BTC/USDT`, `1d`, `continuous_utc_fixed`.
Observations nonempty list/tuple of mappings, row fields exactly observation fields,
provenance exactly kind/reference/declared_by. Strings preserved without trim/case/
Unicode normalization; source/revision and required evidence/actor strings nonempty
valid UTF-8 without NUL or surrogates. Exact provenance enum, no inferred defaults.
Clocks signed unbounded int excluding bool; available_ts may explicit None.
Daily grid `(ts-anchor_ts)%86400000==0`, close_ts=ts+86400000;
known availability>=close, delays retained. No batch completeness/stage filtering.
All rows retained in strict chronological order; duplicate opens reject before
chronology after row validation, even equal duplicates; alternate revisions require
separate documents. OHLCV finite int/float excluding bool, prices>0, volume>=0,
high>=max(open,close), low<=min(open,close), high>=low. Integers intrinsically finite;
only floats use math.isfinite. No float coercion, rounding or precision bounds.

Unknown provenance requires reference/declared_by/availability all None.
Researcher-attested requires nonempty reference and actor; availability may unknown.
Controlled-fixture requires nonempty reference, actor None, known availability.
All source labels and references are claims, never authenticated truth. A future
trusted fixture importer must reproduce/bind rows before fixture capability can be
used; actual historical publication/revision verification remains separate work.
No reference fetching, availability inference from ingestion/open/close, or trust upgrade.

**New explicitly delegated v1 identity convention:** canonical identity document
contains validated detached wire fields, preserving row order; every numeric field
(anchor and row ts/close/known available plus OHLCV) becomes
`{'kind':'int','value':hex(value)}` (signed lowercase 0x) or
`{'kind':'float','value':value.hex()}`. None stays null. Raw input/record values remain
int/float. No unbounded bare ints in identity JSON, decimal-digit limit or global
runtime setting change. This is neither existing fingerprint nor inferred RFC format.
IEEE float content identity differs from runner's Decimal(str(value)) simulation
interpretation; snapshot certifies no execution compatibility. Serialize
`json.dumps(identity_document, sort_keys=True, separators=(',',':'),
ensure_ascii=False, allow_nan=False).encode('utf-8')`, no BOM/newline.
`snapshot_id='sha256:'+hashlib.sha256(canonical_bytes).hexdigest()`.
Int/float and signed zero distinct, exact nearby float values distinct. Mapping key
insertion order irrelevant; any valid field change alters content identity. Current
factory rejects unsupported version/rule. Existing fingerprint unchanged. Mapping
cannot detect already-discarded duplicate JSON keys; future parser must reject them
before mapping admission, no such claim here.

**Failure order:** exact document fields; ordered top tokens; anchor type;
observations container/nonempty; per-row mapping/exact fields; ts/close/available
types; grid/close equality/known availability; OHLCV type/sign in open/high/low/close/
volume order; OHLC bounds; source/revision text; provenance exact fields/kind/string
conditional constraints; duplicate then chronology. Canonicalize only after validation.
One ERROR on `quant.engine.research_input` and identical ValueError, success silent,
no payload/actor/reference leakage or broad exception/fallback. Paths use
`observations[i]` (nested `.provenance`). Exact templates:

- `<path> must contain exactly the declared fields` (document/row/provenance).
- `<field> must be <exact token>`; `anchor_ts must be an integer excluding bool`;
  `<path>.<clockfield> must be an integer excluding bool` (available permits None).
- `observations must be a nonempty list or tuple of mappings`;
  `observations[i] must be a mapping`.
- `<path>.ts must align with the declared daily grid`;
  `<path>.close_ts must equal ts plus one day`;
  `<path>.available_ts must be at or after close_ts`.
- `<path>.<pricefield> must be a finite positive int or float excluding bool`;
  `<path>.volume must be a finite nonnegative int or float excluding bool`;
  `<path> must have consistent OHLC bounds`.
- `<path>.<textfield> must be a nonempty UTF-8 string without NUL`.
- `<path>.provenance.kind must be controlled_fixture, researcher_attested, or unknown`;
  `<path>.provenance must match the declared kind and availability`.
- `<path>.ts duplicates an earlier observation`;
  `observations must be strictly chronological`.

**Tests:** hardcoded independent complete canonical bytes and known digest; insertion
order/repeat determinism; int/float/-0.0/nearby float identity; changed payload/clocks/
source/revision/provenance/reference identities; frozen nested records and deep caller
mutation isolation; duplicates/conflicting revisions/order; exact fields/nulls/types/
bool/NaN/inf/grid/OHLC; provenance/delays/claims without eligibility flags; UTF-8,
nonascii/surrogate/NUL; competing-invalid precedence and one exact redacted ERROR.
Arithmetic-built valid ints exceeding 4300 decimal digits must succeed in anchor,
clocks and OHLCV without coercion/runtime settings, including negative huge clocks.
Meaningful public factory coverage of private helpers; no redundant existing matrices.

**Acceptance from root, existing venv:** `python -m ruff check .`;
`python -m mypy --strict backend/src`; `python -m pytest backend/tests -q`;
`git diff --check`; `git status --short`. One completed full suite by doer and fresh
independent reviewer; repeats only justified by corrections/new failures. Preserve
complete failures/output, maximum five loops. One terminal implementation commit:
`feat(engine): preserve immutable research input evidence (Phase 18.2h)`.
Doer never edits STATE or self-accepts. Independent acceptance and separate STATE
commit precede coordinator-authorized PR/checks/merge verification and later readiness.
Readiness changed documentation only; Python suites not run under WORKFLOW §5.
Remaining 18.2 NOT_STARTED, 18.3/18.4 NOT_STARTED, Phase18 IN_PROGRESS,
next_task null, last_completed_task18.2g.1, human_transition_required false.

End of verbatim records moved from STATE.md for 18.2i acceptance on 2026-10-04 Asia/Manila.
