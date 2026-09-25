from nautilus_trader.model.data import Bar, BarType  # type: ignore[import-not-found]
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.identifiers import (  # type: ignore[import-not-found]
    InstrumentId,
)
from nautilus_trader.model.objects import Quantity  # type: ignore[import-not-found]
from nautilus_trader.trading.strategy import Strategy  # type: ignore[import-not-found]


class BuyHold(Strategy):  # type: ignore[misc]
    def __init__(
        self,
        instrument_id: str,
        bar_type: str,
        trade_size: str = "1",
    ) -> None:
        super().__init__()
        self.instrument_id = instrument_id
        self.bar_type = bar_type
        self.trade_size = trade_size
        self._entered = False

    def on_start(self) -> None:
        self.subscribe_bars(BarType.from_str(self.bar_type))

    def on_bar(self, bar: Bar) -> None:
        if self._entered:
            return
        order = self.order_factory.market(
            instrument_id=InstrumentId.from_str(self.instrument_id),
            order_side=OrderSide.BUY,
            quantity=Quantity.from_str(self.trade_size),
        )
        self.submit_order(order)
        self._entered = True
