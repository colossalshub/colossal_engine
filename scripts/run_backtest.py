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

from quant import config
from quant.data.normalize import to_epoch_ms
from quant.data.runs_store import RunRecord, init_runs_schema, insert_run
from quant.engine.orchestrator import _CANONICAL_TIMEFRAMES, execute_run
from quant.logging_setup import configure_logging

_DATE_ONLY_LEN = 10

logger = logging.getLogger(__name__)


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


def _metric_token(value: object) -> str:
    if value is None:
        return "null"
    return str(value)


def build_arg_parser() -> argparse.ArgumentParser:
    """Configure CLI arguments."""
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
        "--maker-fee",
        default="0.001",
        help="Maker fee as decimal string (default: 0.001 = 0.1%%)",
    )
    parser.add_argument(
        "--taker-fee",
        default="0.001",
        help="Taker fee as decimal string (default: 0.001 = 0.1%%)",
    )
    parser.add_argument(
        "--benchmark-symbol",
        default="",
        help="Benchmark symbol for equity overlay (default: disabled)",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Run display name (auto if omitted)",
    )
    parser.add_argument(
        "--db",
        default=None,
        help=f"DuckDB bars file (default: {config.bars_db_path()})",
    )
    parser.add_argument(
        "--runs-db",
        default=None,
        help=f"SQLite meta_runs file (default: {config.runs_db_path()})",
    )
    parser.add_argument(
        "--artifacts-dir",
        default=None,
        help=f"Parquet base directory (default: {config.artifacts_dir()})",
    )
    return parser


def main() -> None:
    """CLI entrypoint."""
    configure_logging()
    args = build_arg_parser().parse_args()
    repo_root = config.repo_root()

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

    symbol = args.symbol
    strategy = args.strategy
    trade_size = args.trade_size
    starting_balance = args.starting_balance
    name = args.name or f"{strategy} {symbol} {timeframe} {args.start}..{args.end}"

    db_path = Path(args.db) if args.db else config.bars_db_path()
    runs_db_path = Path(args.runs_db) if args.runs_db else config.runs_db_path()
    artifacts_dir = (
        Path(args.artifacts_dir) if args.artifacts_dir else config.artifacts_dir()
    )

    run_id = str(uuid.uuid4())
    git_sha, git_dirty = _git_state(repo_root)

    runs_db = Path(runs_db_path)
    init_runs_schema(runs_db)
    now = int(datetime.now(UTC).timestamp() * 1000)
    record = RunRecord(
        run_id=run_id,
        name=name,
        strategy=strategy,
        params={
            "trade_size": trade_size,
            "starting_balance": starting_balance,
            "timeframe": timeframe,
            "venue": args.venue,
            "maker_fee": args.maker_fee,
            "taker_fee": args.taker_fee,
            "benchmark_symbol": args.benchmark_symbol,
        },
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
    )

    record = execute_run(
        record,
        bars_db_path=db_path,
        artifacts_dir=artifacts_dir,
        starting_balance=starting_balance,
        trade_size=trade_size,
    )
    insert_run(runs_db, record)

    out_artifacts_dir = artifacts_dir / run_id
    print(f"run_id={run_id}")  # noqa: T201
    print(f"artifacts_dir={out_artifacts_dir}")  # noqa: T201
    print(  # noqa: T201
        f"sharpe={_metric_token(record.metrics.get('sharpe'))}  "
        f"cagr={_metric_token(record.metrics.get('cagr'))}  "
        f"max_drawdown={_metric_token(record.metrics.get('max_drawdown'))}",
    )


if __name__ == "__main__":
    main()
