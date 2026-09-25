"""End-to-end backtest CLI: Nautilus run → extract equity/metrics/artifacts → meta_runs.

On success, inserts one ``meta_runs`` row with ``status='done'``. Does not implement
the §4.5 queued → running → done worker lifecycle (Phase 7). ``data_snapshot`` is left
NULL until snapshot capture is implemented.
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

from quant.data.normalize import to_epoch_ms
from quant.data.read import read_bars_json
from quant.data.runs_store import RunRecord, init_runs_schema, insert_run
from quant.engine.runner import run_backtest
from quant.extract.artifacts import write_artifacts
from quant.extract.equity import extract_equity
from quant.extract.metrics import TradeSummary, extract_metrics

_DATE_ONLY_LEN = 10

_CANONICAL_TIMEFRAMES = frozenset(
    {"1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1mo"},
)

_TIMEFRAME_TO_NT_UNIT: dict[str, str] = {
    "1m": "1-MINUTE",
    "5m": "5-MINUTE",
    "15m": "15-MINUTE",
    "30m": "30-MINUTE",
    "1h": "1-HOUR",
    "4h": "4-HOUR",
    "1d": "1-DAY",
    "1w": "1-WEEK",
    "1mo": "1-MONTH",
}

_TIMEFRAME_TO_PERIODS_PER_YEAR: dict[str, int] = {
    "1m": 365 * 24 * 60,
    "5m": 365 * 24 * 12,
    "15m": 365 * 24 * 4,
    "30m": 365 * 24 * 2,
    "1h": 365 * 24,
    "4h": 365 * 6,
    "1d": 365,
    "1w": 52,
    "1mo": 12,
}

logger = logging.getLogger(__name__)


def find_repo_root(start: Path) -> Path:
    """Walk up from ``start`` to the directory that contains ``pyproject.toml``."""
    resolved = start.resolve()
    for directory in (resolved, *resolved.parents):
        if (directory / "pyproject.toml").is_file():
            return directory
    msg = f"Could not find repo root (pyproject.toml) from {start}"
    raise RuntimeError(msg)


def parse_cli_timestamp(raw: str) -> int:
    """Parse ISO-8601 date or datetime to epoch ms (plain dates = UTC midnight)."""
    text = raw.strip()
    if len(text) == _DATE_ONLY_LEN and text[4] == "-" and text[7] == "-":
        return to_epoch_ms(f"{text}T00:00:00+00:00")
    return to_epoch_ms(text)


def _git_state(repo_root: Path) -> tuple[str | None, bool]:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        ).stdout.strip()
        porcelain = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        ).stdout
        return sha or None, bool(porcelain.strip())
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        return None, False


def _parse_money_string(value: object) -> float:
    """Parse "-4.41795500 USDT" or 4.417955 or None → float."""
    if value is None:
        return 0.0
    if isinstance(value, int | float):
        return float(value)
    text = str(value).strip()
    if not text:
        return 0.0
    return float(text.split()[0])


def _trade_summaries(position_report: list[dict[str, object]]) -> list[TradeSummary]:
    trades: list[TradeSummary] = []
    for row in position_report:
        avg_px_open = row.get("avg_px_open")
        if avg_px_open is None:
            continue
        trades.append(
            TradeSummary(
                pnl=_parse_money_string(row.get("realized_pnl")),
                duration_s=(
                    float(row["duration_ns"]) / 1e9
                    if row.get("duration_ns") is not None
                    else 0.0
                ),
                entry_px=float(avg_px_open),
                qty=float(row["quantity"]),
            )
        )
    return trades


def _metric_token(value: object) -> str:
    if value is None:
        return "null"
    return str(value)


def build_arg_parser() -> argparse.ArgumentParser:
    """Configure CLI arguments."""
    repo_root = find_repo_root(Path(__file__).parent)
    parser = argparse.ArgumentParser(
        description=(
            "Run a Nautilus backtest and persist meta_runs + parquet artifacts."
        ),
    )
    parser.add_argument("--venue", required=True, help="Venue id, e.g. binance")
    parser.add_argument("--symbol", required=True, help="Unified symbol, e.g. BTC/USDT")
    parser.add_argument(
        "--timeframe",
        required=True,
        help="Canonical timeframe: 1m 5m 15m 30m 1h 4h 1d 1w 1mo",
    )
    parser.add_argument(
        "--start",
        required=True,
        help="ISO-8601 start (inclusive), UTC",
    )
    parser.add_argument("--end", required=True, help="ISO-8601 end (inclusive), UTC")
    parser.add_argument(
        "--strategy",
        default="buy_hold",
        help="Strategy name (default: buy_hold)",
    )
    parser.add_argument(
        "--trade-size",
        default="1",
        help="Trade size in base units (default: 1)",
    )
    parser.add_argument(
        "--starting-balance",
        type=float,
        default=100_000.0,
        help="Starting USDT balance (default: 100000)",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Run display name (auto if omitted)",
    )
    parser.add_argument(
        "--db",
        default=None,
        help=f"DuckDB bars file (default: {repo_root / 'data' / 'quant.duckdb'})",
    )
    parser.add_argument(
        "--runs-db",
        default=None,
        help=f"SQLite meta_runs file (default: {repo_root / 'data' / 'quant.sqlite'})",
    )
    parser.add_argument(
        "--artifacts-dir",
        default=None,
        help=f"Parquet base directory (default: {repo_root / 'data' / 'runs'})",
    )
    return parser


def main() -> None:
    """CLI entrypoint."""
    logging.basicConfig(level=logging.WARNING)
    args = build_arg_parser().parse_args()
    repo_root = find_repo_root(Path(__file__).parent)

    timeframe = args.timeframe.strip()
    if timeframe not in _CANONICAL_TIMEFRAMES:
        print(  # noqa: T201
            f"Invalid timeframe '{timeframe}'; expected one of: "
            f"{', '.join(sorted(_CANONICAL_TIMEFRAMES))}",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        start_ms = parse_cli_timestamp(args.start)
        end_ms = parse_cli_timestamp(args.end)
    except (ValueError, TypeError) as exc:
        print(exc, file=sys.stderr)  # noqa: T201
        sys.exit(2)

    venue = args.venue
    symbol = args.symbol
    strategy = args.strategy
    trade_size = args.trade_size
    starting_balance = args.starting_balance
    name = args.name or f"{strategy} {symbol} {timeframe} {args.start}..{args.end}"

    db_path = Path(args.db) if args.db else repo_root / "data" / "quant.duckdb"
    runs_db_path = (
        Path(args.runs_db) if args.runs_db else repo_root / "data" / "quant.sqlite"
    )
    artifacts_dir = (
        Path(args.artifacts_dir) if args.artifacts_dir else repo_root / "data" / "runs"
    )

    run_id = str(uuid.uuid4())
    base, quote = symbol.split("/")
    instrument_str = f"{base}{quote}.{venue.upper()}"
    nt_unit = _TIMEFRAME_TO_NT_UNIT[timeframe]
    bar_type_str = f"{instrument_str}-{nt_unit}-LAST-EXTERNAL"
    periods_per_year = _TIMEFRAME_TO_PERIODS_PER_YEAR[timeframe]

    git_sha, git_dirty = _git_state(repo_root)

    result = run_backtest(
        venue=venue,
        symbol=symbol,
        bar_type_str=bar_type_str,
        bars_db_path=db_path,
        start_ts=start_ms,
        end_ts=end_ms,
        starting_balance_usdt=starting_balance,
        trade_size=trade_size,
    )

    extraction = extract_equity(result, first_bar_ts=start_ms)
    trades = _trade_summaries(result.position_report)
    metrics = extract_metrics(
        result.portfolio_returns,
        trades,
        periods_per_year=periods_per_year,
        starting_balance=starting_balance,
    )

    price_bars = read_bars_json(
        db_path=db_path,
        venue=venue,
        symbol=symbol,
        timeframe=timeframe,
        start_ts=start_ms,
        end_ts=end_ms,
    )
    artifacts = write_artifacts(
        run_id,
        base_dir=artifacts_dir,
        extraction=extraction,
        price_bars=price_bars,
        position_report=result.position_report,
        fills_report=result.fills_report,
    )

    runs_db = Path(runs_db_path)
    init_runs_schema(runs_db)
    now = int(datetime.now(UTC).timestamp() * 1000)
    record = RunRecord(
        run_id=run_id,
        name=name,
        strategy=strategy,
        params={"trade_size": trade_size, "starting_balance": starting_balance},
        universe=[symbol],
        start_ts=start_ms,
        end_ts=end_ms,
        created_at=now,
        finished_at=now,
        heartbeat_ts=now,
        status="done",
        error=None,
        git_sha=git_sha,
        git_dirty=git_dirty,
        data_snapshot=None,
        seed=0,
        metrics=metrics,
        artifacts=artifacts,
    )
    insert_run(runs_db, record)

    out_artifacts_dir = artifacts_dir / run_id
    print(f"run_id={run_id}")  # noqa: T201
    print(f"artifacts_dir={out_artifacts_dir}")  # noqa: T201
    print(  # noqa: T201
        f"sharpe={_metric_token(metrics.get('sharpe'))}  "
        f"cagr={_metric_token(metrics.get('cagr'))}  "
        f"max_drawdown={_metric_token(metrics.get('max_drawdown'))}",
    )


if __name__ == "__main__":
    main()
