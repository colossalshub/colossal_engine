from __future__ import annotations

from pathlib import Path

import pytest

from quant.data.store import ensure_canonical_bars, upsert_bars
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
