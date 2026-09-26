from __future__ import annotations

import pytest

from quant.engine.runner import BacktestResult
from quant.extract.equity import extract_equity

_EMPTY_REPORTS: dict[str, object] = {}
_EMPTY_LIST: list[dict[str, object]] = []


def _result(
    *,
    starting_balance: float,
    ending_balance: float,
    portfolio_returns: list[tuple[int, float]],
    independent_ending_balance: float | None = None,
) -> BacktestResult:
    return BacktestResult(
        portfolio_returns=portfolio_returns,
        starting_balance=starting_balance,
        ending_balance=ending_balance,
        independent_ending_balance=independent_ending_balance,
        position_report=_EMPTY_LIST,
        fills_report=_EMPTY_LIST,
        account_report=_EMPTY_REPORTS,
    )


def test_basic_equity_series() -> None:
    second_return = 50.0 / 1050.0
    result = _result(
        starting_balance=1000.0,
        ending_balance=1100.0,
        portfolio_returns=[(2000, 0.05), (3000, second_return)],
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert len(extraction.equity) == 3
    assert extraction.equity[0].ts == 1000
    assert extraction.equity[0].equity == 1000.0
    assert extraction.equity[1].ts == 2000
    assert extraction.equity[1].equity == pytest.approx(1050.0)
    assert extraction.equity[2].equity == pytest.approx(1100.0)


def test_verification_exact_reconstruction() -> None:
    second_return = 50.0 / 1050.0
    result = _result(
        starting_balance=1000.0,
        ending_balance=1100.0,
        portfolio_returns=[(2000, 0.05), (3000, second_return)],
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert extraction.verification.verified is True
    assert extraction.verification.discrepancy_pct < 0.001
    assert extraction.verification.source == "self_consistent"


def test_verification_drifted_ending_balance() -> None:
    second_return = 50.0 / 1050.0
    result = _result(
        starting_balance=1000.0,
        ending_balance=1050.0,
        portfolio_returns=[(2000, 0.05), (3000, second_return)],
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert extraction.verification.verified is False
    assert extraction.verification.discrepancy_pct == pytest.approx(
        4.761904761904762,
        rel=1e-4,
    )


def test_verification_against_account_report_agrees() -> None:
    second_return = 50.0 / 1050.0
    result = _result(
        starting_balance=1000.0,
        ending_balance=1050.0,  # deliberately different from independent
        portfolio_returns=[(2000, 0.05), (3000, second_return)],
        independent_ending_balance=1100.0,
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert extraction.verification.source == "account_report"
    assert extraction.verification.verified is True
    assert extraction.verification.discrepancy_pct < 0.001


def test_verification_against_account_report_flags_discrepancy() -> None:
    second_return = 50.0 / 1050.0
    result = _result(
        starting_balance=1000.0,
        ending_balance=1050.0,
        portfolio_returns=[(2000, 0.05), (3000, second_return)],
        independent_ending_balance=1050.0,
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert extraction.verification.verified is False
    assert extraction.verification.source == "account_report"
    assert extraction.verification.discrepancy_pct > 0.5


def test_verification_falls_back_to_self_consistent_when_independent_none() -> None:
    second_return = 50.0 / 1050.0
    result = _result(
        starting_balance=1000.0,
        ending_balance=1100.0,
        portfolio_returns=[(2000, 0.05), (3000, second_return)],
        independent_ending_balance=None,
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert extraction.verification.source == "self_consistent"


def test_verification_zero_ending_balance() -> None:
    result = _result(
        starting_balance=1000.0,
        ending_balance=0.0,
        portfolio_returns=[(2000, -1.0)],
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert extraction.verification.verified is True
    assert extraction.verification.discrepancy_pct == 0.0


def test_drawdown_rising_equity_all_zero() -> None:
    result = _result(
        starting_balance=100.0,
        ending_balance=121.0,
        portfolio_returns=[(2000, 0.1), (3000, 0.1)],
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert all(p.dd == 0.0 for p in extraction.drawdown)


def test_drawdown_peak_then_drop() -> None:
    # Equity path: 100 -> 110 -> 105 -> 90 -> 95
    r1 = 0.1
    r2 = 105.0 / 110.0 - 1.0
    r3 = 90.0 / 105.0 - 1.0
    r4 = 95.0 / 90.0 - 1.0
    result = _result(
        starting_balance=100.0,
        ending_balance=95.0,
        portfolio_returns=[(2000, r1), (3000, r2), (4000, r3), (5000, r4)],
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    dds = [p.dd for p in extraction.drawdown]
    expected = [
        0.0,
        0.0,
        -0.045454545454545456,
        -0.18181818181818182,
        -0.13636363636363635,
    ]
    assert dds == pytest.approx(expected)


def test_drawdown_recovery_to_new_high() -> None:
    r1 = 0.1
    r2 = 105.0 / 110.0 - 1.0
    r3 = 120.0 / 105.0 - 1.0
    result = _result(
        starting_balance=100.0,
        ending_balance=120.0,
        portfolio_returns=[(2000, r1), (3000, r2), (4000, r3)],
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert extraction.drawdown[-1].dd == 0.0


def test_benchmark_none() -> None:
    result = _result(
        starting_balance=1000.0,
        ending_balance=1100.0,
        portfolio_returns=[(2000, 0.05), (3000, 50.0 / 1050.0)],
    )
    extraction = extract_equity(result, first_bar_ts=1000, benchmark_bars=None)
    assert all(p.benchmark is None for p in extraction.equity)


def test_benchmark_normalized_values() -> None:
    result = _result(
        starting_balance=1000.0,
        ending_balance=900.0,
        portfolio_returns=[(2000, 0.1), (3000, -0.18181818181818182)],
    )
    bars = [(1000, 100.0), (2000, 110.0), (3000, 90.0)]
    extraction = extract_equity(result, first_bar_ts=1000, benchmark_bars=bars)
    benchmarks = [p.benchmark for p in extraction.equity]
    assert benchmarks == pytest.approx([1000.0, 1100.0, 900.0])


def test_benchmark_forward_fill_sparse_bars() -> None:
    result = _result(
        starting_balance=1000.0,
        ending_balance=1100.0,
        portfolio_returns=[(2000, 0.05), (3000, 50.0 / 1050.0)],
    )
    bars = [(1000, 100.0), (3000, 110.0)]
    extraction = extract_equity(result, first_bar_ts=1000, benchmark_bars=bars)
    assert extraction.equity[1].benchmark == pytest.approx(1000.0)


@pytest.mark.parametrize(
    ("benchmark_bars", "first_bar_ts"),
    [
        ([], 1000),
        ([(1000, 100.0)], 1000),
        ([(2000, 100.0), (3000, 110.0)], 1000),
        ([(1000, 100.0), (2000, 110.0)], 1000),
    ],
)
def test_benchmark_raises_when_invalid(
    benchmark_bars: list[tuple[int, float]],
    first_bar_ts: int,
) -> None:
    result = _result(
        starting_balance=1000.0,
        ending_balance=1100.0,
        portfolio_returns=[(2000, 0.05), (3000, 50.0 / 1050.0)],
    )
    with pytest.raises(ValueError):
        extract_equity(result, first_bar_ts=first_bar_ts, benchmark_bars=benchmark_bars)


def test_empty_portfolio_returns_raises() -> None:
    result = _result(
        starting_balance=1000.0,
        ending_balance=1000.0,
        portfolio_returns=[],
    )
    with pytest.raises(ValueError, match="no returns"):
        extract_equity(result, first_bar_ts=1000)


def test_zero_starting_balance_raises() -> None:
    result = _result(
        starting_balance=0.0,
        ending_balance=0.0,
        portfolio_returns=[(2000, 0.0)],
    )
    with pytest.raises(ValueError, match="starting_balance"):
        extract_equity(result, first_bar_ts=1000)
