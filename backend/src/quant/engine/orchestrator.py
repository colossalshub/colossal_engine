"""Backtest-execution pipeline, callable by both the CLI and the worker.

Extracted from ``scripts/run_backtest.py::main`` (Phase 7.3a). Covers only
the middle of the pipeline: read bars → run the Nautilus backtest → extract
equity/metrics/artifacts → return an updated ``RunRecord``. Does NOT parse
CLI args, does NOT spawn subprocesses, and does NOT write to any database —
the caller (CLI script today, worker in Phase 7.3b) decides what to persist
and how to handle ``status`` transitions.

**Venue:** ``record`` has no top-level ``venue`` field (§4.1). Venue is read
from ``params["venue"]``, defaulting to ``"binance"`` when absent. A non-string
``params["venue"]`` raises ``ValueError``.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import TYPE_CHECKING

from quant.data.read import read_bars_json
from quant.engine.runner import run_backtest
from quant.extract.artifacts import write_artifacts
from quant.extract.equity import extract_equity
from quant.extract.metrics import TradeSummary, extract_metrics

if TYPE_CHECKING:
    from quant.data.runs_store import RunRecord

_DEFAULT_VENUE = "binance"

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


def _as_float(value: object) -> float:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        return float(value)
    msg = f"expected numeric value, got {type(value)!r}"
    raise TypeError(msg)


def _trade_summaries(position_report: list[dict[str, object]]) -> list[TradeSummary]:
    trades: list[TradeSummary] = []
    for row in position_report:
        avg_px_open = row.get("avg_px_open")
        if avg_px_open is None:
            continue
        duration_ns = row.get("duration_ns")
        duration_s = _as_float(duration_ns) / 1e9 if duration_ns is not None else 0.0
        trades.append(
            TradeSummary(
                pnl=_parse_money_string(row.get("realized_pnl")),
                duration_s=duration_s,
                entry_px=_as_float(avg_px_open),
                qty=_as_float(row["quantity"]),
            )
        )
    return trades


def execute_run(
    record: RunRecord,
    *,
    bars_db_path: Path,
    artifacts_dir: Path,
    starting_balance: float = 100_000.0,
    trade_size: str = "1",
    periods_per_year: int | None = None,
) -> RunRecord:
    """Execute a backtest for the given run record.

    Reads bars from ``bars_db_path``, runs the Nautilus backtest, extracts
    equity / metrics / artifacts, and returns a NEW RunRecord with
    ``metrics`` and ``artifacts`` populated. Does NOT write to the DB —
    the caller decides what to persist.

    Reads ``venue`` from ``params["venue"]``, defaulting to ``"binance"`` when
    absent. Raises ValueError if ``params["venue"]`` is present but not a
    string, if no bars are in range, or if the record's ``params`` lack a
    valid timeframe and ``periods_per_year`` cannot be inferred. The caller is
    responsible for updating status='failed' on exception.
    """
    venue_value = record.params.get("venue")
    if venue_value is None:
        venue = _DEFAULT_VENUE
    elif not isinstance(venue_value, str):
        msg = f"record.params['venue'] must be a string, got {type(venue_value)!r}"
        raise ValueError(msg)
    else:
        venue = venue_value

    timeframe = record.params.get("timeframe")
    if not isinstance(timeframe, str) or timeframe not in _CANONICAL_TIMEFRAMES:
        msg = (
            f"record.params['timeframe'] must be one of "
            f"{sorted(_CANONICAL_TIMEFRAMES)}, got {timeframe!r}"
        )
        raise ValueError(msg)

    if not record.universe:
        msg = "record.universe must contain at least one symbol"
        raise ValueError(msg)
    symbol = record.universe[0]

    base, quote = symbol.split("/")
    instrument_str = f"{base}{quote}.{venue.upper()}"
    nt_unit = _TIMEFRAME_TO_NT_UNIT[timeframe]
    bar_type_str = f"{instrument_str}-{nt_unit}-LAST-EXTERNAL"
    resolved_periods_per_year = (
        periods_per_year
        if periods_per_year is not None
        else _TIMEFRAME_TO_PERIODS_PER_YEAR[timeframe]
    )

    result = run_backtest(
        venue=venue,
        symbol=symbol,
        bar_type_str=bar_type_str,
        bars_db_path=bars_db_path,
        start_ts=record.start_ts,
        end_ts=record.end_ts,
        starting_balance_usdt=starting_balance,
        trade_size=trade_size,
    )

    extraction = extract_equity(result, first_bar_ts=record.start_ts)
    trades = _trade_summaries(result.position_report)
    metrics = extract_metrics(
        result.portfolio_returns,
        trades,
        periods_per_year=resolved_periods_per_year,
        starting_balance=starting_balance,
    )

    price_bars = read_bars_json(
        db_path=bars_db_path,
        venue=venue,
        symbol=symbol,
        timeframe=timeframe,
        start_ts=record.start_ts,
        end_ts=record.end_ts,
    )
    artifacts = write_artifacts(
        record.run_id,
        base_dir=artifacts_dir,
        extraction=extraction,
        price_bars=price_bars,
        position_report=result.position_report,
        fills_report=result.fills_report,
    )

    return dataclasses.replace(record, metrics=metrics, artifacts=artifacts)
