"""KPI metrics (§4.4 ``KpiBlock``) from portfolio returns and trade summaries.

Computes Sharpe, Sortino, CAGR, volatility, max drawdown, Calmar, win rate,
profit factor, turnover, total trades, and average trade duration. Pure math —
no I/O.

``periods_per_year`` is supplied by the caller (e.g. 365 for daily crypto
bars, 8760 for hourly). Annualized metrics (Sharpe, Sortino, volatility)
scale with ``sqrt(periods_per_year)``; a wrong value shifts them by a constant
factor.

``starting_balance`` is required to express average equity in dollars for
``turnover`` (total traded notional divided by average dollar equity).

Any metric that cannot be computed is returned as ``None`` — never ``NaN`` or
``inf``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TradeSummary:
    """Minimal shape from §4.4 Trade — the fields metrics actually needs."""

    pnl: float
    duration_s: float
    entry_px: float
    qty: float


def _returns_only(portfolio_returns: list[tuple[int, float]]) -> list[float]:
    return [r for _, r in portfolio_returns]


def _population_std(values: list[float]) -> float:
    n = len(values)
    if n == 0:
        return 0.0
    mean_v = sum(values) / n
    variance = sum((v - mean_v) ** 2 for v in values) / n
    return math.sqrt(variance)


def _sharpe(returns: list[float], periods_per_year: int) -> float | None:
    n = len(returns)
    if n < 2:
        return None
    mean_r = sum(returns) / n
    std_r = _population_std(returns)
    if std_r == 0:
        return None
    return (mean_r / std_r) * math.sqrt(periods_per_year)


def _sortino(returns: list[float], periods_per_year: int) -> float | None:
    n = len(returns)
    if n < 2:
        return None
    mean_r = sum(returns) / n
    downside = [r for r in returns if r < 0]
    if not downside:
        return None
    downside_std = math.sqrt(sum(d ** 2 for d in downside) / n)
    if downside_std == 0:
        return None
    return (mean_r / downside_std) * math.sqrt(periods_per_year)


def _cagr(portfolio_returns: list[tuple[int, float]]) -> float | None:
    n = len(portfolio_returns)
    if n < 2:
        return None
    first_ts = portfolio_returns[0][0]
    last_ts = portfolio_returns[-1][0]
    years = (last_ts - first_ts) / (1000 * 60 * 60 * 24 * 365.25)
    if years <= 0:
        return None
    growth = 1.0
    for _, r in portfolio_returns:
        growth *= 1.0 + r
    if growth <= 0:
        return None
    try:
        cagr = growth ** (1.0 / years) - 1.0
    except OverflowError:
        return None
    if not math.isfinite(cagr):
        return None
    return float(cagr)


def _volatility(returns: list[float], periods_per_year: int) -> float | None:
    n = len(returns)
    if n < 2:
        return None
    return _population_std(returns) * math.sqrt(periods_per_year)


def _max_drawdown(portfolio_returns: list[tuple[int, float]]) -> float | None:
    n = len(portfolio_returns)
    if n < 1:
        return None
    equity = 1.0
    peak = 1.0
    max_dd = 0.0
    for _, r in portfolio_returns:
        equity *= 1.0 + r
        if equity > peak:
            peak = equity
        dd = (equity / peak) - 1.0
        if dd < max_dd:
            max_dd = dd
    return max_dd


def _calmar(cagr: float | None, max_drawdown: float | None) -> float | None:
    if cagr is None or max_drawdown is None or max_drawdown == 0:
        return None
    return cagr / abs(max_drawdown)


def _win_rate(trades: list[TradeSummary]) -> float | None:
    if not trades:
        return None
    wins = sum(1 for t in trades if t.pnl > 0)
    return wins / len(trades)


def _profit_factor(trades: list[TradeSummary]) -> float | None:
    if not trades:
        return None
    gross_profit = sum(t.pnl for t in trades if t.pnl > 0)
    gross_loss = sum(-t.pnl for t in trades if t.pnl < 0)
    if gross_loss == 0:
        return None
    return gross_profit / gross_loss


def _unit_equity_series(portfolio_returns: list[tuple[int, float]]) -> list[float]:
    equity_series = [1.0]
    e = 1.0
    for _, r in portfolio_returns:
        e *= 1.0 + r
        equity_series.append(e)
    return equity_series


def _turnover(
    portfolio_returns: list[tuple[int, float]],
    trades: list[TradeSummary],
    starting_balance: float,
) -> float | None:
    if not trades:
        return None
    equity_series = _unit_equity_series(portfolio_returns)
    avg_equity_unit = sum(equity_series) / len(equity_series)
    avg_equity_dollars = starting_balance * avg_equity_unit
    if avg_equity_dollars == 0:
        return None
    total_notional = sum(abs(t.entry_px * t.qty) for t in trades)
    return total_notional / avg_equity_dollars


def _avg_duration_days(trades: list[TradeSummary]) -> float | None:
    if not trades:
        return None
    avg_s = sum(t.duration_s for t in trades) / len(trades)
    return avg_s / 86400.0


def extract_metrics(
    portfolio_returns: list[tuple[int, float]],
    trades: list[TradeSummary],
    *,
    periods_per_year: int,
    starting_balance: float,
) -> dict[str, Any]:
    returns = _returns_only(portfolio_returns)
    cagr = _cagr(portfolio_returns)
    max_dd = _max_drawdown(portfolio_returns)

    return {
        "sharpe": _sharpe(returns, periods_per_year),
        "sortino": _sortino(returns, periods_per_year),
        "cagr": cagr,
        "volatility": _volatility(returns, periods_per_year),
        "max_drawdown": max_dd,
        "calmar": _calmar(cagr, max_dd),
        "win_rate": _win_rate(trades),
        "profit_factor": _profit_factor(trades),
        "turnover": _turnover(portfolio_returns, trades, starting_balance),
        "total_trades": float(len(trades)),
        "avg_duration_days": _avg_duration_days(trades),
    }
