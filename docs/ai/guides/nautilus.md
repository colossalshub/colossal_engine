# Nautilus and Backend Integration Guide

Read this guide only when a task touches NautilusTrader, engine reports,
tear-sheet lifecycle behavior, or Nautilus strategy logging. These notes
were established through repository probes and should not be rediscovered.

## Nautilus 1.231.0 construction

### Imports

- `from nautilus_trader.backtest.config import BacktestEngineConfig, BacktestVenueConfig`
- `from nautilus_trader.backtest.engine import BacktestEngine`
- `from nautilus_trader.model.data import Bar, BarType`
- `from nautilus_trader.model.objects import Money, Price, Quantity`

### `BacktestEngine.add_venue` (NOT `add_venue(config)`)

Requires positional args, not a config object:

```python
engine.add_venue(
    venue=Venue("BINANCE"),
    oms_type=oms_type_from_str("NETTING"),
    account_type=account_type_from_str("CASH"),
    starting_balances=[Money.from_str("100000 USDT")],
)
```

### `BacktestVenueConfig` required kwargs

`name, oms_type, account_type, starting_balances`. `starting_balances`
accepts strings like `"100000 USDT"` — no explicit `Money()` needed.

### `CurrencyPair` requires 10 positional args

`instrument_id, raw_symbol, base_currency, quote_currency,
price_precision, size_precision, price_increment, size_increment,
ts_event, ts_init`. `ts_event`/`ts_init` are in **nanoseconds** (multiply
ms by 1,000,000).

### `Bar` constructor

Keyword args work: `Bar(bar_type=bt, open=Price, high=Price, low=Price,
close=Price, volume=Quantity, ts_event=ns, ts_init=ns)`.

## Portfolio and reports

### `Portfolio.equity(Venue)` returns `dict[Currency, Money]`

NOT `equity(Currency)`. Get total equity in USDT:

```python
venue_obj = InstrumentId.from_str(self._instrument_id_str).venue
money = self.portfolio.equity(venue_obj)[USDT]
equity = float(money.as_double())
```

### `portfolio.analyzer.portfolio_returns()` returns empty for open positions

For buy-and-hold with an open position in a CASH account, this returns an
empty Series and the account report has only 3 rows (all with the same
timestamp — start snapshot, end snapshot, BTC snapshot). This is why
Phase 2.2.2 moved to per-bar equity snapshots taken inside
`BuyHold.on_bar`.

### Retrieve a strategy instance

`engine.trader.strategies()[0]` — `engine.cache.strategies` does not exist.

### Reports have Money-shaped strings

- `realized_pnl` is a string like `"-4.41795500 USDT"` — parse with `float(value.split()[0])`.
- `commissions` is a list of strings — sum after parsing each.
- `commission` (fills) is a string — same parsing.

### Reports mix timestamps and nanosecond integers

- `ts_opened`, `ts_event`, `ts_init` (fills): `pd.Timestamp` → `int(ts.value // 1_000_000)`
- `ts_init`, `ts_last` (positions): raw `int64` nanoseconds → `/ 1_000_000`
- Do not assume consistency between columns or between reports.

### DataFrame index drops on `to_dict(orient="records")`

`generate_positions_report().to_dict(orient="records")` loses
`position_id` (the index). **Call `reset_index()` first** — Phase 2.2.3
does this.

### `pandas.Timestamp.utcnow` deprecation warning

Emitted from inside Nautilus's `engine.run()`. Not our code. Ignore until
Nautilus updates.

## Tear-sheet lifecycle

`GET /api/runs/{id}/tearsheet` must return a 200 empty shell for any
non-done status (queued, running, failed, archived). Never read parquet
files for a non-done run — they may not exist.

## Nautilus logging does not go through Python logging

- `self.log.warning(...)` inside a Nautilus strategy emits to stdout via
  the Rust bridge, NOT through Python's `logging` module.
- `caplog` captures zero records from Nautilus log calls.
- `capsys` misses them synchronously too — they may only appear during
  pytest teardown.
- To assert on Nautilus log output, monkeypatch `strategy.log` with a
  spy and assert on the spy. This is the first-choice approach —
  deterministic, unlike `capfd`.
- `capfd` with a bounded poll (see
  `backend/tests/strategies/test_buy_hold.py` for the pattern) is
  discouraged: its timing is unpredictable and it caused repeated flakes
  (see [`../INCIDENTS.md`](../INCIDENTS.md), I-005).
- Discovered during Phase 12.3.1.
