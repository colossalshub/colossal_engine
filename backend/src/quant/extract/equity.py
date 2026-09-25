"""Equity, drawdown, and verification extraction from ``BacktestResult``.

Rebuilds the equity curve from ``portfolio_returns`` (§4.3) and verifies it
against ``ending_balance``. Callers supply ``first_bar_ts`` so bar 1 is
included at ``starting_balance``.
"""

from __future__ import annotations

import bisect
from dataclasses import dataclass

from quant.engine.runner import BacktestResult

_VERIFICATION_SOURCE = "reconstructed_from_portfolio_returns"
_VERIFICATION_THRESHOLD = 0.005


@dataclass(frozen=True)
class EquityPoint:
    ts: int
    equity: float
    benchmark: float | None


@dataclass(frozen=True)
class DrawdownPoint:
    ts: int
    dd: float  # in [-1, 0]


@dataclass(frozen=True)
class Verification:
    verified: bool
    discrepancy_pct: float
    source: str


@dataclass(frozen=True)
class EquityExtraction:
    equity: list[EquityPoint]
    drawdown: list[DrawdownPoint]
    verification: Verification


def _build_equity_series(
    result: BacktestResult,
    first_bar_ts: int,
    benchmark_bars: list[tuple[int, float]] | None,
) -> list[EquityPoint]:
    if result.starting_balance == 0:
        msg = "cannot build equity series: starting_balance is zero"
        raise ValueError(msg)
    if not result.portfolio_returns:
        msg = "cannot build equity series: no returns"
        raise ValueError(msg)

    bench_ts: list[int] = []
    bench_equity: list[float] = []
    if benchmark_bars is not None:
        if len(benchmark_bars) < 2:
            msg = "benchmark_bars must contain at least two bars"
            raise ValueError(msg)
        first_close = benchmark_bars[0][1]
        if first_close == 0:
            msg = "benchmark first close must be non-zero"
            raise ValueError(msg)
        for ts, close in benchmark_bars:
            bench_ts.append(ts)
            bench_equity.append(result.starting_balance * close / first_close)

        equity_last_ts = result.portfolio_returns[-1][0]
        if benchmark_bars[0][0] > first_bar_ts:
            msg = "benchmark bars do not cover equity time range"
            raise ValueError(msg)
        if benchmark_bars[-1][0] < equity_last_ts:
            msg = "benchmark bars do not cover equity time range"
            raise ValueError(msg)

    def benchmark_at(ts: int) -> float | None:
        if benchmark_bars is None:
            return None
        idx = bisect.bisect_right(bench_ts, ts) - 1
        return bench_equity[idx]

    points: list[EquityPoint] = [
        EquityPoint(
            ts=first_bar_ts,
            equity=result.starting_balance,
            benchmark=benchmark_at(first_bar_ts),
        ),
    ]
    prev_equity = result.starting_balance
    for ts, ret in result.portfolio_returns:
        prev_equity *= 1.0 + ret
        points.append(
            EquityPoint(
                ts=ts,
                equity=prev_equity,
                benchmark=benchmark_at(ts),
            ),
        )
    return points


def _verify_ending_balance(result: BacktestResult) -> Verification:
    reconstructed_final = result.starting_balance
    for _, ret in result.portfolio_returns:
        reconstructed_final *= 1.0 + ret

    ending = result.ending_balance
    if ending == 0:
        return Verification(
            verified=True,
            discrepancy_pct=0.0,
            source=_VERIFICATION_SOURCE,
        )

    discrepancy = abs(reconstructed_final - ending) / ending
    verified = discrepancy < _VERIFICATION_THRESHOLD
    discrepancy_pct = discrepancy * 100.0
    return Verification(
        verified=verified,
        discrepancy_pct=discrepancy_pct,
        source=_VERIFICATION_SOURCE,
    )


def _compute_drawdown(equity_points: list[EquityPoint]) -> list[DrawdownPoint]:
    peak = equity_points[0].equity
    drawdown_points: list[DrawdownPoint] = []
    for point in equity_points:
        if point.equity > peak:
            peak = point.equity
        if peak > 0:
            dd = (point.equity / peak) - 1.0
        else:
            dd = 0.0
        dd = min(0.0, max(-1.0, dd))
        drawdown_points.append(DrawdownPoint(ts=point.ts, dd=dd))
    return drawdown_points


def extract_equity(
    result: BacktestResult,
    *,
    first_bar_ts: int,
    benchmark_bars: list[tuple[int, float]] | None = None,
) -> EquityExtraction:
    equity_points = _build_equity_series(result, first_bar_ts, benchmark_bars)
    verification = _verify_ending_balance(result)
    drawdown_points = _compute_drawdown(equity_points)
    return EquityExtraction(
        equity=equity_points,
        drawdown=drawdown_points,
        verification=verification,
    )
