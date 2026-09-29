from decimal import Decimal

from nautilus_trader.backtest.config import BacktestEngineConfig
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.model.currencies import BTC, USDT
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import (
    OrderSide,
    OrderType,
    account_type_from_str,
    oms_type_from_str,
)
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.model.instruments import CurrencyPair
from nautilus_trader.model.objects import Money, Price, Quantity
from nautilus_trader.trading.strategy import Strategy

from quant.strategies.ema_cross import (
    EmaCross,
    crossover_signals,
    ema_series,
    net_position_as_float,
)

_INSTRUMENT_ID = "BTCUSDT.BINANCE"
_BAR_TYPE = "BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL"
_TICK = Price.from_str("0.10")
_DAY_NS = 86_400 * 1_000_000_000


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
    assert not hasattr(strategy, "_is_long")


def _limit_px(close: float, side: OrderSide) -> Price:
    close_px = Price.from_str(f"{close:.2f}")
    if side == OrderSide.BUY:
        return close_px - _TICK
    return close_px + _TICK


def _bars(closes: list[float], *, span: float) -> list[Bar]:
    bar_type = BarType.from_str(_BAR_TYPE)
    origin_ns = 1_700_000_000_000_000_000
    bars: list[Bar] = []
    for i, close in enumerate(closes):
        close_px = Price.from_str(f"{close:.2f}")
        low = Price.from_str(f"{max(close - span, 0.01):.2f}")
        high = Price.from_str(f"{close + span:.2f}")
        ts = origin_ns + (i + 1) * _DAY_NS
        bars.append(
            Bar(
                bar_type=bar_type,
                open=close_px,
                high=high,
                low=low,
                close=close_px,
                volume=Quantity.from_str("1.000000"),
                ts_event=ts,
                ts_init=ts,
            )
        )
    return bars


def _run(
    closes: list[float],
    *,
    span: float,
) -> list[tuple[OrderSide, OrderType, str, bool]]:
    instrument_id = InstrumentId.from_str(_INSTRUMENT_ID)
    instrument = CurrencyPair(
        instrument_id=instrument_id,
        raw_symbol=Symbol("BTCUSDT"),
        base_currency=BTC,
        quote_currency=USDT,
        price_precision=2,
        size_precision=6,
        price_increment=_TICK,
        size_increment=Quantity.from_str("0.000001"),
        ts_event=0,
        ts_init=0,
        maker_fee=Decimal(0),
        taker_fee=Decimal(0),
    )
    engine = BacktestEngine(config=BacktestEngineConfig())
    engine.add_venue(
        venue=Venue("BINANCE"),
        oms_type=oms_type_from_str("NETTING"),
        account_type=account_type_from_str("CASH"),
        starting_balances=[Money.from_str("100000 USDT")],
    )
    engine.add_instrument(instrument)
    engine.add_data(_bars(closes, span=span))
    engine.add_strategy(
        EmaCross(
            instrument_id=_INSTRUMENT_ID,
            bar_type=_BAR_TYPE,
            trade_size="1.000000",
        )
    )
    try:
        engine.run()
        return [
            (order.side, order.order_type, str(order.price), bool(order.is_post_only))
            for order in engine.cache.orders()
        ]
    finally:
        engine.dispose()


def test_ema_cross_submits_post_only_limits_one_tick_from_close() -> None:
    closes = _crossover_test_closes()
    signals = crossover_signals(ema_series(closes, 9), ema_series(closes, 21))
    buy_i = signals.index("buy")
    sell_i = signals.index("sell")

    orders = _run(closes, span=5.0)

    buy_px = str(_limit_px(closes[buy_i], OrderSide.BUY))
    sell_px = str(_limit_px(closes[sell_i], OrderSide.SELL))
    assert orders == [
        (OrderSide.BUY, OrderType.LIMIT, buy_px, True),
        (OrderSide.SELL, OrderType.LIMIT, sell_px, True),
    ]


def _two_buy_closes_above_first_limit() -> list[float]:
    """Two bullish crosses whose later bars never trade through the first limit."""
    closes = [120.0] * 25
    for i in range(12):
        closes.append(120.0 + (i + 1) * 1.0)
    for _ in range(25):
        closes.append(closes[-1] - 0.15)
    for _ in range(25):
        closes.append(closes[-1] + 0.8)
    return closes


def test_ema_cross_does_not_stack_orders_while_one_is_working() -> None:
    closes = _two_buy_closes_above_first_limit()
    signals = crossover_signals(ema_series(closes, 9), ema_series(closes, 21))
    buy_indexes = [i for i, signal in enumerate(signals) if signal == "buy"]
    assert len(buy_indexes) == 2

    orders = _run(closes, span=0.0)

    assert orders == [
        (
            OrderSide.BUY,
            OrderType.LIMIT,
            str(_limit_px(closes[buy_indexes[0]], OrderSide.BUY)),
            True,
        ),
    ]
