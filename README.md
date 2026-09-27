# Colossal Quant

A personal portfolio and research project built to serve as a local quant research workstation. Configure backtests, browse historical runs, and inspect tear sheets — with [NautilusTrader](https://nautilustrader.io/) as the simulation engine.

## What it does

* Configure and launch backtests from a web UI
* Execute runs in the background via a worker process
* Tear sheets with 11 KPIs, candlestick charts with fills, equity curves, drawdown, monthly heatmaps, and trade ledgers
* Data Manager with coverage heatmaps and additional bar ingestion via CCXT
* Local storage using DuckDB for market data, SQLite for run metadata, and Parquet for artifacts

## Stack

| Layer           | Choice                        |
| --------------- | ----------------------------- |
| Engine          | NautilusTrader                |
| Backend         | FastAPI + Pydantic v2         |
| Store           | DuckDB (bars) + SQLite (runs) |
| Artifacts       | Parquet on local disk         |
| Frontend        | React 19 + Vite + TypeScript  |
| Charts / Tables | lightweight-charts + AG Grid  |

## Quickstart

### Prerequisites

* Python 3.12+
* Node.js 20+
* Git

### 1. Clone and install the backend

```powershell
git clone https://github.com/colossalshub/colossal_quant
cd colossal_quant

python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
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

Copy `.env.example` to `.env` if you want to override defaults such as the data directory, CORS origins, or log level.

The default configuration works without an `.env` file.

```powershell
copy .env.example .env  # Windows
# cp .env.example .env  # macOS / Linux
```

### 4. Ingest some data

Example:

```powershell
python scripts/ingest_bars.py --venue binance --symbol BTC/USDT --timeframe 1d --start 2024-01-01 --end 2024-12-31
```

### 5. Start the API

In terminal 1:

```powershell
python -m uvicorn quant.api.main:app --port 8000 --reload
```

In each new terminal, activate the virtual environment again:

```powershell
.venv\Scripts\Activate.ps1
```

### 6. Start the frontend

In terminal 2:

```powershell
cd frontend
npm run dev
```

### 7. Start the worker

In terminal 3:

```powershell
python scripts/run_worker.py
```

### 8. Open the app

Open:

http://localhost:5173

## Verify

### API health

```powershell
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### Backend tests

```powershell
python -m pytest backend/tests -q
```

### Frontend tests

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

PROJECT.md      Full specification for the platform
WORKFLOW.md     Playbook for AI collaborators
REVIEWER.md     Playbook for the reviewer role
```

## Known Limitations

* Fees default to `0.001` (0.1%) for `maker_fee` and `taker_fee`, set per run from the form or the CLI flags `--maker-fee` and `--taker-fee`.
* Benchmarking is optional. Set `benchmark_symbol` on the run. An empty value, or no bars for that symbol, leaves the overlay disabled and the run still succeeds.
* The fill model uses NautilusTrader's default behavior (fills at bar price with zero slippage). This can be reasonable for some daily-bar research but is optimistic for intraday simulations.
* `BuyHold` deploys 100% of equity by default. Change `% Deployed` in the run form, or use `--deploy-pct` on the CLI, to size positions differently.
* Single-worker architecture: only one backtest runs at a time.
* Single-instrument per run: cross-sectional strategies are not currently supported.
* No walk-forward analysis, Monte Carlo simulation, or parameter optimization.
* Local-only: no authentication, multi-user support, or cloud deployment.
* Personal research project: built for individual backtesting and portfolio demonstration rather than multi-tenant production use.

## Scripts

* `scripts/ingest_bars.py` — fetch OHLCV bars from CCXT into DuckDB
* `scripts/run_backtest.py` — run one backtest synchronously from the CLI
* `scripts/run_worker.py` — process queued runs from the SQLite queue
* `scripts/cleanup.py` — purge Parquet artifacts older than 30 days (Phase 9.6)

## License

Copyright (C) 2026 Michael Angelo Calupas Gamet

This project is licensed under the **GNU General Public License v3.0**.

See [`LICENSE`](LICENSE) for the complete license terms.

## Disclaimer

Colossal Quant is a personal quantitative research and backtesting project.

Backtest results are not guarantees of future performance. The software may contain bugs, implementation limitations, data-quality issues, or modeling assumptions that can affect results.

The project is provided as-is and is not intended to provide financial, investment, or trading advice.