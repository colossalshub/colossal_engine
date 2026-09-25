from nautilus_trader.model.currencies import USDT
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.objects import Quantity
from nautilus_trader.trading.strategy import Strategy


class BuyHold(Strategy):  # type: ignore[misc]  # Strategy resolves to Any without stubs
    """Buy once on the first bar; hold thereafter.

    After ``engine.run()``, the runner reads ``equity_snapshots``: one
    ``(bar_ts_ms, usdt_equity)`` per ``on_bar``, marked at bar close via
    ``portfolio.equity(venue)[USDT]``.
    """

    def __init__(
        self,
        instrument_id: str,
        bar_type: str,
        trade_size: str = "1",
    ) -> None:
        super().__init__()
        self._instrument_id_str = instrument_id
        self._bar_type_str = bar_type
        self._trade_size = trade_size
        self._entered = False
        self.equity_snapshots: list[tuple[int, float]] = []

    def on_start(self) -> None:
        self.subscribe_bars(BarType.from_str(self._bar_type_str))

    def on_bar(self, bar: Bar) -> None:
        venue_obj = InstrumentId.from_str(self._instrument_id_str).venue
        money = self.portfolio.equity(venue_obj)[USDT]
        equity = float(money.as_double())
        self.equity_snapshots.append((bar.ts_event // 1_000_000, equity))

        if self._entered:
            return
        order = self.order_factory.market(
            instrument_id=InstrumentId.from_str(self._instrument_id_str),
            order_side=OrderSide.BUY,
            quantity=Quantity.from_str(self._trade_size),
        )
        self.submit_order(order)
        self._entered = True
