import time
from decimal import Decimal
from types import SimpleNamespace

import pytest
from nautilus_trader.backtest.config import BacktestEngineConfig
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.common.config import LoggingConfig
from nautilus_trader.model.currencies import BTC, USDT
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import account_type_from_str, oms_type_from_str
from nautilus_trader.model.events import OrderFilled
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.model.instruments import CurrencyPair
from nautilus_trader.model.objects import Money, Price, Quantity
from nautilus_trader.trading.strategy import Strategy

from quant.strategies.buy_hold import BuyHold

_INSTRUMENT_ID = "BTCUSDT.BINANCE"
_BAR_TYPE = "BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL"
_DAY_NS = 86_400 * 1_000_000_000
_WARN_CAPTURE_TIMEOUT_S = 2.0


def _assert_fd_warning(
    capfd: pytest.CaptureFixture[str],
    needle: str,
) -> None:
    """Nautilus logs via a Rust bridge; stdout may arrive after the callback returns."""
    captured = ""
    deadline = time.monotonic() + _WARN_CAPTURE_TIMEOUT_S
    while time.monotonic() < deadline:
        captured += capfd.readouterr().out
        if needle in captured:
            return
        time.sleep(0.01)
    assert needle in captured


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
    assert strategy.equity_snapshots == []


def test_buy_hold_equity_snapshots_empty_at_construction() -> None:
    strategy = BuyHold(
        instrument_id="BTCUSDT.BINANCE",
        bar_type="BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL",
    )
    assert strategy.equity_snapshots == []


def test_buy_hold_default_trade_size() -> None:
    strategy = BuyHold(
        instrument_id="BTCUSDT.BINANCE",
        bar_type="BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL",
    )
    assert strategy._trade_size == "1"


def test_buy_hold_default_deploy_pct_is_disabled() -> None:
    strategy = BuyHold(
        instrument_id="BTCUSDT.BINANCE",
        bar_type="BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL",
    )
    assert strategy._deploy_pct == "0"


def test_buy_hold_constructor_stores_deploy_pct() -> None:
    strategy = BuyHold(
        instrument_id="BTCUSDT.BINANCE",
        bar_type="BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL",
        deploy_pct="1.0",
    )
    assert strategy._deploy_pct == "1.0"


def test_buy_hold_defines_lifecycle_methods() -> None:
    assert hasattr(BuyHold, "on_start")
    assert hasattr(BuyHold, "on_bar")
    assert hasattr(BuyHold, "on_order_filled")
    assert hasattr(BuyHold, "on_order_rejected")
    assert hasattr(BuyHold, "on_order_denied")


def _engine() -> BacktestEngine:
    engine = BacktestEngine(
        config=BacktestEngineConfig(
            logging=LoggingConfig(log_level="WARNING", log_colors=False),
        ),
    )
    engine.add_venue(
        venue=Venue("BINANCE"),
        oms_type=oms_type_from_str("NETTING"),
        account_type=account_type_from_str("CASH"),
        starting_balances=[Money.from_str("100000 USDT")],
    )
    return engine


def _strategy() -> BuyHold:
    return BuyHold(instrument_id=_INSTRUMENT_ID, bar_type=_BAR_TYPE)


def test_on_order_filled_sets_entered_flag(
    capfd: pytest.CaptureFixture[str],
) -> None:
    fill_ts_ms = 1_735_776_000_000
    with capfd.disabled():
        engine = _engine()
        engine.add_instrument(
            CurrencyPair(
                instrument_id=InstrumentId.from_str(_INSTRUMENT_ID),
                raw_symbol=Symbol("BTCUSDT"),
                base_currency=BTC,
                quote_currency=USDT,
                price_precision=2,
                size_precision=6,
                price_increment=Price.from_str("0.01"),
                size_increment=Quantity.from_str("0.000001"),
                ts_event=0,
                ts_init=0,
                maker_fee=Decimal(0),
                taker_fee=Decimal(0),
            ),
        )
        engine.add_data(_bars([100.0]))
        strategy = BuyHold(
            instrument_id=_INSTRUMENT_ID,
            bar_type=_BAR_TYPE,
            trade_size="1.000000",
        )
        engine.add_strategy(strategy)
    try:
        # The portfolio only holds account state once the engine has run.
        with capfd.disabled():
            engine.run()
        strategy._entered = False
        strategy.equity_snapshots[:] = [(fill_ts_ms, 0.0)]
        strategy.on_order_filled(
            SimpleNamespace(ts_event=fill_ts_ms * 1_000_000),  # type: ignore[arg-type]  # handler reads ts_event only; portfolio comes from the registered engine
        )
        assert strategy._entered is True
        assert len(strategy.equity_snapshots) == 1
        assert strategy.equity_snapshots[0][0] == fill_ts_ms
        assert strategy.equity_snapshots[0][1] != 0.0
    finally:
        with capfd.disabled():
            engine.dispose()


def test_on_order_rejected_warns_and_resets_entered(
    capfd: pytest.CaptureFixture[str],
) -> None:
    with capfd.disabled():
        engine = _engine()
        strategy = _strategy()
        engine.add_strategy(strategy)
    try:
        strategy._entered = True
        strategy.on_order_rejected(
            SimpleNamespace(reason="insufficient margin"),  # type: ignore[arg-type]  # callback reads reason only
        )
        assert strategy._entered is False
        _assert_fd_warning(capfd, "order rejected: insufficient margin")
    finally:
        with capfd.disabled():
            engine.dispose()


def test_on_order_denied_warns_and_resets_entered(
    capfd: pytest.CaptureFixture[str],
) -> None:
    with capfd.disabled():
        engine = _engine()
        strategy = _strategy()
        engine.add_strategy(strategy)
    try:
        strategy._entered = True
        strategy.on_order_denied(
            SimpleNamespace(reason="risk limit"),  # type: ignore[arg-type]  # callback reads reason only
        )
        assert strategy._entered is False
        _assert_fd_warning(capfd, "order denied: risk limit")
    finally:
        with capfd.disabled():
            engine.dispose()


class _FillProbe(BuyHold):  # type: ignore[misc]  # Strategy resolves to Any without stubs
    """Records ``_entered`` at the start of the first fill callback."""

    def __init__(
        self,
        instrument_id: str,
        bar_type: str,
        trade_size: str = "1",
        deploy_pct: str = "0",
    ) -> None:
        super().__init__(
            instrument_id=instrument_id,
            bar_type=bar_type,
            trade_size=trade_size,
            deploy_pct=deploy_pct,
        )
        self.entered_before_fill: bool | None = None

    def on_order_filled(self, event: OrderFilled) -> None:
        if self.entered_before_fill is None:
            self.entered_before_fill = self._entered
        super().on_order_filled(event)


def _bars(closes: list[float]) -> list[Bar]:
    bar_type = BarType.from_str(_BAR_TYPE)
    origin_ns = 1_700_000_000_000_000_000
    bars: list[Bar] = []
    for i, close in enumerate(closes):
        px = Price.from_str(f"{close:.2f}")
        ts = origin_ns + (i + 1) * _DAY_NS
        bars.append(
            Bar(
                bar_type=bar_type,
                open=px,
                high=px,
                low=px,
                close=px,
                volume=Quantity.from_str("1.000000"),
                ts_event=ts,
                ts_init=ts,
            ),
        )
    return bars


def test_entered_stays_false_until_fill_and_buys_once() -> None:
    instrument_id = InstrumentId.from_str(_INSTRUMENT_ID)
    instrument = CurrencyPair(
        instrument_id=instrument_id,
        raw_symbol=Symbol("BTCUSDT"),
        base_currency=BTC,
        quote_currency=USDT,
        price_precision=2,
        size_precision=6,
        price_increment=Price.from_str("0.01"),
        size_increment=Quantity.from_str("0.000001"),
        ts_event=0,
        ts_init=0,
        maker_fee=Decimal(0),
        taker_fee=Decimal(0),
    )
    engine = _engine()
    engine.add_instrument(instrument)
    engine.add_data(_bars([100.0, 101.0, 102.0, 103.0]))
    strategy = _FillProbe(
        instrument_id=_INSTRUMENT_ID,
        bar_type=_BAR_TYPE,
        trade_size="1.000000",
    )
    engine.add_strategy(strategy)
    try:
        engine.run()
        assert strategy.entered_before_fill is False
        assert strategy._entered is True
        assert len(engine.cache.orders()) == 1
    finally:
        engine.dispose()
