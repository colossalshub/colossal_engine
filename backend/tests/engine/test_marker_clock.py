from __future__ import annotations

from pandas import Timestamp

from quant.api.routers.runs import _build_markers
from quant.engine.runner import run_backtest
from quant.extract.artifacts import _map_fill_row, _map_position_row

_BAR_TYPE = "BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL"
_START_TS = 1_735_689_600_000
_FIRST_BAR_CLOSE_TS = 1_735_776_000_000
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


def test_buy_marker_is_not_earlier_than_the_fill() -> None:
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

    fill_ts_values: list[int] = []
    for row in result.fills_report:
        ts_event = row["ts_event"]
        assert isinstance(ts_event, Timestamp)
        fill_ts_values.append(int(ts_event.value // 1_000_000))

    assert fill_ts_values == [_FILL_TS_MS, _FILL_TS_MS]

    mapped_fills = [_map_fill_row(row) for row in result.fills_report]
    assert len(mapped_fills) == 2
    for mapped in mapped_fills:
        assert mapped["ts"] == _FILL_TS_MS
        assert mapped["order_side"] == "buy"

    mapped_positions = [_map_position_row(row) for row in result.position_report]
    assert len(mapped_positions) == 1
    assert mapped_positions[0]["exit_ts"] is None

    markers = _build_markers(mapped_positions)
    assert len(markers) == 1
    marker = markers[0]
    assert marker.side == "buy"
    assert marker.ts == _FILL_TS_MS

    for fill_ts in fill_ts_values:
        assert marker.ts == fill_ts
    assert marker.ts > _START_TS
