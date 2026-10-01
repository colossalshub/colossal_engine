# Colossal Quant — Local Quant Research Workstation

A personal portfolio and research project built to serve as a local quant research workstation. Configure backtests, browse history, and inspect tear sheets — all running on [NautilusTrader](https://nautilustrader.io/) for the simulation engine.

## What it does

- Configure and fire backtests from a web UI
- Runs execute in the background via a worker process
- Tear sheet shows 11 KPIs, candlestick chart with fills, equity curve, drawdown, monthly heatmap, trade ledger
- Data Manager shows coverage heatmap and lets you ingest more bars via ccxt
- Storage: DuckDB (bars), SQLite (run metadata), Parquet (artifacts)

## Stack

| Layer | Choice |
| --- | --- |
| Engine | NautilusTrader |
| Backend | FastAPI + Pydantic v2 |
| Store | DuckDB (bars) + SQLite (runs) |
| Artifacts | Parquet on local disk |
| Frontend | React 18 + Vite + TypeScript |
| Charts / tables | lightweight-charts, AG Grid |

## Quickstart

Prerequisites: Python 3.12+, Node 20+, git.

### 1. Clone and install the backend

```powershell
git clone https://github.com/colossalshub/colossal_quant
cd colossal_quant
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
# source .venv/bin/activate  # macOS / Linux
pip install -e ".[dev]"
pip install -e ".[ingestion]"
```

### 2. Install the frontend

```powershell
cd frontend
npm install
cd ..
```

### 3. Configure (optional)

Copy `.env.example` to `.env` if you want to override defaults
(data dir, CORS origins, log level). Defaults work without it.

```powershell
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

### 4. Ingest some data

```powershell
python scripts/ingest_bars.py --venue binance --symbol BTC/USDT --timeframe 1d --start 2024-01-01 --end 2024-12-31
```

### 5. Start the API (terminal 1)

```powershell
python -m uvicorn quant.api.main:app --port 8000 --reload
```

In each new terminal, activate the virtual environment again (`.venv\Scripts\Activate.ps1` on Windows).

### 6. Start the frontend (terminal 2)

```powershell
cd frontend
npm run dev
```

### 7. Start the worker (terminal 3)

```powershell
python scripts/run_worker.py
```

### 8. Open the app

http://localhost:5173

## Verify

- API health: `curl http://127.0.0.1:8000/health` → `{"status":"ok"}`
- Backend tests: `python -m pytest backend/tests -q` → all pass
- Frontend tests:

```powershell
cd frontend
npx vitest run
```

## Layout

```text
backend/        FastAPI + NautilusTrader + storage
frontend/       React + Vite + TypeScript
scripts/        CLI entrypoints (ingest, run, worker, cleanup)
data/           DuckDB + SQLite + Parquet (gitignored)
configs/        Universe and strategy YAML (future)
AGENTS.md       Entry point and startup protocol for AI agents
PROJECT.md      Permanent specification, contracts, and complete phase roadmap
STATE.md        Authoritative live execution state
docs/ai/        AI workflow, review playbook, incidents, and routed guides
```

## Documentation authority

For AI-assisted development, the Markdown files have distinct responsibilities:

- `AGENTS.md` is the entry point for AI agents and defines the startup protocol and reading order.
- `PROJECT.md` is the permanent specification and complete phase roadmap.
- `STATE.md` is the authoritative current phase/task state and must be read before work begins.
- `docs/ai/WORKFLOW.md` defines how an agent executes one task at a time.
- `docs/ai/REVIEWER.md` defines how completed work is checked and accepted.
- `docs/ai/INCIDENTS.md` records observed failure patterns and must be read before reviewing any report.
- `docs/ai/guides/` contains subsystem notes loaded only when relevant.
- `README.md` is descriptive/user-facing documentation and must not be used to infer current execution state.

If these files conflict with repository evidence, stop and resolve the conflict rather than guessing.

## Known limitations

- Fees default to 0.001 (0.1%) for `maker_fee` and `taker_fee`, set per run
  from the form or the CLI flags `--maker-fee` and `--taker-fee`.
- Benchmark is optional. Set `benchmark_symbol` on the run. An empty value,
  or no bars for that symbol, leaves the overlay off and the run still succeeds.
- Fill model uses Nautilus's default (fills at bar price, zero slippage).
  Realistic for daily bars; optimistic for intraday.
- `BuyHold` deploys 100% of equity by default. Change "% Deployed" in
  the run form (or `--deploy-pct` on the CLI) to size positions
  differently.
- Single-worker. Only one backtest runs at a time.
- Single-instrument per run. No cross-sectional strategies.
- No walk-forward, no Monte Carlo, no parameter optimization.
- Local-only. No auth, no multi-user, no cloud deployment.
- Personal research project. Built for individual backtesting and portfolio demonstration rather than multi-tenant production use.

## License

MIT — see [LICENSE](LICENSE).

## Scripts

- `scripts/ingest_bars.py` — fetch OHLCV bars from ccxt into DuckDB
- `scripts/run_backtest.py` — run one backtest synchronously (CLI)
- `scripts/run_worker.py` — process queued runs from the SQLite queue
- `scripts/cleanup.py` — purge parquet artifacts older than 30 days (Phase 9.6)
