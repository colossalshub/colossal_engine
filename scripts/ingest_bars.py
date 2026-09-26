"""Fetch OHLCV bars from a ccxt exchange and upsert them into DuckDB curated_bars.

Asset-class inference: if ``--asset-class`` is omitted, symbols containing ``/``
(e.g. ``BTC/USDT``) are treated as ``crypto``; all other symbols are ``equity``.

Requires the ingestion extra: ``pip install -e ".[ingestion]"`` (installs ccxt).
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import ccxt

from quant.data.normalize import normalize_timeframe, to_epoch_ms
from quant.data.store import ensure_canonical_bars, upsert_bars
from quant.logging_setup import configure_logging

_MAX_PAGES = 100
_PAGE_LIMIT = 1000
_DATE_ONLY_LEN = 10

logger = logging.getLogger(__name__)


def find_repo_root(start: Path) -> Path:
    """Walk up from ``start`` to the directory that contains ``pyproject.toml``."""
    resolved = start.resolve()
    for directory in (resolved, *resolved.parents):
        if (directory / "pyproject.toml").is_file():
            return directory
    msg = f"Could not find repo root (pyproject.toml) from {start}"
    raise RuntimeError(msg)


def default_db_path() -> Path:
    """Default DuckDB path at ``<repo_root>/data/quant.duckdb``."""
    return find_repo_root(Path(__file__).parent) / "data" / "quant.duckdb"


def infer_asset_class(symbol: str) -> str:
    """Infer asset class from unified symbol shape."""
    return "crypto" if "/" in symbol else "equity"


def parse_cli_timestamp(raw: str) -> int:
    """Parse ISO-8601 date or datetime to epoch ms (plain dates = UTC midnight)."""
    text = raw.strip()
    if len(text) == _DATE_ONLY_LEN and text[4] == "-" and text[7] == "-":
        return to_epoch_ms(f"{text}T00:00:00+00:00")
    return to_epoch_ms(text)


def candle_to_row(
    candle: list[float | int],
    *,
    venue: str,
    symbol: str,
    asset_class: str,
    timeframe: str,
    source: str,
    ingested_at: int,
) -> dict[str, object]:
    """Build a curated_bars row dict from a ccxt OHLCV candle."""
    ts = int(candle[0])
    return {
        "venue": venue,
        "symbol": symbol,
        "asset_class": asset_class,
        "timeframe": timeframe,
        "ts": ts,
        "open": float(candle[1]),
        "high": float(candle[2]),
        "low": float(candle[3]),
        "close": float(candle[4]),
        "volume": float(candle[5]),
        "vwap": None,
        "trades": None,
        "source": source,
        "ingested_at": ingested_at,
    }


def fetch_and_ingest(
    exchange: ccxt.Exchange,
    *,
    venue: str,
    symbol: str,
    ccxt_timeframe: str,
    canonical_timeframe: str,
    asset_class: str,
    start_ms: int,
    end_ms: int,
    db_path: Path,
) -> int:
    """Page ccxt OHLCV and upsert into DuckDB; returns total rows written."""
    ensure_canonical_bars(db_path)
    source = f"ccxt:{venue}"
    total_written = 0
    since = start_ms
    pages = 0

    while since <= end_ms and pages < _MAX_PAGES:
        batch = exchange.fetch_ohlcv(
            symbol,
            ccxt_timeframe,
            since=since,
            limit=_PAGE_LIMIT,
        )
        pages += 1
        if not batch:
            break

        ingested_at = int(time.time() * 1000)
        rows = [
            candle_to_row(
                candle,
                venue=venue,
                symbol=symbol,
                asset_class=asset_class,
                timeframe=canonical_timeframe,
                source=source,
                ingested_at=ingested_at,
            )
            for candle in batch
            if start_ms <= int(candle[0]) <= end_ms
        ]
        total_written += upsert_bars(db_path, rows)

        last_ts = int(batch[-1][0])
        if last_ts >= end_ms:
            break
        since = last_ts + 1

    if pages >= _MAX_PAGES and since <= end_ms:
        logger.warning(
            "Stopped after %s pages (since=%s still <= end_ms=%s)",
            _MAX_PAGES,
            since,
            end_ms,
        )

    return total_written


def build_arg_parser() -> argparse.ArgumentParser:
    """Configure CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Ingest OHLCV bars from a ccxt exchange into curated_bars.",
    )
    parser.add_argument(
        "--venue",
        required=True,
        help="ccxt exchange id, e.g. binance",
    )
    parser.add_argument(
        "--symbol",
        required=True,
        help="Unified ccxt symbol, e.g. BTC/USDT",
    )
    parser.add_argument(
        "--timeframe",
        required=True,
        help="ccxt timeframe token, e.g. 1d",
    )
    parser.add_argument(
        "--start",
        required=True,
        help="ISO-8601 start (inclusive), UTC",
    )
    parser.add_argument("--end", required=True, help="ISO-8601 end (inclusive), UTC")
    parser.add_argument(
        "--db",
        default=None,
        help="DuckDB file path (default: <repo_root>/data/quant.duckdb)",
    )
    parser.add_argument(
        "--asset-class",
        choices=("crypto", "equity", "fx"),
        default=None,
        help="Override inferred asset class",
    )
    return parser


def main() -> None:
    """CLI entrypoint."""
    configure_logging()
    args = build_arg_parser().parse_args()

    try:
        canonical_timeframe = normalize_timeframe(args.timeframe, source="ccxt")
    except ValueError as exc:
        print(exc, file=sys.stderr)  # noqa: T201
        sys.exit(2)

    try:
        start_ms = parse_cli_timestamp(args.start)
        end_ms = parse_cli_timestamp(args.end)
    except (ValueError, TypeError) as exc:
        print(exc, file=sys.stderr)  # noqa: T201
        sys.exit(2)

    if start_ms > end_ms:
        print("--start must be <= --end", file=sys.stderr)  # noqa: T201
        sys.exit(2)

    db_path = Path(args.db) if args.db else default_db_path()
    asset_class = args.asset_class or infer_asset_class(args.symbol)

    try:
        exchange_cls = getattr(ccxt, args.venue)
    except AttributeError:
        print(f"Unknown ccxt venue: {args.venue}", file=sys.stderr)  # noqa: T201
        sys.exit(2)

    exchange = exchange_cls()
    total = fetch_and_ingest(
        exchange,
        venue=args.venue,
        symbol=args.symbol,
        ccxt_timeframe=args.timeframe,
        canonical_timeframe=canonical_timeframe,
        asset_class=asset_class,
        start_ms=start_ms,
        end_ms=end_ms,
        db_path=db_path,
    )

    print(  # noqa: T201
        f"ingested {total} bars: {args.venue} {args.symbol} "
        f"{canonical_timeframe} -> {db_path.resolve()}",
    )


if __name__ == "__main__":
    main()
