from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd  # type: ignore[import-untyped]  # stubs not in dev deps; pandas via nautilus_trader
from nautilus_trader.backtest.config import (
    BacktestEngineConfig,
    BacktestVenueConfig,
)
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.model.currencies import BTC, USDT
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import account_type_from_str, oms_type_from_str
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.model.instruments import CurrencyPair
from nautilus_trader.model.objects import Money, Price, Quantity

from quant.data.read import read_bars_json
from quant.strategies.buy_hold import BuyHold
from quant.strategies.ema_cross import EmaCross

# The execution path settles one spot pair. Currencies are taken from this
# map, then checked against the symbol, so a non-BTC symbol cannot be built
# as BTC/USDT.
_SUPPORTED_SPOT: dict[str, tuple[Any, Any]] = {
    "BTC/USDT": (BTC, USDT),
}

_NT_TIMEFRAME_TO_CANONICAL: dict[str, str] = {
    "MINUTE": "1m",  # only used when count == 1
    "HOUR": "1h",
    "DAY": "1d",
    "WEEK": "1w",
    "MONTH": "1mo",
}

def _resolve_spot_instrument(symbol: str) -> tuple[str, str, Any, Any]:
    """Map a symbol to its base/quote currencies, or fail closed.

    Only ``BTC/USDT`` is supported. The returned currencies are the Nautilus
    objects whose codes rejoin to ``symbol``.
    """
    currencies = _SUPPORTED_SPOT.get(symbol)
    if currencies is None:
        msg = f"unsupported instrument {symbol!r}: only BTC/USDT spot is supported"
        raise ValueError(msg)
    base_currency, quote_currency = currencies
    base = str(base_currency.code)
    quote = str(quote_currency.code)
    if f"{base}/{quote}" != symbol:
        msg = (
            f"instrument currency mapping mismatch for {symbol!r}: "
            f"{base}/{quote}"
        )
        raise ValueError(msg)
    return base, quote, base_currency, quote_currency


def _as_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        return int(value)
    msg = f"expected int-coercible value, got {type(value)!r}"
    raise TypeError(msg)


_BAR_TYPE_SUFFIX_RE = re.compile(
    r"^(?P<prefix>.+)-(?P<count>\d+)-"
    r"(?P<unit>MINUTE|HOUR|DAY|WEEK|MONTH)-"
    r"(?P<price_type>[^-]+)-(?P<source>[^-]+)$"
)


def _canonical_from_bar_type(bar_type_str: str) -> str:
    match = _BAR_TYPE_SUFFIX_RE.match(bar_type_str)
    if not match:
        msg = f"invalid bar type string: {bar_type_str}"
        raise ValueError(msg)
    count = int(match.group("count"))
    unit = match.group("unit")
    if unit == "MINUTE":
        if count not in (1, 5, 15, 30):
            msg = f"unsupported MINUTE bar count: {count}"
            raise ValueError(msg)
        if count == 1:
            return _NT_TIMEFRAME_TO_CANONICAL["MINUTE"]
        return f"{count}m"
    if unit == "HOUR":
        if count not in (1, 4):
            msg = f"unsupported HOUR bar count: {count}"
            raise ValueError(msg)
        if count == 1:
            return _NT_TIMEFRAME_TO_CANONICAL["HOUR"]
        return f"{count}h"
    if unit not in _NT_TIMEFRAME_TO_CANONICAL:
        msg = f"unsupported bar unit: {unit}"
        raise ValueError(msg)
    if count != 1:
        msg = f"unsupported {unit} bar count: {count}"
        raise ValueError(msg)
    return _NT_TIMEFRAME_TO_CANONICAL[unit]


@dataclass(frozen=True)
class BacktestResult:
    portfolio_returns: list[tuple[int, float]]
    starting_balance: float
    ending_balance: float
    independent_ending_balance: float | None
    position_report: list[dict[str, object]]
    fills_report: list[dict[str, object]]
    account_report: dict[str, object]


def run_backtest(
    *,
    venue: str,
    symbol: str,
    bar_type_str: str,
    bars_db_path: Path,
    start_ts: int,
    end_ts: int,
    starting_balance_usdt: float = 100_000.0,
    trade_size: str = "1",
    deploy_pct: str = "0",
    maker_fee: str = "0.001",
    taker_fee: str = "0.001",
    strategy: str = "buy_hold",
) -> BacktestResult:
    """Run a backtest with either ``BuyHold`` or ``EmaCross`` and return the raw result.

    ``strategy`` selects which Nautilus ``Strategy`` subclass is constructed:
    ``"buy_hold"`` (default) constructs ``BuyHold`` only; ``"ema_cross"``
    constructs ``EmaCross`` only, with ``fast=9`` and ``slow=21``. Any other
    value raises ``ValueError`` before the ``BacktestEngine`` is created.
    Any symbol other than ``BTC/USDT`` raises ``ValueError`` before the
    engine is created.

    ``deploy_pct`` (string decimal, default ``"0"``) is forwarded to the
    selected strategy: when positive, the entry is sized as a fraction of
    equity (``deploy_pct * equity / bar.close``, buffered by 0.999 for fees);
    when ``"0"`` or empty, the fixed ``trade_size`` is used instead.
    """
    if strategy not in ("buy_hold", "ema_cross"):
        msg = f"unknown strategy: {strategy!r}"
        raise ValueError(msg)

    base, quote, base_currency, quote_currency = _resolve_spot_instrument(symbol)

    canonical_timeframe = _canonical_from_bar_type(bar_type_str)
    rows = read_bars_json(
        db_path=bars_db_path,
        venue=venue,
        symbol=symbol,
        timeframe=canonical_timeframe,
        start_ts=start_ts,
        end_ts=end_ts,
    )
    if not rows:
        msg = f"no bars in range for {venue} {symbol} {canonical_timeframe}"
        raise ValueError(msg)

    venue_config = BacktestVenueConfig(
        name=venue.upper(),
        oms_type="NETTING",
        account_type="CASH",
        starting_balances=[f"{starting_balance_usdt:.0f} USDT"],
    )
    engine_config = BacktestEngineConfig()
    engine = BacktestEngine(config=engine_config)
    engine.add_venue(
        venue=Venue(venue_config.name),
        oms_type=oms_type_from_str(venue_config.oms_type),
        account_type=account_type_from_str(venue_config.account_type),
        starting_balances=[
            Money.from_str(balance) for balance in venue_config.starting_balances
        ],
    )

    instrument_id = InstrumentId.from_str(f"{base}{quote}.{venue.upper()}")
    instrument = CurrencyPair(
        instrument_id=instrument_id,
        raw_symbol=Symbol(f"{base}{quote}"),
        base_currency=base_currency,
        quote_currency=quote_currency,
        price_precision=2,
        size_precision=6,
        price_increment=Price.from_str("0.01"),
        size_increment=Quantity.from_str("0.000001"),
        ts_event=start_ts * 1_000_000,
        ts_init=start_ts * 1_000_000,
        maker_fee=Decimal(maker_fee),
        taker_fee=Decimal(taker_fee),
    )
    mapped_base = str(instrument.base_currency.code)
    mapped_quote = str(instrument.quote_currency.code)
    if mapped_base != base or mapped_quote != quote:
        engine.dispose()
        msg = (
            f"instrument currency mapping mismatch for {symbol!r}: "
            f"expected {base}/{quote}, got {mapped_base}/{mapped_quote}"
        )
        raise ValueError(msg)
    engine.add_instrument(instrument)

    bar_type = BarType.from_str(bar_type_str)
    interval_ns = _as_int(bar_type.spec.get_interval_ns())
    bars: list[Bar] = []
    for i, row in enumerate(rows):
        open_ns = _as_int(row["ts"]) * 1_000_000
        if i + 1 < len(rows):
            close_ns = _as_int(rows[i + 1]["ts"]) * 1_000_000
        elif canonical_timeframe == "1mo":
            close_ns = open_ns + (30 * 86_400 * 1_000_000_000)
        else:
            close_ns = open_ns + interval_ns
        bars.append(
            Bar(
                bar_type=bar_type,
                open=Price.from_str(f"{row['open']:.2f}"),
                high=Price.from_str(f"{row['high']:.2f}"),
                low=Price.from_str(f"{row['low']:.2f}"),
                close=Price.from_str(f"{row['close']:.2f}"),
                volume=Quantity.from_str(f"{row['volume']:.6f}"),
                ts_event=close_ns,
                ts_init=close_ns,
            )
        )
    engine.add_data(bars)

    normalized_trade_size = f"{Decimal(trade_size):.6f}"
    strategy_instance: BuyHold | EmaCross
    if strategy == "buy_hold":
        strategy_instance = BuyHold(
            instrument_id=str(instrument_id),
            bar_type=bar_type_str,
            trade_size=normalized_trade_size,
            deploy_pct=deploy_pct,
        )
    else:
        strategy_instance = EmaCross(
            instrument_id=str(instrument_id),
            bar_type=bar_type_str,
            trade_size=normalized_trade_size,
            deploy_pct=deploy_pct,
            fast=9,
            slow=21,
        )
    engine.add_strategy(strategy_instance)

    portfolio_returns: list[tuple[int, float]] = []
    starting_balance = float(starting_balance_usdt)
    ending_balance = 0.0
    position_report: list[dict[str, object]] = []
    fills_report: list[dict[str, object]] = []
    account_report: list[dict[str, object]] = []
    last_row: dict[str, object] = {}

    try:
        engine.run()

        strategies = engine.trader.strategies()
        if not strategies:
            raise RuntimeError("no strategies registered after backtest run")
        ran_strategy = strategies[0]
        if not isinstance(ran_strategy, BuyHold | EmaCross):
            msg = f"expected BuyHold or EmaCross strategy, got {type(ran_strategy)!r}"
            raise RuntimeError(msg)

        snapshots = ran_strategy.equity_snapshots
        if len(snapshots) >= 2:
            for i in range(1, len(snapshots)):
                _prev_ts, prev_eq = snapshots[i - 1]
                curr_ts, curr_eq = snapshots[i]
                if prev_eq == 0:
                    ret = 0.0
                else:
                    ret = (curr_eq - prev_eq) / prev_eq
                portfolio_returns.append((curr_ts, float(ret)))

        if snapshots:
            starting_balance = snapshots[0][1]
            ending_balance = snapshots[-1][1]
        else:
            starting_balance = float(starting_balance_usdt)
            ending_balance = 0.0

        # Per-currency snapshot at run end — not a time series; USDT row is cash-only.
        account_df: pd.DataFrame = engine.trader.generate_account_report(
            Venue(venue.upper())
        )
        account_report = account_df.to_dict(orient="records")
        if not account_report:
            raise RuntimeError("account report is empty — engine did not run")

        # The account report contains one row per state change. We want the last
        # row per currency — the post-fill, end-of-run state. Do NOT use next()
        # or [0]; those pick the initial pre-fill row and inflate the independent
        # ending balance by the starting cash.
        usdt_rows = [r for r in account_report if r.get("currency") == "USDT"]
        base_rows = [r for r in account_report if r.get("currency") == base]
        usdt_row = usdt_rows[-1] if usdt_rows else None
        base_row = base_rows[-1] if base_rows else None
        last_row = usdt_row if usdt_row is not None else account_report[-1]

        # Independent ending equity: USDT cash + base currency × last bar close.
        # Computed from Nautilus's authoritative account report, not from the
        # equity_snapshots reconstruction — this is what makes verification
        # genuinely independent rather than self-consistent.
        last_bar_close = float(rows[-1]["close"])  # type: ignore[arg-type]  # rows[-1]["close"] is float from read_bars_json
        if usdt_row is not None and base_row is not None:
            usdt_cash = float(usdt_row.get("total", 0.0))  # type: ignore[arg-type]  # account report values are numeric objects
            base_qty = float(base_row.get("total", 0.0))  # type: ignore[arg-type]  # account report values are numeric objects
            independent_ending: float | None = usdt_cash + base_qty * last_bar_close
        else:
            independent_ending = None

        positions_df: pd.DataFrame = (
            engine.trader.generate_positions_report().reset_index()
        )
        position_report = positions_df.to_dict(orient="records")

        fills_df: pd.DataFrame = engine.trader.generate_fills_report().reset_index()
        fills_report = fills_df.to_dict(orient="records")
    finally:
        engine.dispose()

    return BacktestResult(
        portfolio_returns=portfolio_returns,
        starting_balance=starting_balance,
        ending_balance=ending_balance,
        independent_ending_balance=independent_ending,
        position_report=position_report,
        fills_report=fills_report,
        account_report=last_row if account_report else {},
    )
