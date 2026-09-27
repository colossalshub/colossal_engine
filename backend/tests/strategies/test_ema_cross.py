from decimal import Decimal

from nautilus_trader.trading.strategy import Strategy

from quant.strategies.ema_cross import (
    EmaCross,
    crossover_signals,
    ema_series,
    net_position_as_float,
)


def _crossover_test_closes() -> list[float]:
    """Flat base, ramp up, then ramp down — one buy and one sell cross."""
    closes = [100.0] * 25
    for i in range(25, 50):
        closes.append(100.0 + (i - 25) * 2.0)
    for i in range(50, 70):
        closes.append(150.0 - (i - 50) * 3.0)
    return closes


def test_ema_flat_series_equals_constant_once_seeded() -> None:
    constant = 42.0
    closes = [constant] * 30
    series = ema_series(closes, 9)
    assert series[:8] == [None] * 8
    assert all(v == constant for v in series[8:])


def test_crossover_signals_buy_then_sell_at_known_indexes() -> None:
    closes = _crossover_test_closes()
    fast = ema_series(closes, 9)
    slow = ema_series(closes, 21)
    signals = crossover_signals(fast, slow)

    assert signals[26] == "buy"
    assert signals[59] == "sell"
    assert signals.count("buy") == 1
    assert signals.count("sell") == 1


def test_crossover_signals_hold_until_slow_ema_exists() -> None:
    closes = _crossover_test_closes()
    fast = ema_series(closes, 9)
    slow = ema_series(closes, 21)
    signals = crossover_signals(fast, slow)

    assert all(s == "hold" for s in signals[:21])


def test_ema_cross_is_strategy_subclass() -> None:
    assert issubclass(EmaCross, Strategy)


def test_net_position_as_float() -> None:
    assert net_position_as_float(None) == 0.0
    assert net_position_as_float(Decimal("1.5")) == 1.5
    assert net_position_as_float(0) == 0.0

    class _Qty:
        def as_double(self) -> float:
            return 2.25

    assert net_position_as_float(_Qty()) == 2.25


def test_ema_cross_constructor_defaults() -> None:
    strategy = EmaCross(
        instrument_id="BTCUSDT.BINANCE",
        bar_type="BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL",
    )
    assert strategy._fast_len == 9
    assert strategy._slow_len == 21
    assert strategy.equity_snapshots == []
