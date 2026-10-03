"""Bound supplied daily clocks to a fresh BTC BuyHold simulation.

This adapter establishes supplied-clock consistency and runtime containment,
not source publication history, frozen selection or research eligibility.
"""

from __future__ import annotations

import logging
import math
from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
from typing import Any, NoReturn

from nautilus_trader.backtest.config import BacktestEngineConfig, BacktestVenueConfig
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.model.currencies import BTC, USDT
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import account_type_from_str, oms_type_from_str
from nautilus_trader.model.events import OrderFilled
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.model.instruments import CurrencyPair
from nautilus_trader.model.objects import Money, Price, Quantity

from quant.engine.bar_coverage import BarClock, validate_bar_coverage
from quant.engine.runner import BacktestResult
from quant.engine.temporal import ResearchInterval
from quant.strategies.buy_hold import BuyHold

logger = logging.getLogger(__name__)
_DAY_MS = 86_400_000
_NS_PER_MS = 1_000_000
_BAR_TYPE = "BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL"
_INSTRUMENT = "BTCUSDT.BINANCE"


def _fail(message: str) -> NoReturn:
    logger.error(message)
    raise ValueError(message)


def _integer(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        _fail(f"{field} must be an integer (bool is not allowed)")
    return value


def _interval(interval: ResearchInterval, field: str, anchor: int) -> None:
    start = _integer(interval.start_ts, f"{field}.start_ts")
    end = _integer(interval.end_ts, f"{field}.end_ts")
    if start >= end:
        _fail(f"{field}.start_ts must be less than {field}.end_ts")
    for name, value in (("start_ts", start), ("end_ts", end)):
        if (value - anchor) % _DAY_MS:
            _fail(f"{field}.{name} must align with the declared daily grid")


def _exact_places(value: Decimal, places: int) -> bool:
    # Inspect decimal digits, avoiding context rounding even for large values.
    _, digits, exponent = value.as_tuple()
    assert isinstance(exponent, int)  # only finite decimals reach this helper
    trailing = 0
    for digit in reversed(digits):
        if digit != 0:
            break
        trailing += 1
    return not any(digits) or exponent + trailing >= -places


def _decimal(value: object, field: str) -> Decimal:
    if not isinstance(value, str):
        _fail(f"{field} must be a finite decimal string")
    try:
        result = Decimal(value)
    except InvalidOperation:
        _fail(f"{field} must be a finite decimal string")
    if not result.is_finite():
        _fail(f"{field} must be a finite decimal string")
    return result


def _ohlcv(row: Mapping[str, object], field: str) -> dict[str, float | int]:
    values: dict[str, float | int] = {}
    for name in ("open", "high", "low", "close", "volume"):
        value = row.get(name)
        if (
            not isinstance(value, int | float)
            or isinstance(value, bool)
            or not math.isfinite(value)
        ):
            _fail(f"{field}.{name} must be a finite int or float excluding bool")
        if value < 0 or (name != "volume" and value == 0):
            requirement = "nonnegative" if name == "volume" else "positive"
            _fail(
                f"{field}.{name} must be {requirement}"
            )
        places = 6 if name == "volume" else 2
        if not _exact_places(Decimal(str(value)), places):
            _fail(
                f"{field}.{name} must be exactly representable "
                f"at {places} decimal places"
            )
        values[name] = value
    if (
        values["high"] < max(values["open"], values["close"])
        or values["low"] > min(values["open"], values["close"])
        or values["high"] < values["low"]
    ):
        _fail(f"{field} must have consistent OHLC bounds")
    return values


def _engine_timestamp(ms: int, field: str) -> int:
    ns = ms * _NS_PER_MS
    if not 0 <= ns <= 2**64 - 1:
        _fail(f"{field} must fit an unsigned 64-bit engine nanosecond timestamp")
    return ns


class _ResearchBuyHold(BuyHold):
    def __init__(
        self,
        *,
        engine: Any,
        active: ResearchInterval,
        active_closes: frozenset[int],
        warmup_closes: frozenset[int],
        trade_size: str,
        deploy_pct: str,
    ) -> None:
        super().__init__(
            instrument_id=_INSTRUMENT,
            bar_type=_BAR_TYPE,
            trade_size=trade_size,
            deploy_pct=deploy_pct,
        )
        self._research_engine = engine
        self._active = active
        self._active_closes = active_closes
        self._warmup_closes = warmup_closes
        self._active_started = False
        self.callback_error: Exception | None = None

    def _raise_retained(self) -> None:
        if self.callback_error is not None:
            raise self.callback_error

    def _retain(self, error: Exception) -> None:
        if self.callback_error is None:
            self.callback_error = error

    def _require_clean(self) -> None:
        engine = self._research_engine
        iid = InstrumentId.from_str(_INSTRUMENT)
        # Evaluate the actual proven queries; exceptions never imply emptiness.
        states = (
            engine.cache.positions_open(),
            engine.cache.positions_open(instrument_id=iid),
            engine.cache.orders_open(instrument_id=iid),
            engine.cache.orders_inflight(instrument_id=iid),
        )
        if any(states):
            message = (
                "research stage must start without positions or open/inflight orders"
            )
            logger.error(message)
            raise RuntimeError(message)

    def on_start(self) -> None:
        try:
            self._raise_retained()
            self._require_clean()
            super().on_start()
        except Exception as exc:
            self._retain(exc)
            raise

    def on_bar(self, bar: Bar) -> None:
        try:
            self._raise_retained()
            ns = bar.ts_event
            if ns in self._warmup_closes:
                return  # BuyHold has no indicators or fitted state to initialize.
            if ns not in self._active_closes:
                raise RuntimeError(
                    "bar callback is outside declared admitted membership"
                )
            if not self._active_started:
                self._require_clean()
                self._active_started = True
            super().on_bar(bar)
        except Exception as exc:
            self._retain(exc)
            raise

    def on_order_filled(self, event: OrderFilled) -> None:
        try:
            self._raise_retained()
            if not (
                self._active.start_ts * _NS_PER_MS
                <= event.ts_event
                < self._active.end_ts * _NS_PER_MS
            ):
                raise RuntimeError(
                    "fill ts_event must be inside the active half-open interval"
                )
            super().on_order_filled(event)
        except Exception as exc:
            self._retain(exc)
            raise


def run_research_buy_hold(
    *,
    active: ResearchInterval,
    warmup: ResearchInterval | None,
    required_warmup_observations: int,
    timeframe: str,
    calendar: str,
    anchor_ts: int,
    clocks: tuple[BarClock, ...],
    rows: Sequence[Mapping[str, object]],
    starting_balance_usdt: float,
    trade_size: str,
    deploy_pct: str,
    maker_fee: str,
    taker_fee: str,
) -> BacktestResult:
    """Run only the declared daily BTC stage, with explicit nontrading warmup.

    Caller rows and clocks are joined by unique open timestamp, independently
    of ordering. Source history and wider research guarantees remain unverified.
    """
    if timeframe != "1d":
        _fail("timeframe must be 1d for the supported research adapter")
    if calendar != "continuous_utc_fixed":
        _fail("calendar must be continuous_utc_fixed")
    anchor = _integer(anchor_ts, "anchor_ts")
    _interval(active, "active", anchor)
    count = _integer(required_warmup_observations, "required_warmup_observations")
    if count < 0:
        _fail("required_warmup_observations must be nonnegative")
    if warmup is None:
        if count != 0:
            _fail("absent warmup requires required_warmup_observations zero")
    else:
        if count == 0:
            _fail("present warmup requires positive required_warmup_observations")
        _interval(warmup, "warmup", anchor)
        if warmup.end_ts > active.start_ts:
            _fail("warmup.end_ts must be at or before active.start_ts")

    by_open: dict[int, Mapping[str, object]] = {}
    for index, row in enumerate(rows):
        ts = _integer(row.get("ts"), f"rows[{index}].ts")
        if ts in by_open:
            _fail(f"rows[{index}].ts duplicates an earlier row")
        by_open[ts] = row
    clock_by_open: dict[int, BarClock] = {}
    for index, clock in enumerate(clocks):
        field = f"clocks[{index}]"
        open_ts = _integer(clock.open_ts, f"{field}.open_ts")
        close_ts = _integer(clock.close_ts, f"{field}.close_ts")
        available_ts = _integer(clock.available_ts, f"{field}.available_ts")
        if (open_ts - anchor) % _DAY_MS:
            _fail(f"{field}.open_ts must align with the declared daily grid")
        if close_ts != open_ts + _DAY_MS:
            _fail(f"{field}.close_ts must equal open_ts plus one day")
        if available_ts != close_ts:
            _fail(f"{field}.available_ts must equal close_ts")
        if open_ts in clock_by_open:
            _fail(f"{field}.open_ts duplicates an earlier clock")
        clock_by_open[open_ts] = clock
    if by_open.keys() != clock_by_open.keys():
        _fail("rows and clocks must have exactly matching open timestamp keys")

    admitted: list[tuple[BarClock, dict[str, float | int]]] = []
    active_evidence: list[Mapping[str, object]] = []
    warmup_evidence: list[Mapping[str, object]] = []
    for ts in sorted(clock_by_open):
        clock = clock_by_open[ts]
        is_active = active.start_ts <= clock.close_ts < active.end_ts
        is_warmup = (
            warmup is not None and warmup.start_ts <= clock.close_ts < warmup.end_ts
        )
        if not is_active and not is_warmup:
            continue
        evidence = {
            "ts": ts,
            "close_ts": clock.close_ts,
            "available_ts": clock.available_ts,
        }
        (active_evidence if is_active else warmup_evidence).append(evidence)
        admitted.append((clock, _ohlcv(by_open[ts], f"row at open {ts}")))
        _engine_timestamp(clock.close_ts, f"clock at open {ts}.close_ts")
    active_clocks = validate_bar_coverage(
        active,
        timeframe=timeframe,
        calendar=calendar,
        anchor_ts=anchor,
        observations=active_evidence,
    )
    if warmup is not None:
        warmup_clocks = validate_bar_coverage(
            warmup,
            timeframe=timeframe,
            calendar=calendar,
            anchor_ts=anchor,
            observations=warmup_evidence,
        )
        if len(warmup_clocks) < count:
            _fail("warmup coverage is less than required_warmup_observations")
    else:
        warmup_clocks = ()
    first_open_ns = _engine_timestamp(
        admitted[0][0].open_ts, "earliest admitted open_ts"
    )
    if (
        not isinstance(starting_balance_usdt, float)
        or not math.isfinite(starting_balance_usdt)
        or starting_balance_usdt <= 0
        or not _exact_places(Decimal(str(starting_balance_usdt)), 0)
    ):
        _fail("starting_balance_usdt must be a finite positive whole-USDT float")
    size = _decimal(trade_size, "trade_size")
    if size <= 0 or not _exact_places(size, 6):
        _fail(
            "trade_size must be positive and exactly representable at 6 decimal places"
        )
    deploy = _decimal(deploy_pct, "deploy_pct")
    if not 0 <= deploy <= 1:
        _fail("deploy_pct must be between zero and one")
    maker = _decimal(maker_fee, "maker_fee")
    taker = _decimal(taker_fee, "taker_fee")
    for field, fee in (("maker_fee", maker), ("taker_fee", taker)):
        if fee < 0:
            _fail(f"{field} must be nonnegative")

    venue_config = BacktestVenueConfig(
        name="BINANCE",
        oms_type="NETTING",
        account_type="CASH",
        starting_balances=[f"{Decimal(str(starting_balance_usdt)):.0f} USDT"],
    )
    engine = BacktestEngine(config=BacktestEngineConfig())
    try:
        engine.add_venue(
            venue=Venue(venue_config.name),
            oms_type=oms_type_from_str(venue_config.oms_type),
            account_type=account_type_from_str(venue_config.account_type),
            starting_balances=[
                Money.from_str(b) for b in venue_config.starting_balances
            ],
        )
        iid = InstrumentId.from_str(_INSTRUMENT)
        engine.add_instrument(
            CurrencyPair(
                instrument_id=iid,
                raw_symbol=Symbol("BTCUSDT"),
                base_currency=BTC,
                quote_currency=USDT,
                price_precision=2,
                size_precision=6,
                price_increment=Price.from_str("0.01"),
                size_increment=Quantity.from_str("0.000001"),
                ts_event=first_open_ns,
                ts_init=first_open_ns,
                maker_fee=maker,
                taker_fee=taker,
            )
        )
        bars = [
            Bar(
                bar_type=BarType.from_str(_BAR_TYPE),
                open=Price.from_str(f"{Decimal(str(row['open'])):.2f}"),
                high=Price.from_str(f"{Decimal(str(row['high'])):.2f}"),
                low=Price.from_str(f"{Decimal(str(row['low'])):.2f}"),
                close=Price.from_str(f"{Decimal(str(row['close'])):.2f}"),
                volume=Quantity.from_str(f"{Decimal(str(row['volume'])):.6f}"),
                ts_event=clock.close_ts * _NS_PER_MS,
                ts_init=clock.close_ts * _NS_PER_MS,
            )
            for clock, row in admitted
        ]
        engine.add_data(bars)
        strategy = _ResearchBuyHold(
            engine=engine,
            active=active,
            active_closes=frozenset(c.close_ts * _NS_PER_MS for c in active_clocks),
            warmup_closes=frozenset(c.close_ts * _NS_PER_MS for c in warmup_clocks),
            trade_size=f"{size:.6f}",
            deploy_pct=deploy_pct,
        )
        engine.add_strategy(strategy)
        engine.run()
        strategy._raise_retained()
        if engine.cache.orders_open(instrument_id=iid) or engine.cache.orders_inflight(
            instrument_id=iid
        ):
            raise RuntimeError("terminal open/inflight orders are unsupported")
        snapshots = strategy.equity_snapshots
        if not snapshots:
            raise RuntimeError("research stage produced no scored snapshots")
        returns: list[tuple[int, float]] = []
        previous = starting_balance_usdt
        for timestamp, equity in snapshots:
            returns.append(
                (timestamp, (equity - previous) / previous if previous else 0.0)
            )
            previous = equity
        account: list[dict[str, Any]] = engine.trader.generate_account_report(
            Venue("BINANCE")
        ).to_dict(orient="records")
        usdt_rows = [r for r in account if r.get("currency") == "USDT"]
        btc_rows = [r for r in account if r.get("currency") == "BTC"]
        if not usdt_rows or not btc_rows:
            raise RuntimeError(
                "account report requires latest USDT and BTC valuation rows"
            )
        last_price = next(
            row["close"]
            for clock, row in reversed(admitted)
            if clock.close_ts == active_clocks[-1].close_ts
        )
        independent = (
            float(usdt_rows[-1]["total"]) + float(btc_rows[-1]["total"]) * last_price
        )
        return BacktestResult(
            portfolio_returns=returns,
            starting_balance=starting_balance_usdt,
            ending_balance=snapshots[-1][1],
            independent_ending_balance=independent,
            position_report=engine.trader.generate_positions_report()
            .reset_index()
            .to_dict(orient="records"),
            fills_report=engine.trader.generate_fills_report()
            .reset_index()
            .to_dict(orient="records"),
            account_report=usdt_rows[-1],
        )
    finally:
        engine.dispose()
