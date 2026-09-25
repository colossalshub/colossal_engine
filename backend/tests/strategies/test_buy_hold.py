from nautilus_trader.trading.strategy import Strategy

from quant.strategies.buy_hold import BuyHold


def test_buy_hold_is_strategy_subclass() -> None:
    assert issubclass(BuyHold, Strategy)


def test_buy_hold_constructor_stores_attributes() -> None:
    strategy = BuyHold(
        instrument_id="BTCUSDT.BINANCE",
        bar_type="BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL",
        trade_size="2",
    )
    assert strategy._instrument_id_str == "BTCUSDT.BINANCE"
    assert strategy._bar_type_str == "BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL"
    assert strategy._trade_size == "2"


def test_buy_hold_default_trade_size() -> None:
    strategy = BuyHold(
        instrument_id="BTCUSDT.BINANCE",
        bar_type="BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL",
    )
    assert strategy._trade_size == "1"


def test_buy_hold_defines_lifecycle_methods() -> None:
    assert hasattr(BuyHold, "on_start")
    assert hasattr(BuyHold, "on_bar")
