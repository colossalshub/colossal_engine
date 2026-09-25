from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.objects import Quantity
from nautilus_trader.trading.strategy import Strategy


class BuyHold(Strategy):
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

    def on_start(self) -> None:
        self.subscribe_bars(BarType.from_str(self._bar_type_str))

    def on_bar(self, bar: Bar) -> None:
        if self._entered:
            return
        order = self.order_factory.market(
            instrument_id=InstrumentId.from_str(self._instrument_id_str),
            order_side=OrderSide.BUY,
            quantity=Quantity.from_str(self._trade_size),
        )
        self.submit_order(order)
        self._entered = True
