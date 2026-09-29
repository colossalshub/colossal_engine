from nautilus_trader.model.currencies import USDT
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.identifiers import InstrumentId, Venue
from nautilus_trader.model.objects import Quantity
from nautilus_trader.trading.strategy import Strategy


def ema_series(closes: list[float], length: int) -> list[float | None]:
    """Exponential moving average seeded with the first ``length`` closes' SMA."""
    n = len(closes)
    result: list[float | None] = [None] * n
    if length <= 0 or n < length:
        return result

    multiplier = 2.0 / (length + 1)
    seed = sum(closes[:length]) / length
    result[length - 1] = seed
    prev = seed
    for i in range(length, n):
        prev = (closes[i] - prev) * multiplier + prev
        result[i] = prev
    return result


def crossover_signals(
    fast: list[float | None],
    slow: list[float | None],
) -> list[str]:
    """Per-bar crossover labels: ``buy``, ``sell``, or ``hold``."""
    n = len(fast)
    if n != len(slow):
        raise ValueError("fast and slow series must have the same length")

    signals: list[str] = []
    for i in range(n):
        if i == 0:
            signals.append("hold")
            continue

        f_prev, f_curr = fast[i - 1], fast[i]
        s_prev, s_curr = slow[i - 1], slow[i]
        if (
            f_prev is None
            or f_curr is None
            or s_prev is None
            or s_curr is None
        ):
            signals.append("hold")
            continue

        if f_prev <= s_prev and f_curr > s_curr:
            signals.append("buy")
        elif f_prev >= s_prev and f_curr < s_curr:
            signals.append("sell")
        else:
            signals.append("hold")
    return signals


def net_position_as_float(value: object | None) -> float:
    """Coerce portfolio net position to float (None, Quantity, Decimal, etc.)."""
    if value is None:
        return 0.0
    as_double = getattr(value, "as_double", None)
    if callable(as_double):
        return float(as_double())
    return float(value)  # type: ignore[arg-type]  # decimal.Decimal and numeric scalars


class EmaCross(Strategy):  # type: ignore[misc]  # Strategy resolves to Any without stubs
    """Long-only EMA crossover using post-only limit orders.

    Position comes from the portfolio, which the engine updates on order and
    position events. A new order is sent only when the book has no open or
    in-flight order for the instrument. Buys are priced one tick below the
    bar close; sells are priced one tick above it.
    """

    def __init__(
        self,
        instrument_id: str,
        bar_type: str,
        trade_size: str = "1",
        deploy_pct: str = "0",
        fast: int = 9,
        slow: int = 21,
    ) -> None:
        super().__init__()
        self._instrument_id_str = instrument_id
        self._bar_type_str = bar_type
        self._trade_size = trade_size
        self._deploy_pct = deploy_pct
        self._fast_len = fast
        self._slow_len = slow
        self._closes: list[float] = []
        self.equity_snapshots: list[tuple[int, float]] = []

    def on_start(self) -> None:
        self.subscribe_bars(BarType.from_str(self._bar_type_str))

    def on_bar(self, bar: Bar) -> None:
        instrument_id = InstrumentId.from_str(self._instrument_id_str)
        venue_obj = instrument_id.venue
        money = self.portfolio.equity(venue_obj)[USDT]
        equity = float(money.as_double())
        self.equity_snapshots.append((bar.ts_event // 1_000_000, equity))

        self._closes.append(float(bar.close))

        fast_ema = ema_series(self._closes, self._fast_len)
        slow_ema = ema_series(self._closes, self._slow_len)
        signal = crossover_signals(fast_ema, slow_ema)[-1]

        if self.cache.orders_open(
            instrument_id=instrument_id,
        ) or self.cache.orders_inflight(instrument_id=instrument_id):
            return

        if signal == "buy" and self.portfolio.is_flat(instrument_id):
            self._submit_limit(instrument_id, venue_obj, bar, OrderSide.BUY)
        elif signal == "sell" and self.portfolio.is_net_long(instrument_id):
            self._submit_limit(instrument_id, venue_obj, bar, OrderSide.SELL)

    def _submit_limit(
        self,
        instrument_id: InstrumentId,
        venue_obj: Venue,
        bar: Bar,
        side: OrderSide,
    ) -> None:
        if side == OrderSide.BUY:
            qty_str = self._entry_qty_str(bar, venue_obj)
            if not qty_str:
                return
        else:
            net_qty = self.portfolio.net_position(instrument_id)
            qty = net_position_as_float(net_qty)
            if qty <= 0:
                return
            qty_str = f"{qty:.6f}"

        instrument = self.cache.instrument(instrument_id)
        if instrument is None:
            msg = f"instrument not in cache: {instrument_id}"
            self.log.error(msg)
            raise RuntimeError(msg)

        tick = instrument.price_increment
        close_px = bar.close
        if side == OrderSide.BUY:
            limit_px = close_px - tick
        else:
            limit_px = close_px + tick

        order = self.order_factory.limit(
            instrument_id=instrument_id,
            order_side=side,
            quantity=Quantity.from_str(qty_str),
            price=limit_px,
            post_only=True,
        )
        self.submit_order(order)

    def _entry_qty_str(self, bar: Bar, venue_obj: Venue) -> str:
        deploy = float(self._deploy_pct) if self._deploy_pct else 0.0
        if deploy > 0:
            if bar.close <= 0:
                self.log.warning(f"bar.close={bar.close}, skipping entry")
                return ""
            venue_equity_money = self.portfolio.equity(venue_obj)[USDT]
            venue_equity = float(venue_equity_money.as_double())
            raw_qty = (venue_equity * deploy * 0.999) / float(bar.close)
            qty_str = f"{raw_qty:.6f}"
            if float(qty_str) <= 0:
                self.log.warning(
                    f"computed qty={qty_str} rounds to 0, skipping entry",
                )
                return ""
            return qty_str
        return self._trade_size
