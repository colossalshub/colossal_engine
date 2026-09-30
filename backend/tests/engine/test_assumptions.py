from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
from nautilus_trader.model.enums import OrderType
from nautilus_trader.model.orders import MarketOrder

import quant.strategies.buy_hold as buy_hold_module
from quant.data.read import read_bars_json
from quant.data.store import ensure_canonical_bars, upsert_bars
from quant.engine import runner as runner_module
from quant.engine.assumptions import CURRENT_ASSUMPTIONS
from quant.engine.runner import run_backtest

_BAR_TYPE = "BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL"
_VENUE = "binance"
_SYMBOL = "BTC/USDT"
_DAY_MS = 86_400_000
_START_TS = 1_735_689_600_000


def _store_daily_bars(
    db_path: Path,
    *,
    start_ts: int,
    count: int = 3,
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


def _rows(db_path: Path, start_ts: int, end_ts: int) -> list[dict[str, object]]:
    return read_bars_json(
        db_path=db_path,
        venue=_VENUE,
        symbol=_SYMBOL,
        timeframe="1d",
        start_ts=start_ts,
        end_ts=end_ts,
    )


def test_current_assumptions_match_runner_behavior(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = CURRENT_ASSUMPTIONS
    assert expected.bar_ts == "open"
    assert expected.nautilus_bar_ts_event == "close"
    assert expected.signal_and_order == "on_bar"
    assert expected.order_type == "market"
    assert expected.sizing_price_when_deploy_pct_positive == "bar.close"
    assert expected.maker_fee_default == "0.001"
    assert expected.taker_fee_default == "0.001"
    assert expected.fill_model == "not_passed"
    assert expected.latency == "not_passed"
    assert expected.spread == "not_passed"
    assert expected.queue_model == "not_passed"
    assert expected.partial_fills == "not_passed"

    add_venue_kwargs: list[dict[str, object]] = []
    currency_pair_kwargs: list[dict[str, object]] = []
    bar_ts_events: list[int] = []
    submitted_during_on_bar: list[object] = []
    inside_on_bar = False

    real_backtest_engine = runner_module.BacktestEngine

    class SpyingBacktestEngine:
        """Proxy: Nautilus BacktestEngine.add_venue is read-only on the type."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            self._inner = real_backtest_engine(*args, **kwargs)

        def add_venue(self, **kwargs: object) -> object:
            add_venue_kwargs.append(dict(kwargs))
            return self._inner.add_venue(**kwargs)

        def __getattr__(self, name: str) -> object:
            return getattr(self._inner, name)

    real_currency_pair = runner_module.CurrencyPair

    def spying_currency_pair(*args: object, **kwargs: object) -> object:
        currency_pair_kwargs.append(dict(kwargs))
        return real_currency_pair(*args, **kwargs)

    real_bar = runner_module.Bar

    def spying_bar(**kwargs: object) -> object:
        ts_event = kwargs["ts_event"]
        assert isinstance(ts_event, int)
        bar_ts_events.append(ts_event)
        return real_bar(**kwargs)

    real_on_bar = buy_hold_module.BuyHold.on_bar
    real_submit_order = buy_hold_module.BuyHold.submit_order

    def spying_on_bar(self: object, bar: object) -> None:
        nonlocal inside_on_bar
        inside_on_bar = True
        try:
            real_on_bar(self, bar)  # type: ignore[arg-type]  # Strategy.on_bar binding
        finally:
            inside_on_bar = False

    def spying_submit_order(self: object, order: object) -> None:
        if inside_on_bar:
            submitted_during_on_bar.append(order)
        real_submit_order(self, order)  # type: ignore[arg-type]  # Strategy.submit_order binding

    monkeypatch.setattr(runner_module, "BacktestEngine", SpyingBacktestEngine)
    monkeypatch.setattr(runner_module, "CurrencyPair", spying_currency_pair)
    monkeypatch.setattr(runner_module, "Bar", spying_bar)
    monkeypatch.setattr(buy_hold_module.BuyHold, "on_bar", spying_on_bar)
    monkeypatch.setattr(buy_hold_module.BuyHold, "submit_order", spying_submit_order)

    db_path = tmp_path / "bars.duckdb"
    start_ts, end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=3)

    run_backtest(
        venue=_VENUE,
        symbol=_SYMBOL,
        bar_type_str=_BAR_TYPE,
        rows=_rows(db_path, start_ts, end_ts),
    )

    assert len(add_venue_kwargs) == 1
    assert set(add_venue_kwargs[0].keys()) == {
        "venue",
        "oms_type",
        "account_type",
        "starting_balances",
    }

    assert len(currency_pair_kwargs) == 1
    assert currency_pair_kwargs[0]["maker_fee"] == Decimal("0.001")
    assert currency_pair_kwargs[0]["taker_fee"] == Decimal("0.001")

    assert len(bar_ts_events) == 3
    second_bar_open_ns = (start_ts + _DAY_MS) * 1_000_000
    first_bar_open_ns = start_ts * 1_000_000
    assert bar_ts_events[0] == second_bar_open_ns
    assert bar_ts_events[0] != first_bar_open_ns

    assert len(submitted_during_on_bar) == 1
    order = submitted_during_on_bar[0]
    assert isinstance(order, MarketOrder)
    assert order.order_type == OrderType.MARKET
