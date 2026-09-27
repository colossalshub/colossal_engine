from __future__ import annotations

from pathlib import Path

import pytest

from quant.data.store import ensure_canonical_bars, upsert_bars
from quant.engine import runner as runner_module
from quant.engine.runner import BacktestResult, run_backtest

_BAR_TYPE = "BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL"
_VENUE = "binance"
_SYMBOL = "BTC/USDT"
_DAY_MS = 86_400_000


def _store_daily_bars(
    db_path: Path,
    *,
    start_ts: int,
    count: int = 10,
) -> tuple[int, int]:
    ensure_canonical_bars(db_path)
    rows: list[dict[str, object]] = []
    for i in range(count):
        ts = start_ts + i * _DAY_MS
        rows.append(
            {
                "venue": _VENUE,
                "symbol": _SYMBOL,
                "asset_class": "crypto",
                "timeframe": "1d",
                "ts": ts,
                "open": 100.0,
                "high": 110.0,
                "low": 90.0,
                "close": 100.0,
                "volume": 1.0,
            }
        )
    upsert_bars(db_path, rows)
    end_ts = start_ts + (count - 1) * _DAY_MS
    return start_ts, end_ts


def test_run_backtest_raises_when_no_bars_in_range(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    ensure_canonical_bars(db_path)
    start_ts = 1_735_689_600_000
    with pytest.raises(ValueError, match="no bars"):
        run_backtest(
            venue=_VENUE,
            symbol=_SYMBOL,
            bar_type_str=_BAR_TYPE,
            bars_db_path=db_path,
            start_ts=start_ts,
            end_ts=start_ts + 9 * _DAY_MS,
        )


def test_run_backtest_happy_path(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    start_ts = 1_735_689_600_000
    start_ts, end_ts = _store_daily_bars(db_path, start_ts=start_ts, count=10)

    result = run_backtest(
        venue=_VENUE,
        symbol=_SYMBOL,
        bar_type_str=_BAR_TYPE,
        bars_db_path=db_path,
        start_ts=start_ts,
        end_ts=end_ts,
    )

    assert isinstance(result, BacktestResult)
    assert len(result.portfolio_returns) >= 9
    second_bar_ts = start_ts + _DAY_MS
    assert result.portfolio_returns[0][0] == second_bar_ts
    ts_values = [pair[0] for pair in result.portfolio_returns]
    assert ts_values == sorted(ts_values)
    assert result.starting_balance == 100_000.0
    assert any(abs(v) > 1e-9 for _, v in result.portfolio_returns)
    assert isinstance(result.ending_balance, float)
    assert result.ending_balance > 55_000
    assert result.ending_balance < 105_000
    assert isinstance(result.account_report, dict)
    assert result.account_report
    assert isinstance(result.position_report, list)
    assert isinstance(result.fills_report, list)


def test_run_backtest_custom_fees_change_pnl(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    start_ts = 1_735_689_600_000
    start_ts, end_ts = _store_daily_bars(db_path, start_ts=start_ts, count=10)

    low_fee = run_backtest(
        venue=_VENUE,
        symbol=_SYMBOL,
        bar_type_str=_BAR_TYPE,
        bars_db_path=db_path,
        start_ts=start_ts,
        end_ts=end_ts,
        maker_fee="0.0001",
        taker_fee="0.0001",
    )
    high_fee = run_backtest(
        venue=_VENUE,
        symbol=_SYMBOL,
        bar_type_str=_BAR_TYPE,
        bars_db_path=db_path,
        start_ts=start_ts,
        end_ts=end_ts,
        maker_fee="0.01",
        taker_fee="0.01",
    )

    assert high_fee.ending_balance < low_fee.ending_balance


def _store_rising_daily_bars(
    db_path: Path,
    *,
    start_ts: int,
    count: int = 10,
) -> tuple[int, int]:
    ensure_canonical_bars(db_path)
    rows: list[dict[str, object]] = []
    for i in range(count):
        ts = start_ts + i * _DAY_MS
        close = 100.0 + float(i)
        rows.append(
            {
                "venue": _VENUE,
                "symbol": _SYMBOL,
                "asset_class": "crypto",
                "timeframe": "1d",
                "ts": ts,
                "open": close,
                "high": close + 10.0,
                "low": close - 10.0,
                "close": close,
                "volume": 1_000_000.0,
            }
        )
    upsert_bars(db_path, rows)
    end_ts = start_ts + (count - 1) * _DAY_MS
    return start_ts, end_ts


def test_run_backtest_higher_deploy_pct_produces_higher_ending_balance(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "bars.duckdb"
    start_ts = 1_735_689_600_000
    start_ts, end_ts = _store_rising_daily_bars(db_path, start_ts=start_ts, count=10)

    low_deploy = run_backtest(
        venue=_VENUE,
        symbol=_SYMBOL,
        bar_type_str=_BAR_TYPE,
        bars_db_path=db_path,
        start_ts=start_ts,
        end_ts=end_ts,
        deploy_pct="0.5",
    )
    high_deploy = run_backtest(
        venue=_VENUE,
        symbol=_SYMBOL,
        bar_type_str=_BAR_TYPE,
        bars_db_path=db_path,
        start_ts=start_ts,
        end_ts=end_ts,
        deploy_pct="1.0",
    )

    assert high_deploy.ending_balance > low_deploy.ending_balance


def test_run_backtest_independent_ending_balance_populated(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    start_ts = 1_735_689_600_000
    start_ts, end_ts = _store_daily_bars(db_path, start_ts=start_ts, count=10)

    result = run_backtest(
        venue=_VENUE,
        symbol=_SYMBOL,
        bar_type_str=_BAR_TYPE,
        bars_db_path=db_path,
        start_ts=start_ts,
        end_ts=end_ts,
    )

    assert result.independent_ending_balance is not None
    assert result.independent_ending_balance > 0.0
    assert result.independent_ending_balance == pytest.approx(
        result.ending_balance, rel=0.05
    )


def test_run_backtest_independent_ending_balance_computed_independently(
    tmp_path: Path,
) -> None:
    """Rising prices: account-report independent equity matches snapshots."""
    db_path = tmp_path / "bars.duckdb"
    start_ts = 1_735_689_600_000
    start_ts, end_ts = _store_rising_daily_bars(db_path, start_ts=start_ts, count=10)

    result = run_backtest(
        venue=_VENUE,
        symbol=_SYMBOL,
        bar_type_str=_BAR_TYPE,
        bars_db_path=db_path,
        start_ts=start_ts,
        end_ts=end_ts,
    )

    assert result.independent_ending_balance is not None
    assert result.ending_balance != 0.0
    relative_diff = abs(
        result.independent_ending_balance - result.ending_balance
    ) / result.ending_balance
    assert relative_diff < 0.01


def test_run_backtest_full_deploy_reconciles_on_flat_prices(tmp_path: Path) -> None:
    """Full deploy on flat bars: independent ending must match snapshot equity."""
    db_path = tmp_path / "bars.duckdb"
    start_ts = 1_735_689_600_000
    start_ts, end_ts = _store_daily_bars(db_path, start_ts=start_ts, count=10)

    result = run_backtest(
        venue=_VENUE,
        symbol=_SYMBOL,
        bar_type_str=_BAR_TYPE,
        bars_db_path=db_path,
        start_ts=start_ts,
        end_ts=end_ts,
        deploy_pct="1.0",
    )

    assert result.independent_ending_balance is not None
    assert result.ending_balance != 0.0
    relative_diff = abs(
        result.independent_ending_balance - result.ending_balance
    ) / result.ending_balance
    assert relative_diff < 0.005


def test_run_backtest_raises_on_invalid_bar_type(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    start_ts = 1_735_689_600_000
    start_ts, end_ts = _store_daily_bars(db_path, start_ts=start_ts, count=10)

    with pytest.raises(ValueError):
        run_backtest(
            venue=_VENUE,
            symbol=_SYMBOL,
            bar_type_str="NOT-A-REAL-BAR-TYPE",
            bars_db_path=db_path,
            start_ts=start_ts,
            end_ts=end_ts,
        )


class _CountingBuyHold(runner_module.BuyHold):  # type: ignore[misc]  # Strategy resolves to Any without stubs
    call_count = 0

    def __init__(self, *args: object, **kwargs: object) -> None:
        _CountingBuyHold.call_count += 1
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]  # forwarding untyped *args/**kwargs to Strategy subclass


class _CountingEmaCross(runner_module.EmaCross):  # type: ignore[misc]  # Strategy resolves to Any without stubs
    call_count = 0

    def __init__(self, *args: object, **kwargs: object) -> None:
        _CountingEmaCross.call_count += 1
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]  # forwarding untyped *args/**kwargs to Strategy subclass


def test_run_backtest_ema_cross_constructs_ema_cross_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "bars.duckdb"
    start_ts = 1_735_689_600_000
    start_ts, end_ts = _store_daily_bars(db_path, start_ts=start_ts, count=10)

    _CountingBuyHold.call_count = 0
    _CountingEmaCross.call_count = 0
    monkeypatch.setattr(runner_module, "BuyHold", _CountingBuyHold)
    monkeypatch.setattr(runner_module, "EmaCross", _CountingEmaCross)

    result = run_backtest(
        venue=_VENUE,
        symbol=_SYMBOL,
        bar_type_str=_BAR_TYPE,
        bars_db_path=db_path,
        start_ts=start_ts,
        end_ts=end_ts,
        strategy="ema_cross",
    )

    assert _CountingEmaCross.call_count == 1
    assert _CountingBuyHold.call_count == 0
    assert isinstance(result, BacktestResult)
    assert len(result.portfolio_returns) + 1 == 10


def test_run_backtest_buy_hold_constructs_buy_hold_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "bars.duckdb"
    start_ts = 1_735_689_600_000
    start_ts, end_ts = _store_daily_bars(db_path, start_ts=start_ts, count=10)

    _CountingBuyHold.call_count = 0
    _CountingEmaCross.call_count = 0
    monkeypatch.setattr(runner_module, "BuyHold", _CountingBuyHold)
    monkeypatch.setattr(runner_module, "EmaCross", _CountingEmaCross)

    result = run_backtest(
        venue=_VENUE,
        symbol=_SYMBOL,
        bar_type_str=_BAR_TYPE,
        bars_db_path=db_path,
        start_ts=start_ts,
        end_ts=end_ts,
        strategy="buy_hold",
    )

    assert _CountingBuyHold.call_count == 1
    assert _CountingEmaCross.call_count == 0
    assert isinstance(result, BacktestResult)
    assert len(result.portfolio_returns) + 1 == 10


def test_run_backtest_unknown_strategy_raises_value_error(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    start_ts = 1_735_689_600_000
    start_ts, end_ts = _store_daily_bars(db_path, start_ts=start_ts, count=10)

    with pytest.raises(ValueError, match="unknown strategy"):
        run_backtest(
            venue=_VENUE,
            symbol=_SYMBOL,
            bar_type_str=_BAR_TYPE,
            bars_db_path=db_path,
            start_ts=start_ts,
            end_ts=end_ts,
            strategy="momentum",
        )
