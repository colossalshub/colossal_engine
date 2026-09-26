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

    Sizing modes: when ``deploy_pct`` is a positive decimal string, the
    entry is sized as ``deploy_pct * equity / bar.close`` (with a 0.999
    buffer for fees). When ``deploy_pct`` is ``"0"`` or empty, the fixed
    ``trade_size`` is used instead.
    """

    def __init__(
        self,
        instrument_id: str,
        bar_type: str,
        trade_size: str = "1",
        deploy_pct: str = "0",
    ) -> None:
        super().__init__()
        self._instrument_id_str = instrument_id
        self._bar_type_str = bar_type
        self._trade_size = trade_size
        self._deploy_pct = deploy_pct
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

        deploy = float(self._deploy_pct) if self._deploy_pct else 0.0
        if deploy > 0:
            if bar.close <= 0:
                self.log.warning(f"bar.close={bar.close}, skipping entry")
                self._entered = True
                return
            venue_equity_money = self.portfolio.equity(venue_obj)[USDT]
            venue_equity = float(venue_equity_money.as_double())
            raw_qty = (venue_equity * deploy * 0.999) / float(bar.close)
            qty_str = f"{raw_qty:.6f}"
            if float(qty_str) <= 0:
                self.log.warning(
                    f"computed qty={qty_str} rounds to 0, skipping entry",
                )
                self._entered = True
                return
        else:
            qty_str = self._trade_size

        order = self.order_factory.market(
            instrument_id=InstrumentId.from_str(self._instrument_id_str),
            order_side=OrderSide.BUY,
            quantity=Quantity.from_str(qty_str),
        )
        self.submit_order(order)
        self._entered = True
