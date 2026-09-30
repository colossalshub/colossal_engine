from __future__ import annotations

import pytest
from pandas import Timestamp

from quant.engine.runner import run_backtest
from quant.extract.equity import extract_equity

_BAR_TYPE = "BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL"
_START_TS = 1_735_689_600_000
_FIRST_BAR_CLOSE_TS = 1_735_776_000_000
_SECOND_EQUITY_TS = 1_735_862_400_000
_DAY_MS = 86_400_000
_BAR_COUNT = 5
_FILL_TS_MS = _FIRST_BAR_CLOSE_TS


def _flat_bars() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for i in range(_BAR_COUNT):
        rows.append(
            {
                "ts": _START_TS + i * _DAY_MS,
                "open": 100.0,
                "high": 100.0,
                "low": 100.0,
                "close": 100.0,
                "volume": 1.0,
            }
        )
    return rows

def test_buy_hold_equity_keeps_every_daily_close() -> None:
    result = run_backtest(
        venue="binance",
        symbol="BTC/USDT",
        bar_type_str=_BAR_TYPE,
        rows=_flat_bars(),
        strategy="buy_hold",
        trade_size="1",
        deploy_pct="0",
        starting_balance_usdt=100_000.0,
    )

    extraction = extract_equity(result, first_bar_ts=_START_TS)
    equity = extraction.equity
    portfolio_returns = result.portfolio_returns

    fill_ts_values: list[int] = []
    for row in result.fills_report:
        ts_event = row["ts_event"]
        assert isinstance(ts_event, Timestamp)
        fill_ts_values.append(int(ts_event.value // 1_000_000))

    assert fill_ts_values == [_FILL_TS_MS, _FILL_TS_MS]

    assert [point.ts for point in equity] == [
        _START_TS + i * _DAY_MS for i in range(_BAR_COUNT + 1)
    ]
    assert equity[0].ts == _START_TS
    assert equity[0].equity == 100_000.0
    assert equity[1].ts == _FILL_TS_MS
    assert equity[1].ts == portfolio_returns[0][0]
    assert equity[1].equity != equity[0].equity
    assert equity[2].equity == pytest.approx(equity[1].equity)
    assert len(equity) == len(portfolio_returns) + 1
    for prev, curr in zip(equity, equity[1:], strict=False):
        assert curr.ts - prev.ts == _DAY_MS
