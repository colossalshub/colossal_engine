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
import logging
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pandas as pd  # type: ignore[import-untyped]  # stubs not in dev deps; pandas via nautilus_trader

from quant.data.fingerprint import fingerprint_bars
from quant.data.read import read_bars_json
from quant.engine.runner import run_backtest
from quant.engine.temporal import validate_research_declaration
from quant.extract.artifacts import write_artifacts
from quant.extract.equity import extract_equity
from quant.extract.metrics import TradeSummary, extract_metrics
from quant.strategies.registry import is_deterministic

if TYPE_CHECKING:
    from quant.data.runs_store import RunRecord

logger = logging.getLogger(__name__)

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

# Epoch-ms length of one bar. ``1mo`` is not listed: its close is open + 30 days (§4.6).
_TIMEFRAME_TO_INTERVAL_MS: dict[str, int] = {
    "1m": 60_000,
    "5m": 5 * 60_000,
    "15m": 15 * 60_000,
    "30m": 30 * 60_000,
    "1h": 60 * 60_000,
    "4h": 4 * 60 * 60_000,
    "1d": 86_400_000,
    "1w": 7 * 86_400_000,
}


def _final_bar_close_ms(open_ms: int, timeframe: str) -> int:
    """Close time (epoch ms) of a final bar whose stored ``ts`` is the open.

    Equity timestamps are bar closes. ``curated_bars.ts`` stays the open, so the
    last stored benchmark timestamp is one interval before the last equity point.
    """
    if timeframe == "1mo":
        return open_ms + (30 * 86_400 * 1_000)
    return open_ms + _TIMEFRAME_TO_INTERVAL_MS[timeframe]


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
                closed=bool(pd.notna(row.get("ts_closed"))),
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
    absent. Reads ``maker_fee`` / ``taker_fee`` from ``params``, each defaulting
    to ``"0.001"`` when absent. Reads ``deploy_pct`` from ``params``, defaulting
    to ``"1.0"`` (100% of equity) when absent; forwarded to ``run_backtest`` /
    the selected strategy for equity-based position sizing. ``record.strategy``
    (``"buy_hold"`` or ``"ema_cross"``) is forwarded to ``run_backtest`` to
    select which Nautilus strategy actually runs. Raises ValueError if
    ``params["venue"]`` is present but not a string, if fee or ``deploy_pct``
    params are present but not strings, if no bars are in range, or if the
    record's ``params`` lack a valid timeframe and ``periods_per_year`` cannot
    be inferred. The caller is responsible for updating status='failed' on
    exception.

    When ``params["benchmark_symbol"]`` is a non-empty string, benchmark bars
    are loaded from the same DuckDB (venue/timeframe as the run) and passed to
    equity extraction; missing or insufficient bars degrade to ``benchmark:
    null`` with a warning, without failing the run.
    """
    validate_research_declaration({
        "research_stage": record.research_stage,
        "in_sample_start_ts": record.in_sample_start_ts,
        "in_sample_end_ts": record.in_sample_end_ts,
        "validation_start_ts": record.validation_start_ts,
        "validation_end_ts": record.validation_end_ts,
        "oos_start_ts": record.oos_start_ts,
        "oos_end_ts": record.oos_end_ts,
    })
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

    maker_fee_raw = record.params.get("maker_fee", "0.001")
    taker_fee_raw = record.params.get("taker_fee", "0.001")
    if not isinstance(maker_fee_raw, str):
        raise ValueError("params['maker_fee'] must be a string")
    if not isinstance(taker_fee_raw, str):
        raise ValueError("params['taker_fee'] must be a string")

    deploy_pct_raw = record.params.get("deploy_pct", "1.0")
    if not isinstance(deploy_pct_raw, str):
        raise ValueError("params['deploy_pct'] must be a string")

    rows = read_bars_json(
        db_path=bars_db_path,
        venue=venue,
        symbol=symbol,
        timeframe=timeframe,
        start_ts=record.start_ts,
        end_ts=record.end_ts,
    )
    if not rows:
        msg = f"no bars in range for {venue} {symbol} {timeframe}"
        raise ValueError(msg)
    snapshot = fingerprint_bars(rows)

    result = run_backtest(
        venue=venue,
        symbol=symbol,
        bar_type_str=bar_type_str,
        rows=rows,
        starting_balance_usdt=starting_balance,
        trade_size=trade_size,
        deploy_pct=deploy_pct_raw,
        maker_fee=maker_fee_raw,
        taker_fee=taker_fee_raw,
        strategy=record.strategy,
    )

    benchmark_symbol_raw = record.params.get("benchmark_symbol", "")
    benchmark_symbol = (
        str(benchmark_symbol_raw) if isinstance(benchmark_symbol_raw, str) else ""
    )

    benchmark_bars: list[tuple[int, float]] | None = None
    if benchmark_symbol:
        benchmark_rows = read_bars_json(
            db_path=bars_db_path,
            venue=venue,
            symbol=benchmark_symbol,
            timeframe=timeframe,
            start_ts=record.start_ts,
            end_ts=record.end_ts,
        )
        if len(benchmark_rows) < 2:
            logger.warning(
                "benchmark %s has %d bars in range, skipping",
                benchmark_symbol,
                len(benchmark_rows),
            )
        else:
            candidate = [
                (int(cast(int, r["ts"])), float(cast(float, r["close"])))
                for r in benchmark_rows
            ]
            first_ts = record.start_ts
            portfolio_returns = result.portfolio_returns
            last_ts = portfolio_returns[-1][0] if portfolio_returns else first_ts
            last_open_ms, last_close_px = candidate[-1]
            last_close_ms = _final_bar_close_ms(last_open_ms, timeframe)
            covers_start = candidate[0][0] <= first_ts
            covers_end = last_open_ms >= last_ts or last_close_ms >= last_ts
            if covers_start and covers_end:
                if last_open_ms >= last_ts:
                    benchmark_bars = candidate
                else:
                    benchmark_bars = [*candidate, (last_close_ms, last_close_px)]
            else:
                logger.warning(
                    "benchmark %s does not cover the equity window, skipping",
                    benchmark_symbol,
                )

    extraction = extract_equity(
        result,
        first_bar_ts=record.start_ts,
        benchmark_bars=benchmark_bars,
    )
    trades = _trade_summaries(result.position_report)
    metrics = extract_metrics(
        result.portfolio_returns,
        trades,
        periods_per_year=resolved_periods_per_year,
        starting_balance=starting_balance,
    )
    # Private key, ignored by KpiBlock/frontend — carries the true (possibly
    # account-report-independent) verification result alongside the KPIs so
    # the tearsheet router can read it without re-deriving it from parquet.
    metrics["_verification"] = {
        "verified": extraction.verification.verified,
        "discrepancy_pct": extraction.verification.discrepancy_pct,
        "source": extraction.verification.source,
    }

    artifacts = write_artifacts(
        record.run_id,
        base_dir=artifacts_dir,
        extraction=extraction,
        price_bars=rows,
        position_report=result.position_report,
        fills_report=result.fills_report,
    )

    seed: int | None
    if is_deterministic(record.strategy):
        seed = None
    else:
        seed_raw = record.params.get("seed", 0)
        seed = int(seed_raw) if isinstance(seed_raw, int | str) else 0

    return dataclasses.replace(
        record,
        metrics=metrics,
        artifacts=artifacts,
        data_snapshot=snapshot,
        seed=seed,
    )
