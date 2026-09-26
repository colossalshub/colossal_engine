# WORKFLOW.md

Companion to `PROJECT.md`. Not a spec — a playbook for how to run the
phases. A fresh AI session should read `PROJECT.md` first, then this file,
then `.cursor/rules/*.mdc`.

---

## 1. Model selection

The right model depends on the task, not the phase. Use this table.

| Task type | Model | Effort | Notes |
|---|---|---|---|
| Scaffolding, boilerplate, config | Composer 2.5 | Default | Fast OFF always |
| Single-file logic with clear spec | Composer 2.5 | Low | Most Phase 1–2 tasks |
| Contract files (schemas, types) | Claude Sonnet 5 | Medium | `schemas.py`, `types.ts` |
| Multi-file routers, DB wiring | Claude Sonnet 5 | Medium | `get_tearsheet`, pagination |
| Complex UI (LWC crosshair, SVG) | Claude Sonnet 5 or Opus | High | `BaseChart.tsx`, `MonthlyHeatmap.tsx` |
| Hard debugging (2 failures) | Claude Opus | High | Escalate only after Sonnet fails |
| API probing (Stage 1) | Composer or Codex CLI | Low | Read-only, no judgment needed |

**Always turn Fast OFF.** Fast costs ~6× for lower latency only — never worth it unless you're actively watching the response stream.

**Never start at Max/Extra High.** Escalate only after lower effort fails.

**Composer's failure mode:** it "improves" specs by normalizing field names, dropping "redundant" validators, or adding "helpful" extras. This is why contract files get Sonnet.

---

## 2. Two-stage prompt pattern

Any task that touches a third-party API (Nautilus, ccxt, pyarrow, FastAPI) gets split into two stages:

**Stage 1 — probe.** Import checks, `inspect.signature`, docstring dumps, live object probes with progressively more kwargs. Report everything verbatim. STOP.

**Human approves.** Adjust Stage 2 based on what the probe found.

**Stage 2 — implement.** Exact calls, pre-verified. If a call fails at runtime, STOP — do not silently adapt.

This pattern saved Phase 2.2 (Nautilus engine construction), Phase 2.2.2 (`portfolio.equity` signature), and Phase 2.4 (Money-string formats). Without it, each task would have been 2 hours of `AttributeError` whack-a-mole.

---

## 3. Phase-splitting rules

- **One file + one test = one commit.** Split if larger.
- If a task needs schema creation + orchestration, split into `.1` / `.2a` / `.2b`.
- If a task needs a bug fix in a prior phase's file to proceed, split into the fix phase + the original phase.
- Documentation and small fixes get suffixes: `Phase 3.1.1`, `Phase 2.2.3`, `Phase 2.1.2`.
- **Commit message format:** `Phase X.Y: description` — no trailing period, no prefixes, no emoji.

---

## 4. Git discipline

- **Never use Cursor's commit UI.** Rule 13. It holds a stale `.git/index.lock` and throws 500 errors. Commit from the terminal.
- **Never let the agent amend without approval.** If it discovers a fix during acceptance, it STOPs and reports. The human decides: amend, fold in, or new mini-phase.
- **One commit per task.** If `pyproject.toml` needs updating mid-task, either include it in the same commit (and note in the report) or create a mini-phase — never an unexplained extra commit.
- **The trailer.** Cursor injects `Co-authored-by: Cursor <cursoragent@cursor.com>` on every commit. Accept it. Fighting it costs more than it saves.

---

## 5. Acceptance discipline (rule 10)

- Acceptance commands run **from the repo root, on the whole tree**, exactly as written in the task prompt.
- Never run on a subset of files.
- If a check fails, report the failure verbatim — **do not silently fix and report green**.
- This rule exists because Phase 1.1 reported `ruff check .` green when the file used `datetime.timezone.utc` (UP017 violation). Phase 1.2's full-tree run caught it. If the rule had been in place earlier, the fix would have been in the original commit.

**Frontend TypeScript (from `frontend/`):**

Note: the root `tsconfig.json` uses project references with `"files": []`. Plain `npx tsc --noEmit` checks nothing. Use `npx tsc -b`.

`tsc -b` follows project references and type-checks every file under `src/`, including test files. The referenced configs already set `noEmit: true`, so `-b` doesn't write output — it's a pure check.

- Standard frontend type-check: `npx tsc -b`

---

## 6. Nautilus 1.231.0 gotchas

Discovered through Phase 2's probes. Do not re-discover these.

### Imports
- `from nautilus_trader.backtest.config import BacktestEngineConfig, BacktestVenueConfig`
- `from nautilus_trader.backtest.engine import BacktestEngine`
- `from nautilus_trader.model.data import Bar, BarType`
- `from nautilus_trader.model.objects import Money, Price, Quantity`

### `BacktestEngine.add_venue` (NOT `add_venue(config)`)
Requires positional args, not a config object:
```python
engine.add_venue(
    venue=Venue("BINANCE"),
    oms_type=oms_type_from_str("NETTING"),
    account_type=account_type_from_str("CASH"),
    starting_balances=[Money.from_str("100000 USDT")],
)
```

### `BacktestVenueConfig` required kwargs
`name, oms_type, account_type, starting_balances`. `starting_balances` accepts strings like `"100000 USDT"` — no explicit `Money()` needed.

### `CurrencyPair` requires 10 positional args
`instrument_id, raw_symbol, base_currency, quote_currency, price_precision, size_precision, price_increment, size_increment, ts_event, ts_init`. `ts_event`/`ts_init` in **nanoseconds** (multiply ms by 1,000,000).

### `Bar` constructor
Keyword args work: `Bar(bar_type=bt, open=Price, high=Price, low=Price, close=Price, volume=Quantity, ts_event=ns, ts_init=ns)`.

### `Portfolio.equity(Venue)` returns `dict[Currency, Money]`
NOT `equity(Currency)`. Get total equity in USDT:
```python
venue_obj = InstrumentId.from_str(self._instrument_id_str).venue
money = self.portfolio.equity(venue_obj)[USDT]
equity = float(money.as_double())
```

### `portfolio.analyzer.portfolio_returns()` returns empty for open positions
For buy-and-hold with an open position in a CASH account, this returns an empty Series and the account report has only 3 rows (all with the same timestamp — start snapshot, end snapshot, BTC snapshot). This is why Phase 2.2.2 moved to per-bar equity snapshots taken inside `BuyHold.on_bar`.

### Retrieve a strategy instance
`engine.trader.strategies()[0]` — `engine.cache.strategies` does not exist.

### Reports have Money-shaped strings
- `realized_pnl` is a string like `"-4.41795500 USDT"` — parse with `float(value.split()[0])`.
- `commissions` is a list of strings — sum after parsing each.
- `commission` (fills) is a string — same parsing.

### Reports have `Timestamp` (UTC-aware, ns precision) and int (ns) columns mixed
- `ts_opened`, `ts_event`, `ts_init` (fills): `pd.Timestamp` → `int(ts.value // 1_000_000)`
- `ts_init`, `ts_last` (positions): raw `int64` nanoseconds → `/ 1_000_000`
- Do not assume consistency between columns or between reports.

### DataFrame index drops on `to_dict(orient="records")`
`generate_positions_report().to_dict(orient="records")` loses `position_id` (the index). **Call `reset_index()` first** — Phase 2.2.3 does this.

### `pandas.Timestamp.utcnow` deprecation warning
Emitted from inside Nautilus's `engine.run()`. Not our code. Ignore until Nautilus updates.

### LWC v5.2.1 specifics

- **Series marker API:** use `createSeriesMarkers(series, markers)` from
  `'lightweight-charts'`. The series object does **not** have a
  `setMarkers` method in v5 — that moved to a plugin API. It returns
  `ISeriesMarkersPluginApi` with `.setMarkers()`, `.markers()`, `.detach()`.
  Chart disposal (`chart.remove()`) handles plugin cleanup; no manual
  `detach()` call is needed for a chart that lives for the component's
  lifetime. Discovered in Phase 6.1 — the original task spec assumed the
  v4 API (`series.setMarkers(...)`), which doesn't exist in v5.

### AG Grid v33+ module registration

- **AG Grid v33+ requires `ModuleRegistry.registerModules([AllCommunityModule])`
  at app initialization (`main.tsx`).** Without it, `AgGridReact` still
  renders rows/columns/sorting/`valueFormatter`/theme CSS variables, but
  features backed by an unregistered module — e.g. `cellStyle` (needs
  `CellStyleModule`, bundled inside `AllCommunityModule`) — **silently
  no-op with no console warning or error**. Discovered in Phase 6.3:
  `TradeLedger.tsx`'s conditional PnL coloring rendered gray instead of
  red/green because this registration call was missing since Phase 4.5
  first wired up AG Grid. Fixed in Phase 6.3.1.

---

## 7. API JSON contract (from `PROJECT.md` §4.4)

Enforced by `backend/src/quant/api/schemas.py` (Phase 3.1). Any field nullability there is the ground truth — if `PROJECT.md` §4.4 disagrees, the schema is correct and §4.4 is stale.

Known §4.4 typo fixed in Phase 3.1.1: `KpiBlock` fields are all `number | null`, not `number`.

---

## 8. Debugging escalation

1. Composer with the full failing output pasted (not summarized).
2. If Composer fails twice, switch to Sonnet Medium.
3. If Sonnet fails twice, Sonnet High effort.
4. If Sonnet still fails, STOP and think — the problem is likely the approach, not the model.
5. Consider Codex CLI as a second opinion if ChatGPT Plus is available.

---

## 9. Anti-patterns to watch for

Things agents have actually tried, that need to be caught:

- **Blanket `# type: ignore` comments on imports.** Configure mypy overrides in `pyproject.toml` instead. Rule 14: every remaining ignore needs a trailing reason comment.
- **Global DB connection singletons.** §5 forbids it. Every request opens and closes its own connection.
- **Scratch files at the repo root.** Rule 11. Use `tmp_path` in tests or a REPL.
- **`pyproject.toml` edits bundled into unrelated commits.** Note them explicitly in the report; if it's a new library, it needs approval.
- **Smoke tests that only check subset of files.** Rule 10. Whole tree, exactly as written.
- **Writing to `data/` in tests.** Every test uses `tmp_path`. Never the real data dir.
- **"Improving" a spec while transcribing.** Composer's failure mode. Verify field names match §4.4 exactly.
- **Adding `/api/health` alias or proxy rewrites to "fix" Phase 0.3.** No — Phase 3.6 mounts the router under `/api`.
- **Scaffolding ahead.** §7. Only build the current task.
- **Screenshot-based browser verification.** Cursor's CDP browser tooling (screenshot, zoom, image-read) consumes context fast and is unreliable on Windows. Instruct agents to verify UI via plain DOM assertions in tests, or by opening the browser manually and describing what they see in text. Never allow screenshot-then-read-image loops in a session.

---

## 10. Environment

- **Python:** 3.14 in the venv (spec says 3.12+; if a package misbehaves, drop to 3.12 in a fresh venv)
- **OS:** Windows (PowerShell 5.x — `&&` is not supported, use `;`)
- **Path issue:** `pip`/`pytest`/`ruff`/`mypy` are not on PATH — use `python -m pip`, `python -m pytest`, etc.
- **Repo root:** `E:\Documents\Projects\colossal_engine`
- **`git status --short` shows `M .cursor/rules/project.mdc`** whenever rules are edited — commit as a mini-phase (`Phase X.Y.1: add rule N`).

---

## 11. State at end of Phase 6

- **Last committed phase:** Phase 6.5 (`f8d6c18` — EmptyState)
- **Next phase:** Phase 7.1 (POST /api/runs router)
- **Phases remaining:** 7.x, 8.x, 9.x
- **Test count:** 105 frontend, 257 backend
- **Real data on disk:** 2 runs, 5 parquets each, 31 BTC/USDT 1d bars