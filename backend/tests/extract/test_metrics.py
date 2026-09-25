from __future__ import annotations

import json
import math

import pytest

from quant.extract.metrics import TradeSummary, extract_metrics

_MS_PER_YEAR = int(365.25 * 86400 * 1000)
_MS_PER_DAY = 86400 * 1000


def _daily_returns(values: list[float], start_ts: int = 0) -> list[tuple[int, float]]:
    return [(start_ts + i * _MS_PER_DAY, r) for i, r in enumerate(values)]


def _call(
    portfolio_returns: list[tuple[int, float]],
    trades: list[TradeSummary],
    *,
    periods_per_year: int = 252,
    starting_balance: float = 10_000.0,
) -> dict[str, object]:
    return extract_metrics(
        portfolio_returns,
        trades,
        periods_per_year=periods_per_year,
        starting_balance=starting_balance,
    )


def test_empty_inputs() -> None:
    m = _call([], [])
    assert m["total_trades"] == 0.0
    for key in (
        "sharpe",
        "sortino",
        "cagr",
        "volatility",
        "max_drawdown",
        "calmar",
        "win_rate",
        "profit_factor",
        "turnover",
        "avg_duration_days",
    ):
        assert m[key] is None


def test_single_return_annualized_none_max_dd() -> None:
    m = _call([(1000, -0.1)], [])
    assert m["sharpe"] is None
    assert m["sortino"] is None
    assert m["cagr"] is None
    assert m["volatility"] is None
    assert m["max_drawdown"] == pytest.approx(-0.1)
    assert m["total_trades"] == 0.0


def test_constant_returns_zero_vol_sharpe_none() -> None:
    returns = _daily_returns([0.001] * 10)
    m = _call(returns, [], periods_per_year=365)
    assert m["sharpe"] is None
    assert m["volatility"] == pytest.approx(0.0, abs=1e-15)


def test_sharpe_sortino_vol_hand_computed() -> None:
    raw = [0.01, -0.005, 0.02, -0.015, 0.005]
    portfolio_returns = _daily_returns(raw)
    n = len(raw)
    mean_r = sum(raw) / n
    std_r = math.sqrt(sum((r - mean_r) ** 2 for r in raw) / n)
    expected_sharpe = (mean_r / std_r) * math.sqrt(252)
    downside_std = math.sqrt(sum(d ** 2 for d in raw if d < 0) / n)
    expected_sortino = (mean_r / downside_std) * math.sqrt(252)
    expected_vol = std_r * math.sqrt(252)

    m = _call(portfolio_returns, [], periods_per_year=252)
    assert m["sharpe"] == pytest.approx(expected_sharpe, abs=1e-9)
    assert m["sortino"] == pytest.approx(expected_sortino, abs=1e-9)
    assert m["volatility"] == pytest.approx(expected_vol, abs=1e-9)


def test_cagr_one_year() -> None:
    # Two returns over exactly one year; compound growth = 1.10
    r1 = 0.048808848
    r2 = 0.048808848
    assert (1.0 + r1) * (1.0 + r2) == pytest.approx(1.10, rel=1e-6)
    portfolio_returns = [(0, r1), (_MS_PER_YEAR, r2)]
    m = _call(portfolio_returns, [])
    assert m["cagr"] == pytest.approx(0.10, rel=1e-5)


def test_cagr_sub_year_sanity() -> None:
    thirty_days_ms = int(30 * 86400 * 1000)
    portfolio_returns = [(0, 0.01), (thirty_days_ms, 0.0)]
    m = _call(portfolio_returns, [])
    assert m["cagr"] is not None
    assert m["cagr"] >= 0.10


@pytest.mark.parametrize(
    ("returns", "expected_dd"),
    [
        ([0.10, -0.20, 0.15], -0.20),
        ([0.05, 0.10, 0.03], 0.0),
    ],
)
def test_max_drawdown(returns: list[float], expected_dd: float) -> None:
    portfolio_returns = _daily_returns(returns)
    m = _call(portfolio_returns, [])
    assert m["max_drawdown"] == pytest.approx(expected_dd, abs=1e-9)


def test_calmar_ratio() -> None:
    portfolio_returns = [(0, 0.10), (_MS_PER_YEAR, -0.20)]
    m = _call(portfolio_returns, [])
    assert m["cagr"] is not None
    assert m["max_drawdown"] is not None
    assert m["calmar"] == pytest.approx(m["cagr"] / abs(m["max_drawdown"]), abs=1e-9)


def test_calmar_max_dd_zero() -> None:
    portfolio_returns = [(0, 0.05), (_MS_PER_YEAR, 0.05)]
    m = _call(portfolio_returns, [])
    assert m["max_drawdown"] == 0.0
    assert m["calmar"] is None


def test_calmar_cagr_none() -> None:
    m = _call([(1000, 0.01)], [])
    assert m["cagr"] is None
    assert m["calmar"] is None


@pytest.mark.parametrize(
    ("pnls", "expected"),
    [
        ([10.0, -5.0, 20.0], 2 / 3),
        ([1.0, 2.0], 1.0),
        ([], None),
    ],
)
def test_win_rate(pnls: list[float], expected: float | None) -> None:
    trades = [
        TradeSummary(pnl=p, duration_s=0.0, entry_px=1.0, qty=1.0) for p in pnls
    ]
    m = _call([(0, 0.0)], trades)
    if expected is None:
        assert m["win_rate"] is None
    else:
        assert m["win_rate"] == pytest.approx(expected)


@pytest.mark.parametrize(
    ("pnls", "expected"),
    [
        ([50.0, 50.0, -50.0], 2.0),
        ([10.0, 20.0], None),
        ([-10.0], 0.0),
        ([], None),
    ],
)
def test_profit_factor(pnls: list[float], expected: float | None) -> None:
    trades = [
        TradeSummary(pnl=p, duration_s=0.0, entry_px=1.0, qty=1.0) for p in pnls
    ]
    m = _call([(0, 0.0)], trades)
    if expected is None:
        assert m["profit_factor"] is None
    else:
        assert m["profit_factor"] == pytest.approx(expected)


def test_turnover_one_trade() -> None:
    trades = [TradeSummary(pnl=0.0, duration_s=0.0, entry_px=100.0, qty=10.0)]
    m = _call([(1000, 0.0)], trades, starting_balance=1000.0)
    assert m["turnover"] == pytest.approx(1.0)


def test_turnover_empty_trades() -> None:
    m = _call([(0, 0.0)], [])
    assert m["turnover"] is None


def test_avg_duration_days() -> None:
    trades = [
        TradeSummary(pnl=0.0, duration_s=86400.0, entry_px=1.0, qty=1.0),
        TradeSummary(pnl=0.0, duration_s=172800.0, entry_px=1.0, qty=1.0),
    ]
    m = _call([(0, 0.0)], trades)
    assert m["avg_duration_days"] == pytest.approx(1.5)


def test_avg_duration_empty() -> None:
    m = _call([], [])
    assert m["avg_duration_days"] is None


def test_total_trades_reflects_len() -> None:
    trades = [
        TradeSummary(pnl=1.0, duration_s=0.0, entry_px=1.0, qty=1.0),
        TradeSummary(pnl=-1.0, duration_s=0.0, entry_px=1.0, qty=1.0),
    ]
    m = _call([], trades)
    assert m["total_trades"] == 2.0


def test_json_safe() -> None:
    portfolio_returns = _daily_returns([0.01, -0.005, 0.02])
    trades = [
        TradeSummary(pnl=100.0, duration_s=3600.0, entry_px=50.0, qty=2.0),
        TradeSummary(pnl=-30.0, duration_s=7200.0, entry_px=50.0, qty=1.0),
    ]
    payload = extract_metrics(
        portfolio_returns,
        trades,
        periods_per_year=365,
        starting_balance=50_000.0,
    )
    json.dumps(payload)
