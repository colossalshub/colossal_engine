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
├── PROJECT.md
├── pyproject.toml
├── .gitignore
├── .cursor/rules/
│   ├── project.mdc
│   ├── backend.mdc
│   └── frontend.mdc
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

* `data_snapshot` — fingerprint of the exact bar set used. Computed as `sha256("\n".join(f"{venue}|{symbol}|{tf}|{max_ts}" for each universe entry))`. Enables cache-busting and reproducibility audits.
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

**Equity reconstruction (mandatory — do not trust Nautilus's built-in equity chart):**

```text
equity[0] = account_starting_balance
equity[t] = equity[t-1] * (1 + portfolio_returns[t])
discrepancy = abs(final_reconstructed - account_ending_balance) / ending_balance
verified = discrepancy < 0.005
```

Store `verified` (bool) and `discrepancy_pct` (the value `discrepancy * 100`, i.e. a percentage where `0.5` means `0.5%`) in the API response. UI shows a badge. See §4.4 `Verification` for units.

**`benchmark`** — buy-and-hold of the first symbol in `universe`, normalized to the starting equity, resampled to the run timeframe. `null` when the first symbol has no bars in range.

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
  source: string;            // "reconstructed_from_portfolio_returns"
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

## 6. Roadmap

Each task = one Cursor session = one file + one test.
Do not scaffold ahead. Do not touch other files.

### Phase 0 — Bootstrap

Goal: Both servers run locally. Nothing else.

* **0.1** — `pyproject.toml` with core deps from §2.1 (`fastapi, uvicorn, duckdb, pyarrow, pydantic, nautilus_trader`) and `[project.optional-dependencies]` blocks `ingestion = [ccxt, yfinance]` and `broker = [ibkr]`. Also create the empty package skeleton `backend/src/quant/__init__.py` so setuptools can resolve `packages.find` under `backend/src`. Also create `.gitignore` at the repo root covering: Python caches (`__pycache__/`, `*.py[cod]`, `*.egg-info/`, `.venv/`, `venv/`), tool caches (`.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`), OS files (`.DS_Store`, `Thumbs.db`), environment files (`.env`, `.env.local`, `.env.*.local`; `.env.example` is *not* ignored — it is committed as the template), and future-phase paths (`data/`, `node_modules/`, `frontend/dist/`). → `pip install -e ".[dev]"` succeeds in the repo, and no cache folders appear in `git status`.
* **0.2** — `backend/src/quant/api/main.py` (`GET /health` → `{"status":"ok"}`) → `curl :8000/health`
* **0.3** — `frontend/` via `npm create vite@latest` (React + TS). Install: `react-router-dom`, `@tanstack/react-query`, `lightweight-charts`, `ag-grid-react`, `ag-grid-community`. Configure `vite.config.ts` to proxy `/api` requests to `http://127.0.0.1:8000` to avoid CORS issues locally. **Note:** the `/api` proxy is wired here, but end-to-end verification of `/api/*` routes only succeeds after Phase 3.6 mounts the routers under `/api`. Do NOT add a `/api/health` alias or proxy rewrite — the 404 on `/api/health` until Phase 3.6 is expected. → `npm run dev` opens `:5173`
* **0.4** — `frontend/src/App.tsx` renders "hello" → browser shows "hello"
* **Note (oxlint)** — `create-vite@9` ships `.oxlintrc.json` and an `oxlint` npm script. Keep them. They are not wired into CI and do not conflict with eslint (Phase 4+). Do not remove without re-evaluating §2.

**Done:** both servers run, commit pushed.

### Phase 1 — Data layer

Goal: Real bars in DuckDB, canonical timeframes.

* **1.1** — `data/normalize.py` (`normalize_timeframe`, `to_epoch_ms`) → `pytest tests/data/test_normalize.py`
* **1.2** — `data/store.py` (`init_schema`, `ensure_canonical_bars`, `upsert_bars`) → `pytest tests/data/test_store.py`
* **1.3** — `scripts/ingest_bars.py` (CLI: venue, symbol, tf, range) → ingest BTC/USDT 1d from ccxt
* **1.4** — `data/read.py` (`read_bars_json`) → `pytest tests/data/test_read.py`

**Done:** `SELECT ts, close FROM curated_bars LIMIT 5` returns real numbers (ts is already epoch ms). Ingest 1M from ccxt → stored as `1mo`.

### Phase 2 — Nautilus extraction

Goal: One backtest, one artifact set, one `meta_runs` row.

* **2.1** — `strategies/buy_hold.py` (nautilus Strategy subclass) → import succeeds
* **2.2** — `engine/runner.py` (run backtest, get stats) → `pytest tests/engine/test_runner.py`
* **2.3** — `extract/equity.py` (reconstruct + verify) → `pytest tests/extract/test_equity.py`
* **2.4** — `extract/artifacts.py` (write 5 parquets) → `pytest tests/extract/test_artifacts.py`
* **2.5** — `scripts/run_backtest.py` (run + extract + insert `meta_runs`) → 1 row with metrics

**Done:** `pd.read_parquet('equity.parquet')` returns continuous curve. `meta_runs` has non-null `metrics`.

### Phase 3 — Read API

Goal: Three endpoints return §4.4 shapes.

* **3.1** — `api/schemas.py` (all Pydantic models + `ApiError`) → `pytest tests/api/test_schemas.py`
* **3.2** — `api/deps.py` (DB dependencies: SQLite per-request connection, scoped DuckDB connection) → import succeeds
* **3.3** — `api/routers/runs.py::list_runs` → `curl :8000/api/runs` returns paginated list
* **3.4** — same file, `get_tearsheet` → curl returns full `TearSheet` (MUST `ORDER BY ts ASC`)
* **3.5** — same file, `get_trades` → curl returns paginated `TradePage`
* **3.6** — `api/main.py` wires router + CORS from `QUANT_CORS_ORIGINS`

**Done:** every `ts` field is `int` in curl output. All three match §4.4.

### Phase 4 — Frontend shell + run history

Goal: Navigate, see runs, click one.

* **4.1** — `api/types.ts` (mirror §4.4) → `tsc -b` passes
* **4.2** — `api/client.ts` + `api/runs.ts` (fetch wrappers) → mock call returns data
* **4.3** — `App.tsx` (React Router, 3 routes) → clicking links changes URL
* **4.4** — `components/layout/Shell.tsx` (sidebar + outlet) → renders on all routes
* **4.5** — `pages/CommandCenter/RunHistoryTable.tsx` (AG Grid) → shows real runs
* **4.6** — `pages/CommandCenter/index.tsx` (query + table) → click row navigates to `/runs/:id`

**Done:** click a row → URL changes → page changes.

### Phase 5 — Tear Sheet skeleton

Goal: Six charts render with real data.

* **5.1** — `pages/TearSheet/index.tsx` (fetch + layout)
* **5.2** — `components/charts/BaseChart.tsx` (LWC wrapper, include HTML floating tooltip mapped to crosshair) → renders empty chart
* **5.3** — `pages/TearSheet/PriceChart.tsx` (candles) → no blank canvas
* **5.4** — `pages/TearSheet/KpiCards.tsx` → 11 KPIs from response
* **5.5** — `pages/TearSheet/EquityCurve.tsx` (line) → curve visible
* **5.6** — `pages/TearSheet/DrawdownChart.tsx` (area) → underwater visible

**Done:** charts render with epoch-ms data. No 0-OHLC. No blank canvas.

### Phase 6 — Tear Sheet polish

Goal: Complete tear sheet.

* **6.1** — price chart: fill markers from `TearSheet.markers` array
* **6.2** — `MonthlyHeatmap.tsx` (SVG, custom) → one row per year, 12 months wide
* **6.3** — `TradeLedger.tsx` (AG Grid, server-paginated)
* **6.4** — `VerificationBadge.tsx` reads `verification` block
* **6.5** — `EmptyState.tsx` for `status=queued|running`

**Done:** six charts + ledger + badge render.

### Phase 7 — Command Center polish

Goal: Fire new runs from UI.

- **7.1** — `POST /api/runs` router (inserts `meta_runs` row with `status='queued'`, returns `RunSummary`; does not touch `heartbeat_ts`)
- **7.2** — `StrategyForm.tsx` (strategy + params + universe + date range; submits to 7.1; invalidates runs query on success)
- **7.3** — worker polling + status polling. Frontend polls every 2s for queued/running runs, stops when done. Watchdog per §4.5 fails runs with stale heartbeat.
- **7.4** — Compare view (select 2 or more, side-by-side)

**Done:** submit form → status flips `queued→done` → redirect to tear sheet.

### Phase 8 — Data Manager

Goal: Coverage visibility, ingestion controls.

* **8.1** — `GET /api/data/coverage` (symbol × month completeness)
* **8.2** — `CoverageHeatmap.tsx` (SVG grid)
* **8.3** — `POST /api/data/ingest` (trigger re-ingest)

**Done:** gaps show red, complete shows green. Trigger works.

### Phase 9 — Operational polish

Goal: Fresh clone → working app.

* **9.1** — structured logging on backend
* **9.2** — Error boundaries + friendly errors on frontend
* **9.3** — `.env` config, no hardcoded paths (includes `QUANT_CORS_ORIGINS`). Also commit `.env.example` with placeholder values for every env var the app reads. README (Phase 9.4) documents `cp .env.example .env`.
* **9.4** — `README.md` with setup steps
* **9.5** — `.gitignore` audit: verify every path created since Phase 0 is either tracked or ignored. Add anything new (e.g. `backend/dist/`, `.coverage`, `.env.local`). If a cache or artifact has slipped into git history, run `git rm -r --cached <path>` and commit the removal. Do not create `.gitignore` — it exists from Phase 0.1.
* **9.6** — `scripts/cleanup.py`: purge parquet artifacts older than 30 days. For affected runs, set `status='archived'` and null out the corresponding entries in `artifacts` so the UI renders an "artifacts expired" state instead of a broken link.

**Done:** `git clone && follow README` → running app without disk bloating.

## 7. AI rules

* Read this file before every response.
* One module per session. If a task is too big, split it — but only after updating this file.
* Do not scaffold ahead. Only build the current task.
* Do not refactor adjacent code "while we're here."
* Do not add libraries outside §2 without asking.
* If a request conflicts with §2 or §4, STOP and flag it.
* Every deliverable includes its test. No test → not done.
* If the spec is ambiguous, ask. Do not guess.
* Prefer boring over clever. No premature abstraction.
* Surface errors, don't swallow them. Log + raise.
* Any change to §4.1, §4.3, or §4.4 requires a migration script and a project-version bump.
* `.gitignore` must exist and cover all tool-generated artifacts before the first commit. Never commit `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `__pycache__/`, `node_modules/`, or `data/`.

## 8. Definition of done (per task)

* [ ] File exists at the specified path
* [ ] Contains exactly what the task describes
* [ ] Has at least one test
* [ ] Test passes locally
* [ ] No TODOs left from this task
* [ ] No other files touched

## 9. UI Design

### 9.1 Design principles

* Dark theme only. Traders stare for hours. No light mode toggle.
* Data is bright, chrome is dim. Page bg `#0e1117`, panels `#131722`, borders `#1f2937`, primary text `#d1d5db`, secondary `#9ca3af`.
* Numbers are monospace, tabular, right-aligned. Font: JetBrains Mono, SF Mono, monospace. Always `font-variant-numeric: tabular-nums`.
* Color has meaning, not decoration. Green `#22c55e` = profit/buy. Red `#ef4444` = loss/sell. Amber `#f59e0b` = warning. Never anything else.
* Density over whitespace. Row height 28px. Padding 8/12px. No `padding: 2rem` anywhere.
* Borders, not shadows. 1px solid `#1f2937`. No `box-shadow`.
* Radius max 4px. No pill buttons. No rounded cards.
* No animation except status transitions and 120ms hovers.
* Empty states are designed, not blank. Every list/chart has one.
* Every screen fits 1440×900 without horizontal scroll.

### 9.2 Tokens (define once in `styles/theme.css`)

```css
:root {
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
  /* semantic */
  --pos:       #22c55e;
  --neg:       #ef4444;
  --warn:      #f59e0b;
  --accent:    #3b82f6;
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
```

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
| TradeLedger | `components/grid/TradeLedger.tsx` | Server-paginated trade table |

*Inventory is not exhaustive — additional presentational components may be added as needed, matching the conventions in §5.*