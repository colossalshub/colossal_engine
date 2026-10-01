# Colossal Quant — Project Context
Source of truth for all AI sessions. Read before every response.
Do not deviate from locked decisions without explicit approval.

---

## 1. Mission
A research/backtesting platform that is a **UI layer on top of NautilusTrader**.
We do not build an engine. We build three screens around Nautilus:
- **Command Center** (`/`)         — configure runs, browse history
- **Tear Sheet** (`/runs/:id`)     — detail view of one backtest
- **Data Manager** (`/data`)       — coverage heatmap, ingestion

**Do not build:** backtest engine, fill model, fee model, portfolio simulator,
metrics from raw PnL, charting library, grid library.
**Do build:** extraction (Nautilus → parquet), read API, React screens.

---

## 2. Locked stack
| Layer | Choice |
|---|---|
| Engine | NautilusTrader |
| Backend | FastAPI + Pydantic v2 |
| Store | DuckDB (bars/OLAP) + SQLite (runs/OLTP) |
| Artifacts | Parquet on local disk |
| Frontend | React 18 + Vite + TypeScript |
| Router | React Router v7 |
| Server state | TanStack Query |
| Charts | lightweight-charts |
| Tables | AG Grid (community) |
| Lint py | ruff + mypy strict |
| Lint ts | eslint + tsc strict |
| Tests py | pytest |
| Tests ts | vitest |

### 2.1 Backend extras
Core backend (`pip install -e .`): `fastapi, uvicorn, duckdb, pyarrow, pydantic, nautilus_trader`.
Ingestion extra (`pip install -e ".[ingestion]"`): `ccxt`, `yfinance`.
Broker extra (`pip install -e ".[broker]"`): `ibkr` (only when needed; not required for Phase 1).

Adding a library outside §2 (or these extras) requires explicit approval per §7.

**Timestamps in API:** epoch milliseconds (int64; on SQLite stored as `INTEGER`). Always.
**Timezone:** UTC. Always. No naive datetimes.
**Nulls in JSON:** `null`. Never `NaN`, never empty string.
**CORS origins:** env-driven, `QUANT_CORS_ORIGINS` (comma-separated). No hardcoded origins.

---

## 3. Folder layout
```text
repo/
├── README.md
├── AGENTS.md
├── STATE.md
├── PROJECT.md
├── pyproject.toml
├── .gitignore
├── .cursor/rules/
│   ├── project.mdc
│   ├── backend.mdc
│   └── frontend.mdc
├── docs/
│   ├── ai/                       # workflow, review, incidents, routed guides
│   ├── evidence/                 # historical execution evidence
│   └── specs/                    # gated design specifications
├── backend/
│   ├── src/quant/
│   │   ├── __init__.py           # package root
│   │   ├── config.py             # settings (env-driven)
│   │   ├── data/                 # normalize.py, store.py, read.py
│   │   ├── engine/               # runner.py (thin Nautilus wrapper)
│   │   ├── extract/              # equity.py, artifacts.py
│   │   ├── api/                  # main.py, deps.py, schemas.py, routers/
│   │   └── strategies/           # nautilus Strategy subclasses
│   └── tests/
├── frontend/
│   └── src/
│       ├── main.tsx
│       ├── App.tsx               # router
│       ├── api/                  # client.ts, runs.ts, types.ts
│       ├── pages/
│       │   ├── CommandCenter/    # index.tsx, RunHistoryTable.tsx, StrategyForm.tsx
│       │   ├── TearSheet/        # index.tsx, PriceChart.tsx, EquityCurve.tsx, ...
│       │   └── DataManager/      # index.tsx, CoverageHeatmap.tsx
│       ├── components/
│       │   ├── charts/           # BaseChart.tsx
│       │   ├── grid/             # AgGrid.tsx
│       │   ├── layout/           # Shell.tsx, Sidebar.tsx, TopBar.tsx
│       │   └── ui/               # Card, Badge, EmptyState, Skeleton, KpiCard, VerificationBadge
│       ├── lib/                  # format.ts, colors.ts
│       └── styles/theme.css
├── configs/                      # YAML: universes, strategies
├── data/                         # duckdb + sqlite + parquet (gitignored)
└── scripts/                      # ingest_bars.py, run_backtest.py, run_worker.py, cleanup.py, migrations/
```

## 4. Data contracts

### 4.1 Database schemas

```sql
-- DuckDB (Immutable, analytical data. No lock contention with metadata)
CREATE TABLE curated_bars (
    venue        VARCHAR NOT NULL,       -- binance | yahoo | ibkr
    symbol       VARCHAR NOT NULL,       -- BTC/USDT | AAPL
    asset_class  VARCHAR NOT NULL,       -- crypto | equity | fx
    timeframe    VARCHAR NOT NULL,       -- 1m 5m 15m 30m 1h 4h 1d 1w 1mo
    ts           BIGINT NOT NULL,        -- bar OPEN time, UTC-aware epoch ms
    open  DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE,
    volume DOUBLE, vwap DOUBLE, trades BIGINT,
    source VARCHAR,
    ingested_at  BIGINT,
    PRIMARY KEY (venue, symbol, timeframe, ts)
);

-- SQLite (Transactional state. Polled safely by UI without blocking DuckDB ingestions)
CREATE TABLE meta_runs (
    run_id        TEXT PRIMARY KEY,       -- UUID string
    name          TEXT NOT NULL,
    strategy      TEXT NOT NULL,
    params        TEXT NOT NULL DEFAULT '{}',   -- JSON-encoded
    universe      TEXT NOT NULL DEFAULT '[]',   -- JSON-encoded
    start_ts      INTEGER NOT NULL,       -- epoch ms
    end_ts        INTEGER NOT NULL,       -- epoch ms
    created_at    INTEGER NOT NULL,
    finished_at   INTEGER,
    heartbeat_ts  INTEGER,                -- watchdog to catch crashed runs
    status        TEXT NOT NULL DEFAULT 'queued',  -- queued|running|done|failed|archived
    error         TEXT,
    git_sha       TEXT,                   -- full SHA of HEAD at run creation; NULL if unavailable
    git_dirty     INTEGER DEFAULT 0,      -- boolean: 1 if working tree dirty at creation
    data_snapshot TEXT,                   -- sha256 of "<venue>|<symbol>|<tf>|<max(ts)>" joined for the universe; NULL if uncaptured
    seed          INTEGER DEFAULT 0,      -- RNG seed passed to the strategy; 0 = deterministic default
    metrics       TEXT DEFAULT '{}',      -- JSON-encoded KpiBlock
    artifacts     TEXT DEFAULT '{}'       -- JSON-encoded map<name, relative_path_under_data/runs/{run_id}/>
);
```

**Field semantics**

* `data_snapshot` — fingerprint of the exact ordered bar rows used by the run. The historical max-timestamp formula is deprecated and MUST NOT be used as a reproducibility identity. Phase 14 defines the exact ordered-row fingerprint contract.
* `seed` — RNG seed injected into the strategy. Strategies that don't consume randomness ignore it.
* `git_sha` / `git_dirty` — captured at run creation time from the repo root. `NULL` / `0` when git is unavailable.
* `artifacts` — keys are logical names (`equity`, `drawdown`, `price`, `trades`, `fills`); values are **relative paths** under `data/runs/{run_id}/`. The API is responsible for turning these into URLs if/when needed.

**Migrations** — hand-written `ALTER` scripts live in `scripts/migrations/NNNN_*.sql`, applied idempotently at API startup by `config.py`. No ORM, no autogen.

### 4.2 Timeframe normalization

Canonical tokens: `1m 5m 15m 30m 1h 4h 1d 1w 1mo`

`1m` = 1 minute. `1mo` = 1 month. Never conflate — different bar counts.

| Source | Source token | Canonical |
| --- | --- | --- |
| ccxt | `1M` | `1mo` (case-sensitive!) |
| ccxt | `1m` | `1m` |
| ccxt | `1w` | `1w` |
| yfinance | `1wk` | `1w` |
| yfinance | `1mo` | `1mo` |
| yfinance | `1d` | `1d` |

Map at the adapter boundary. **Reject any token not in the Canonical column loudly** — raise `ValueError`, do not silently pass through.

### 4.3 Nautilus → parquet extraction

Every run writes to `data/runs/{run_id}/`:

| File | Source | Columns |
| --- | --- | --- |
| `equity.parquet` | `portfolio_returns()` + `account_report` | ts, equity, benchmark |
| `drawdown.parquet` | computed from equity | ts, dd (dd in [-1,0]) |
| `price.parquet` | bars fed into engine | ts, open, high, low, close, volume |
| `trades.parquet` | `generate_positions_report()` | see §4.4 Trade |
| `fills.parquet` | `generate_fills_report()` | ts, order_side, last_px, last_qty, commission |

**Equity reconstruction and verification (mandatory — do not trust Nautilus's built-in equity chart):**

The equity series is rebuilt from per-bar snapshots taken inside the strategy:

```text
equity[0] = account_starting_balance
equity[t] = equity[t-1] * (1 + portfolio_returns[t])
```

Two verification modes exist (see §4.4 `Verification.source`):

1. `"account_report"` — reconstruction is compared against Nautilus's authoritative end-of-run account state (USDT cash + base-currency balance marked at the last bar's close). This is the independent check.

```text
discrepancy = abs(reconstructed_final - independent_ending_balance) / independent_ending_balance
verified = discrepancy < 0.005
```

2. `"self_consistent"` — fallback for runs where the account report is unavailable. Reconstruction is compared against the snapshot-derived ending balance. Self-referential; treated as a weaker check.

Store `verified` (bool) and `discrepancy_pct` (the value `discrepancy * 100`, i.e. a percentage where `0.5` means `0.5%`) in the API response. UI shows a badge. See §4.4 `Verification` for units.

**`benchmark`** — controlled by `params["benchmark_symbol"]`. When set to a non-empty symbol that has bars in the same venue and timeframe as the run, the benchmark is a buy-and-hold of that symbol normalized to the starting equity. When empty, or when the symbol has no bars in range, all `EquityPoint.benchmark` values are `null` and the run still succeeds.

### 4.4 API JSON shapes

All timestamps are epoch ms (int64). All nulls are `null`. All key names are `snake_case`. `OHLCV` uses **full field names** to match the parquet and DB schemas.

**Error contract** — every non-2xx response has shape:

```ts
interface ApiError {
  error: {
    code: string;          // stable, SCREAMING_SNAKE: "NOT_FOUND", "VALIDATION", "INTERNAL"
    message: string;       // human-readable, safe to surface
    details?: unknown;     // optional structured payload
  };
}
```

**Pagination contract** — all list endpoints: `page` ≥ 1 (default 1), `page_size` ∈ [1, 500] (default per endpoint). `page` beyond the last page returns `items: []`, `total` unchanged, `200`. Never 404 on empty page.

```ts
// GET /api/runs?strategy=&status=&page=1&page_size=50
interface RunList {
  items: RunSummary[];
  total: number;
  page: number;
  page_size: number;
}

interface RunSummary {
  run_id: string;
  name: string;
  strategy: string;
  universe: string[];
  start_ts: number;
  end_ts: number;
  created_at: number;
  git_sha: string | null;
  git_dirty: boolean;
  status: 'queued' | 'running' | 'done' | 'failed' | 'archived';
  sharpe: number | null;
  cagr: number | null;
  max_drawdown: number | null;   // canonical name; matches KpiBlock
}

// POST /api/runs
interface RunCreate {
  name?: string;
  strategy: string;
  params: Record<string, unknown>;
  universe: string[];
  start_ts: number;
  end_ts: number;
}

// GET /api/runs/{id}/tearsheet
// Note: `markers` is used strictly for chart plotting to avoid relying on paginated trades.
interface TearSheet {
  run: RunSummary;
  params: Record<string, unknown>;
  kpis: KpiBlock;
  equity: EquityPoint[];
  drawdown: DrawdownPoint[];
  price: OHLCV[];
  markers: TradeMarker[];
  monthly_returns: MonthlyReturns[];
  verification: Verification;
  execution_assumptions: ExecutionAssumptions;
  artifacts: Record<string, string>;  // name -> URL served by /api/runs/{id}/artifacts/{name}
}

interface KpiBlock {
  sharpe: number | null; sortino: number | null; cagr: number | null;
  volatility: number | null; max_drawdown: number | null; calmar: number | null;
  win_rate: number | null; profit_factor: number | null; turnover: number | null;
  total_trades: number | null; avg_duration_days: number | null;
}

interface EquityPoint    { ts: number; equity: number; benchmark: number | null; }
interface DrawdownPoint  { ts: number; dd: number; } // dd in [-1, 0]
interface OHLCV {
  ts: number;
  open: number; high: number; low: number; close: number;
  volume: number;
}
interface TradeMarker    { ts: number; side: 'buy' | 'sell'; price: number; qty: number; }
interface MonthlyReturns { year: number; months: (number | null)[]; } // length 12
interface Verification {
  verified: boolean;
  discrepancy_pct: number;   // percentage, e.g. 0.5 means 0.5%
  source: string;            // "account_report" | "self_consistent"
}

// Pinned execution assumptions (Phase 15.2/16.4). Structural fields are
// copied verbatim from `quant.engine.assumptions.CURRENT_ASSUMPTIONS`;
// maker_fee/taker_fee are the effective rates for the specific run.
interface ExecutionAssumptions {
  bar_ts: string;
  nautilus_bar_ts_event: string;
  signal_and_order: string;
  order_type: string;
  sizing_price_when_deploy_pct_positive: string;
  maker_fee_default: string;
  taker_fee_default: string;
  maker_fee: string;
  taker_fee: string;
  fill_model: string;
  latency: string;
  spread: string;
  queue_model: string;
  partial_fills: string;
  equity_ts: string;
  fill_ts: string;
  marker_ts: string;
  fill_included_in_equity: string;
}

// GET /api/runs/{id}/trades?page=1&page_size=100
interface TradePage {
  items: Trade[];
  total: number;
  page: number;
  page_size: number;
}

interface Trade {
  trade_id: string; symbol: string; side: 'long' | 'short';
  entry_ts: number; exit_ts: number | null;
  entry_px: number; exit_px: number | null;
  qty: number; pnl: number; pnl_pct: number;
  fees: number; duration_s: number;
}

// Artifact files are served at:
// GET /api/runs/{id}/artifacts/{name}  -> application/octet-stream (parquet)
// 404 -> ApiError with code "NOT_FOUND"
```

### 4.5 Run execution model

Runs are executed by a **separate worker process**, never inline in the API request.

1. `POST /api/runs` inserts a `meta_runs` row with `status='queued'`, `heartbeat_ts=created_at`, and returns the `run_id` immediately. The API does **not** start the backtest.
2. `scripts/run_worker.py` polls SQLite every 1s for the oldest `status='queued'` row. It atomically flips it to `running`, sets `heartbeat_ts=now()`, and calls `engine.runner`.
3. While the runner is executing, the worker updates `heartbeat_ts=now()` every 5s.
4. On success the worker writes parquet artifacts, populates `metrics` and `artifacts`, sets `status='done'`, `finished_at=now()`.
5. On exception the worker sets `status='failed'` and `error=<traceback summary>`.
6. **Watchdog:** the API's `GET /api/runs` handler and the worker itself check for `status='running' AND heartbeat_ts < now() - 60000`. Those rows are marked `failed` with `error='heartbeat timeout'`. This recovers from a crashed worker without manual intervention.

Only one worker runs at a time. Parallelism is out of scope until §2 is amended.

## 5. Conventions

**Python** — 3.12+, ruff, mypy strict, pydantic v2. Type hints on every function. `logging`, never `print()`. Import from `quant.*`, not relative.

**File I/O** — Any script or module writing to the `data/` directory (or its subdirectories) must explicitly ensure the folder exists using `Path(...).mkdir(parents=True, exist_ok=True)` before writing, as `data/` is gitignored.

**TypeScript & React** — Strict mode, no `any` (use `unknown` and narrow). One component per file, matching filename. Named exports for components, default for pages. `interface` for object shapes. Explicitly handle null states in all visual components (e.g., render gracefully if `benchmark: null` in `EquityCurve`).

**DB access & concurrency**

* **DuckDB:** used strictly for `curated_bars`. Instantiate short-lived connections per request (open → query → close). Never use a global read-only singleton — that causes write-lock errors during ingestion/backtesting. On `TransactionContext Error` during a read, retry up to 3× with 50ms backoff.
* **SQLite:** used for `meta_runs`. One connection per request (WAL mode, `busy_timeout=5000`). Safe for UI polling while DuckDB is locked by the engine.

**Data delivery**

* **Strict sorting:** all time-series data served to the frontend (bars, equity, drawdown, markers) MUST be explicitly deduplicated and strictly sorted by `ORDER BY ts ASC`. lightweight-charts will crash on misordered or duplicated timestamps.
* **Pagination:** see §4.4 — `page` beyond the end returns empty `items`, never 404.

**Both**

* `snake_case` in Python, SQL, JSON keys. `camelCase` for TS vars, `PascalCase` for types/components.
* Frontend API client uses **relative** `/api/*` paths. The Vite dev proxy (Phase 0.3) forwards them to the backend. Never hardcode `http://localhost:8000` in frontend code.
* No premature abstraction — wait for the 2nd use case.

## 6. Roadmap — authoritative phase definitions

This section defines **WHAT** the project must become. `STATE.md` defines **WHERE the project currently is**. `docs/ai/WORKFLOW.md` defines **HOW an agent executes work**. `docs/ai/REVIEWER.md` defines **HOW completed work is accepted**.

### 6.0 Authority and anti-hallucination rules

1. Do not infer the current phase from conversation history, commit messages, README text, old audit reports, or agent memory.
2. Read `STATE.md` before planning or implementing any task.
3. `PROJECT.md` is the permanent specification. `STATE.md` is the mutable execution state.
4. If these files conflict with repository evidence, **STOP** and report the conflict. Do not silently reconcile it.
5. A task is not complete because code exists, tests were added, or an agent says it is complete. Acceptance evidence is required.
6. Do not implement future-phase functionality merely because it would be useful or because a dependency is nearby.
7. Do not duplicate NautilusTrader's event loop, matching, portfolio accounting, commissions, or other responsibilities assigned to Nautilus.
8. Every phase has an explicit goal, non-goals, tasks, acceptance requirements, and completion evidence.
9. Historical notes must be labeled historical. They never override `STATE.md`.
10. When a phase is completed, update `STATE.md` with the evidence before advancing.
11. Commits follow Conventional Commits with the roadmap phase as a parenthetical suffix: `type(scope): description (Phase X.Y)`. See `docs/ai/WORKFLOW.md` §3.

### Phase 0 — Bootstrap

**Goal:** Both servers run locally. Nothing else.

**Tasks:** 0.1 backend/package/gitignore; 0.2 `/health`; 0.3 Vite/React shell and `/api` proxy; 0.4 hello page.

**Acceptance:** backend installs and health endpoint works; frontend starts; repository ignores required generated files; no future-phase scaffolding.

### Phase 1 — Data Layer

**Goal:** Real bars in DuckDB using canonical timeframes.

**Tasks:** 1.1 normalization; 1.2 DuckDB schema/upsert; 1.3 ingestion CLI; 1.4 read layer.

**Acceptance:** canonical timeframe mapping works, invalid tokens fail loudly, bars are stored/read with UTC epoch-ms timestamps.

### Phase 2 — Nautilus Extraction

**Goal:** One backtest produces one coherent artifact set and one run record.

**Tasks:** 2.1 BuyHold strategy; 2.2 Nautilus runner; 2.3 equity reconstruction; 2.4 parquet artifacts; 2.5 synchronous backtest CLI.

**Acceptance:** Nautilus owns simulation; artifacts are written; account/equity reconciliation is tested; run metadata is recorded.

### Phase 3 — Read API

**Goal:** API endpoints return the frozen §4.4 shapes.

**Tasks:** 3.1 Pydantic schemas; 3.2 DB dependencies; 3.3 run listing; 3.4 tear sheet; 3.5 trades; 3.6 router/CORS wiring.

**Acceptance:** all timestamps are epoch ms, all series are ordered, pagination follows §4.4, and field names are not changed for convenience.

### Phase 4 — Frontend Shell + Run History

**Goal:** Navigate between routes and inspect existing runs.

**Tasks:** API types/client; routing; shell; run table; Command Center integration.

**Acceptance:** a real run can be listed and opened without invented data.

### Phase 5 — Tear Sheet Skeleton

**Goal:** Render the core tear sheet using real artifacts/API data.

**Tasks:** fetch/layout, charts, equity, drawdown, price, markers, KPI/ledger surfaces as specified by the existing UI contract.

**Acceptance:** all displayed values originate from API/artifacts; null and empty states are handled.

### Phase 6 — Tear Sheet Polish

**Goal:** Improve visual clarity without changing research semantics.

**Tasks:** crosshair/tooltip behavior, chart synchronization, responsive layout, visual states, formatting.

**Acceptance:** UI changes do not alter backend calculations or artifact contents.

### Phase 7 — Command Center Polish

**Goal:** Make run configuration/history usable without expanding research scope.

**Tasks:** StrategyForm, filters, validation, loading/error states, history interactions.

**Acceptance:** submitted parameters exactly match the API contract and invalid requests fail clearly.

### Phase 8 — Data Manager

**Goal:** Inspect coverage and perform controlled ingestion.

**Tasks:** coverage heatmap, ingestion controls, status/error reporting.

**Acceptance:** ingestion is explicit, canonicalized, and never silently substitutes data.

### Phase 9 — Operational Polish

**Goal:** Make the local research workstation robust.

**Tasks:** worker/watchdog behavior, cleanup/archive, operational errors, final UI states, artifact serving.

**Acceptance:** queued/running/done/failed/archived lifecycle is deterministic and failures are visible.

### Phase 10 — Research Execution Integrity

**Goal:** Establish correct event-driven execution semantics around orders, fills, timestamps, fees, equity, and artifacts.

**Scope:** Nautilus remains the simulation authority. Colossal Quant verifies and extracts behavior; it does not implement a second engine.

**Acceptance:** event ordering, fill-driven strategy state, fee effects, artifact extraction, and account/equity reconciliation are covered by tests/probes appropriate to the actual Nautilus API.

### Phase 11 — Bar-Clock and Phantom-State Integrity

**Goal:** Remove the known phantom order/state problems and establish an explicit bar-close clock contract.

**Important limitation:** Phase 11 does **not** by itself prove elimination of look-ahead bias. Same-bar close execution remains an execution assumption until Phase 15 and causal invariance requires dedicated tests.

**Acceptance:** signal timestamps, order state, fill-driven state transitions, and artifact timestamps are internally coherent; future-bar mutation testing is still required before claiming causal integrity.

### Phase 12 — Fail Closed

**Status target:** P0 research-integrity foundation.

**Goal:** A run cannot quietly produce apparently valid research from invalid data, wrong instrument accounting, truncated ingestion, or a universe the current engine does not actually trade.

**Non-goals:** multi-asset execution, perpetual futures, custom matching, custom portfolio accounting, optimizer, walk-forward, or statistical-model expansion.

#### 12.1 — Instrument Identity

- Verify symbol → instrument → base/quote currency mapping.
- Current supported execution path is one BTC/USDT spot instrument unless the specification is explicitly amended.
- Reject non-supported instruments before backtest execution.
- Do not build a second accounting engine to compensate for an incorrect Nautilus configuration.

**Acceptance:** BTC/USDT works; ETH/USDT and non-USDT quote examples fail closed; no non-BTC run can settle as BTC.

#### 12.2 — OHLCV Integrity

Validate at ingestion/read boundaries as appropriate:

- timestamps are present and finite;
- timestamps are strictly ordered after canonicalization;
- no duplicate primary-key timestamps;
- prices are finite and positive where the instrument contract requires it;
- `high >= max(open, close, low)`;
- `low <= min(open, close, high)`;
- volume is finite and non-negative when supplied;
- no silent dropping, filling, or repair of invalid records.

**Acceptance:** malformed synthetic bars fail with explicit errors; valid bars continue to load unchanged.

#### 12.3 — Ingestion Completeness

- Detect provider/page caps.
- If the requested range may remain incomplete at the ingestion cap, return a non-zero failure or explicit incomplete status.
- Never report a truncated dataset as complete.
- Preserve the requested start/end range in the result.

**Acceptance:** a deliberately capped ingestion cannot produce a successful complete dataset claim.

#### 12.4 — Universe Contract

- Current execution is single-instrument.
- Reject `len(universe) != 1` until Phase 23 explicitly changes the architecture.
- Tear sheet metadata must not claim symbols were traded when only the first symbol was executed.

**Phase 12 completion:** all four tasks implemented, tested, whole-tree acceptance green, and `STATE.md` updated with evidence.

### Phase 12.5 — UI Redesign

**Goal:** Modernize the UI to a light-first dashboard aesthetic: card-
based layouts, tabbed tear sheet navigation, generous whitespace on KPI
surfaces. Keep dark mode available. Fix chart scroll hijacking.

**Non-goals:** research semantics, metric calculations, API contracts.
KPI values, chart data, and grid columns are unchanged.

**Sequencing:** Tasks U.0–U.3.1 ship before Phase 13. Tasks U.3.2
(methodology header) and U.4 (KPI polish) ship after Phase 13, because
Phase 13 changes the KPI semantics (win_rate, profit_factor,
avg_duration_days become null for open positions) and polishing those
cards twice is wasted work. U.3.1 is layout and routing only — it moves
where components render, not what they display, so it is independent of
the KPI change.

**Tasks:**

- **U.0 — Chart scroll fix** — disable wheel-based chart scroll/zoom in
  `BaseChart.tsx`. Preserve drag-to-scale on the price axis and
  pinch-to-zoom on touch. DONE in 12.5.0 + 12.5.0.1.
- **U.1 — Theme foundation** — light + dark token sets in
  `styles/theme.css`, `data-theme` attribute on `<html>`, inline
  pre-mount script in `index.html` to prevent flash, theme toggle in
  TopBar, localStorage persistence, default light. Vitest for the theme
  provider.
- **U.2 — Chart theme migration** — LWC options and AG Grid theme class
  read from active theme. On theme change, call `chart.applyOptions()`
  only — do NOT remount. Series colors (candles, equity line, drawdown,
  markers) are semantic and constant across themes. DONE.
- **U.3.1 — Tear Sheet tabbed layout** — tabbed navigation with nav
  rail. Real tabs: Overview (KPIs + monthly heatmap), Performance
  (price, equity, underwater), Trades (ledger), Data (placeholder).
  Placeholder tabs: Regimes, Robustness, Execution. Removes
  react-grid-layout from the tear sheet. DONE.
- **U.3.2 — Methodology header (deferred to after Phase 13)** — populate
  the Data tab with the reproducibility header: strategy version, git
  SHA, dataset identity, timeframe, fees, benchmark, verification.
- **U.4 — Polish (deferred to after Phase 13)** — KPI card restyle,
  spacing, hover transitions. Also fix: Qty column renders `0.0000`
  instead of `0`; Avg Duration renders `—` when it should show a
  computed value or be removed.
- **U.5 — Grouped KPI cards** — the cards render one group at a time,
  defaulting to Returns. Tear-sheet Overview later moved to
  `OverviewSummary` (16.5.2); the one-group `KpiCards` behavior remains
  for Compare.

**Acceptance:** light theme renders on all three screens; dark theme
renders on all three screens; page scroll is not hijacked by charts;
theme persists across reload without flash; tear sheet fits 1440×900
with one tab visible at a time; all existing frontend tests pass; new
theme-provider test passes.

**Phase 12.5 completion:** all tasks implemented, tested, whole-tree
acceptance green, and `STATE.md` updated with evidence.

### Phase 13 — Closed-Trade Statistics

**Goal:** Trade-level KPIs represent closed trades only.

- Exclude positions without `ts_closed` from win rate, profit factor, and duration calculations.
- Keep unrealized/open-position value in equity/account results.
- Test a BuyHold run that remains open at the end.

**Acceptance:** open-position fees cannot become a synthetic losing trade; closed-trade metrics reconcile with the actual closed position set.

### Phase 14 — Run Identity and Reproducibility

**Goal:** A run records enough identity to determine exactly what code and bars produced it.

- Capture git SHA through UI/worker execution paths.
- Replace the weak max-timestamp dataset identity with a fingerprint of the exact ordered bar rows consumed by the run.
- Record venue, symbol, timeframe, range, strategy, parameters, and experiment identity.
- Make seed semantics honest: a stored seed is only meaningful when randomness can affect execution.
- Add reproducibility tests.

**Acceptance:** changing a historical bar changes the dataset fingerprint; changing only max timestamp is not sufficient; repeated deterministic runs can be compared by identity and artifacts.

### Phase 15 — Execution Assumptions

**Goal:** Make execution assumptions explicit before claiming realistic execution.

Record at minimum:

- bar timestamp convention;
- signal-to-order timing;
- current same-bar close execution behavior;
- fee model/rates and fee currency;
- current zero-slippage/default FillModel behavior;
- absence/presence of latency, spread, queue, and partial-fill assumptions.

**Rule:** Do not implement a custom matcher. If configurable Nautilus execution behavior is required, probe the actual Nautilus API first and delegate execution to Nautilus.

**Acceptance:** tear sheet/run metadata exposes the assumptions; tests pin the current behavior; future-bar mutation does not alter earlier completed artifacts.

### Phase 16 — Clock and Artifact Alignment

**Goal:** Every research artifact uses an explicit and coherent timestamp contract.

Align and test:

- candle open time;
- candle close time;
- signal time;
- order time;
- fill time;
- equity point time;
- trade marker time;
- benchmark time.

No chart should imply that a fill occurred before the information that caused the order existed.

**Target clock (human-confirmed 2026-10-01):** For daily bars, the close
of one bar and the open of the next bar are the same timestamp. The
equity series keeps the account start on the first open and a point on
every bar close, including the first close. The same-bar fill and that
first close share one timestamp, and the equity point at that timestamp
includes the fill.

**Acceptance:** synthetic clock tests prove the intended mapping; benchmark series are aligned to the same research clock; artifact timestamps are documented.

### Phase 16.5 — Tear Sheet Research Report UI

**Goal:** Redesign the Tear Sheet research report UI around the data
the API already provides, without changing KPI values, chart data, or
API contracts.

### Phase 16.5 tasks

- [x] **16.5.1 — Experiment identity header** — COMPLETE
- [x] **16.5.2 — Overview executive summary** — COMPLETE. Headline and secondary KPIs visible together, plus existing equity, drawdown, and monthly heatmap. No new metrics. No rolling series.
- [x] **16.5.3 — Performance investigation layout** — COMPLETE. Existing price, equity, and underwater charts, equity dominant. No rolling Sharpe or volatility unless a series already exists on the tear sheet.
- [x] **16.5.4 — Trades summary** — COMPLETE. Existing closed-trade KPIs above the current ledger. No MAE, MFE, or R-multiple charts.
- [x] **16.5.5 — Data methodology layout** — COMPLETE. Reorganize fields the Data tab already renders, including the recorded equity clock. No new identity fields.
- [x] **16.5.6 — Honest unavailable sections** — COMPLETE. Regimes and Robustness stay empty of fabricated analysis. Execution shows assumptions already on the response, not a cost breakdown.

### Phase 17 — Research Experiment Foundation

**Goal:** Separate research experiments from ordinary run history.

Add explicit metadata for:

- experiment/research group;
- hypothesis identifier;
- strategy/version identity;
- parameter set;
- in-sample range;
- validation range when applicable;
- out-of-sample range when applicable;
- trial index/count when multiple alternatives are tested;
- dataset/code identity.

**Non-goal:** Do not add a parameter optimizer yet.

**Acceptance:** a researcher can distinguish exploratory trials from a designated holdout/OOS run without relying on filenames or memory.

### Phase 18 — OOS and Walk-Forward Validation

**Goal:** Provide explicit temporal validation that prevents the same data interval from being used ambiguously for selection and final evaluation.

- Define IS/validation/OOS semantics.
- Add embargo/gap rules where required by the strategy/data frequency.
- Add walk-forward windows only after the specification is explicit.
- Preserve every window's identity and results.

**Acceptance:** OOS data cannot silently enter parameter selection; window boundaries are testable and reproducible.

### Phase 19 — Multiple Testing and Overfitting Controls

**Goal:** Record and expose the research-selection process rather than treating one winning backtest as independent evidence.

- Track trial groups and candidate counts.
- Record selection criteria.
- Separate exploration from final evaluation.
- Preserve rejected/alternative trials when the experiment requires them.

**Non-goal:** Do not add a decorative “anti-overfitting” checkbox without an underlying research design.

### Phase 20 — Statistical Validation

**Goal:** Make statistical metrics mathematically explicit and appropriately caveated.

- Verify return frequency and annualization assumptions.
- Verify Sharpe/Sortino definitions and risk-free-rate treatment.
- Report sample size and observation window.
- Add confidence/uncertainty methods where specified.
- Account for serial dependence/autocorrelation where appropriate.
- Avoid presenting annualized metrics from tiny samples as evidence of robustness.

**Acceptance:** formulas and units are documented and independently testable.

### Phase 21 — Regime and Robustness Testing

**Goal:** Determine whether research conclusions persist under materially different conditions.

Test, where applicable:

- market regimes;
- costs/fees;
- execution delay;
- spread/slippage assumptions through Nautilus configuration;
- parameter neighborhoods;
- missing-data/gap conditions;
- different but defensible time windows.

Results must preserve the assumptions under which each result was produced.

### Phase 22 — Strategy Research Engine

**Goal:** Move from hardcoded demonstration strategies toward reusable research components.

- Parameterized strategies with explicit schemas.
- Reusable indicators/features.
- Causal signal generation.
- Explicit risk/position-sizing configuration.
- Strategy version identity.

**Rule:** Do not add feature engineering that cannot be traced to information available at the decision timestamp.

### Phase 23 — Portfolio and Multi-Asset Research

**Goal:** Extend from the current one-instrument contract to real multi-instrument research without faking a loop around a single-symbol engine.

- Define instrument/account model.
- Define cross-asset event ordering.
- Define portfolio exposure and capital allocation.
- Delegate matching/account mechanics to Nautilus.
- Extend artifacts and API schemas to represent actual traded instruments.

**Acceptance:** multiple instruments are actually instantiated and traded by the simulation, not merely displayed in metadata.

### Phase 24 — Crypto Derivatives Mechanics

**Goal:** Support perpetual/futures research only after the contract mechanics are specified.

Define and test, as applicable:

- contract size;
- quote/base settlement;
- leverage/margin;
- funding-rate timing and payment;
- liquidation rules;
- mark/index/last-price roles;
- exchange-specific fee semantics.

**Rule:** No perpetual funding/liquidation implementation based on assumptions. Probe the relevant Nautilus APIs and specify the mechanics first.

### Phase 25 — Benchmark and Baseline Framework

**Goal:** Benchmarks become reproducible research baselines with the same timestamp and dataset identity discipline as strategies.

- Define benchmark universe and sizing.
- Align benchmark timestamps to the run clock.
- Preserve benchmark data identity.
- Distinguish benchmark return from strategy equity.
- Test matched buy-and-hold calculations independently.

### Phase 26 — Research Artifact and Reporting System

**Goal:** Every material research conclusion can be traced to code, data, parameters, assumptions, and outputs.

Each report/run should be able to identify:

- code version;
- dataset fingerprint;
- strategy/version;
- parameters;
- experiment/trial group;
- IS/validation/OOS ranges;
- execution assumptions;
- metrics;
- artifacts;
- acceptance/audit status.

### Phase 27 — Backtest/Live Parity

**Goal:** Define shared strategy semantics between research simulation and paper/live execution without duplicating execution engines.

- Shared strategy inputs and decision semantics.
- Explicit market-data normalization.
- Explicit clock and order-state contracts.
- Nautilus/broker adapter boundaries.
- Differences between historical and live execution documented rather than hidden.

### Phase 28 — Paper/Live Research Loop

**Goal:** Move validated research into paper/live observation while preserving the same provenance and audit trail.

- Paper execution before live deployment where required.
- Record live/paper assumptions.
- Compare expected vs observed execution.
- Preserve model/data/code identity.
- Define rollback/disable conditions.

### Phase 29 — Continuous Quant Research Loop

**Goal:** Turn the platform into a repeatable research process rather than a backtest generator.

```text
DATA ACQUISITION
      ↓
DATA VALIDATION
      ↓
DATA FINGERPRINT
      ↓
HYPOTHESIS
      ↓
STRATEGY SPECIFICATION
      ↓
IN-SAMPLE RESEARCH
      ↓
VALIDATION
      ↓
OUT-OF-SAMPLE TEST
      ↓
ROBUSTNESS / REGIME / COST TESTS
      ↓
RESEARCH REVIEW
      ↓
RETAIN / REJECT / REVISE
      ↓
PAPER / LIVE OBSERVATION
      ↓
NEW HYPOTHESIS
```

Every loop iteration must preserve provenance and must not convert exploratory performance into an unqualified claim of predictive validity.

### Phase completion protocol

A phase may move from `READY`/`IN_PROGRESS` to `COMPLETE` only when:

1. All tasks are implemented or explicitly marked not applicable by approved specification change.
2. Required tests exist and test the actual behavior.
3. Whole-tree acceptance commands pass.
4. No undeclared scope changes remain.
5. Any third-party API use was probed according to `docs/ai/WORKFLOW.md`.
6. The agent reports exact changed files and exact acceptance output.
7. `docs/ai/REVIEWER.md` accepts the work.
8. `STATE.md` is updated with the completion evidence.
9. A human-approved transition moves execution to the next phase.

### Continuous audit gates

Mandatory fresh audit gates occur after:

- Phase 11
- Phase 16
- Phase 20
- Phase 24
- Phase 27
- Phase 29

A fresh adversarial research-integrity audit may also be requested at any time. An audit is read-only unless explicitly authorized otherwise.

## 7. AI rules

1. Read `STATE.md`, the relevant `PROJECT.md` sections, and
   `docs/ai/WORKFLOW.md` before implementation. Read
   `docs/ai/REVIEWER.md` when reviewing or preparing acceptance evidence.
2. Never infer the current phase from memory.
3. Never silently resolve contradictions between documentation and code.
4. Stop when a specification is ambiguous or technically disproven.
5. Use the smallest change that satisfies the current task.
6. Do not scaffold future phases.
7. Do not add dependencies without explicit approval.
8. Do not duplicate Nautilus responsibilities.
9. Do not silently change API field names, units, timestamp semantics, or null behavior.
10. Do not claim a research-integrity property merely because a nearby implementation detail exists.
11. Research validity and software correctness are separate acceptance dimensions.
12. Never mark a task complete without evidence.

## 8. Definition of done (per task)

- [ ] Correct phase/task from `STATE.md`
- [ ] Goal and acceptance criteria from `PROJECT.md`
- [ ] Only declared files changed
- [ ] Required tests added/updated
- [ ] Whole-tree acceptance passed where required
- [ ] No unapproved dependency/spec changes
- [ ] Deviations explicitly reported
- [ ] Exact acceptance output recorded
- [ ] Reviewer accepted
- [ ] `STATE.md` updated before advancing

## 9. UI Design

### 9.1 Design principles

- Both light and dark themes are supported via `data-theme` on `<html>`.
  Default: light. Toggle in TopBar. Choice persists via localStorage.
- Chrome is quiet; data is high-contrast. In light mode this means grey
  page background with white content cards. In dark mode this means a
  near-black page with slightly lighter panels.
- Numbers are monospace, tabular, right-aligned in both themes. Font:
  JetBrains Mono, SF Mono, monospace. Always `font-variant-numeric:
  tabular-nums`.
- Color has meaning, not decoration. Green `#22c55e` = profit/buy. Red
  `#ef4444` = loss/sell. Amber `#f59e0b` = warning. Same values in both
  themes.
- Density:
  - Tables and grids: row height 28px, cell padding 8/12px.
  - Sections and cards: 16–24px padding. KPI cards may breathe.
- Borders, not shadows. 1px solid `var(--border)` in both themes.
- Radius: 4px for tables and dense panels; 6px for KPI cards is allowed.
- No animation except status transitions, 120ms hovers, and 150ms tab
  switches.
- Empty states are designed, not blank. Every list/chart has one.
- Every screen fits 1440×900 without horizontal scroll.

### 9.2 Tokens (define once in `styles/theme.css`)

```css
:root,
[data-theme="light"] {
  /* surfaces */
  --bg:        #f7f7f8;
  --panel:     #ffffff;
  --panel-2:   #f4f5f7;
  --border:    #e5e7eb;
  --border-2:  #d1d5db;
  /* text */
  --text:      #111827;
  --text-dim:  #4b5563;
  --text-mute: #9ca3af;
  /* semantic — chart fills and candles (bright) */
  --pos:       #22c55e;
  --neg:       #ef4444;
  --warn:      #f59e0b;
  --accent:    #3b82f6;
  /* semantic — text and numbers (contrast-safe on light bg) */
  --pos-text:  #15803d;
  --neg-text:  #dc2626;
  --warn-text: #b45309;
  /* spacing scale (px) */
  --s-1: 4px; --s-2: 8px; --s-3: 12px; --s-4: 16px; --s-6: 24px;
  /* type scale */
  --fs-xs: 11px; --fs-sm: 12px; --fs-md: 13px;
  --fs-lg: 16px; --fs-xl: 20px; --fs-2xl: 28px;
  /* layout */
  --sidebar-w: 200px;
  --topbar-h:  48px;
  --row-h:     28px;
  --radius:    4px;
}

[data-theme="dark"] {
  /* surfaces */
  --bg:        #0e1117;
  --panel:     #131722;
  --panel-2:   #1a1f2e;
  --border:    #1f2937;
  --border-2:  #2a3441;
  /* text */
  --text:      #d1d5db;
  --text-dim:  #9ca3af;
  --text-mute: #6b7280;
  /* semantic — same as light for fills */
  --pos:       #22c55e;
  --neg:       #ef4444;
  --warn:      #f59e0b;
  --accent:    #3b82f6;
  /* semantic — text on dark bg uses bright colors directly */
  --pos-text:  #22c55e;
  --neg-text:  #ef4444;
  --warn-text: #f59e0b;
}
```

Components that render numbers, badges, or values use `--pos-text` /
`--neg-text` / `--warn-text`. Charts and candle fills use `--pos` /
`--neg`. On dark theme these are identical; on light theme the text
variants are darker to meet WCAG AA contrast (4.5:1).

Font stack: Inter, -apple-system, sans-serif for text. JetBrains Mono for numbers.

### 9.3 Shell layout (applies to all routes)

```text
┌──────────┬──────────────────────────────────────────────────────┐
│          │  TOPBAR (48px) — breadcrumb, status, actions         │
│ SIDEBAR  ├──────────────────────────────────────────────────────┤
│ (200px)  │                                                      │
│          │  <Outlet/> — page content                            │
│  Logo    │                                                      │
│  ────    │                                                      │
│  ▸ Cmd   │                                                      │
│  ▸ Data  │                                                      │
│          │                                                      │
└──────────┴──────────────────────────────────────────────────────┘
```

Sidebar: fixed 200px, `--panel` bg, right border. Nav items: 36px tall, 12px left pad, active item has 2px left accent bar (`--accent`). Two nav items only — Command Center (`/`) and Data (`/data`). Tear Sheet is reached by clicking a row in the history grid; it is not a top-level nav destination. Topbar: breadcrumb left, run-status pill right.

### 9.4 Command Center (`/`)

Two stacked sections, single column, max-width 1200px, centered.

```text
┌─────────────────────────────────────────────────────────────┐
│  NEW RUN                                       [card, panel]│
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │ Strategy ▾   │ lookback [ ] │ skip     [ ] │             │
│  │              │ long_short ☑ │              │             │
│  ├──────────────┴──────────────┴──────────────┤             │
│  │ Universe: [BTC/USDT ✕][ETH/USDT ✕][+ add]  │             │
│  ├──────────────────────────────────────────────┤           │
│  │ Range: [2020-01-01] → [2026-01-01]           │           │
│  ├──────────────────────────────────────────────┤           │
│  │                              [ ▶ RUN ]       │           │
│  └──────────────────────────────────────────────┘           │
├─────────────────────────────────────────────────────────────┤
│  RUN HISTORY                                   [card, panel]│
│  Filter: [strategy▾][status▾][30d▾]        [Compare 2+]     │
│  ┌─────────────────────────────────────────────────────────┐│
│  │☐│Name      │Strategy  │Created│Sharpe│CAGR │MaxDD│Stat ││
│  │…│  (AG Grid, 480px tall, row height 28px)               ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

Form: 2-column grid inside card. Inputs 32px tall. RUN button: `--accent` bg, 40px tall, right-aligned, disabled while submitting. History grid: `ag-theme-quartz-dark`, click row → `/runs/:id`, multi-select → Compare (2 or more).

### 9.5 Tear Sheet (`/runs/:id`)

Single column, full width, vertical scroll. Sections stacked.

```text
┌─────────────────────────────────────────────────────────────┐
│  ← Back   mom-12-1 v4              ● done    [Re-run]       │
│  BTC/USDT · ETH/USDT · 2020-01-01 → 2026-01-01 · git 7a3f9c1│
├─────────────────────────────────────────────────────────────┤
│  KPI STRIP — 11 cards, wrap, 4 per row                      │
│  ┌──────┐┌──────┐┌──────┐┌──────┐                           │
│  │SHARPE││ CAGR ││MAX DD││ VOL  │  ← value 24px mono        │
│  │ 1.42 ││21.4% ││-18.3%││15.1% │  ← label 11px uppercase   │
│  └──────┘└──────┘└──────┘└──────┘    dim, letter-spacing 1px│
├─────────────────────────────────────────────────────────────┤
│  PRICE + FILLS           [chart, 420px, candles + markers]  │
├─────────────────────────────────────────────────────────────┤
│  ┌─── EQUITY (line, 280px) ───┐┌── UNDERWATER (area, 280px)┐│
│  └────────────────────────────┘└───────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│  MONTHLY RETURNS         [custom SVG heatmap, 240px]        │
├─────────────────────────────────────────────────────────────┤
│  TRADE LEDGER            [AG Grid, paginated, 500px]        │
│  Showing 1–50 of 142                     [1 2 3 …] next →   │
└─────────────────────────────────────────────────────────────┘
```

Back button target: `/` (Command Center). Section headers: `--fs-lg`, 16px top pad, 1px bottom border. Every chart wrapped in a `--panel` card with 1px border.

### 9.6 Data Manager (`/data`)

```text
┌─────────────────────────────────────────────────────────────┐
│  COVERAGE                    2020 2021 2022 2023 2024 2025  │
│  BTC/USDT  1d                ████ ████ ████ ████ ████ ████  │
│  BTC/USDT  1h                ████ ████ ████ ████ ████ ████  │
│  ETH/USDT  1d                ████ ████ ░░░░ ████ ████ ████  │
│  AAPL      1d                ████ ████ ████ ████ ████ ████  │
│                                                             │
│  ████ >99%   ▓▓ 75–99%   ░░ <75%   ░ missing                │
├─────────────────────────────────────────────────────────────┤
│  INGESTION                                                  │
│  [Re-ingest BTC/USDT 1d]  [Backfill gaps]  [Full refresh]   │
└─────────────────────────────────────────────────────────────┘
```

Heatmap: SVG, cell 16×16px, gap 1px. One row per `(symbol, timeframe)`, columns are years (not fixed at 7 — width is the distinct year range present in `curated_bars`). Each cell is a year; the tooltip expands to per-month detail: `symbol · timeframe · year · bars · coverage%`.

### 9.7 Chart defaults (lightweight-charts)

Every chart uses these options unless overridden:

```ts
{
  layout: {
    background: { color: '#131722' },
    textColor:  '#9ca3af',
    fontSize:   11,
    fontFamily: 'Inter, sans-serif',
  },
  grid: {
    vertLines: { color: '#1f2937' },
    horzLines: { color: '#1f2937' },
  },
  rightPriceScale: { borderColor: '#1f2937' },
  timeScale:       { borderColor: '#1f2937', timeVisible: true, secondsVisible: false },
  crosshair: {
    mode: 1,
    vertLine: { color: '#6b7280', style: 3 },
    horzLine: { color: '#6b7280', style: 3 },
  },
}
```

**Per-series & tooltips:**

* Candles: up `--pos`, down `--neg`, wick same, border invisible.
* Equity line: `--accent`, lineWidth 2.
* Drawdown area: `--neg`, top `rgba(239,68,68,0.20)`, bottom `rgba(239,68,68,0.02)`.
* Markers: buy = `--pos` arrowUp below bar; sell = `--neg` arrowDown above bar.
* Tooltips: default crosshair labels are insufficient. `BaseChart.tsx` must implement absolutely positioned HTML `<div>` floating tooltips tied to `chart.subscribeCrosshairMove` to display precise OHLCV values.

### 9.8 AG Grid defaults

Theme: `ag-theme-quartz-dark`. Always apply these overrides:

```css
.ag-theme-quartz-dark {
  --ag-background-color:        #131722;
  --ag-foreground-color:        #d1d5db;
  --ag-border-color:            #1f2937;
  --ag-header-background-color: #1a1f2e;
  --ag-header-foreground-color: #9ca3af;
  --ag-row-height:              28px;
  --ag-header-height:           32px;
  --ag-font-size:               12px;
  --ag-font-family:             'JetBrains Mono', monospace;
  --ag-odd-row-background-color: transparent;
  --ag-row-border-color:        #1f2937;
  --ag-cell-horizontal-padding: 12px;
}
```

Rules:

* Numeric columns: `type: 'numericColumn'` → right-align, tabular-nums.
* P&L columns: conditional color (green if > 0, red if < 0).
* No row striping. Borders only.
* Selection: single for history (click → navigate), multiple for compare mode.

### 9.9 State patterns

* **Loading skeleton:** 3 rows of gray shimmer bars at the final height. Never a spinner in the middle of a page.
* **Empty state:** centered, 40px icon (dim), 14px message, optional action button. Examples:
  * No runs: "No backtest runs yet." + [Create your first run]
  * Run queued: "Backtest in progress…" + progress dot animation
  * No trades: "No trades generated for this period."
  * Archived run: "Artifacts expired." + [Re-run]
* **Error state:** red left border, error message, retry button. Never a toast alone — always inline.
* **Status pills:**
  * `queued` → `--text-mute` bg, gray dot
  * `running` → `--accent` bg, pulsing dot
  * `done` → `--pos` bg, checkmark
  * `failed` → `--neg` bg, × mark
  * `archived` → `--text-mute` bg, box icon

### 9.10 Component inventory

| Component | File | Purpose |
| --- | --- | --- |
| Card | `components/ui/Card.tsx` | Panel wrapper, 1px border, 8px pad |
| Badge | `components/ui/Badge.tsx` | Status pill, 5 variants |
| EmptyState | `components/ui/EmptyState.tsx` | Icon + message + action |
| Skeleton | `components/ui/Skeleton.tsx` | Loading shimmer |
| KpiCard | `components/ui/KpiCard.tsx` | Label + value + delta (single presentational card; `TearSheet/KpiCards.tsx` composes them) |
| VerificationBadge | `components/ui/VerificationBadge.tsx` | Equity check badge |
| BaseChart | `components/charts/BaseChart.tsx` | LWC lifecycle wrapper + HTML tooltip |
| AgGrid | `components/grid/AgGrid.tsx` | Themed wrapper + defaults |
| Shell | `components/layout/Shell.tsx` | Sidebar + TopBar + Outlet |
| MonthlyHeatmap | `pages/TearSheet/MonthlyHeatmap.tsx` | Year × 12-month SVG heatmap |
| TradeLedger | `pages/TearSheet/TradeLedger.tsx` | Server-paginated trade table |

*Inventory is not exhaustive — additional presentational components may be added as needed, matching the conventions in §5.*
