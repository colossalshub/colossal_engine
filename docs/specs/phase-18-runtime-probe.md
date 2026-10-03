# Phase 18.2f — Stage 1 research runtime probe

Status: doer evidence for independent acceptance; no self-acceptance or Stage 2 implementation.
Rule: `phase18-temporal-v1`. Only this document changes in the repository.

## Environment, authorization, and execution

Baseline: clean `phase18/18.2f-runtime-probe`, HEAD
`59257d113f1649138c6d768fb4ba392bfb6c7189`; parent merged prerequisite
`7c8466f8ca3081b134022e9b28dc46c046c74893`. Startup log/status agreed with
STATE: 18.2f READY, remaining 18.2 NOT_STARTED, no next task or Stage 2 approval.
Required AGENTS, STATE, WORKFLOW, REVIEWER, INCIDENTS, relevant PROJECT
architecture/data/extraction/execution/conventions/Phases 16–18/completion/AI
rules, project/backend rules, confirmed Phase 18 spec and Nautilus guide were
inspected. The cloud runtime skill and enforced current policy were inspected;
no credentials or network configuration changed.

Initial restricted `git ls-remote origin HEAD` exited 128:

```text
fatal: unable to access 'https://github.com/colossalshub/colossal_quant.git/': Failed to connect to proxy port 8080 after 0 ms: Could not connect to server
```

Command-only network permission preserved inherited proxy and TLS. Subsequent
`git ls-remote --heads origin main` exited 0:

```text
7c8466f8ca3081b134022e9b28dc46c046c74893	refs/heads/main
```

This is present prerequisite/connectivity evidence, not publication or future
freshness evidence. Python 3.12.14; NautilusTrader 1.231.0; existing `.venv`,
no installs. Each run used exactly, from repository root:

```bash
source .venv/bin/activate
python /tmp/phase18f-runtime-probe.py > /tmp/phase18f-doer-probe.log 2>&1
```

Attempt 1 exited **1**, stopping at a doer-added exact float assertion after the
ordinary control. Original source and complete log were saved before correction
as `/tmp/phase18f-runtime-probe-attempt1.py` and
`/tmp/phase18f-doer-probe-attempt1.log`. Expected exact `99999.9` differed from
observed snapshot `99999.90000000001`. The coordinator explicitly authorized
only the representation correction: `math.isclose` against the independently
reported cash plus base valuation, `abs_tol=1e-8, rel_tol=0`. Temporal and query
assertions were unchanged. Attempt 2 exited **0**, running both cases. There
were no position-query failures, signature exceptions, hidden substitutions,
fixture changes, passive-limit cases or further corrections. Nautilus emits its
existing `Timestamp.utcnow` deprecation warning; it remains in raw output.

## Observations and limits

The live bound `engine.cache.positions_open` signature was:

```text
(venue=None, instrument_id=None, strategy_id=None, side=<PositionSide.NO_POSITION_SIDE: 0>, account_id=None)
```

Exact new live calls, each returning a list:

```python
engine.cache.positions_open()
engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
```

The full live docstring and actual position property docstrings/values are in the
raw transcript. Both position calls and copied instrument-filtered
`orders_open`/`orders_inflight` returned zero items at fresh construction and
on_start in each case. All four returned zero at gated active-start, before the
first eligible order. Terminal position calls each returned one open LONG
position of quantity 1 BTC; open and inflight orders returned zero. These
queries are actual observations, not deductions from equity or empty reports.
Pending-order survival across stop is unproven; no proposal relies on it.

The ordinary callback order was on_bar before, _submit_entry before/after,
on_bar after, then on_order_filled before/after, with fill `ts_event` and
`ts_init` equal to the first close, 1735776000000 ms. The first snapshot was
100000 before the fill callback, then replaced with 99999.90000000001 after it.
Four ordinary snapshots remained at all four fixture closes. The gated case
skipped inherited trading/scoring at warmup 1735776000000 and sentinel
1736035200000; it submitted and filled at 1735862400000, with the same inherited
snapshot replacement order. Its only snapshots were 1735862400000 and
1735948800000. Numbered traces preserve raw nanoseconds and derived milliseconds.
No new strategy clock accessor or speculative callback was introduced.

Both account reports independently give latest USDT cash 99899.9 and BTC base
1.0. At last eligible close 1735948800000 and price 100, valuation is 99999.9.
The residual position is genuinely open: no closing order, closed timestamp or
fabricated liquidation. One market BUY fill of 1 BTC at 100 incurred
0.10000000 USDT commission. Full original report columns, dtypes, index and
records retain IDs. Fill ts_event/ts_init and position ts_opened are Timestamp
objects converted through `.value`; position ts_init/ts_last are raw ns integers.
Absent timestamp fields are printed explicitly. Account index timestamps are
preserved, without treating account rows as an equity time series.

**All four fixture bars, including the end-exclusive sentinel, reached the
engine in both scratch cases.** The gated sentinel skipped BuyHold actions,
but it still reached matching/valuation. Identical fixture prices conceal any
price effect; this is not a runtime fix or proof that later data cannot influence
an engine. Explicit fixture `available_ts=close_ts` is scratch evidence only,
not certification of source publication history. No availability, eligibility,
realistic same-bar execution, gaps, frozen selection, dependency, OOS
contamination, multi-instrument or walk-forward guarantee is established.

## Bounded future Stage 2 recommendation — approval required

Recommend a separately approved research-only BuyHold adapter, with explicit
keyword-only inputs and no numeric defaults. A concrete suggested internal
interface is:

```text
run_research_buy_hold(*, active: ResearchInterval,
    warmup: ResearchInterval | None, clocks: tuple[BarClock, ...],
    rows: Sequence[Mapping[str, object]], starting_balance_usdt: float,
    trade_size: str, deploy_pct: str, maker_fee: str, taker_fee: str)
```

This is a proposal, not implemented or an approved exact production signature.
Require explicit `warmup=None` when absent; when present, bind its declared
requirements and allowed earlier history to the rows/clocks. Verify supplied
active coverage with the accepted coverage helper and preserve original event
timestamps. Bind each row to its verified open/close/available clock; unknown
historical availability must fail supported admission or remain explicitly
unverified under a separately approved transport/policy contract. The current
stored-open inference is not that evidence.

Before engine.add_data, feed only permitted declared warmup and active rows;
never feed the active end-exclusive sentinel or later rows. Within the research
strategy, warmup may update only approved causal initialization, with no orders
or scored snapshots; inherited BuyHold action order runs only for active rows.
This scratch BuyHold does no indicator initialization and proves no EMA support.
Use fresh engines with declared cash. Before any active submission, enforce
all-engine `positions_open()` plus the proven instrument-filtered
`positions_open(instrument_id=...)` and existing instrument-filtered
`orders_open`/`orders_inflight` zero counts; query exceptions abort, never become
empty state. Scope stays one BTCUSDT instrument. Retain actual fills/fees and
residual positions, valued from last eligible price with latest per-currency
account rows; do not liquidate or carry state into another stage. Preserve the
ordinary runner path and its timestamps. No pending-order stop assumption,
engine.run boundary kwargs, EMA, automatic windows or availability invention.

This small recommendation is not all of 18.2. **WORKFLOW §2 requires reporting
this probe verbatim, STOP, and explicit post-probe human approval before any
Stage 2 implementation.** Auto-merge authority for documentation does not
approve this future call or interface. Independent replay and reviewer STATE
completion are still required; remaining 18.2 remains NOT_STARTED.

## Durable corrected source — exact replay target

The first fenced source below is the complete corrected standalone source.
Independent reviewer extracts it without edits to
`/tmp/phase18f-review-runtime-probe.py` and runs from repository root:

```bash
source .venv/bin/activate
python /tmp/phase18f-review-runtime-probe.py > /tmp/phase18f-review-probe.log 2>&1
git diff --check
git status --short
```

Each exit and complete replay output must be recorded. Compare causal clocks,
query counts/states and reports; runtime UUIDs, IDs, wall clocks and durations
can vary. No Python repository files changed; pytest/ruff/mypy were not rerun
under WORKFLOW §5. No frontend changes or frontend checks. No data writes,
worker, push, PR, merge, STATE edit or self-acceptance by doer.

### Corrected complete source (attempt 2)

```python
"""Authorized Phase 18.2f scratch probe: two cases, no persisted data."""
import inspect
import math
import subprocess
import sys
import traceback
from decimal import Decimal
from importlib.metadata import version
from pprint import pprint
from typing import Any

from nautilus_trader.backtest.config import BacktestEngineConfig, BacktestVenueConfig
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.model.currencies import BTC, USDT
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import account_type_from_str, oms_type_from_str
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.model.instruments import CurrencyPair
from nautilus_trader.model.objects import Money, Price, Quantity
from quant.strategies.buy_hold import BuyHold

T = 1735689600000
D = 86400000
ACTIVE_START = T + 2 * D
ACTIVE_END = T + 4 * D
BT = 'BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL'
IID = InstrumentId.from_str('BTCUSDT.BINANCE')
FIXTURE = [dict(open_ts=T+i*D, close_ts=T+(i+1)*D,
                available_ts=T+(i+1)*D, ts_event=(T+(i+1)*D)*1000000,
                ts_init=(T+(i+1)*D)*1000000, open=100, high=101,
                low=99, close=100, volume=1000) for i in range(4)]


def emit(*args: Any) -> None:
    print(*args, flush=True)


def query(engine: Any, label: str) -> dict[str, int]:
    emit('STATE QUERY', label)
    results = {}
    calls = [
        ('positions_open()', lambda: engine.cache.positions_open()),
        ("positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))",
         lambda: engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))),
        ("orders_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))",
         lambda: engine.cache.orders_open(instrument_id=IID)),
        ("orders_inflight(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))",
         lambda: engine.cache.orders_inflight(instrument_id=IID)),
    ]
    for expression, call in calls:
        emit('CALL engine.cache.' + expression)
        try:
            value = call()
        except Exception:
            traceback.print_exc()
            emit('STOP: query failure is unknown state, never empty; no substitution')
            raise
        emit('RETURN', type(value), 'count', len(value))
        results[expression] = len(value)
        for item in value:
            emit('ITEM', type(item), repr(item))
            for field in ('id', 'client_order_id', 'instrument_id', 'is_open',
                          'is_closed', 'side', 'quantity', 'signed_qty', 'status'):
                if hasattr(item, field):
                    emit('FIELD', field, repr(getattr(item, field)),
                         'DOC', inspect.getdoc(getattr(type(item), field, None)))
                else:
                    emit('FIELD', field, 'ABSENT')
    return results


class TraceBuyHold(BuyHold):
    def __init__(self, engine: Any, gated: bool) -> None:
        super().__init__(instrument_id=str(IID), bar_type=BT,
                         trade_size='1.000000', deploy_pct='0')
        self.probe_engine = engine
        self.gated = gated
        self.sequence = 0
        self.submission_times = []
        self.fill_times = []
        self.active_started = False
        self.excluded = []

    def trace(self, label: str, obj: Any = None) -> None:
        self.sequence += 1
        emit('TRACE', self.sequence, label)
        if obj is not None:
            emit('OBJECT', type(obj), repr(obj))
            for field in ('ts_event', 'ts_init', 'client_order_id', 'venue_order_id',
                          'position_id', 'last_qty', 'last_px'):
                if hasattr(obj, field):
                    value = getattr(obj, field)
                    emit(field, repr(value), 'ms', value // 1000000 if field.startswith('ts_') else 'N/A')
                else:
                    emit(field, 'ABSENT')
        emit('equity_snapshots', repr(self.equity_snapshots))

    def on_start(self) -> None:
        self.trace('on_start before')
        assert all(n == 0 for n in query(self.probe_engine, 'on_start').values())
        super().on_start()
        self.trace('on_start after')

    def on_bar(self, bar: Bar) -> None:
        self.trace('on_bar before', bar)
        close = bar.ts_event // 1000000
        if self.gated and not ACTIVE_START <= close < ACTIVE_END:
            before = (len(self.submission_times), list(self.equity_snapshots))
            emit('GATE', 'warmup' if close < ACTIVE_START else 'excluded sentinel', close)
            self.excluded.append(close)
            assert before == (len(self.submission_times), list(self.equity_snapshots))
        else:
            if self.gated and not self.active_started:
                assert all(n == 0 for n in query(self.probe_engine, 'active-start before first eligible order').values())
                self.active_started = True
            super().on_bar(bar)
        self.trace('on_bar after', bar)

    def _submit_entry(self, bar: Bar, venue_obj: Venue) -> None:
        self.trace('_submit_entry before', bar)
        self.submission_times.append(bar.ts_event // 1000000)
        super()._submit_entry(bar, venue_obj)
        self.trace('_submit_entry after', bar)

    def on_order_filled(self, event: Any) -> None:
        self.trace('on_order_filled before', event)
        self.fill_times.append(event.ts_event // 1000000)
        super().on_order_filled(event)
        self.trace('on_order_filled after', event)

    def on_stop(self) -> None:
        self.trace('on_stop before')
        super().on_stop()
        self.trace('on_stop after')


def report(name: str, frame: Any) -> list[dict[str, Any]]:
    emit('REPORT', name, 'class', type(frame))
    emit('columns', repr(frame.columns.tolist()), 'dtypes', repr(frame.dtypes.to_dict()))
    emit('index class', type(frame.index), 'index name', repr(frame.index.name),
         'index values', repr(frame.index.tolist()))
    emit('FULL FRAME\n' + frame.to_string())
    records = frame.reset_index().to_dict(orient='records')
    emit('FULL RECORDS (index retained)')
    pprint(records, sort_dicts=False)
    for record in records:
        for field in ('ts_opened', 'ts_event', 'ts_init', 'ts_last'):
            if field in record:
                value = record[field]
                ns = value.value if hasattr(value, 'value') else value
                emit('TIME ORIGINAL', field, repr(value), 'type', type(value), 'ms', ns // 1000000)
            else:
                emit('TIME', field, 'ABSENT')
    return records


def run_case(gated: bool) -> None:
    emit('CASE', 'scratch gated' if gated else 'ordinary control')
    venue_config = BacktestVenueConfig(name='BINANCE', oms_type='NETTING',
        account_type='CASH', starting_balances=['100000 USDT'])
    engine_config = BacktestEngineConfig()
    engine = BacktestEngine(config=engine_config)
    try:
        engine.add_venue(venue=Venue(venue_config.name),
            oms_type=oms_type_from_str(venue_config.oms_type),
            account_type=account_type_from_str(venue_config.account_type),
            starting_balances=[Money.from_str(balance) for balance in venue_config.starting_balances])
        instrument = CurrencyPair(instrument_id=IID, raw_symbol=Symbol('BTCUSDT'),
            base_currency=BTC, quote_currency=USDT, price_precision=2, size_precision=6,
            price_increment=Price.from_str('0.01'), size_increment=Quantity.from_str('0.000001'),
            ts_event=T*1000000, ts_init=T*1000000,
            maker_fee=Decimal('0.001'), taker_fee=Decimal('0.001'))
        engine.add_instrument(instrument)
        emit('LIVE positions_open signature')
        try:
            emit(inspect.signature(engine.cache.positions_open))
        except (TypeError, ValueError):
            traceback.print_exc()
            emit('Cython signature unavailable; full docstring fallback follows')
        emit('FULL LIVE positions_open DOCSTRING\n' + str(inspect.getdoc(engine.cache.positions_open)))
        assert all(n == 0 for n in query(engine, 'fresh engine before run').values())
        bars = [Bar(bar_type=BarType.from_str(BT), open=Price.from_str('100.00'),
                    high=Price.from_str('101.00'), low=Price.from_str('99.00'),
                    close=Price.from_str('100.00'), volume=Quantity.from_str('1000.000000'),
                    ts_event=row['ts_event'], ts_init=row['ts_init']) for row in FIXTURE]
        emit('FULL FIXTURE'); pprint(FIXTURE, sort_dicts=False)
        emit('ACTUAL BARS', repr(bars))
        engine.add_data(bars)
        strategy = TraceBuyHold(engine, gated)
        engine.add_strategy(strategy)
        emit('CALL engine.run() -- all four bars INCLUDING end-exclusive sentinel reach engine')
        engine.run()
        query(engine, 'postrun before disposal')
        emit('FINAL equity_snapshots', repr(strategy.equity_snapshots))
        emit('ENTRY SUBMISSION TIMES', repr(strategy.submission_times), 'FILL TIMES', repr(strategy.fill_times))
        report('fills', engine.trader.generate_fills_report())
        report('positions', engine.trader.generate_positions_report())
        account = report('account', engine.trader.generate_account_report(Venue('BINANCE')))
        cash_rows = [r for r in account if r.get('currency') == 'USDT']
        base_rows = [r for r in account if r.get('currency') == 'BTC']
        cash = float(cash_rows[-1]['total']) if cash_rows else None
        base = float(base_rows[-1]['total']) if base_rows else None
        emit('TERMINAL last report row per currency: cash USDT', cash, 'base BTC', base,
             'last eligible close', ACTIVE_END-D, 'last eligible price', 100,
             'cash + base * last eligible price', cash + base*100 if cash is not None and base is not None else None,
             'NO liquidation; sentinel price equals eligible price but still reached matching/valuation')
        expected = [ACTIVE_START, ACTIVE_START+D] if gated else [r['close_ts'] for r in FIXTURE]
        assert [ts for ts, _ in strategy.equity_snapshots] == expected
        assert strategy.submission_times == expected[:1]
        assert strategy.fill_times == expected[:1]
        assert cash is not None and base is not None
        assert math.isclose(strategy.equity_snapshots[0][1], cash + base * 100,
                            abs_tol=1e-8, rel_tol=0)
        if gated:
            assert strategy.excluded == [T+D, ACTIVE_END]
            assert all(ACTIVE_START <= ts < ACTIVE_END for ts in strategy.submission_times)
            emit('PASS zero warmup/sentinel submissions/scored snapshots; clean active-start; inherited same-bar fill/snapshot clock')
        emit('CASE PASS')
    finally:
        emit('CALL engine.dispose()')
        engine.dispose()


def main() -> None:
    emit('Python', sys.version)
    emit('NautilusTrader', version('nautilus_trader'))
    emit('baseline HEAD', subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip())
    emit('IMPORT SUCCESS')
    emit('Scratch constants only: T', T, 'D', D, 'active', ACTIVE_START, ACTIVE_END)
    run_case(False)
    run_case(True)
    emit('PROBE PASS; no actual historical availability certification; Stage2 requires explicit post-probe human approval')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        emit('PROBE STOP; failure retained; no silent substitution')
        sys.exit(1)
```

### Corrected complete raw stdout/stderr (attempt 2; exit 0)

```text
Python 3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]
NautilusTrader 1.231.0
baseline HEAD 59257d113f1649138c6d768fb4ba392bfb6c7189
IMPORT SUCCESS
Scratch constants only: T 1735689600000 D 86400000 active 1735862400000 1736035200000
CASE ordinary control
[1m2026-10-03T06:39:06.488181819Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:39:06.488214500Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  NAUTILUS TRADER - Automated Algorithmic Trading Platform[0m
[1m2026-10-03T06:39:06.488216955Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  by Nautech Systems Pty Ltd.[0m
[1m2026-10-03T06:39:06.488217182Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  Copyright (C) 2015-2026. All rights reserved.[0m
[1m2026-10-03T06:39:06.488217417Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:39:06.488217586Z[0m [INFO] BACKTESTER-001.BacktestEngine: [0m
[1m2026-10-03T06:39:06.488218158Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣶⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[0m
[1m2026-10-03T06:39:06.488218409Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣾⣿⣿⣿⠀⢸⣿⣿⣿⣿⣶⣶⣤⣀⠀⠀⠀⠀⠀[0m
[1m2026-10-03T06:39:06.488218863Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⠀⠀⢀⣴⡇⢀⣾⣿⣿⣿⣿⣿⠀⣾⣿⣿⣿⣿⣿⣿⣿⠿⠓⠀⠀⠀⠀[0m
[1m2026-10-03T06:39:06.488219213Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⠀⣰⣿⣿⡀⢸⣿⣿⣿⣿⣿⣿⠀⣿⣿⣿⣿⣿⣿⠟⠁⣠⣄⠀⠀⠀⠀[0m
[1m2026-10-03T06:39:06.488219608Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⢠⣿⣿⣿⣇⠀⢿⣿⣿⣿⣿⣿⠀⢻⣿⣿⣿⡿⢃⣠⣾⣿⣿⣧⡀⠀⠀[0m
[1m2026-10-03T06:39:06.488219828Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠠⣾⣿⣿⣿⣿⣿⣧⠈⠋⢀⣴⣧⠀⣿⡏⢠⡀⢸⣿⣿⣿⣿⣿⣿⣿⡇⠀[0m
[1m2026-10-03T06:39:06.488220171Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⣀⠙⢿⣿⣿⣿⣿⣿⠇⢠⣿⣿⣿⡄⠹⠃⠼⠃⠈⠉⠛⠛⠛⠛⠛⠻⠇⠀[0m
[1m2026-10-03T06:39:06.488220376Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⢸⡟⢠⣤⠉⠛⠿⢿⣿⠀⢸⣿⡿⠋⣠⣤⣄⠀⣾⣿⣿⣶⣶⣶⣦⡄⠀⠀⠀[0m
[1m2026-10-03T06:39:06.488220837Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠸⠀⣾⠏⣸⣷⠂⣠⣤⠀⠘⢁⣴⣾⣿⣿⣿⡆⠘⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀[0m
[1m2026-10-03T06:39:06.488222347Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⠛⠀⣿⡟⠀⢻⣿⡄⠸⣿⣿⣿⣿⣿⣿⣿⡀⠘⣿⣿⣿⣿⠟⠀⠀⠀⠀[0m
[1m2026-10-03T06:39:06.488222688Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⠀⠀⣿⠇⠀⠀⢻⡿⠀⠈⠻⣿⣿⣿⣿⣿⡇⠀⢹⣿⠿⠋⠀⠀⠀⠀⠀[0m
[1m2026-10-03T06:39:06.488222874Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⠀⠀⠋⠀⠀⠀⡘⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀[0m
[1m2026-10-03T06:39:06.488223202Z[0m [INFO] BACKTESTER-001.BacktestEngine: [0m
[1m2026-10-03T06:39:06.488223329Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:39:06.488223559Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  SYSTEM SPECIFICATION[0m
[1m2026-10-03T06:39:06.488223734Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:39:06.488224773Z[0m [INFO] BACKTESTER-001.BacktestEngine: CPU architecture: INTEL(R) XEON(R) PLATINUM 8573C[0m
[1m2026-10-03T06:39:06.488225483Z[0m [INFO] BACKTESTER-001.BacktestEngine: CPU(s): 3 @ 2299 MHz[0m
[1m2026-10-03T06:39:06.488227320Z[0m [INFO] BACKTESTER-001.BacktestEngine: OS: kernel-6.18.44 Linux (Debian GNU/Linux 13)[0m
[1m2026-10-03T06:39:06.488253031Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:39:06.488253390Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  MEMORY USAGE[0m
[1m2026-10-03T06:39:06.488253542Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:39:06.488261856Z[0m [INFO] BACKTESTER-001.BacktestEngine: RAM-Total: 9.73 GiB[0m
[1m2026-10-03T06:39:06.488265688Z[0m [INFO] BACKTESTER-001.BacktestEngine: RAM-Used: 0.92 GiB (9.48%)[0m
[1m2026-10-03T06:39:06.488266271Z[0m [INFO] BACKTESTER-001.BacktestEngine: RAM-Avail: 8.81 GiB (90.52%)[0m
[1m2026-10-03T06:39:06.488267061Z[0m [INFO] BACKTESTER-001.BacktestEngine: Swap: disabled[0m
[1m2026-10-03T06:39:06.488269234Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:39:06.488269635Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  IDENTIFIERS[0m
[1m2026-10-03T06:39:06.488269799Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:39:06.488270971Z[0m [INFO] BACKTESTER-001.BacktestEngine: trader_id: BACKTESTER-001[0m
[1m2026-10-03T06:39:06.488271494Z[0m [INFO] BACKTESTER-001.BacktestEngine: machine_id: 3df73ebcbb2d[0m
[1m2026-10-03T06:39:06.488273020Z[0m [INFO] BACKTESTER-001.BacktestEngine: instance_id: 0e6ad64c-8ebd-4036-b3c3-b08c68e6c666[0m
[1m2026-10-03T06:39:06.488274734Z[0m [INFO] BACKTESTER-001.BacktestEngine: PID: 24209[0m
[1m2026-10-03T06:39:06.488275027Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:39:06.488275213Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  VERSIONING[0m
[1m2026-10-03T06:39:06.488275380Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:39:06.488307333Z[0m [INFO] BACKTESTER-001.BacktestEngine: nautilus_trader: 1.231.0[0m
[1m2026-10-03T06:39:06.488333337Z[0m [INFO] BACKTESTER-001.BacktestEngine: python: 3.12.14[0m
[1m2026-10-03T06:39:06.489647851Z[0m [INFO] BACKTESTER-001.BacktestEngine: numpy: 2.5.3[0m
[1m2026-10-03T06:39:06.489651931Z[0m [INFO] BACKTESTER-001.BacktestEngine: pandas: 3.0.6[0m
[1m2026-10-03T06:39:06.489653666Z[0m [INFO] BACKTESTER-001.BacktestEngine: msgspec: 0.22.0[0m
[1m2026-10-03T06:39:06.489655667Z[0m [INFO] BACKTESTER-001.BacktestEngine: pyarrow: 25.0.1[0m
[1m2026-10-03T06:39:06.489657732Z[0m [INFO] BACKTESTER-001.BacktestEngine: pytz: 2026.4[0m
[1m2026-10-03T06:39:06.489660610Z[0m [INFO] BACKTESTER-001.BacktestEngine: uvloop: 0.22.1[0m
[1m2026-10-03T06:39:06.489660909Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:39:06.489691604Z[0m [INFO] BACKTESTER-001.BacktestEngine: Building system kernel[0m
[1m2026-10-03T06:39:06.489792209Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.database=None[0m
[1m2026-10-03T06:39:06.489803456Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.encoding='json'[0m
[1m2026-10-03T06:39:06.489805137Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.timestamps_as_iso8601=False[0m
[1m2026-10-03T06:39:06.489805785Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.buffer_interval_ms=None[0m
[1m2026-10-03T06:39:06.489806367Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.autotrim_mins=None[0m
[1m2026-10-03T06:39:06.489807296Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.use_trader_prefix=True[0m
[1m2026-10-03T06:39:06.489807755Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.use_trader_id=True[0m
[1m2026-10-03T06:39:06.489808409Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.use_instance_id=False[0m
[1m2026-10-03T06:39:06.489809270Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.streams_prefix='stream'[0m
[1m2026-10-03T06:39:06.489810159Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.types_filter=None[0m
[1m2026-10-03T06:39:06.489885183Z[0m [INFO] BACKTESTER-001.Cache: READY[0m
[1m2026-10-03T06:39:06.490747823Z[0m [INFO] BACKTESTER-001.DataEngine: READY[0m
[1m2026-10-03T06:39:06.490881865Z[0m [INFO] BACKTESTER-001.RiskEngine: READY[0m
[1m2026-10-03T06:39:06.491006606Z[0m [94m[INFO] BACKTESTER-001.RiskEngine: TradingState is ACTIVE[0m
[1m2026-10-03T06:39:06.491167069Z[0m [INFO] BACKTESTER-001.Throttler-ORDER_SUBMIT_THROTTLER: READY[0m
[1m2026-10-03T06:39:06.491202097Z[0m [94m[INFO] BACKTESTER-001.RiskEngine: Set MAX_ORDER_SUBMIT_RATE: 100/00:00:01[0m
[1m2026-10-03T06:39:06.491231946Z[0m [INFO] BACKTESTER-001.Throttler-ORDER_MODIFY_THROTTLER: READY[0m
[1m2026-10-03T06:39:06.491247741Z[0m [94m[INFO] BACKTESTER-001.RiskEngine: Set MAX_ORDER_MODIFY_RATE: 100/00:00:01[0m
[1m2026-10-03T06:39:06.491315438Z[0m [INFO] BACKTESTER-001.ExecEngine: READY[0m
[1m2026-10-03T06:39:06.491355393Z[0m [94m[INFO] BACKTESTER-001.ExecEngine: config.snapshot_orders=False[0m
[1m2026-10-03T06:39:06.491363557Z[0m [94m[INFO] BACKTESTER-001.ExecEngine: config.snapshot_positions=False[0m
[1m2026-10-03T06:39:06.491364761Z[0m [94m[INFO] BACKTESTER-001.ExecEngine: config.snapshot_positions_interval_secs=None[0m
[1m2026-10-03T06:39:06.491365172Z[0m [94m[INFO] BACKTESTER-001.ExecEngine: config.allow_overfills=False[0m
[1m2026-10-03T06:39:06.491402763Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 general objects from database[0m
[1m2026-10-03T06:39:06.491416585Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 currencies from database[0m
[1m2026-10-03T06:39:06.491426509Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 instruments from database[0m
[1m2026-10-03T06:39:06.491434415Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 accounts from database[0m
[1m2026-10-03T06:39:06.491445470Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 orders from database[0m
[1m2026-10-03T06:39:06.491451156Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 order lists from database[0m
[1m2026-10-03T06:39:06.491462221Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 positions from database[0m
[1m2026-10-03T06:39:06.491478586Z[0m [INFO] BACKTESTER-001.Cache: Checking data integrity[0m
[1m2026-10-03T06:39:06.491511967Z[0m [92m[INFO] BACKTESTER-001.Cache: Integrity check passed in 33μs[0m
[1m2026-10-03T06:39:06.491634482Z[0m [INFO] BACKTESTER-001.ExecEngine: Loaded cache in 0ms[0m
[1m2026-10-03T06:39:06.491701416Z[0m [INFO] BACKTESTER-001.OrderEmulator: READY[0m
[1m2026-10-03T06:39:06.491762194Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: READY[0m
[1m2026-10-03T06:39:06.491806705Z[0m [INFO] BACKTESTER-001.BacktestEngine: Initialized in 8ms[0m
[1m2026-10-03T06:39:06.491978053Z[0m [INFO] BACKTESTER-001.SimulatedExchange(BINANCE): OmsType=NETTING[0m
[1m2026-10-03T06:39:06.492039190Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: READY[0m
[1m2026-10-03T06:39:06.492090916Z[0m [INFO] BACKTESTER-001.SimulatedExchange(BINANCE): Registered ExecutionClient-BINANCE[0m
[1m2026-10-03T06:39:06.492108438Z[0m [INFO] BACKTESTER-001.ExecEngine: Registered ExecutionClient-BINANCE[0m
[1m2026-10-03T06:39:06.492161413Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: READY[0m
[1m2026-10-03T06:39:06.492185264Z[0m [INFO] BACKTESTER-001.DataEngine: Registered BINANCE[0m
[1m2026-10-03T06:39:06.492198408Z[0m [INFO] BACKTESTER-001.BacktestEngine: Added SimulatedExchange(id=BINANCE, oms_type=NETTING, account_type=CASH)[0m
[1m2026-10-03T06:39:06.492454462Z[0m [INFO] BACKTESTER-001.SimulatedExchange(BINANCE): Added instrument BTCUSDT.BINANCE and created matching engine[0m
LIVE positions_open signature
[1m2026-10-03T06:39:06.492471204Z[0m [INFO] BACKTESTER-001.BacktestEngine: Added BTCUSDT.BINANCE Instrument[0m
(venue=None, instrument_id=None, strategy_id=None, side=<PositionSide.NO_POSITION_SIDE: 0>, account_id=None)
FULL LIVE positions_open DOCSTRING
Cache.positions_open(self, Venue venue=None, InstrumentId instrument_id=None, StrategyId strategy_id=None, PositionSide side=PositionSide.NO_POSITION_SIDE, AccountId account_id=None) -> list

Return all open positions with the given query filters.

*No particular order of list elements is guaranteed.*

Parameters
----------
venue : Venue, optional
    The venue ID query filter.
instrument_id : InstrumentId, optional
    The instrument ID query filter.
strategy_id : StrategyId, optional
    The strategy ID query filter.
side : PositionSide, default ``NO_POSITION_SIDE`` (no filter)
    The position side query filter.
account_id : AccountId, optional
    The account ID query filter.

Returns
-------
list[Position]
STATE QUERY fresh engine before run
CALL engine.cache.positions_open()
RETURN <class 'list'> count 0
CALL engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_inflight(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
FULL FIXTURE
[{'open_ts': 1735689600000,
  'close_ts': 1735776000000,
  'available_ts': 1735776000000,
  'ts_event': 1735776000000000000,
  'ts_init': 1735776000000000000,
  'open': 100,
  'high': 101,
  'low': 99,
  'close': 100,
  'volume': 1000},
 {'open_ts': 1735776000000,
  'close_ts': 1735862400000,
  'available_ts': 1735862400000,
  'ts_event': 1735862400000000000,
  'ts_init': 1735862400000000000,
  'open': 100,
  'high': 101,
  'low': 99,
  'close': 100,
  'volume': 1000},
 {'open_ts': 1735862400000,
  'close_ts': 1735948800000,
  'available_ts': 1735948800000,
  'ts_event': 1735948800000000000,
  'ts_init': 1735948800000000000,
  'open': 100,
  'high': 101,
  'low': 99,
  'close': 100,
  'volume': 1000},
 {'open_ts': 1735948800000,
  'close_ts': 1736035200000,
  'available_ts': 1736035200000,
  'ts_event': 1736035200000000000,
  'ts_init': 1736035200000000000,
  'open': 100,
  'high': 101,
  'low': 99,
  'close': 100,
  'volume': 1000}]
ACTUAL BARS [Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735776000000000000), Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735862400000000000), Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735948800000000000), Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1736035200000000000)]
[1m2026-10-03T06:39:06.496610365Z[0m [INFO] BACKTESTER-001.BacktestEngine: Added 4 BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL Bar elements[0m
[1m2026-10-03T06:39:06.496747290Z[0m [INFO] BACKTESTER-001.TraceBuyHold: READY[0m
CALL engine.run() -- all four bars INCLUDING end-exclusive sentinel reach engine
[1m2026-10-03T06:39:06.496847719Z[0m [INFO] BACKTESTER-001.ExecEngine: Registered OMS.UNSPECIFIED for Strategy TraceBuyHold-000[0m
[1m2026-10-03T06:39:06.496864650Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: Registered Strategy TraceBuyHold-000[0m
/tmp/phase18f-runtime-probe.py:192: Pandas4Warning: Timestamp.utcnow is deprecated and will be removed in a future version. Use Timestamp.now('UTC') instead.
  engine.run()
[1m2026-10-03T06:39:06.497282210Z[0m [INFO] BACKTESTER-001.Portfolio: Updated AccountState(account_id=BINANCE-001, account_type=CASH, base_currency=None, is_reported=True, balances=[AccountBalance(total=100_000.00000000 USDT, locked=0.00000000 USDT, free=100_000.00000000 USDT)], margins=[], event_id=cb3f6ae5-61c9-4c47-921a-32e04c8a3a25)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: STARTING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: Connecting...[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: Connected[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataEngine: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.RiskEngine: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: Connecting...[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: Connected[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecEngine: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataEngine: Connecting all clients...[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecEngine: Connecting all clients...[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.OrderEmulator: No emulated orders to reactivate[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.OrderEmulator: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.Portfolio: Initialized 0 open orders[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.Portfolio: Initialized 0 open positions[0m
[1m2025-01-02T00:00:00.000000000Z[0m [94m[INFO] BACKTESTER-001.TraceBuyHold: self.config.oms_type=None[0m
[1m2025-01-02T00:00:00.000000000Z[0m [94m[INFO] BACKTESTER-001.TraceBuyHold: self.config.external_order_claims=None[0m
[1m2025-01-02T00:00:00.000000000Z[0m [94m[INFO] BACKTESTER-001.TraceBuyHold: self.config.manage_gtd_expiry=False[0m
[1m2025-01-02T00:00:00.000000000Z[0m [94m[INFO] BACKTESTER-001.TraceBuyHold: Set ClientOrderIdGenerator client_order_id count to 0[0m
[1m2025-01-02T00:00:00.000000000Z[0m [94m[INFO] BACKTESTER-001.TraceBuyHold: Set ClientOrderIdGenerator order_list_id count to 0[0m
TRACE 1 on_start before
equity_snapshots []
STATE QUERY on_start
CALL engine.cache.positions_open()
RETURN <class 'list'> count 0
CALL engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_inflight(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: [CMD]--> SubscribeBars(bar_type=BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL, client_id=None, venue=BINANCE)[0m
TRACE 2 on_start after
equity_snapshots []
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  MEMORY USAGE[0m
[1m2025-01-02T00:00:00.000000000Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: RAM-Total: 9.73 GiB[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: RAM-Used: 0.93 GiB (9.51%)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: RAM-Avail: 8.81 GiB (90.49%)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Swap: disabled[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m SimulatedVenue BINANCE[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: CashAccount(id=BINANCE-001, type=CASH, base=None)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Balances starting:[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: 100_000.00000000 USDT[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m BACKTEST RUN[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run config ID:  None[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run ID:         b7015091-2e0e-4493-9ddb-5559765a1156[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run started:    2026-10-03T06:39:06.497133000Z[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Backtest start: 2025-01-02T00:00:00.000000000Z[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Batch start:    2025-01-02T00:00:00.000000000Z[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Batch end:      2025-01-05T00:00:00.000000000Z[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
TRACE 3 on_bar before
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735776000000000000)
ts_event 1735776000000000000 ms 1735776000000
ts_init 1735776000000000000 ms 1735776000000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots []
TRACE 4 _submit_entry before
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735776000000000000)
ts_event 1735776000000000000 ms 1735776000000
ts_init 1735776000000000000 ms 1735776000000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots []
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: <--[EVT] OrderInitialized(instrument_id=BTCUSDT.BINANCE, client_order_id=O-20250102-000000-001-000-1, side=BUY, type=MARKET, quantity=1.000000, time_in_force=GTC, post_only=False, reduce_only=False, quote_quantity=False, options={}, emulation_trigger=NO_TRIGGER, trigger_instrument_id=None, contingency_type=NO_CONTINGENCY, order_list_id=None, linked_order_ids=None, parent_order_id=None, exec_algorithm_id=None, exec_algorithm_params=None, exec_spawn_id=None, tags=None)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: [CMD]--> [Risk] SubmitOrder(order=MarketOrder(BUY 1.000000 BTCUSDT.BINANCE MARKET GTC, status=INITIALIZED, client_order_id=O-20250102-000000-001-000-1, venue_order_id=None, position_id=None, tags=None), position_id=None)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [1;33m[WARN] BACKTESTER-001.RiskEngine: Cannot check MARKET order risk: no prices for BTCUSDT.BINANCE[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: <--[EVT] OrderSubmitted(instrument_id=BTCUSDT.BINANCE, client_order_id=O-20250102-000000-001-000-1, account_id=BINANCE-001, ts_event=1735776000000000000)[0m
TRACE 5 _submit_entry after
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735776000000000000)
ts_event 1735776000000000000 ms 1735776000000
ts_init 1735776000000000000 ms 1735776000000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots []
TRACE 6 on_bar after
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735776000000000000)
ts_event 1735776000000000000 ms 1735776000000
ts_init 1735776000000000000 ms 1735776000000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735776000000, 100000.0)]
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.Portfolio: Updated AccountState(account_id=BINANCE-001, account_type=CASH, base_currency=None, is_reported=False, balances=[AccountBalance(total=99_899.90000000 USDT, locked=0.00000000 USDT, free=99_899.90000000 USDT), AccountBalance(total=1.00000000 BTC, locked=0.00000000 BTC, free=1.00000000 BTC)], margins=[], event_id=259b3c76-5c8c-4bcf-a509-5d125590e190)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.Portfolio: BTCUSDT.BINANCE account=BINANCE-001 net_position=1.000000[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: <--[EVT] OrderFilled(instrument_id=BTCUSDT.BINANCE, client_order_id=O-20250102-000000-001-000-1, venue_order_id=BINANCE-1-001, account_id=BINANCE-001, trade_id=T-1e0a8050dcb6f2a1-005, position_id=BTCUSDT.BINANCE-TraceBuyHold-000, order_side=BUY, order_type=MARKET, last_qty=1.000000, last_px=100.00 USDT, commission=0.10000000 USDT, liquidity_side=TAKER, ts_event=1735776000000000000)[0m
TRACE 7 on_order_filled before
OBJECT <class 'nautilus_trader.model.events.order.OrderFilled'> OrderFilled(trader_id=BACKTESTER-001, strategy_id=TraceBuyHold-000, instrument_id=BTCUSDT.BINANCE, client_order_id=O-20250102-000000-001-000-1, venue_order_id=BINANCE-1-001, account_id=BINANCE-001, trade_id=T-1e0a8050dcb6f2a1-005, position_id=BTCUSDT.BINANCE-TraceBuyHold-000, order_side=BUY, order_type=MARKET, last_qty=1.000000, last_px=100.00 USDT, commission=0.10000000 USDT, liquidity_side=TAKER, event_id=741d22d6-0a40-44f6-8299-baba6ae29242, ts_event=1735776000000000000, ts_init=1735776000000000000)
ts_event 1735776000000000000 ms 1735776000000
ts_init 1735776000000000000 ms 1735776000000
client_order_id ClientOrderId('O-20250102-000000-001-000-1') ms N/A
venue_order_id VenueOrderId('BINANCE-1-001') ms N/A
position_id PositionId('BTCUSDT.BINANCE-TraceBuyHold-000') ms N/A
last_qty Quantity(1.000000) ms N/A
last_px Price(100.00) ms N/A
equity_snapshots [(1735776000000, 100000.0)]
TRACE 8 on_order_filled after
OBJECT <class 'nautilus_trader.model.events.order.OrderFilled'> OrderFilled(trader_id=BACKTESTER-001, strategy_id=TraceBuyHold-000, instrument_id=BTCUSDT.BINANCE, client_order_id=O-20250102-000000-001-000-1, venue_order_id=BINANCE-1-001, account_id=BINANCE-001, trade_id=T-1e0a8050dcb6f2a1-005, position_id=BTCUSDT.BINANCE-TraceBuyHold-000, order_side=BUY, order_type=MARKET, last_qty=1.000000, last_px=100.00 USDT, commission=0.10000000 USDT, liquidity_side=TAKER, event_id=741d22d6-0a40-44f6-8299-baba6ae29242, ts_event=1735776000000000000, ts_init=1735776000000000000)
ts_event 1735776000000000000 ms 1735776000000
ts_init 1735776000000000000 ms 1735776000000
client_order_id ClientOrderId('O-20250102-000000-001-000-1') ms N/A
venue_order_id VenueOrderId('BINANCE-1-001') ms N/A
position_id PositionId('BTCUSDT.BINANCE-TraceBuyHold-000') ms N/A
last_qty Quantity(1.000000) ms N/A
last_px Price(100.00) ms N/A
equity_snapshots [(1735776000000, 99999.90000000001)]
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: <--[EVT] PositionOpened(instrument_id=BTCUSDT.BINANCE, position_id=BTCUSDT.BINANCE-TraceBuyHold-000, account_id=BINANCE-001, opening_order_id=O-20250102-000000-001-000-1, closing_order_id=None, entry=BUY, side=LONG, signed_qty=1.0, quantity=1.000000, peak_qty=1.000000, currency=USDT, avg_px_open=100.0, avg_px_close=0.0, realized_return=0.00000, realized_pnl=-0.10000000 USDT, unrealized_pnl=0.00000000 USDT, ts_opened=1735776000000000000, ts_last=1735776000000000000, ts_closed=0, duration_ns=0)[0m
TRACE 9 on_bar before
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735862400000000000)
ts_event 1735862400000000000 ms 1735862400000
ts_init 1735862400000000000 ms 1735862400000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735776000000, 99999.90000000001)]
TRACE 10 on_bar after
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735862400000000000)
ts_event 1735862400000000000 ms 1735862400000
ts_init 1735862400000000000 ms 1735862400000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001)]
TRACE 11 on_bar before
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735948800000000000)
ts_event 1735948800000000000 ms 1735948800000
ts_init 1735948800000000000 ms 1735948800000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001)]
TRACE 12 on_bar after
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735948800000000000)
ts_event 1735948800000000000 ms 1735948800000
ts_init 1735948800000000000 ms 1735948800000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001)]
TRACE 13 on_bar before
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1736035200000000000)
ts_event 1736035200000000000 ms 1736035200000
ts_init 1736035200000000000 ms 1736035200000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001)]
TRACE 14 on_bar after
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1736035200000000000)
ts_event 1736035200000000000 ms 1736035200000
ts_init 1736035200000000000 ms 1736035200000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001), (1736035200000, 99999.90000000001)]
TRACE 15 on_stop before
equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001), (1736035200000, 99999.90000000001)]
TRACE 16 on_stop after
equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001), (1736035200000, 99999.90000000001)]
[1m2025-01-05T00:00:00.000000000Z[0m [1;33m[WARN] BACKTESTER-001.TraceBuyHold: The `Strategy.on_stop` handler was called when not overridden. It's expected that any actions required when stopping the strategy occur here, such as unsubscribing from data[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: Disconnecting...[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: Disconnected[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataEngine: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.RiskEngine: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: Disconnecting...[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: Disconnected[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecEngine: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.OrderEmulator: STOPPED[0m
[1m2026-10-03T06:39:06.507262214Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:39:06.507274343Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m BACKTEST POST-RUN[0m
[1m2026-10-03T06:39:06.507275302Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:39:06.507277754Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run config ID:  None[0m
[1m2026-10-03T06:39:06.507281136Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run ID:         b7015091-2e0e-4493-9ddb-5559765a1156[0m
[1m2026-10-03T06:39:06.507289731Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run started:    2026-10-03T06:39:06.497133000Z[0m
[1m2026-10-03T06:39:06.507290588Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run finished:   2026-10-03T06:39:06.507208000Z[0m
[1m2026-10-03T06:39:06.507307160Z[0m [INFO] BACKTESTER-001.BacktestEngine: Elapsed time:   0 days 00:00:00.010075[0m
[1m2026-10-03T06:39:06.507315960Z[0m [INFO] BACKTESTER-001.BacktestEngine: Backtest start: 2025-01-02T00:00:00.000000000Z[0m
[1m2026-10-03T06:39:06.507317358Z[0m [INFO] BACKTESTER-001.BacktestEngine: Backtest end:   2025-01-05T00:00:00.000000000Z[0m
[1m2026-10-03T06:39:06.507323806Z[0m [INFO] BACKTESTER-001.BacktestEngine: Backtest range: 3 days 00:00:00[0m
[1m2026-10-03T06:39:06.507332703Z[0m [INFO] BACKTESTER-001.BacktestEngine: Iterations: 4[0m
[1m2026-10-03T06:39:06.507335902Z[0m [INFO] BACKTESTER-001.BacktestEngine: Total events: 2[0m
[1m2026-10-03T06:39:06.507344021Z[0m [INFO] BACKTESTER-001.BacktestEngine: Total orders: 1[0m
[1m2026-10-03T06:39:06.507359652Z[0m [INFO] BACKTESTER-001.BacktestEngine: Total positions: 1[0m
[1m2026-10-03T06:39:06.507402071Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:39:06.507407267Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m SimulatedVenue BINANCE[0m
[1m2026-10-03T06:39:06.507407705Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:39:06.507412417Z[0m [INFO] BACKTESTER-001.BacktestEngine: CashAccount(id=BINANCE-001, type=CASH, base=None)[0m
[1m2026-10-03T06:39:06.507412898Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.507413591Z[0m [INFO] BACKTESTER-001.BacktestEngine: Balances starting:[0m
[1m2026-10-03T06:39:06.507423452Z[0m [INFO] BACKTESTER-001.BacktestEngine: 100_000.00000000 USDT[0m
[1m2026-10-03T06:39:06.507431061Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.507431783Z[0m [INFO] BACKTESTER-001.BacktestEngine: Balances ending:[0m
[1m2026-10-03T06:39:06.507437058Z[0m [INFO] BACKTESTER-001.BacktestEngine: 99_899.90000000 USDT[0m
[1m2026-10-03T06:39:06.507439288Z[0m [INFO] BACKTESTER-001.BacktestEngine: 1.00000000 BTC[0m
[1m2026-10-03T06:39:06.507446364Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.507447204Z[0m [INFO] BACKTESTER-001.BacktestEngine: Commissions:[0m
[1m2026-10-03T06:39:06.507457825Z[0m [INFO] BACKTESTER-001.BacktestEngine: -0.10000000 USDT[0m
[1m2026-10-03T06:39:06.507465276Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.507466583Z[0m [INFO] BACKTESTER-001.BacktestEngine: Unrealized PnLs (included in totals):[0m
[1m2026-10-03T06:39:06.507528263Z[0m [INFO] BACKTESTER-001.BacktestEngine: 0.00000000 USDT[0m
[1m2026-10-03T06:39:06.507580545Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:39:06.507588655Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m PORTFOLIO PERFORMANCE[0m
[1m2026-10-03T06:39:06.507589494Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:39:06.508857666Z[0m [INFO] BACKTESTER-001.BacktestEngine:  PnL Statistics (BTC)[0m
[1m2026-10-03T06:39:06.508882858Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.509000292Z[0m [INFO] BACKTESTER-001.BacktestEngine: PnL (total):                    1.0[0m
[1m2026-10-03T06:39:06.509012715Z[0m [INFO] BACKTESTER-001.BacktestEngine: PnL% (total):                   0.0[0m
[1m2026-10-03T06:39:06.509013521Z[0m [INFO] BACKTESTER-001.BacktestEngine: Max Winner:                     nan[0m
[1m2026-10-03T06:39:06.509013828Z[0m [INFO] BACKTESTER-001.BacktestEngine: Avg Winner:                     nan[0m
[1m2026-10-03T06:39:06.509014073Z[0m [INFO] BACKTESTER-001.BacktestEngine: Min Winner:                     nan[0m
[1m2026-10-03T06:39:06.509014628Z[0m [INFO] BACKTESTER-001.BacktestEngine: Min Loser:                      nan[0m
[1m2026-10-03T06:39:06.509015128Z[0m [INFO] BACKTESTER-001.BacktestEngine: Avg Loser:                      nan[0m
[1m2026-10-03T06:39:06.509015588Z[0m [INFO] BACKTESTER-001.BacktestEngine: Max Loser:                      nan[0m
[1m2026-10-03T06:39:06.509015850Z[0m [INFO] BACKTESTER-001.BacktestEngine: Expectancy:                     nan[0m
[1m2026-10-03T06:39:06.509017699Z[0m [INFO] BACKTESTER-001.BacktestEngine: Win Rate:                       nan[0m
[1m2026-10-03T06:39:06.509018538Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.509019525Z[0m [INFO] BACKTESTER-001.BacktestEngine:  PnL Statistics (USDT)[0m
[1m2026-10-03T06:39:06.509019884Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.509163194Z[0m [INFO] BACKTESTER-001.BacktestEngine: PnL (total):                    -100.1[0m
[1m2026-10-03T06:39:06.509174366Z[0m [INFO] BACKTESTER-001.BacktestEngine: PnL% (total):                   -0.10009999999999128[0m
[1m2026-10-03T06:39:06.509175647Z[0m [INFO] BACKTESTER-001.BacktestEngine: Max Winner:                     nan[0m
[1m2026-10-03T06:39:06.509175927Z[0m [INFO] BACKTESTER-001.BacktestEngine: Avg Winner:                     nan[0m
[1m2026-10-03T06:39:06.509176205Z[0m [INFO] BACKTESTER-001.BacktestEngine: Min Winner:                     nan[0m
[1m2026-10-03T06:39:06.509176417Z[0m [INFO] BACKTESTER-001.BacktestEngine: Min Loser:                      -0.1[0m
[1m2026-10-03T06:39:06.509176597Z[0m [INFO] BACKTESTER-001.BacktestEngine: Avg Loser:                      -0.1[0m
[1m2026-10-03T06:39:06.509176785Z[0m [INFO] BACKTESTER-001.BacktestEngine: Max Loser:                      -0.1[0m
[1m2026-10-03T06:39:06.509177051Z[0m [INFO] BACKTESTER-001.BacktestEngine: Expectancy:                     -0.1[0m
[1m2026-10-03T06:39:06.509177261Z[0m [INFO] BACKTESTER-001.BacktestEngine: Win Rate:                       0.0[0m
[1m2026-10-03T06:39:06.509178238Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.509179000Z[0m [INFO] BACKTESTER-001.BacktestEngine:  Returns Statistics[0m
[1m2026-10-03T06:39:06.509179346Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.509235271Z[0m [INFO] BACKTESTER-001.BacktestEngine: Returns Volatility (252 days):  nan[0m
[1m2026-10-03T06:39:06.509243268Z[0m [INFO] BACKTESTER-001.BacktestEngine: Average (Return):               nan[0m
[1m2026-10-03T06:39:06.509244027Z[0m [INFO] BACKTESTER-001.BacktestEngine: Average Loss (Return):          nan[0m
[1m2026-10-03T06:39:06.509244287Z[0m [INFO] BACKTESTER-001.BacktestEngine: Average Win (Return):           nan[0m
[1m2026-10-03T06:39:06.509244536Z[0m [INFO] BACKTESTER-001.BacktestEngine: Sharpe Ratio (252 days):        nan[0m
[1m2026-10-03T06:39:06.509244776Z[0m [INFO] BACKTESTER-001.BacktestEngine: Sortino Ratio (252 days):       nan[0m
[1m2026-10-03T06:39:06.509245034Z[0m [INFO] BACKTESTER-001.BacktestEngine: Profit Factor:                  nan[0m
[1m2026-10-03T06:39:06.509245265Z[0m [INFO] BACKTESTER-001.BacktestEngine: Risk Return Ratio:              nan[0m
[1m2026-10-03T06:39:06.509245845Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.509246607Z[0m [INFO] BACKTESTER-001.BacktestEngine:  General Statistics[0m
[1m2026-10-03T06:39:06.509246918Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.509274619Z[0m [INFO] BACKTESTER-001.BacktestEngine: Long Ratio:                     1.0[0m
[1m2026-10-03T06:39:06.509282843Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
STATE QUERY postrun before disposal
CALL engine.cache.positions_open()
RETURN <class 'list'> count 1
ITEM <class 'nautilus_trader.model.position.Position'> Position(LONG 1.000000 BTCUSDT.BINANCE, id=BTCUSDT.BINANCE-TraceBuyHold-000)
FIELD id PositionId('BTCUSDT.BINANCE-TraceBuyHold-000') DOC The position ID.

:returns: `PositionId`
FIELD client_order_id ABSENT
FIELD instrument_id InstrumentId('BTCUSDT.BINANCE') DOC The position instrument ID.

:returns: `InstrumentId`
FIELD is_open True DOC Return whether the position side is **not** ``FLAT``.

Returns
-------
bool
FIELD is_closed False DOC Return whether the position side is ``FLAT``.

Returns
-------
bool
FIELD side <PositionSide.LONG: 2> DOC The current position side.

:returns: `PositionSide`
FIELD quantity Quantity(1.000000) DOC The current open quantity.

:returns: `Quantity`
FIELD signed_qty 1.0 DOC The current signed quantity (positive for position side ``LONG``, negative for ``SHORT``).

:returns: `double`
FIELD status ABSENT
CALL engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 1
ITEM <class 'nautilus_trader.model.position.Position'> Position(LONG 1.000000 BTCUSDT.BINANCE, id=BTCUSDT.BINANCE-TraceBuyHold-000)
FIELD id PositionId('BTCUSDT.BINANCE-TraceBuyHold-000') DOC The position ID.

:returns: `PositionId`
FIELD client_order_id ABSENT
FIELD instrument_id InstrumentId('BTCUSDT.BINANCE') DOC The position instrument ID.

:returns: `InstrumentId`
FIELD is_open True DOC Return whether the position side is **not** ``FLAT``.

Returns
-------
bool
FIELD is_closed False DOC Return whether the position side is ``FLAT``.

Returns
-------
bool
FIELD side <PositionSide.LONG: 2> DOC The current position side.

:returns: `PositionSide`
FIELD quantity Quantity(1.000000) DOC The current open quantity.

:returns: `Quantity`
FIELD signed_qty 1.0 DOC The current signed quantity (positive for position side ``LONG``, negative for ``SHORT``).

:returns: `double`
FIELD status ABSENT
CALL engine.cache.orders_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_inflight(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
FINAL equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001), (1736035200000, 99999.90000000001)]
ENTRY SUBMISSION TIMES [1735776000000] FILL TIMES [1735776000000]
REPORT fills class <class 'pandas.DataFrame'>
columns ['trader_id', 'strategy_id', 'instrument_id', 'venue_order_id', 'account_id', 'trade_id', 'position_id', 'order_side', 'order_type', 'last_qty', 'last_px', 'currency', 'commission', 'liquidity_side', 'event_id', 'ts_event', 'ts_init', 'info', 'reconciliation'] dtypes {'trader_id': <StringDtype(na_value=nan)>, 'strategy_id': <StringDtype(na_value=nan)>, 'instrument_id': <StringDtype(na_value=nan)>, 'venue_order_id': <StringDtype(na_value=nan)>, 'account_id': <StringDtype(na_value=nan)>, 'trade_id': <StringDtype(na_value=nan)>, 'position_id': <StringDtype(na_value=nan)>, 'order_side': <StringDtype(na_value=nan)>, 'order_type': <StringDtype(na_value=nan)>, 'last_qty': <StringDtype(na_value=nan)>, 'last_px': <StringDtype(na_value=nan)>, 'currency': <StringDtype(na_value=nan)>, 'commission': <StringDtype(na_value=nan)>, 'liquidity_side': <StringDtype(na_value=nan)>, 'event_id': <StringDtype(na_value=nan)>, 'ts_event': datetime64[ns, UTC], 'ts_init': datetime64[ns, UTC], 'info': dtype('O'), 'reconciliation': dtype('bool')}
index class <class 'pandas.Index'> index name 'client_order_id' index values ['O-20250102-000000-001-000-1']
FULL FRAME
                                  trader_id       strategy_id    instrument_id venue_order_id   account_id                trade_id                       position_id order_side order_type  last_qty last_px currency       commission liquidity_side                              event_id                  ts_event                   ts_init info  reconciliation
client_order_id                                                                                                                                                                                                                                                                                                                                                     
O-20250102-000000-001-000-1  BACKTESTER-001  TraceBuyHold-000  BTCUSDT.BINANCE  BINANCE-1-001  BINANCE-001  T-1e0a8050dcb6f2a1-005  BTCUSDT.BINANCE-TraceBuyHold-000        BUY     MARKET  1.000000  100.00     USDT  0.10000000 USDT          TAKER  741d22d6-0a40-44f6-8299-baba6ae29242 2025-01-02 00:00:00+00:00 2025-01-02 00:00:00+00:00   {}           False
FULL RECORDS (index retained)
[{'client_order_id': 'O-20250102-000000-001-000-1',
  'trader_id': 'BACKTESTER-001',
  'strategy_id': 'TraceBuyHold-000',
  'instrument_id': 'BTCUSDT.BINANCE',
  'venue_order_id': 'BINANCE-1-001',
  'account_id': 'BINANCE-001',
  'trade_id': 'T-1e0a8050dcb6f2a1-005',
  'position_id': 'BTCUSDT.BINANCE-TraceBuyHold-000',
  'order_side': 'BUY',
  'order_type': 'MARKET',
  'last_qty': '1.000000',
  'last_px': '100.00',
  'currency': 'USDT',
  'commission': '0.10000000 USDT',
  'liquidity_side': 'TAKER',
  'event_id': '741d22d6-0a40-44f6-8299-baba6ae29242',
  'ts_event': Timestamp('2025-01-02 00:00:00+0000', tz='UTC'),
  'ts_init': Timestamp('2025-01-02 00:00:00+0000', tz='UTC'),
  'info': {},
  'reconciliation': False}]
TIME ts_opened ABSENT
TIME ORIGINAL ts_event Timestamp('2025-01-02 00:00:00+0000', tz='UTC') type <class 'pandas.Timestamp'> ms 1735776000000
TIME ORIGINAL ts_init Timestamp('2025-01-02 00:00:00+0000', tz='UTC') type <class 'pandas.Timestamp'> ms 1735776000000
TIME ts_last ABSENT
REPORT positions class <class 'pandas.DataFrame'>
columns ['trader_id', 'strategy_id', 'instrument_id', 'account_id', 'opening_order_id', 'closing_order_id', 'entry', 'side', 'quantity', 'peak_qty', 'ts_init', 'ts_opened', 'ts_last', 'ts_closed', 'duration_ns', 'avg_px_open', 'avg_px_close', 'commissions', 'realized_return', 'realized_pnl', 'is_snapshot'] dtypes {'trader_id': <StringDtype(na_value=nan)>, 'strategy_id': <StringDtype(na_value=nan)>, 'instrument_id': <StringDtype(na_value=nan)>, 'account_id': <StringDtype(na_value=nan)>, 'opening_order_id': <StringDtype(na_value=nan)>, 'closing_order_id': dtype('O'), 'entry': <StringDtype(na_value=nan)>, 'side': <StringDtype(na_value=nan)>, 'quantity': <StringDtype(na_value=nan)>, 'peak_qty': <StringDtype(na_value=nan)>, 'ts_init': dtype('int64'), 'ts_opened': datetime64[ns, UTC], 'ts_last': dtype('int64'), 'ts_closed': dtype('O'), 'duration_ns': dtype('O'), 'avg_px_open': dtype('float64'), 'avg_px_close': dtype('O'), 'commissions': dtype('O'), 'realized_return': dtype('float64'), 'realized_pnl': <StringDtype(na_value=nan)>, 'is_snapshot': dtype('bool')}
index class <class 'pandas.Index'> index name 'position_id' index values ['BTCUSDT.BINANCE-TraceBuyHold-000']
FULL FRAME
                                       trader_id       strategy_id    instrument_id   account_id             opening_order_id closing_order_id entry  side  quantity  peak_qty              ts_init                 ts_opened              ts_last ts_closed duration_ns  avg_px_open avg_px_close        commissions  realized_return      realized_pnl  is_snapshot
position_id                                                                                                                                                                                                                                                                                                                                                          
BTCUSDT.BINANCE-TraceBuyHold-000  BACKTESTER-001  TraceBuyHold-000  BTCUSDT.BINANCE  BINANCE-001  O-20250102-000000-001-000-1             None   BUY  LONG  1.000000  1.000000  1735776000000000000 2025-01-02 00:00:00+00:00  1735776000000000000      <NA>        None        100.0         None  [0.10000000 USDT]              0.0  -0.10000000 USDT        False
FULL RECORDS (index retained)
[{'position_id': 'BTCUSDT.BINANCE-TraceBuyHold-000',
  'trader_id': 'BACKTESTER-001',
  'strategy_id': 'TraceBuyHold-000',
  'instrument_id': 'BTCUSDT.BINANCE',
  'account_id': 'BINANCE-001',
  'opening_order_id': 'O-20250102-000000-001-000-1',
  'closing_order_id': None,
  'entry': 'BUY',
  'side': 'LONG',
  'quantity': '1.000000',
  'peak_qty': '1.000000',
  'ts_init': 1735776000000000000,
  'ts_opened': Timestamp('2025-01-02 00:00:00+0000', tz='UTC'),
  'ts_last': 1735776000000000000,
  'ts_closed': None,
  'duration_ns': None,
  'avg_px_open': 100.0,
  'avg_px_close': None,
  'commissions': ['0.10000000 USDT'],
  'realized_return': 0.0,
  'realized_pnl': '-0.10000000 USDT',
  'is_snapshot': False}]
TIME ORIGINAL ts_opened Timestamp('2025-01-02 00:00:00+0000', tz='UTC') type <class 'pandas.Timestamp'> ms 1735776000000
TIME ts_event ABSENT
TIME ORIGINAL ts_init 1735776000000000000 type <class 'int'> ms 1735776000000
TIME ORIGINAL ts_last 1735776000000000000 type <class 'int'> ms 1735776000000
REPORT account class <class 'pandas.DataFrame'>
columns ['total', 'locked', 'free', 'currency', 'account_id', 'account_type', 'base_currency', 'margins', 'reported', 'info'] dtypes {'total': <StringDtype(na_value=nan)>, 'locked': <StringDtype(na_value=nan)>, 'free': <StringDtype(na_value=nan)>, 'currency': <StringDtype(na_value=nan)>, 'account_id': <StringDtype(na_value=nan)>, 'account_type': <StringDtype(na_value=nan)>, 'base_currency': dtype('O'), 'margins': dtype('O'), 'reported': dtype('bool'), 'info': dtype('O')}
index class <class 'pandas.DatetimeIndex'> index name None index values [Timestamp('2025-01-02 00:00:00+0000', tz='UTC'), Timestamp('2025-01-02 00:00:00+0000', tz='UTC'), Timestamp('2025-01-02 00:00:00+0000', tz='UTC')]
FULL FRAME
                                     total      locked             free currency   account_id account_type base_currency margins  reported info
2025-01-02 00:00:00+00:00  100000.00000000  0.00000000  100000.00000000     USDT  BINANCE-001         CASH          None      []      True   {}
2025-01-02 00:00:00+00:00   99899.90000000  0.00000000   99899.90000000     USDT  BINANCE-001         CASH          None      []     False   {}
2025-01-02 00:00:00+00:00       1.00000000  0.00000000       1.00000000      BTC  BINANCE-001         CASH          None      []     False   {}
FULL RECORDS (index retained)
[{'index': Timestamp('2025-01-02 00:00:00+0000', tz='UTC'),
  'total': '100000.00000000',
  'locked': '0.00000000',
  'free': '100000.00000000',
  'currency': 'USDT',
  'account_id': 'BINANCE-001',
  'account_type': 'CASH',
  'base_currency': None,
  'margins': [],
  'reported': True,
  'info': {}},
 {'index': Timestamp('2025-01-02 00:00:00+0000', tz='UTC'),
  'total': '99899.90000000',
  'locked': '0.00000000',
  'free': '99899.90000000',
  'currency': 'USDT',
  'account_id': 'BINANCE-001',
  'account_type': 'CASH',
  'base_currency': None,
  'margins': [],
  'reported': False,
  'info': {}},
 {'index': Timestamp('2025-01-02 00:00:00+0000', tz='UTC'),
  'total': '1.00000000',
  'locked': '0.00000000',
  'free': '1.00000000',
  'currency': 'BTC',
  'account_id': 'BINANCE-001',
  'account_type': 'CASH',
  'base_currency': None,
  'margins': [],
  'reported': False,
  'info': {}}]
TIME ts_opened ABSENT
TIME ts_event ABSENT
TIME ts_init ABSENT
TIME ts_last ABSENT
TIME ts_opened ABSENT
TIME ts_event ABSENT
TIME ts_init ABSENT
TIME ts_last ABSENT
TIME ts_opened ABSENT
TIME ts_event ABSENT
TIME ts_init ABSENT
TIME ts_last ABSENT
TERMINAL last report row per currency: cash USDT 99899.9 base BTC 1.0 last eligible close 1735948800000 last eligible price 100 cash + base * last eligible price 99999.9 NO liquidation; sentinel price equals eligible price but still reached matching/valuation
CASE PASS
CALL engine.dispose()
[1m2026-10-03T06:39:06.540704736Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: DISPOSED[0m
[1m2026-10-03T06:39:06.540734886Z[0m [INFO] BACKTESTER-001.DataEngine: DISPOSED[0m
[1m2026-10-03T06:39:06.540742900Z[0m [INFO] BACKTESTER-001.RiskEngine: DISPOSED[0m
[1m2026-10-03T06:39:06.540755248Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: DISPOSED[0m
[1m2026-10-03T06:39:06.540760410Z[0m [INFO] BACKTESTER-001.ExecEngine: DISPOSED[0m
[1m2026-10-03T06:39:06.540778036Z[0m [INFO] BACKTESTER-001.OrderEmulator: DISPOSED[0m
[1m2026-10-03T06:39:06.540796905Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: Cleared actors[0m
[1m2026-10-03T06:39:06.540816146Z[0m [INFO] BACKTESTER-001.TraceBuyHold: DISPOSED[0m
[1m2026-10-03T06:39:06.540831806Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: Cleared trading strategies[0m
[1m2026-10-03T06:39:06.540840872Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: Cleared execution algorithms[0m
[1m2026-10-03T06:39:06.540847593Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: DISPOSED[0m
CASE scratch gated
[1m2026-10-03T06:39:06.540887068Z[0m [INFO] BACKTESTER-001.Cache: Reset[0m
[1m2026-10-03T06:39:06.540911033Z[0m [INFO] BACKTESTER-001.MessageBus: Closed message bus[0m
[1m2026-10-03T06:39:06.540956870Z[0m [INFO] BACKTESTER-001.BacktestEngine: Building system kernel[0m
[1m2026-10-03T06:39:06.540975550Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.database=None[0m
[1m2026-10-03T06:39:06.540983723Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.encoding='json'[0m
[1m2026-10-03T06:39:06.540984920Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.timestamps_as_iso8601=False[0m
[1m2026-10-03T06:39:06.540985578Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.buffer_interval_ms=None[0m
[1m2026-10-03T06:39:06.540986151Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.autotrim_mins=None[0m
[1m2026-10-03T06:39:06.540986863Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.use_trader_prefix=True[0m
[1m2026-10-03T06:39:06.540987302Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.use_trader_id=True[0m
[1m2026-10-03T06:39:06.540987760Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.use_instance_id=False[0m
[1m2026-10-03T06:39:06.540989312Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.streams_prefix='stream'[0m
[1m2026-10-03T06:39:06.540989852Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.types_filter=None[0m
[1m2026-10-03T06:39:06.541016696Z[0m [INFO] BACKTESTER-001.Cache: READY[0m
[1m2026-10-03T06:39:06.541239394Z[0m [INFO] BACKTESTER-001.DataEngine: READY[0m
[1m2026-10-03T06:39:06.541303925Z[0m [INFO] BACKTESTER-001.RiskEngine: READY[0m
[1m2026-10-03T06:39:06.541334414Z[0m [94m[INFO] BACKTESTER-001.RiskEngine: TradingState is ACTIVE[0m
[1m2026-10-03T06:39:06.541377555Z[0m [INFO] BACKTESTER-001.Throttler-ORDER_SUBMIT_THROTTLER: READY[0m
[1m2026-10-03T06:39:06.541404863Z[0m [94m[INFO] BACKTESTER-001.RiskEngine: Set MAX_ORDER_SUBMIT_RATE: 100/00:00:01[0m
[1m2026-10-03T06:39:06.541420630Z[0m [INFO] BACKTESTER-001.Throttler-ORDER_MODIFY_THROTTLER: READY[0m
[1m2026-10-03T06:39:06.541435960Z[0m [94m[INFO] BACKTESTER-001.RiskEngine: Set MAX_ORDER_MODIFY_RATE: 100/00:00:01[0m
[1m2026-10-03T06:39:06.541485881Z[0m [INFO] BACKTESTER-001.ExecEngine: READY[0m
[1m2026-10-03T06:39:06.541512926Z[0m [94m[INFO] BACKTESTER-001.ExecEngine: config.snapshot_orders=False[0m
[1m2026-10-03T06:39:06.541520836Z[0m [94m[INFO] BACKTESTER-001.ExecEngine: config.snapshot_positions=False[0m
[1m2026-10-03T06:39:06.541522002Z[0m [94m[INFO] BACKTESTER-001.ExecEngine: config.snapshot_positions_interval_secs=None[0m
[1m2026-10-03T06:39:06.541522476Z[0m [94m[INFO] BACKTESTER-001.ExecEngine: config.allow_overfills=False[0m
[1m2026-10-03T06:39:06.541565253Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 general objects from database[0m
[1m2026-10-03T06:39:06.541575729Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 currencies from database[0m
[1m2026-10-03T06:39:06.541578397Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 instruments from database[0m
[1m2026-10-03T06:39:06.541581736Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 accounts from database[0m
[1m2026-10-03T06:39:06.541590801Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 orders from database[0m
[1m2026-10-03T06:39:06.541593486Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 order lists from database[0m
[1m2026-10-03T06:39:06.541595341Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 positions from database[0m
[1m2026-10-03T06:39:06.541603881Z[0m [INFO] BACKTESTER-001.Cache: Checking data integrity[0m
[1m2026-10-03T06:39:06.541618215Z[0m [92m[INFO] BACKTESTER-001.Cache: Integrity check passed in 12μs[0m
[1m2026-10-03T06:39:06.541631424Z[0m [INFO] BACKTESTER-001.ExecEngine: Loaded cache in 0ms[0m
[1m2026-10-03T06:39:06.541665019Z[0m [INFO] BACKTESTER-001.OrderEmulator: READY[0m
[1m2026-10-03T06:39:06.541706993Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: READY[0m
[1m2026-10-03T06:39:06.541735648Z[0m [INFO] BACKTESTER-001.BacktestEngine: Initialized in 0ms[0m
[1m2026-10-03T06:39:06.541821532Z[0m [INFO] BACKTESTER-001.SimulatedExchange(BINANCE): OmsType=NETTING[0m
[1m2026-10-03T06:39:06.541880858Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: READY[0m
[1m2026-10-03T06:39:06.541907467Z[0m [INFO] BACKTESTER-001.SimulatedExchange(BINANCE): Registered ExecutionClient-BINANCE[0m
[1m2026-10-03T06:39:06.541918978Z[0m [INFO] BACKTESTER-001.ExecEngine: Registered ExecutionClient-BINANCE[0m
[1m2026-10-03T06:39:06.541938067Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: READY[0m
[1m2026-10-03T06:39:06.541954431Z[0m [INFO] BACKTESTER-001.DataEngine: Registered BINANCE[0m
[1m2026-10-03T06:39:06.541964807Z[0m [INFO] BACKTESTER-001.BacktestEngine: Added SimulatedExchange(id=BINANCE, oms_type=NETTING, account_type=CASH)[0m
LIVE positions_open signature
[1m2026-10-03T06:39:06.542060492Z[0m [INFO] BACKTESTER-001.SimulatedExchange(BINANCE): Added instrument BTCUSDT.BINANCE and created matching engine[0m
[1m2026-10-03T06:39:06.542075771Z[0m [INFO] BACKTESTER-001.BacktestEngine: Added BTCUSDT.BINANCE Instrument[0m
(venue=None, instrument_id=None, strategy_id=None, side=<PositionSide.NO_POSITION_SIDE: 0>, account_id=None)
FULL LIVE positions_open DOCSTRING
Cache.positions_open(self, Venue venue=None, InstrumentId instrument_id=None, StrategyId strategy_id=None, PositionSide side=PositionSide.NO_POSITION_SIDE, AccountId account_id=None) -> list

Return all open positions with the given query filters.

*No particular order of list elements is guaranteed.*

Parameters
----------
venue : Venue, optional
    The venue ID query filter.
instrument_id : InstrumentId, optional
    The instrument ID query filter.
strategy_id : StrategyId, optional
    The strategy ID query filter.
side : PositionSide, default ``NO_POSITION_SIDE`` (no filter)
    The position side query filter.
account_id : AccountId, optional
    The account ID query filter.

Returns
-------
list[Position]
STATE QUERY fresh engine before run
CALL engine.cache.positions_open()
RETURN <class 'list'> count 0
CALL engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_inflight(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
FULL FIXTURE
[{'open_ts': 1735689600000,
  'close_ts': 1735776000000,
  'available_ts': 1735776000000,
  'ts_event': 1735776000000000000,
  'ts_init': 1735776000000000000,
  'open': 100,
  'high': 101,
  'low': 99,
  'close': 100,
  'volume': 1000},
 {'open_ts': 1735776000000,
  'close_ts': 1735862400000,
  'available_ts': 1735862400000,
  'ts_event': 1735862400000000000,
  'ts_init': 1735862400000000000,
  'open': 100,
  'high': 101,
  'low': 99,
  'close': 100,
  'volume': 1000},
 {'open_ts': 1735862400000,
  'close_ts': 1735948800000,
  'available_ts': 1735948800000,
  'ts_event': 1735948800000000000,
  'ts_init': 1735948800000000000,
  'open': 100,
  'high': 101,
  'low': 99,
  'close': 100,
  'volume': 1000},
 {'open_ts': 1735948800000,
  'close_ts': 1736035200000,
  'available_ts': 1736035200000,
  'ts_event': 1736035200000000000,
  'ts_init': 1736035200000000000,
  'open': 100,
  'high': 101,
  'low': 99,
  'close': 100,
  'volume': 1000}]
ACTUAL BARS [Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735776000000000000), Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735862400000000000), Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735948800000000000), Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1736035200000000000)]
[1m2026-10-03T06:39:06.542524504Z[0m [INFO] BACKTESTER-001.BacktestEngine: Added 4 BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL Bar elements[0m
[1m2026-10-03T06:39:06.542621171Z[0m [INFO] BACKTESTER-001.TraceBuyHold: READY[0m
[1m2026-10-03T06:39:06.542679048Z[0m [INFO] BACKTESTER-001.ExecEngine: Registered OMS.UNSPECIFIED for Strategy TraceBuyHold-000[0m
[1m2026-10-03T06:39:06.542691475Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: Registered Strategy TraceBuyHold-000[0m
CALL engine.run() -- all four bars INCLUDING end-exclusive sentinel reach engine
/tmp/phase18f-runtime-probe.py:192: Pandas4Warning: Timestamp.utcnow is deprecated and will be removed in a future version. Use Timestamp.now('UTC') instead.
  engine.run()
[1m2026-10-03T06:39:06.542842773Z[0m [INFO] BACKTESTER-001.Portfolio: Updated AccountState(account_id=BINANCE-001, account_type=CASH, base_currency=None, is_reported=True, balances=[AccountBalance(total=100_000.00000000 USDT, locked=0.00000000 USDT, free=100_000.00000000 USDT)], margins=[], event_id=c826c397-c62c-43e5-92ae-270bd6f3e7e7)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: STARTING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: Connecting...[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: Connected[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataEngine: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.RiskEngine: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: Connecting...[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: Connected[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecEngine: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataEngine: Connecting all clients...[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecEngine: Connecting all clients...[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.OrderEmulator: No emulated orders to reactivate[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.OrderEmulator: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.Portfolio: Initialized 0 open orders[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.Portfolio: Initialized 0 open positions[0m
[1m2025-01-02T00:00:00.000000000Z[0m [94m[INFO] BACKTESTER-001.TraceBuyHold: self.config.oms_type=None[0m
[1m2025-01-02T00:00:00.000000000Z[0m [94m[INFO] BACKTESTER-001.TraceBuyHold: self.config.external_order_claims=None[0m
[1m2025-01-02T00:00:00.000000000Z[0m [94m[INFO] BACKTESTER-001.TraceBuyHold: self.config.manage_gtd_expiry=False[0m
[1m2025-01-02T00:00:00.000000000Z[0m [94m[INFO] BACKTESTER-001.TraceBuyHold: Set ClientOrderIdGenerator client_order_id count to 0[0m
[1m2025-01-02T00:00:00.000000000Z[0m [94m[INFO] BACKTESTER-001.TraceBuyHold: Set ClientOrderIdGenerator order_list_id count to 0[0m
TRACE 1 on_start before
equity_snapshots []
STATE QUERY on_start
CALL engine.cache.positions_open()
RETURN <class 'list'> count 0
CALL engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_inflight(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: [CMD]--> SubscribeBars(bar_type=BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL, client_id=None, venue=BINANCE)[0m
TRACE 2 on_start after
equity_snapshots []
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  MEMORY USAGE[0m
[1m2025-01-02T00:00:00.000000000Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: RAM-Total: 9.73 GiB[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: RAM-Used: 0.93 GiB (9.58%)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: RAM-Avail: 8.80 GiB (90.42%)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Swap: disabled[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m SimulatedVenue BINANCE[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: CashAccount(id=BINANCE-001, type=CASH, base=None)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Balances starting:[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: 100_000.00000000 USDT[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m BACKTEST RUN[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run config ID:  None[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run ID:         3442171e-28a5-4384-8efc-db3278a96f82[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run started:    2026-10-03T06:39:06.542780000Z[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Backtest start: 2025-01-02T00:00:00.000000000Z[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Batch start:    2025-01-02T00:00:00.000000000Z[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Batch end:      2025-01-05T00:00:00.000000000Z[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
TRACE 3 on_bar before
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735776000000000000)
ts_event 1735776000000000000 ms 1735776000000
ts_init 1735776000000000000 ms 1735776000000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots []
GATE warmup 1735776000000
TRACE 4 on_bar after
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735776000000000000)
ts_event 1735776000000000000 ms 1735776000000
ts_init 1735776000000000000 ms 1735776000000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots []
TRACE 5 on_bar before
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735862400000000000)
ts_event 1735862400000000000 ms 1735862400000
ts_init 1735862400000000000 ms 1735862400000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots []
STATE QUERY active-start before first eligible order
CALL engine.cache.positions_open()
RETURN <class 'list'> count 0
CALL engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_inflight(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
TRACE 6 _submit_entry before
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735862400000000000)
ts_event 1735862400000000000 ms 1735862400000
ts_init 1735862400000000000 ms 1735862400000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots []
[1m2025-01-03T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: <--[EVT] OrderInitialized(instrument_id=BTCUSDT.BINANCE, client_order_id=O-20250103-000000-001-000-1, side=BUY, type=MARKET, quantity=1.000000, time_in_force=GTC, post_only=False, reduce_only=False, quote_quantity=False, options={}, emulation_trigger=NO_TRIGGER, trigger_instrument_id=None, contingency_type=NO_CONTINGENCY, order_list_id=None, linked_order_ids=None, parent_order_id=None, exec_algorithm_id=None, exec_algorithm_params=None, exec_spawn_id=None, tags=None)[0m
[1m2025-01-03T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: [CMD]--> [Risk] SubmitOrder(order=MarketOrder(BUY 1.000000 BTCUSDT.BINANCE MARKET GTC, status=INITIALIZED, client_order_id=O-20250103-000000-001-000-1, venue_order_id=None, position_id=None, tags=None), position_id=None)[0m
[1m2025-01-03T00:00:00.000000000Z[0m [1;33m[WARN] BACKTESTER-001.RiskEngine: Cannot check MARKET order risk: no prices for BTCUSDT.BINANCE[0m
[1m2025-01-03T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: <--[EVT] OrderSubmitted(instrument_id=BTCUSDT.BINANCE, client_order_id=O-20250103-000000-001-000-1, account_id=BINANCE-001, ts_event=1735862400000000000)[0m
TRACE 7 _submit_entry after
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735862400000000000)
ts_event 1735862400000000000 ms 1735862400000
ts_init 1735862400000000000 ms 1735862400000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots []
TRACE 8 on_bar after
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735862400000000000)
ts_event 1735862400000000000 ms 1735862400000
ts_init 1735862400000000000 ms 1735862400000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735862400000, 100000.0)]
[1m2025-01-03T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.Portfolio: Updated AccountState(account_id=BINANCE-001, account_type=CASH, base_currency=None, is_reported=False, balances=[AccountBalance(total=99_899.90000000 USDT, locked=0.00000000 USDT, free=99_899.90000000 USDT), AccountBalance(total=1.00000000 BTC, locked=0.00000000 BTC, free=1.00000000 BTC)], margins=[], event_id=e9cc6200-9971-4eba-b020-5d6b9dd377db)[0m
[1m2025-01-03T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.Portfolio: BTCUSDT.BINANCE account=BINANCE-001 net_position=1.000000[0m
[1m2025-01-03T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: <--[EVT] OrderFilled(instrument_id=BTCUSDT.BINANCE, client_order_id=O-20250103-000000-001-000-1, venue_order_id=BINANCE-1-001, account_id=BINANCE-001, trade_id=T-14bdfb8338158f4c-009, position_id=BTCUSDT.BINANCE-TraceBuyHold-000, order_side=BUY, order_type=MARKET, last_qty=1.000000, last_px=100.00 USDT, commission=0.10000000 USDT, liquidity_side=TAKER, ts_event=1735862400000000000)[0m
TRACE 9 on_order_filled before
OBJECT <class 'nautilus_trader.model.events.order.OrderFilled'> OrderFilled(trader_id=BACKTESTER-001, strategy_id=TraceBuyHold-000, instrument_id=BTCUSDT.BINANCE, client_order_id=O-20250103-000000-001-000-1, venue_order_id=BINANCE-1-001, account_id=BINANCE-001, trade_id=T-14bdfb8338158f4c-009, position_id=BTCUSDT.BINANCE-TraceBuyHold-000, order_side=BUY, order_type=MARKET, last_qty=1.000000, last_px=100.00 USDT, commission=0.10000000 USDT, liquidity_side=TAKER, event_id=7b82198b-c884-4200-996c-be2fafd673fc, ts_event=1735862400000000000, ts_init=1735862400000000000)
ts_event 1735862400000000000 ms 1735862400000
ts_init 1735862400000000000 ms 1735862400000
client_order_id ClientOrderId('O-20250103-000000-001-000-1') ms N/A
venue_order_id VenueOrderId('BINANCE-1-001') ms N/A
position_id PositionId('BTCUSDT.BINANCE-TraceBuyHold-000') ms N/A
last_qty Quantity(1.000000) ms N/A
last_px Price(100.00) ms N/A
equity_snapshots [(1735862400000, 100000.0)]
TRACE 10 on_order_filled after
OBJECT <class 'nautilus_trader.model.events.order.OrderFilled'> OrderFilled(trader_id=BACKTESTER-001, strategy_id=TraceBuyHold-000, instrument_id=BTCUSDT.BINANCE, client_order_id=O-20250103-000000-001-000-1, venue_order_id=BINANCE-1-001, account_id=BINANCE-001, trade_id=T-14bdfb8338158f4c-009, position_id=BTCUSDT.BINANCE-TraceBuyHold-000, order_side=BUY, order_type=MARKET, last_qty=1.000000, last_px=100.00 USDT, commission=0.10000000 USDT, liquidity_side=TAKER, event_id=7b82198b-c884-4200-996c-be2fafd673fc, ts_event=1735862400000000000, ts_init=1735862400000000000)
ts_event 1735862400000000000 ms 1735862400000
ts_init 1735862400000000000 ms 1735862400000
client_order_id ClientOrderId('O-20250103-000000-001-000-1') ms N/A
venue_order_id VenueOrderId('BINANCE-1-001') ms N/A
position_id PositionId('BTCUSDT.BINANCE-TraceBuyHold-000') ms N/A
last_qty Quantity(1.000000) ms N/A
last_px Price(100.00) ms N/A
equity_snapshots [(1735862400000, 99999.90000000001)]
[1m2025-01-03T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: <--[EVT] PositionOpened(instrument_id=BTCUSDT.BINANCE, position_id=BTCUSDT.BINANCE-TraceBuyHold-000, account_id=BINANCE-001, opening_order_id=O-20250103-000000-001-000-1, closing_order_id=None, entry=BUY, side=LONG, signed_qty=1.0, quantity=1.000000, peak_qty=1.000000, currency=USDT, avg_px_open=100.0, avg_px_close=0.0, realized_return=0.00000, realized_pnl=-0.10000000 USDT, unrealized_pnl=0.00000000 USDT, ts_opened=1735862400000000000, ts_last=1735862400000000000, ts_closed=0, duration_ns=0)[0m
TRACE 11 on_bar before
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735948800000000000)
ts_event 1735948800000000000 ms 1735948800000
ts_init 1735948800000000000 ms 1735948800000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735862400000, 99999.90000000001)]
TRACE 12 on_bar after
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735948800000000000)
ts_event 1735948800000000000 ms 1735948800000
ts_init 1735948800000000000 ms 1735948800000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001)]
TRACE 13 on_bar before
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1736035200000000000)
ts_event 1736035200000000000 ms 1736035200000
ts_init 1736035200000000000 ms 1736035200000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001)]
GATE excluded sentinel 1736035200000
TRACE 14 on_bar after
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1736035200000000000)
ts_event 1736035200000000000 ms 1736035200000
ts_init 1736035200000000000 ms 1736035200000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001)]
TRACE 15 on_stop before
equity_snapshots [(1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001)]
TRACE 16 on_stop after
equity_snapshots [(1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001)]
[1m2025-01-05T00:00:00.000000000Z[0m [1;33m[WARN] BACKTESTER-001.TraceBuyHold: The `Strategy.on_stop` handler was called when not overridden. It's expected that any actions required when stopping the strategy occur here, such as unsubscribing from data[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: Disconnecting...[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: Disconnected[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataEngine: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.RiskEngine: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: Disconnecting...[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: Disconnected[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecEngine: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.OrderEmulator: STOPPED[0m
[1m2026-10-03T06:39:06.545012947Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:39:06.545021511Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m BACKTEST POST-RUN[0m
[1m2026-10-03T06:39:06.545022350Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:39:06.545022939Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run config ID:  None[0m
[1m2026-10-03T06:39:06.545024621Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run ID:         3442171e-28a5-4384-8efc-db3278a96f82[0m
[1m2026-10-03T06:39:06.545029744Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run started:    2026-10-03T06:39:06.542780000Z[0m
[1m2026-10-03T06:39:06.545037969Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run finished:   2026-10-03T06:39:06.544977000Z[0m
[1m2026-10-03T06:39:06.545053591Z[0m [INFO] BACKTESTER-001.BacktestEngine: Elapsed time:   0 days 00:00:00.002197[0m
[1m2026-10-03T06:39:06.545068119Z[0m [INFO] BACKTESTER-001.BacktestEngine: Backtest start: 2025-01-02T00:00:00.000000000Z[0m
[1m2026-10-03T06:39:06.545076485Z[0m [INFO] BACKTESTER-001.BacktestEngine: Backtest end:   2025-01-05T00:00:00.000000000Z[0m
[1m2026-10-03T06:39:06.545083341Z[0m [INFO] BACKTESTER-001.BacktestEngine: Backtest range: 3 days 00:00:00[0m
[1m2026-10-03T06:39:06.545085212Z[0m [INFO] BACKTESTER-001.BacktestEngine: Iterations: 4[0m
[1m2026-10-03T06:39:06.545094111Z[0m [INFO] BACKTESTER-001.BacktestEngine: Total events: 2[0m
[1m2026-10-03T06:39:06.545098341Z[0m [INFO] BACKTESTER-001.BacktestEngine: Total orders: 1[0m
[1m2026-10-03T06:39:06.545102529Z[0m [INFO] BACKTESTER-001.BacktestEngine: Total positions: 1[0m
[1m2026-10-03T06:39:06.545112309Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:39:06.545114287Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m SimulatedVenue BINANCE[0m
[1m2026-10-03T06:39:06.545114731Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:39:06.545117971Z[0m [INFO] BACKTESTER-001.BacktestEngine: CashAccount(id=BINANCE-001, type=CASH, base=None)[0m
[1m2026-10-03T06:39:06.545124950Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.545126048Z[0m [INFO] BACKTESTER-001.BacktestEngine: Balances starting:[0m
[1m2026-10-03T06:39:06.545133135Z[0m [INFO] BACKTESTER-001.BacktestEngine: 100_000.00000000 USDT[0m
[1m2026-10-03T06:39:06.545143367Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.545144135Z[0m [INFO] BACKTESTER-001.BacktestEngine: Balances ending:[0m
[1m2026-10-03T06:39:06.545149252Z[0m [INFO] BACKTESTER-001.BacktestEngine: 99_899.90000000 USDT[0m
[1m2026-10-03T06:39:06.545151111Z[0m [INFO] BACKTESTER-001.BacktestEngine: 1.00000000 BTC[0m
[1m2026-10-03T06:39:06.545153048Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.545153347Z[0m [INFO] BACKTESTER-001.BacktestEngine: Commissions:[0m
[1m2026-10-03T06:39:06.545158834Z[0m [INFO] BACKTESTER-001.BacktestEngine: -0.10000000 USDT[0m
[1m2026-10-03T06:39:06.545166330Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.545167317Z[0m [INFO] BACKTESTER-001.BacktestEngine: Unrealized PnLs (included in totals):[0m
[1m2026-10-03T06:39:06.545209104Z[0m [INFO] BACKTESTER-001.BacktestEngine: 0.00000000 USDT[0m
[1m2026-10-03T06:39:06.545217884Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:39:06.545218754Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m PORTFOLIO PERFORMANCE[0m
[1m2026-10-03T06:39:06.545219126Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:39:06.545848310Z[0m [INFO] BACKTESTER-001.BacktestEngine:  PnL Statistics (BTC)[0m
[1m2026-10-03T06:39:06.545872455Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.545937061Z[0m [INFO] BACKTESTER-001.BacktestEngine: PnL (total):                    1.0[0m
[1m2026-10-03T06:39:06.545948963Z[0m [INFO] BACKTESTER-001.BacktestEngine: PnL% (total):                   0.0[0m
[1m2026-10-03T06:39:06.545949693Z[0m [INFO] BACKTESTER-001.BacktestEngine: Max Winner:                     nan[0m
[1m2026-10-03T06:39:06.545950180Z[0m [INFO] BACKTESTER-001.BacktestEngine: Avg Winner:                     nan[0m
[1m2026-10-03T06:39:06.545950411Z[0m [INFO] BACKTESTER-001.BacktestEngine: Min Winner:                     nan[0m
[1m2026-10-03T06:39:06.545950655Z[0m [INFO] BACKTESTER-001.BacktestEngine: Min Loser:                      nan[0m
[1m2026-10-03T06:39:06.545951028Z[0m [INFO] BACKTESTER-001.BacktestEngine: Avg Loser:                      nan[0m
[1m2026-10-03T06:39:06.545951265Z[0m [INFO] BACKTESTER-001.BacktestEngine: Max Loser:                      nan[0m
[1m2026-10-03T06:39:06.545951734Z[0m [INFO] BACKTESTER-001.BacktestEngine: Expectancy:                     nan[0m
[1m2026-10-03T06:39:06.545951911Z[0m [INFO] BACKTESTER-001.BacktestEngine: Win Rate:                       nan[0m
[1m2026-10-03T06:39:06.545952678Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.545953635Z[0m [INFO] BACKTESTER-001.BacktestEngine:  PnL Statistics (USDT)[0m
[1m2026-10-03T06:39:06.545953917Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.546005264Z[0m [INFO] BACKTESTER-001.BacktestEngine: PnL (total):                    -100.1[0m
[1m2026-10-03T06:39:06.546013108Z[0m [INFO] BACKTESTER-001.BacktestEngine: PnL% (total):                   -0.10009999999999128[0m
[1m2026-10-03T06:39:06.546013800Z[0m [INFO] BACKTESTER-001.BacktestEngine: Max Winner:                     nan[0m
[1m2026-10-03T06:39:06.546015835Z[0m [INFO] BACKTESTER-001.BacktestEngine: Avg Winner:                     nan[0m
[1m2026-10-03T06:39:06.546016035Z[0m [INFO] BACKTESTER-001.BacktestEngine: Min Winner:                     nan[0m
[1m2026-10-03T06:39:06.546016229Z[0m [INFO] BACKTESTER-001.BacktestEngine: Min Loser:                      -0.1[0m
[1m2026-10-03T06:39:06.546016463Z[0m [INFO] BACKTESTER-001.BacktestEngine: Avg Loser:                      -0.1[0m
[1m2026-10-03T06:39:06.546016780Z[0m [INFO] BACKTESTER-001.BacktestEngine: Max Loser:                      -0.1[0m
[1m2026-10-03T06:39:06.546017170Z[0m [INFO] BACKTESTER-001.BacktestEngine: Expectancy:                     -0.1[0m
[1m2026-10-03T06:39:06.546017480Z[0m [INFO] BACKTESTER-001.BacktestEngine: Win Rate:                       0.0[0m
[1m2026-10-03T06:39:06.546018115Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.546018593Z[0m [INFO] BACKTESTER-001.BacktestEngine:  Returns Statistics[0m
[1m2026-10-03T06:39:06.546018899Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.546057996Z[0m [INFO] BACKTESTER-001.BacktestEngine: Returns Volatility (252 days):  nan[0m
[1m2026-10-03T06:39:06.546065277Z[0m [INFO] BACKTESTER-001.BacktestEngine: Average (Return):               nan[0m
[1m2026-10-03T06:39:06.546066723Z[0m [INFO] BACKTESTER-001.BacktestEngine: Average Loss (Return):          nan[0m
[1m2026-10-03T06:39:06.546066961Z[0m [INFO] BACKTESTER-001.BacktestEngine: Average Win (Return):           nan[0m
[1m2026-10-03T06:39:06.546067225Z[0m [INFO] BACKTESTER-001.BacktestEngine: Sharpe Ratio (252 days):        nan[0m
[1m2026-10-03T06:39:06.546067467Z[0m [INFO] BACKTESTER-001.BacktestEngine: Sortino Ratio (252 days):       nan[0m
[1m2026-10-03T06:39:06.546067769Z[0m [INFO] BACKTESTER-001.BacktestEngine: Profit Factor:                  nan[0m
[1m2026-10-03T06:39:06.546068006Z[0m [INFO] BACKTESTER-001.BacktestEngine: Risk Return Ratio:              nan[0m
[1m2026-10-03T06:39:06.546068589Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.546069139Z[0m [INFO] BACKTESTER-001.BacktestEngine:  General Statistics[0m
[1m2026-10-03T06:39:06.546069563Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:39:06.546092002Z[0m [INFO] BACKTESTER-001.BacktestEngine: Long Ratio:                     1.0[0m
[1m2026-10-03T06:39:06.546099439Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
STATE QUERY postrun before disposal
CALL engine.cache.positions_open()
RETURN <class 'list'> count 1
ITEM <class 'nautilus_trader.model.position.Position'> Position(LONG 1.000000 BTCUSDT.BINANCE, id=BTCUSDT.BINANCE-TraceBuyHold-000)
FIELD id PositionId('BTCUSDT.BINANCE-TraceBuyHold-000') DOC The position ID.

:returns: `PositionId`
FIELD client_order_id ABSENT
FIELD instrument_id InstrumentId('BTCUSDT.BINANCE') DOC The position instrument ID.

:returns: `InstrumentId`
FIELD is_open True DOC Return whether the position side is **not** ``FLAT``.

Returns
-------
bool
FIELD is_closed False DOC Return whether the position side is ``FLAT``.

Returns
-------
bool
FIELD side <PositionSide.LONG: 2> DOC The current position side.

:returns: `PositionSide`
FIELD quantity Quantity(1.000000) DOC The current open quantity.

:returns: `Quantity`
FIELD signed_qty 1.0 DOC The current signed quantity (positive for position side ``LONG``, negative for ``SHORT``).

:returns: `double`
FIELD status ABSENT
CALL engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 1
ITEM <class 'nautilus_trader.model.position.Position'> Position(LONG 1.000000 BTCUSDT.BINANCE, id=BTCUSDT.BINANCE-TraceBuyHold-000)
FIELD id PositionId('BTCUSDT.BINANCE-TraceBuyHold-000') DOC The position ID.

:returns: `PositionId`
FIELD client_order_id ABSENT
FIELD instrument_id InstrumentId('BTCUSDT.BINANCE') DOC The position instrument ID.

:returns: `InstrumentId`
FIELD is_open True DOC Return whether the position side is **not** ``FLAT``.

Returns
-------
bool
FIELD is_closed False DOC Return whether the position side is ``FLAT``.

Returns
-------
bool
FIELD side <PositionSide.LONG: 2> DOC The current position side.

:returns: `PositionSide`
FIELD quantity Quantity(1.000000) DOC The current open quantity.

:returns: `Quantity`
FIELD signed_qty 1.0 DOC The current signed quantity (positive for position side ``LONG``, negative for ``SHORT``).

:returns: `double`
FIELD status ABSENT
CALL engine.cache.orders_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_inflight(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
FINAL equity_snapshots [(1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001)]
ENTRY SUBMISSION TIMES [1735862400000] FILL TIMES [1735862400000]
REPORT fills class <class 'pandas.DataFrame'>
columns ['trader_id', 'strategy_id', 'instrument_id', 'venue_order_id', 'account_id', 'trade_id', 'position_id', 'order_side', 'order_type', 'last_qty', 'last_px', 'currency', 'commission', 'liquidity_side', 'event_id', 'ts_event', 'ts_init', 'info', 'reconciliation'] dtypes {'trader_id': <StringDtype(na_value=nan)>, 'strategy_id': <StringDtype(na_value=nan)>, 'instrument_id': <StringDtype(na_value=nan)>, 'venue_order_id': <StringDtype(na_value=nan)>, 'account_id': <StringDtype(na_value=nan)>, 'trade_id': <StringDtype(na_value=nan)>, 'position_id': <StringDtype(na_value=nan)>, 'order_side': <StringDtype(na_value=nan)>, 'order_type': <StringDtype(na_value=nan)>, 'last_qty': <StringDtype(na_value=nan)>, 'last_px': <StringDtype(na_value=nan)>, 'currency': <StringDtype(na_value=nan)>, 'commission': <StringDtype(na_value=nan)>, 'liquidity_side': <StringDtype(na_value=nan)>, 'event_id': <StringDtype(na_value=nan)>, 'ts_event': datetime64[ns, UTC], 'ts_init': datetime64[ns, UTC], 'info': dtype('O'), 'reconciliation': dtype('bool')}
index class <class 'pandas.Index'> index name 'client_order_id' index values ['O-20250103-000000-001-000-1']
FULL FRAME
                                  trader_id       strategy_id    instrument_id venue_order_id   account_id                trade_id                       position_id order_side order_type  last_qty last_px currency       commission liquidity_side                              event_id                  ts_event                   ts_init info  reconciliation
client_order_id                                                                                                                                                                                                                                                                                                                                                     
O-20250103-000000-001-000-1  BACKTESTER-001  TraceBuyHold-000  BTCUSDT.BINANCE  BINANCE-1-001  BINANCE-001  T-14bdfb8338158f4c-009  BTCUSDT.BINANCE-TraceBuyHold-000        BUY     MARKET  1.000000  100.00     USDT  0.10000000 USDT          TAKER  7b82198b-c884-4200-996c-be2fafd673fc 2025-01-03 00:00:00+00:00 2025-01-03 00:00:00+00:00   {}           False
FULL RECORDS (index retained)
[{'client_order_id': 'O-20250103-000000-001-000-1',
  'trader_id': 'BACKTESTER-001',
  'strategy_id': 'TraceBuyHold-000',
  'instrument_id': 'BTCUSDT.BINANCE',
  'venue_order_id': 'BINANCE-1-001',
  'account_id': 'BINANCE-001',
  'trade_id': 'T-14bdfb8338158f4c-009',
  'position_id': 'BTCUSDT.BINANCE-TraceBuyHold-000',
  'order_side': 'BUY',
  'order_type': 'MARKET',
  'last_qty': '1.000000',
  'last_px': '100.00',
  'currency': 'USDT',
  'commission': '0.10000000 USDT',
  'liquidity_side': 'TAKER',
  'event_id': '7b82198b-c884-4200-996c-be2fafd673fc',
  'ts_event': Timestamp('2025-01-03 00:00:00+0000', tz='UTC'),
  'ts_init': Timestamp('2025-01-03 00:00:00+0000', tz='UTC'),
  'info': {},
  'reconciliation': False}]
TIME ts_opened ABSENT
TIME ORIGINAL ts_event Timestamp('2025-01-03 00:00:00+0000', tz='UTC') type <class 'pandas.Timestamp'> ms 1735862400000
TIME ORIGINAL ts_init Timestamp('2025-01-03 00:00:00+0000', tz='UTC') type <class 'pandas.Timestamp'> ms 1735862400000
TIME ts_last ABSENT
REPORT positions class <class 'pandas.DataFrame'>
columns ['trader_id', 'strategy_id', 'instrument_id', 'account_id', 'opening_order_id', 'closing_order_id', 'entry', 'side', 'quantity', 'peak_qty', 'ts_init', 'ts_opened', 'ts_last', 'ts_closed', 'duration_ns', 'avg_px_open', 'avg_px_close', 'commissions', 'realized_return', 'realized_pnl', 'is_snapshot'] dtypes {'trader_id': <StringDtype(na_value=nan)>, 'strategy_id': <StringDtype(na_value=nan)>, 'instrument_id': <StringDtype(na_value=nan)>, 'account_id': <StringDtype(na_value=nan)>, 'opening_order_id': <StringDtype(na_value=nan)>, 'closing_order_id': dtype('O'), 'entry': <StringDtype(na_value=nan)>, 'side': <StringDtype(na_value=nan)>, 'quantity': <StringDtype(na_value=nan)>, 'peak_qty': <StringDtype(na_value=nan)>, 'ts_init': dtype('int64'), 'ts_opened': datetime64[ns, UTC], 'ts_last': dtype('int64'), 'ts_closed': dtype('O'), 'duration_ns': dtype('O'), 'avg_px_open': dtype('float64'), 'avg_px_close': dtype('O'), 'commissions': dtype('O'), 'realized_return': dtype('float64'), 'realized_pnl': <StringDtype(na_value=nan)>, 'is_snapshot': dtype('bool')}
index class <class 'pandas.Index'> index name 'position_id' index values ['BTCUSDT.BINANCE-TraceBuyHold-000']
FULL FRAME
                                       trader_id       strategy_id    instrument_id   account_id             opening_order_id closing_order_id entry  side  quantity  peak_qty              ts_init                 ts_opened              ts_last ts_closed duration_ns  avg_px_open avg_px_close        commissions  realized_return      realized_pnl  is_snapshot
position_id                                                                                                                                                                                                                                                                                                                                                          
BTCUSDT.BINANCE-TraceBuyHold-000  BACKTESTER-001  TraceBuyHold-000  BTCUSDT.BINANCE  BINANCE-001  O-20250103-000000-001-000-1             None   BUY  LONG  1.000000  1.000000  1735862400000000000 2025-01-03 00:00:00+00:00  1735862400000000000      <NA>        None        100.0         None  [0.10000000 USDT]              0.0  -0.10000000 USDT        False
FULL RECORDS (index retained)
[{'position_id': 'BTCUSDT.BINANCE-TraceBuyHold-000',
  'trader_id': 'BACKTESTER-001',
  'strategy_id': 'TraceBuyHold-000',
  'instrument_id': 'BTCUSDT.BINANCE',
  'account_id': 'BINANCE-001',
  'opening_order_id': 'O-20250103-000000-001-000-1',
  'closing_order_id': None,
  'entry': 'BUY',
  'side': 'LONG',
  'quantity': '1.000000',
  'peak_qty': '1.000000',
  'ts_init': 1735862400000000000,
  'ts_opened': Timestamp('2025-01-03 00:00:00+0000', tz='UTC'),
  'ts_last': 1735862400000000000,
  'ts_closed': None,
  'duration_ns': None,
  'avg_px_open': 100.0,
  'avg_px_close': None,
  'commissions': ['0.10000000 USDT'],
  'realized_return': 0.0,
  'realized_pnl': '-0.10000000 USDT',
  'is_snapshot': False}]
TIME ORIGINAL ts_opened Timestamp('2025-01-03 00:00:00+0000', tz='UTC') type <class 'pandas.Timestamp'> ms 1735862400000
TIME ts_event ABSENT
TIME ORIGINAL ts_init 1735862400000000000 type <class 'int'> ms 1735862400000
TIME ORIGINAL ts_last 1735862400000000000 type <class 'int'> ms 1735862400000
REPORT account class <class 'pandas.DataFrame'>
columns ['total', 'locked', 'free', 'currency', 'account_id', 'account_type', 'base_currency', 'margins', 'reported', 'info'] dtypes {'total': <StringDtype(na_value=nan)>, 'locked': <StringDtype(na_value=nan)>, 'free': <StringDtype(na_value=nan)>, 'currency': <StringDtype(na_value=nan)>, 'account_id': <StringDtype(na_value=nan)>, 'account_type': <StringDtype(na_value=nan)>, 'base_currency': dtype('O'), 'margins': dtype('O'), 'reported': dtype('bool'), 'info': dtype('O')}
index class <class 'pandas.DatetimeIndex'> index name None index values [Timestamp('2025-01-02 00:00:00+0000', tz='UTC'), Timestamp('2025-01-03 00:00:00+0000', tz='UTC'), Timestamp('2025-01-03 00:00:00+0000', tz='UTC')]
FULL FRAME
                                     total      locked             free currency   account_id account_type base_currency margins  reported info
2025-01-02 00:00:00+00:00  100000.00000000  0.00000000  100000.00000000     USDT  BINANCE-001         CASH          None      []      True   {}
2025-01-03 00:00:00+00:00   99899.90000000  0.00000000   99899.90000000     USDT  BINANCE-001         CASH          None      []     False   {}
2025-01-03 00:00:00+00:00       1.00000000  0.00000000       1.00000000      BTC  BINANCE-001         CASH          None      []     False   {}
FULL RECORDS (index retained)
[{'index': Timestamp('2025-01-02 00:00:00+0000', tz='UTC'),
  'total': '100000.00000000',
  'locked': '0.00000000',
  'free': '100000.00000000',
  'currency': 'USDT',
  'account_id': 'BINANCE-001',
  'account_type': 'CASH',
  'base_currency': None,
  'margins': [],
  'reported': True,
  'info': {}},
 {'index': Timestamp('2025-01-03 00:00:00+0000', tz='UTC'),
  'total': '99899.90000000',
  'locked': '0.00000000',
  'free': '99899.90000000',
  'currency': 'USDT',
  'account_id': 'BINANCE-001',
  'account_type': 'CASH',
  'base_currency': None,
  'margins': [],
  'reported': False,
  'info': {}},
 {'index': Timestamp('2025-01-03 00:00:00+0000', tz='UTC'),
  'total': '1.00000000',
  'locked': '0.00000000',
  'free': '1.00000000',
  'currency': 'BTC',
  'account_id': 'BINANCE-001',
  'account_type': 'CASH',
  'base_currency': None,
  'margins': [],
  'reported': False,
  'info': {}}]
TIME ts_opened ABSENT
TIME ts_event ABSENT
TIME ts_init ABSENT
TIME ts_last ABSENT
TIME ts_opened ABSENT
TIME ts_event ABSENT
TIME ts_init ABSENT
TIME ts_last ABSENT
TIME ts_opened ABSENT
TIME ts_event ABSENT
TIME ts_init ABSENT
TIME ts_last ABSENT
TERMINAL last report row per currency: cash USDT 99899.9 base BTC 1.0 last eligible close 1735948800000 last eligible price 100 cash + base * last eligible price 99999.9 NO liquidation; sentinel price equals eligible price but still reached matching/valuation
PASS zero warmup/sentinel submissions/scored snapshots; clean active-start; inherited same-bar fill/snapshot clock
CASE PASS
CALL engine.dispose()
[1m2026-10-03T06:39:06.567364562Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: DISPOSED[0m
[1m2026-10-03T06:39:06.567403715Z[0m [INFO] BACKTESTER-001.DataEngine: DISPOSED[0m
[1m2026-10-03T06:39:06.567412305Z[0m [INFO] BACKTESTER-001.RiskEngine: DISPOSED[0m
[1m2026-10-03T06:39:06.567420762Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: DISPOSED[0m
[1m2026-10-03T06:39:06.567426213Z[0m [INFO] BACKTESTER-001.ExecEngine: DISPOSED[0m
[1m2026-10-03T06:39:06.567445943Z[0m [INFO] BACKTESTER-001.OrderEmulator: DISPOSED[0m
[1m2026-10-03T06:39:06.567464199Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: Cleared actors[0m
[1m2026-10-03T06:39:06.567484774Z[0m [INFO] BACKTESTER-001.TraceBuyHold: DISPOSED[0m
[1m2026-10-03T06:39:06.567500082Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: Cleared trading strategies[0m
[1m2026-10-03T06:39:06.567509366Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: Cleared execution algorithms[0m
[1m2026-10-03T06:39:06.567515795Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: DISPOSED[0m
[1m2026-10-03T06:39:06.567569775Z[0m [INFO] BACKTESTER-001.Cache: Reset[0m
[1m2026-10-03T06:39:06.567591999Z[0m [INFO] BACKTESTER-001.MessageBus: Closed message bus[0m
PROBE PASS; no actual historical availability certification; Stage2 requires explicit post-probe human approval
```

### Original complete source (attempt 1)

```python
"""Authorized Phase 18.2f scratch probe: two cases, no persisted data."""
import inspect
import subprocess
import sys
import traceback
from decimal import Decimal
from importlib.metadata import version
from pprint import pprint
from typing import Any

from nautilus_trader.backtest.config import BacktestEngineConfig, BacktestVenueConfig
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.model.currencies import BTC, USDT
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import account_type_from_str, oms_type_from_str
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.model.instruments import CurrencyPair
from nautilus_trader.model.objects import Money, Price, Quantity
from quant.strategies.buy_hold import BuyHold

T = 1735689600000
D = 86400000
ACTIVE_START = T + 2 * D
ACTIVE_END = T + 4 * D
BT = 'BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL'
IID = InstrumentId.from_str('BTCUSDT.BINANCE')
FIXTURE = [dict(open_ts=T+i*D, close_ts=T+(i+1)*D,
                available_ts=T+(i+1)*D, ts_event=(T+(i+1)*D)*1000000,
                ts_init=(T+(i+1)*D)*1000000, open=100, high=101,
                low=99, close=100, volume=1000) for i in range(4)]


def emit(*args: Any) -> None:
    print(*args, flush=True)


def query(engine: Any, label: str) -> dict[str, int]:
    emit('STATE QUERY', label)
    results = {}
    calls = [
        ('positions_open()', lambda: engine.cache.positions_open()),
        ("positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))",
         lambda: engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))),
        ("orders_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))",
         lambda: engine.cache.orders_open(instrument_id=IID)),
        ("orders_inflight(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))",
         lambda: engine.cache.orders_inflight(instrument_id=IID)),
    ]
    for expression, call in calls:
        emit('CALL engine.cache.' + expression)
        try:
            value = call()
        except Exception:
            traceback.print_exc()
            emit('STOP: query failure is unknown state, never empty; no substitution')
            raise
        emit('RETURN', type(value), 'count', len(value))
        results[expression] = len(value)
        for item in value:
            emit('ITEM', type(item), repr(item))
            for field in ('id', 'client_order_id', 'instrument_id', 'is_open',
                          'is_closed', 'side', 'quantity', 'signed_qty', 'status'):
                if hasattr(item, field):
                    emit('FIELD', field, repr(getattr(item, field)),
                         'DOC', inspect.getdoc(getattr(type(item), field, None)))
                else:
                    emit('FIELD', field, 'ABSENT')
    return results


class TraceBuyHold(BuyHold):
    def __init__(self, engine: Any, gated: bool) -> None:
        super().__init__(instrument_id=str(IID), bar_type=BT,
                         trade_size='1.000000', deploy_pct='0')
        self.probe_engine = engine
        self.gated = gated
        self.sequence = 0
        self.submission_times = []
        self.fill_times = []
        self.active_started = False
        self.excluded = []

    def trace(self, label: str, obj: Any = None) -> None:
        self.sequence += 1
        emit('TRACE', self.sequence, label)
        if obj is not None:
            emit('OBJECT', type(obj), repr(obj))
            for field in ('ts_event', 'ts_init', 'client_order_id', 'venue_order_id',
                          'position_id', 'last_qty', 'last_px'):
                if hasattr(obj, field):
                    value = getattr(obj, field)
                    emit(field, repr(value), 'ms', value // 1000000 if field.startswith('ts_') else 'N/A')
                else:
                    emit(field, 'ABSENT')
        emit('equity_snapshots', repr(self.equity_snapshots))

    def on_start(self) -> None:
        self.trace('on_start before')
        assert all(n == 0 for n in query(self.probe_engine, 'on_start').values())
        super().on_start()
        self.trace('on_start after')

    def on_bar(self, bar: Bar) -> None:
        self.trace('on_bar before', bar)
        close = bar.ts_event // 1000000
        if self.gated and not ACTIVE_START <= close < ACTIVE_END:
            before = (len(self.submission_times), list(self.equity_snapshots))
            emit('GATE', 'warmup' if close < ACTIVE_START else 'excluded sentinel', close)
            self.excluded.append(close)
            assert before == (len(self.submission_times), list(self.equity_snapshots))
        else:
            if self.gated and not self.active_started:
                assert all(n == 0 for n in query(self.probe_engine, 'active-start before first eligible order').values())
                self.active_started = True
            super().on_bar(bar)
        self.trace('on_bar after', bar)

    def _submit_entry(self, bar: Bar, venue_obj: Venue) -> None:
        self.trace('_submit_entry before', bar)
        self.submission_times.append(bar.ts_event // 1000000)
        super()._submit_entry(bar, venue_obj)
        self.trace('_submit_entry after', bar)

    def on_order_filled(self, event: Any) -> None:
        self.trace('on_order_filled before', event)
        self.fill_times.append(event.ts_event // 1000000)
        super().on_order_filled(event)
        self.trace('on_order_filled after', event)

    def on_stop(self) -> None:
        self.trace('on_stop before')
        super().on_stop()
        self.trace('on_stop after')


def report(name: str, frame: Any) -> list[dict[str, Any]]:
    emit('REPORT', name, 'class', type(frame))
    emit('columns', repr(frame.columns.tolist()), 'dtypes', repr(frame.dtypes.to_dict()))
    emit('index class', type(frame.index), 'index name', repr(frame.index.name),
         'index values', repr(frame.index.tolist()))
    emit('FULL FRAME\n' + frame.to_string())
    records = frame.reset_index().to_dict(orient='records')
    emit('FULL RECORDS (index retained)')
    pprint(records, sort_dicts=False)
    for record in records:
        for field in ('ts_opened', 'ts_event', 'ts_init', 'ts_last'):
            if field in record:
                value = record[field]
                ns = value.value if hasattr(value, 'value') else value
                emit('TIME ORIGINAL', field, repr(value), 'type', type(value), 'ms', ns // 1000000)
            else:
                emit('TIME', field, 'ABSENT')
    return records


def run_case(gated: bool) -> None:
    emit('CASE', 'scratch gated' if gated else 'ordinary control')
    venue_config = BacktestVenueConfig(name='BINANCE', oms_type='NETTING',
        account_type='CASH', starting_balances=['100000 USDT'])
    engine_config = BacktestEngineConfig()
    engine = BacktestEngine(config=engine_config)
    try:
        engine.add_venue(venue=Venue(venue_config.name),
            oms_type=oms_type_from_str(venue_config.oms_type),
            account_type=account_type_from_str(venue_config.account_type),
            starting_balances=[Money.from_str(balance) for balance in venue_config.starting_balances])
        instrument = CurrencyPair(instrument_id=IID, raw_symbol=Symbol('BTCUSDT'),
            base_currency=BTC, quote_currency=USDT, price_precision=2, size_precision=6,
            price_increment=Price.from_str('0.01'), size_increment=Quantity.from_str('0.000001'),
            ts_event=T*1000000, ts_init=T*1000000,
            maker_fee=Decimal('0.001'), taker_fee=Decimal('0.001'))
        engine.add_instrument(instrument)
        emit('LIVE positions_open signature')
        try:
            emit(inspect.signature(engine.cache.positions_open))
        except (TypeError, ValueError):
            traceback.print_exc()
            emit('Cython signature unavailable; full docstring fallback follows')
        emit('FULL LIVE positions_open DOCSTRING\n' + str(inspect.getdoc(engine.cache.positions_open)))
        assert all(n == 0 for n in query(engine, 'fresh engine before run').values())
        bars = [Bar(bar_type=BarType.from_str(BT), open=Price.from_str('100.00'),
                    high=Price.from_str('101.00'), low=Price.from_str('99.00'),
                    close=Price.from_str('100.00'), volume=Quantity.from_str('1000.000000'),
                    ts_event=row['ts_event'], ts_init=row['ts_init']) for row in FIXTURE]
        emit('FULL FIXTURE'); pprint(FIXTURE, sort_dicts=False)
        emit('ACTUAL BARS', repr(bars))
        engine.add_data(bars)
        strategy = TraceBuyHold(engine, gated)
        engine.add_strategy(strategy)
        emit('CALL engine.run() -- all four bars INCLUDING end-exclusive sentinel reach engine')
        engine.run()
        query(engine, 'postrun before disposal')
        emit('FINAL equity_snapshots', repr(strategy.equity_snapshots))
        emit('ENTRY SUBMISSION TIMES', repr(strategy.submission_times), 'FILL TIMES', repr(strategy.fill_times))
        report('fills', engine.trader.generate_fills_report())
        report('positions', engine.trader.generate_positions_report())
        account = report('account', engine.trader.generate_account_report(Venue('BINANCE')))
        cash_rows = [r for r in account if r.get('currency') == 'USDT']
        base_rows = [r for r in account if r.get('currency') == 'BTC']
        cash = float(cash_rows[-1]['total']) if cash_rows else None
        base = float(base_rows[-1]['total']) if base_rows else None
        emit('TERMINAL last report row per currency: cash USDT', cash, 'base BTC', base,
             'last eligible close', ACTIVE_END-D, 'last eligible price', 100,
             'cash + base * last eligible price', cash + base*100 if cash is not None and base is not None else None,
             'NO liquidation; sentinel price equals eligible price but still reached matching/valuation')
        expected = [ACTIVE_START, ACTIVE_START+D] if gated else [r['close_ts'] for r in FIXTURE]
        assert [ts for ts, _ in strategy.equity_snapshots] == expected
        assert strategy.submission_times == expected[:1]
        assert strategy.fill_times == expected[:1]
        assert strategy.equity_snapshots[0][1] == 99999.9
        if gated:
            assert strategy.excluded == [T+D, ACTIVE_END]
            assert all(ACTIVE_START <= ts < ACTIVE_END for ts in strategy.submission_times)
            emit('PASS zero warmup/sentinel submissions/scored snapshots; clean active-start; inherited same-bar fill/snapshot clock')
        emit('CASE PASS')
    finally:
        emit('CALL engine.dispose()')
        engine.dispose()


def main() -> None:
    emit('Python', sys.version)
    emit('NautilusTrader', version('nautilus_trader'))
    emit('baseline HEAD', subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip())
    emit('IMPORT SUCCESS')
    emit('Scratch constants only: T', T, 'D', D, 'active', ACTIVE_START, ACTIVE_END)
    run_case(False)
    run_case(True)
    emit('PROBE PASS; no actual historical availability certification; Stage2 requires explicit post-probe human approval')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        emit('PROBE STOP; failure retained; no silent substitution')
        sys.exit(1)
```

### Original complete raw stdout/stderr (attempt 1; exit 1)

```text
Python 3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]
NautilusTrader 1.231.0
baseline HEAD 59257d113f1649138c6d768fb4ba392bfb6c7189
IMPORT SUCCESS
Scratch constants only: T 1735689600000 D 86400000 active 1735862400000 1736035200000
CASE ordinary control
[1m2026-10-03T06:38:24.218906813Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:38:24.218942186Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  NAUTILUS TRADER - Automated Algorithmic Trading Platform[0m
[1m2026-10-03T06:38:24.218944626Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  by Nautech Systems Pty Ltd.[0m
[1m2026-10-03T06:38:24.218944875Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  Copyright (C) 2015-2026. All rights reserved.[0m
[1m2026-10-03T06:38:24.218945207Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:38:24.218945504Z[0m [INFO] BACKTESTER-001.BacktestEngine: [0m
[1m2026-10-03T06:38:24.218946043Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣶⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[0m
[1m2026-10-03T06:38:24.218946326Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣾⣿⣿⣿⠀⢸⣿⣿⣿⣿⣶⣶⣤⣀⠀⠀⠀⠀⠀[0m
[1m2026-10-03T06:38:24.218946663Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⠀⠀⢀⣴⡇⢀⣾⣿⣿⣿⣿⣿⠀⣾⣿⣿⣿⣿⣿⣿⣿⠿⠓⠀⠀⠀⠀[0m
[1m2026-10-03T06:38:24.218946975Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⠀⣰⣿⣿⡀⢸⣿⣿⣿⣿⣿⣿⠀⣿⣿⣿⣿⣿⣿⠟⠁⣠⣄⠀⠀⠀⠀[0m
[1m2026-10-03T06:38:24.218947310Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⢠⣿⣿⣿⣇⠀⢿⣿⣿⣿⣿⣿⠀⢻⣿⣿⣿⡿⢃⣠⣾⣿⣿⣧⡀⠀⠀[0m
[1m2026-10-03T06:38:24.218947505Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠠⣾⣿⣿⣿⣿⣿⣧⠈⠋⢀⣴⣧⠀⣿⡏⢠⡀⢸⣿⣿⣿⣿⣿⣿⣿⡇⠀[0m
[1m2026-10-03T06:38:24.218947826Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⣀⠙⢿⣿⣿⣿⣿⣿⠇⢠⣿⣿⣿⡄⠹⠃⠼⠃⠈⠉⠛⠛⠛⠛⠛⠻⠇⠀[0m
[1m2026-10-03T06:38:24.218948112Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⢸⡟⢠⣤⠉⠛⠿⢿⣿⠀⢸⣿⡿⠋⣠⣤⣄⠀⣾⣿⣿⣶⣶⣶⣦⡄⠀⠀⠀[0m
[1m2026-10-03T06:38:24.218948421Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠸⠀⣾⠏⣸⣷⠂⣠⣤⠀⠘⢁⣴⣾⣿⣿⣿⡆⠘⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀[0m
[1m2026-10-03T06:38:24.218949833Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⠛⠀⣿⡟⠀⢻⣿⡄⠸⣿⣿⣿⣿⣿⣿⣿⡀⠘⣿⣿⣿⣿⠟⠀⠀⠀⠀[0m
[1m2026-10-03T06:38:24.218950309Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⠀⠀⣿⠇⠀⠀⢻⡿⠀⠈⠻⣿⣿⣿⣿⣿⡇⠀⢹⣿⠿⠋⠀⠀⠀⠀⠀[0m
[1m2026-10-03T06:38:24.218950522Z[0m [INFO] BACKTESTER-001.BacktestEngine: ⠀⠀⠀⠀⠀⠀⠋⠀⠀⠀⡘⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀[0m
[1m2026-10-03T06:38:24.218950823Z[0m [INFO] BACKTESTER-001.BacktestEngine: [0m
[1m2026-10-03T06:38:24.218950951Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:38:24.218951219Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  SYSTEM SPECIFICATION[0m
[1m2026-10-03T06:38:24.218951413Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:38:24.218952312Z[0m [INFO] BACKTESTER-001.BacktestEngine: CPU architecture: INTEL(R) XEON(R) PLATINUM 8573C[0m
[1m2026-10-03T06:38:24.218952866Z[0m [INFO] BACKTESTER-001.BacktestEngine: CPU(s): 3 @ 2299 MHz[0m
[1m2026-10-03T06:38:24.218954900Z[0m [INFO] BACKTESTER-001.BacktestEngine: OS: kernel-6.18.44 Linux (Debian GNU/Linux 13)[0m
[1m2026-10-03T06:38:24.218979787Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:38:24.218980128Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  MEMORY USAGE[0m
[1m2026-10-03T06:38:24.218980339Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:38:24.218988290Z[0m [INFO] BACKTESTER-001.BacktestEngine: RAM-Total: 9.73 GiB[0m
[1m2026-10-03T06:38:24.218992036Z[0m [INFO] BACKTESTER-001.BacktestEngine: RAM-Used: 0.92 GiB (9.44%)[0m
[1m2026-10-03T06:38:24.218992666Z[0m [INFO] BACKTESTER-001.BacktestEngine: RAM-Avail: 8.82 GiB (90.56%)[0m
[1m2026-10-03T06:38:24.218993574Z[0m [INFO] BACKTESTER-001.BacktestEngine: Swap: disabled[0m
[1m2026-10-03T06:38:24.218995988Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:38:24.218996302Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  IDENTIFIERS[0m
[1m2026-10-03T06:38:24.218996501Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:38:24.218997744Z[0m [INFO] BACKTESTER-001.BacktestEngine: trader_id: BACKTESTER-001[0m
[1m2026-10-03T06:38:24.218998518Z[0m [INFO] BACKTESTER-001.BacktestEngine: machine_id: 3df73ebcbb2d[0m
[1m2026-10-03T06:38:24.219000222Z[0m [INFO] BACKTESTER-001.BacktestEngine: instance_id: a23eef2e-3490-497c-871b-64cb947268af[0m
[1m2026-10-03T06:38:24.219002015Z[0m [INFO] BACKTESTER-001.BacktestEngine: PID: 24167[0m
[1m2026-10-03T06:38:24.219002332Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:38:24.219002789Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  VERSIONING[0m
[1m2026-10-03T06:38:24.219002971Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:38:24.219034388Z[0m [INFO] BACKTESTER-001.BacktestEngine: nautilus_trader: 1.231.0[0m
[1m2026-10-03T06:38:24.219043155Z[0m [INFO] BACKTESTER-001.BacktestEngine: python: 3.12.14[0m
[1m2026-10-03T06:38:24.219057127Z[0m [INFO] BACKTESTER-001.BacktestEngine: numpy: 2.5.3[0m
[1m2026-10-03T06:38:24.219059958Z[0m [INFO] BACKTESTER-001.BacktestEngine: pandas: 3.0.6[0m
[1m2026-10-03T06:38:24.219061314Z[0m [INFO] BACKTESTER-001.BacktestEngine: msgspec: 0.22.0[0m
[1m2026-10-03T06:38:24.219062639Z[0m [INFO] BACKTESTER-001.BacktestEngine: pyarrow: 25.0.1[0m
[1m2026-10-03T06:38:24.219064423Z[0m [INFO] BACKTESTER-001.BacktestEngine: pytz: 2026.4[0m
[1m2026-10-03T06:38:24.219066862Z[0m [INFO] BACKTESTER-001.BacktestEngine: uvloop: 0.22.1[0m
[1m2026-10-03T06:38:24.219067059Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2026-10-03T06:38:24.219088973Z[0m [INFO] BACKTESTER-001.BacktestEngine: Building system kernel[0m
[1m2026-10-03T06:38:24.219126181Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.database=None[0m
[1m2026-10-03T06:38:24.219137803Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.encoding='json'[0m
[1m2026-10-03T06:38:24.219139381Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.timestamps_as_iso8601=False[0m
[1m2026-10-03T06:38:24.219140012Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.buffer_interval_ms=None[0m
[1m2026-10-03T06:38:24.219140583Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.autotrim_mins=None[0m
[1m2026-10-03T06:38:24.219141392Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.use_trader_prefix=True[0m
[1m2026-10-03T06:38:24.219142008Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.use_trader_id=True[0m
[1m2026-10-03T06:38:24.219142602Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.use_instance_id=False[0m
[1m2026-10-03T06:38:24.219143284Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.streams_prefix='stream'[0m
[1m2026-10-03T06:38:24.219143780Z[0m [94m[INFO] BACKTESTER-001.MessageBus: config.types_filter=None[0m
[1m2026-10-03T06:38:24.219214825Z[0m [INFO] BACKTESTER-001.Cache: READY[0m
[1m2026-10-03T06:38:24.220061443Z[0m [INFO] BACKTESTER-001.DataEngine: READY[0m
[1m2026-10-03T06:38:24.220202618Z[0m [INFO] BACKTESTER-001.RiskEngine: READY[0m
[1m2026-10-03T06:38:24.220301077Z[0m [94m[INFO] BACKTESTER-001.RiskEngine: TradingState is ACTIVE[0m
[1m2026-10-03T06:38:24.220452985Z[0m [INFO] BACKTESTER-001.Throttler-ORDER_SUBMIT_THROTTLER: READY[0m
[1m2026-10-03T06:38:24.220489098Z[0m [94m[INFO] BACKTESTER-001.RiskEngine: Set MAX_ORDER_SUBMIT_RATE: 100/00:00:01[0m
[1m2026-10-03T06:38:24.220511588Z[0m [INFO] BACKTESTER-001.Throttler-ORDER_MODIFY_THROTTLER: READY[0m
[1m2026-10-03T06:38:24.220518137Z[0m [94m[INFO] BACKTESTER-001.RiskEngine: Set MAX_ORDER_MODIFY_RATE: 100/00:00:01[0m
[1m2026-10-03T06:38:24.220602831Z[0m [INFO] BACKTESTER-001.ExecEngine: READY[0m
[1m2026-10-03T06:38:24.220645679Z[0m [94m[INFO] BACKTESTER-001.ExecEngine: config.snapshot_orders=False[0m
[1m2026-10-03T06:38:24.220654183Z[0m [94m[INFO] BACKTESTER-001.ExecEngine: config.snapshot_positions=False[0m
[1m2026-10-03T06:38:24.220655534Z[0m [94m[INFO] BACKTESTER-001.ExecEngine: config.snapshot_positions_interval_secs=None[0m
[1m2026-10-03T06:38:24.220656056Z[0m [94m[INFO] BACKTESTER-001.ExecEngine: config.allow_overfills=False[0m
[1m2026-10-03T06:38:24.220693155Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 general objects from database[0m
[1m2026-10-03T06:38:24.220707080Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 currencies from database[0m
[1m2026-10-03T06:38:24.220716688Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 instruments from database[0m
[1m2026-10-03T06:38:24.220724031Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 accounts from database[0m
[1m2026-10-03T06:38:24.220734942Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 orders from database[0m
[1m2026-10-03T06:38:24.220740618Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 order lists from database[0m
[1m2026-10-03T06:38:24.220751204Z[0m [INFO] BACKTESTER-001.Cache: Cached 0 positions from database[0m
[1m2026-10-03T06:38:24.220768048Z[0m [INFO] BACKTESTER-001.Cache: Checking data integrity[0m
[1m2026-10-03T06:38:24.220803203Z[0m [92m[INFO] BACKTESTER-001.Cache: Integrity check passed in 33μs[0m
[1m2026-10-03T06:38:24.220828869Z[0m [INFO] BACKTESTER-001.ExecEngine: Loaded cache in 0ms[0m
[1m2026-10-03T06:38:24.220887376Z[0m [INFO] BACKTESTER-001.OrderEmulator: READY[0m
[1m2026-10-03T06:38:24.220944995Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: READY[0m
[1m2026-10-03T06:38:24.220983842Z[0m [INFO] BACKTESTER-001.BacktestEngine: Initialized in 11ms[0m
[1m2026-10-03T06:38:24.221154869Z[0m [INFO] BACKTESTER-001.SimulatedExchange(BINANCE): OmsType=NETTING[0m
[1m2026-10-03T06:38:24.221225412Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: READY[0m
[1m2026-10-03T06:38:24.221277420Z[0m [INFO] BACKTESTER-001.SimulatedExchange(BINANCE): Registered ExecutionClient-BINANCE[0m
[1m2026-10-03T06:38:24.221293732Z[0m [INFO] BACKTESTER-001.ExecEngine: Registered ExecutionClient-BINANCE[0m
[1m2026-10-03T06:38:24.221347023Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: READY[0m
[1m2026-10-03T06:38:24.221369994Z[0m [INFO] BACKTESTER-001.DataEngine: Registered BINANCE[0m
[1m2026-10-03T06:38:24.221383136Z[0m [INFO] BACKTESTER-001.BacktestEngine: Added SimulatedExchange(id=BINANCE, oms_type=NETTING, account_type=CASH)[0m
LIVE positions_open signature
[1m2026-10-03T06:38:24.221687198Z[0m [INFO] BACKTESTER-001.SimulatedExchange(BINANCE): Added instrument BTCUSDT.BINANCE and created matching engine[0m
[1m2026-10-03T06:38:24.221702431Z[0m [INFO] BACKTESTER-001.BacktestEngine: Added BTCUSDT.BINANCE Instrument[0m
(venue=None, instrument_id=None, strategy_id=None, side=<PositionSide.NO_POSITION_SIDE: 0>, account_id=None)
FULL LIVE positions_open DOCSTRING
Cache.positions_open(self, Venue venue=None, InstrumentId instrument_id=None, StrategyId strategy_id=None, PositionSide side=PositionSide.NO_POSITION_SIDE, AccountId account_id=None) -> list

Return all open positions with the given query filters.

*No particular order of list elements is guaranteed.*

Parameters
----------
venue : Venue, optional
    The venue ID query filter.
instrument_id : InstrumentId, optional
    The instrument ID query filter.
strategy_id : StrategyId, optional
    The strategy ID query filter.
side : PositionSide, default ``NO_POSITION_SIDE`` (no filter)
    The position side query filter.
account_id : AccountId, optional
    The account ID query filter.

Returns
-------
list[Position]
STATE QUERY fresh engine before run
CALL engine.cache.positions_open()
RETURN <class 'list'> count 0
CALL engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_inflight(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
FULL FIXTURE
[{'open_ts': 1735689600000,
  'close_ts': 1735776000000,
  'available_ts': 1735776000000,
  'ts_event': 1735776000000000000,
  'ts_init': 1735776000000000000,
  'open': 100,
  'high': 101,
  'low': 99,
  'close': 100,
  'volume': 1000},
 {'open_ts': 1735776000000,
  'close_ts': 1735862400000,
  'available_ts': 1735862400000,
  'ts_event': 1735862400000000000,
  'ts_init': 1735862400000000000,
  'open': 100,
  'high': 101,
  'low': 99,
  'close': 100,
  'volume': 1000},
 {'open_ts': 1735862400000,
  'close_ts': 1735948800000,
  'available_ts': 1735948800000,
  'ts_event': 1735948800000000000,
  'ts_init': 1735948800000000000,
  'open': 100,
  'high': 101,
  'low': 99,
  'close': 100,
  'volume': 1000},
 {'open_ts': 1735948800000,
  'close_ts': 1736035200000,
  'available_ts': 1736035200000,
  'ts_event': 1736035200000000000,
  'ts_init': 1736035200000000000,
  'open': 100,
  'high': 101,
  'low': 99,
  'close': 100,
  'volume': 1000}]
ACTUAL BARS [Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735776000000000000), Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735862400000000000), Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735948800000000000), Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1736035200000000000)]
[1m2026-10-03T06:38:24.229053674Z[0m [INFO] BACKTESTER-001.BacktestEngine: Added 4 BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL Bar elements[0m
[1m2026-10-03T06:38:24.229241755Z[0m [INFO] BACKTESTER-001.TraceBuyHold: READY[0m
CALL engine.run() -- all four bars INCLUDING end-exclusive sentinel reach engine
[1m2026-10-03T06:38:24.229346150Z[0m [INFO] BACKTESTER-001.ExecEngine: Registered OMS.UNSPECIFIED for Strategy TraceBuyHold-000[0m
[1m2026-10-03T06:38:24.229362566Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: Registered Strategy TraceBuyHold-000[0m
/tmp/phase18f-runtime-probe.py:191: Pandas4Warning: Timestamp.utcnow is deprecated and will be removed in a future version. Use Timestamp.now('UTC') instead.
  engine.run()
[1m2026-10-03T06:38:24.229822081Z[0m [INFO] BACKTESTER-001.Portfolio: Updated AccountState(account_id=BINANCE-001, account_type=CASH, base_currency=None, is_reported=True, balances=[AccountBalance(total=100_000.00000000 USDT, locked=0.00000000 USDT, free=100_000.00000000 USDT)], margins=[], event_id=61d1445b-a68f-4a11-8db5-1abfc3217cf2)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: STARTING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: Connecting...[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: Connected[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataEngine: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.RiskEngine: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: Connecting...[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: Connected[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecEngine: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataEngine: Connecting all clients...[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecEngine: Connecting all clients...[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.OrderEmulator: No emulated orders to reactivate[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.OrderEmulator: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.Portfolio: Initialized 0 open orders[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.Portfolio: Initialized 0 open positions[0m
[1m2025-01-02T00:00:00.000000000Z[0m [94m[INFO] BACKTESTER-001.TraceBuyHold: self.config.oms_type=None[0m
[1m2025-01-02T00:00:00.000000000Z[0m [94m[INFO] BACKTESTER-001.TraceBuyHold: self.config.external_order_claims=None[0m
[1m2025-01-02T00:00:00.000000000Z[0m [94m[INFO] BACKTESTER-001.TraceBuyHold: self.config.manage_gtd_expiry=False[0m
[1m2025-01-02T00:00:00.000000000Z[0m [94m[INFO] BACKTESTER-001.TraceBuyHold: Set ClientOrderIdGenerator client_order_id count to 0[0m
[1m2025-01-02T00:00:00.000000000Z[0m [94m[INFO] BACKTESTER-001.TraceBuyHold: Set ClientOrderIdGenerator order_list_id count to 0[0m
TRACE 1 on_start before
equity_snapshots []
STATE QUERY on_start
CALL engine.cache.positions_open()
RETURN <class 'list'> count 0
CALL engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_inflight(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: [CMD]--> SubscribeBars(bar_type=BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL, client_id=None, venue=BINANCE)[0m
TRACE 2 on_start after
equity_snapshots []
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: RUNNING[0m
[1m2025-01-02T00:00:00.000000000Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine:  MEMORY USAGE[0m
[1m2025-01-02T00:00:00.000000000Z[0m [36m[INFO] BACKTESTER-001.BacktestEngine: =================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: RAM-Total: 9.73 GiB[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: RAM-Used: 0.92 GiB (9.48%)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: RAM-Avail: 8.81 GiB (90.52%)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Swap: disabled[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m SimulatedVenue BINANCE[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: CashAccount(id=BINANCE-001, type=CASH, base=None)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Balances starting:[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: 100_000.00000000 USDT[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m BACKTEST RUN[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run config ID:  None[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run ID:         9fd14928-038f-4dca-839e-501a65caa064[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run started:    2026-10-03T06:38:24.229670000Z[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Backtest start: 2025-01-02T00:00:00.000000000Z[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Batch start:    2025-01-02T00:00:00.000000000Z[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: Batch end:      2025-01-05T00:00:00.000000000Z[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
TRACE 3 on_bar before
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735776000000000000)
ts_event 1735776000000000000 ms 1735776000000
ts_init 1735776000000000000 ms 1735776000000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots []
TRACE 4 _submit_entry before
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735776000000000000)
ts_event 1735776000000000000 ms 1735776000000
ts_init 1735776000000000000 ms 1735776000000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots []
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: <--[EVT] OrderInitialized(instrument_id=BTCUSDT.BINANCE, client_order_id=O-20250102-000000-001-000-1, side=BUY, type=MARKET, quantity=1.000000, time_in_force=GTC, post_only=False, reduce_only=False, quote_quantity=False, options={}, emulation_trigger=NO_TRIGGER, trigger_instrument_id=None, contingency_type=NO_CONTINGENCY, order_list_id=None, linked_order_ids=None, parent_order_id=None, exec_algorithm_id=None, exec_algorithm_params=None, exec_spawn_id=None, tags=None)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: [CMD]--> [Risk] SubmitOrder(order=MarketOrder(BUY 1.000000 BTCUSDT.BINANCE MARKET GTC, status=INITIALIZED, client_order_id=O-20250102-000000-001-000-1, venue_order_id=None, position_id=None, tags=None), position_id=None)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [1;33m[WARN] BACKTESTER-001.RiskEngine: Cannot check MARKET order risk: no prices for BTCUSDT.BINANCE[0m
TRACE 5 _submit_entry after
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: <--[EVT] OrderSubmitted(instrument_id=BTCUSDT.BINANCE, client_order_id=O-20250102-000000-001-000-1, account_id=BINANCE-001, ts_event=1735776000000000000)[0m
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735776000000000000)
ts_event 1735776000000000000 ms 1735776000000
ts_init 1735776000000000000 ms 1735776000000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots []
TRACE 6 on_bar after
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735776000000000000)
ts_event 1735776000000000000 ms 1735776000000
ts_init 1735776000000000000 ms 1735776000000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735776000000, 100000.0)]
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.Portfolio: Updated AccountState(account_id=BINANCE-001, account_type=CASH, base_currency=None, is_reported=False, balances=[AccountBalance(total=99_899.90000000 USDT, locked=0.00000000 USDT, free=99_899.90000000 USDT), AccountBalance(total=1.00000000 BTC, locked=0.00000000 BTC, free=1.00000000 BTC)], margins=[], event_id=864507f3-d3ea-4229-9923-e3620fe402b8)[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.Portfolio: BTCUSDT.BINANCE account=BINANCE-001 net_position=1.000000[0m
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: <--[EVT] OrderFilled(instrument_id=BTCUSDT.BINANCE, client_order_id=O-20250102-000000-001-000-1, venue_order_id=BINANCE-1-001, account_id=BINANCE-001, trade_id=T-1e0a8050dcb6f2a1-005, position_id=BTCUSDT.BINANCE-TraceBuyHold-000, order_side=BUY, order_type=MARKET, last_qty=1.000000, last_px=100.00 USDT, commission=0.10000000 USDT, liquidity_side=TAKER, ts_event=1735776000000000000)[0m
TRACE 7 on_order_filled before
OBJECT <class 'nautilus_trader.model.events.order.OrderFilled'> OrderFilled(trader_id=BACKTESTER-001, strategy_id=TraceBuyHold-000, instrument_id=BTCUSDT.BINANCE, client_order_id=O-20250102-000000-001-000-1, venue_order_id=BINANCE-1-001, account_id=BINANCE-001, trade_id=T-1e0a8050dcb6f2a1-005, position_id=BTCUSDT.BINANCE-TraceBuyHold-000, order_side=BUY, order_type=MARKET, last_qty=1.000000, last_px=100.00 USDT, commission=0.10000000 USDT, liquidity_side=TAKER, event_id=511b2651-a52b-408e-97a7-24b48818f638, ts_event=1735776000000000000, ts_init=1735776000000000000)
ts_event 1735776000000000000 ms 1735776000000
ts_init 1735776000000000000 ms 1735776000000
client_order_id ClientOrderId('O-20250102-000000-001-000-1') ms N/A
venue_order_id VenueOrderId('BINANCE-1-001') ms N/A
position_id PositionId('BTCUSDT.BINANCE-TraceBuyHold-000') ms N/A
last_qty Quantity(1.000000) ms N/A
last_px Price(100.00) ms N/A
equity_snapshots [(1735776000000, 100000.0)]
TRACE 8 on_order_filled after
OBJECT <class 'nautilus_trader.model.events.order.OrderFilled'> OrderFilled(trader_id=BACKTESTER-001, strategy_id=TraceBuyHold-000, instrument_id=BTCUSDT.BINANCE, client_order_id=O-20250102-000000-001-000-1, venue_order_id=BINANCE-1-001, account_id=BINANCE-001, trade_id=T-1e0a8050dcb6f2a1-005, position_id=BTCUSDT.BINANCE-TraceBuyHold-000, order_side=BUY, order_type=MARKET, last_qty=1.000000, last_px=100.00 USDT, commission=0.10000000 USDT, liquidity_side=TAKER, event_id=511b2651-a52b-408e-97a7-24b48818f638, ts_event=1735776000000000000, ts_init=1735776000000000000)
ts_event 1735776000000000000 ms 1735776000000
ts_init 1735776000000000000 ms 1735776000000
client_order_id ClientOrderId('O-20250102-000000-001-000-1') ms N/A
venue_order_id VenueOrderId('BINANCE-1-001') ms N/A
position_id PositionId('BTCUSDT.BINANCE-TraceBuyHold-000') ms N/A
last_qty Quantity(1.000000) ms N/A
last_px Price(100.00) ms N/A
equity_snapshots [(1735776000000, 99999.90000000001)]
[1m2025-01-02T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: <--[EVT] PositionOpened(instrument_id=BTCUSDT.BINANCE, position_id=BTCUSDT.BINANCE-TraceBuyHold-000, account_id=BINANCE-001, opening_order_id=O-20250102-000000-001-000-1, closing_order_id=None, entry=BUY, side=LONG, signed_qty=1.0, quantity=1.000000, peak_qty=1.000000, currency=USDT, avg_px_open=100.0, avg_px_close=0.0, realized_return=0.00000, realized_pnl=-0.10000000 USDT, unrealized_pnl=0.00000000 USDT, ts_opened=1735776000000000000, ts_last=1735776000000000000, ts_closed=0, duration_ns=0)[0m
TRACE 9 on_bar before
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735862400000000000)
ts_event 1735862400000000000 ms 1735862400000
ts_init 1735862400000000000 ms 1735862400000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735776000000, 99999.90000000001)]
TRACE 10 on_bar after
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735862400000000000)
ts_event 1735862400000000000 ms 1735862400000
ts_init 1735862400000000000 ms 1735862400000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001)]
TRACE 11 on_bar before
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735948800000000000)
ts_event 1735948800000000000 ms 1735948800000
ts_init 1735948800000000000 ms 1735948800000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001)]
TRACE 12 on_bar after
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1735948800000000000)
ts_event 1735948800000000000 ms 1735948800000
ts_init 1735948800000000000 ms 1735948800000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001)]
TRACE 13 on_bar before
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1736035200000000000)
ts_event 1736035200000000000 ms 1736035200000
ts_init 1736035200000000000 ms 1736035200000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001)]
TRACE 14 on_bar after
OBJECT <class 'nautilus_trader.model.data.Bar'> Bar(BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL,100.00,101.00,99.00,100.00,1000.000000,1736035200000000000)
ts_event 1736035200000000000 ms 1736035200000
ts_init 1736035200000000000 ms 1736035200000
client_order_id ABSENT
venue_order_id ABSENT
position_id ABSENT
last_qty ABSENT
last_px ABSENT
equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001), (1736035200000, 99999.90000000001)]
TRACE 15 on_stop before
equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001), (1736035200000, 99999.90000000001)]
TRACE 16 on_stop after
equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001), (1736035200000, 99999.90000000001)]
[1m2025-01-05T00:00:00.000000000Z[0m [1;33m[WARN] BACKTESTER-001.TraceBuyHold: The `Strategy.on_stop` handler was called when not overridden. It's expected that any actions required when stopping the strategy occur here, such as unsubscribing from data[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.TraceBuyHold: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: Disconnecting...[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: Disconnected[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.DataEngine: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.RiskEngine: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: Disconnecting...[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: Disconnected[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.ExecEngine: STOPPED[0m
[1m2025-01-05T00:00:00.000000000Z[0m [INFO] BACKTESTER-001.OrderEmulator: STOPPED[0m
[1m2026-10-03T06:38:24.240114340Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:38:24.240126624Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m BACKTEST POST-RUN[0m
[1m2026-10-03T06:38:24.240127811Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:38:24.240130211Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run config ID:  None[0m
[1m2026-10-03T06:38:24.240133629Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run ID:         9fd14928-038f-4dca-839e-501a65caa064[0m
[1m2026-10-03T06:38:24.240140342Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run started:    2026-10-03T06:38:24.229670000Z[0m
[1m2026-10-03T06:38:24.240141131Z[0m [INFO] BACKTESTER-001.BacktestEngine: Run finished:   2026-10-03T06:38:24.239982000Z[0m
[1m2026-10-03T06:38:24.240158900Z[0m [INFO] BACKTESTER-001.BacktestEngine: Elapsed time:   0 days 00:00:00.010312[0m
[1m2026-10-03T06:38:24.240167769Z[0m [INFO] BACKTESTER-001.BacktestEngine: Backtest start: 2025-01-02T00:00:00.000000000Z[0m
[1m2026-10-03T06:38:24.240169043Z[0m [INFO] BACKTESTER-001.BacktestEngine: Backtest end:   2025-01-05T00:00:00.000000000Z[0m
[1m2026-10-03T06:38:24.240175582Z[0m [INFO] BACKTESTER-001.BacktestEngine: Backtest range: 3 days 00:00:00[0m
[1m2026-10-03T06:38:24.240184016Z[0m [INFO] BACKTESTER-001.BacktestEngine: Iterations: 4[0m
[1m2026-10-03T06:38:24.240187130Z[0m [INFO] BACKTESTER-001.BacktestEngine: Total events: 2[0m
[1m2026-10-03T06:38:24.240195532Z[0m [INFO] BACKTESTER-001.BacktestEngine: Total orders: 1[0m
[1m2026-10-03T06:38:24.240211620Z[0m [INFO] BACKTESTER-001.BacktestEngine: Total positions: 1[0m
[1m2026-10-03T06:38:24.240225004Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:38:24.240229889Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m SimulatedVenue BINANCE[0m
[1m2026-10-03T06:38:24.240237049Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:38:24.240242560Z[0m [INFO] BACKTESTER-001.BacktestEngine: CashAccount(id=BINANCE-001, type=CASH, base=None)[0m
[1m2026-10-03T06:38:24.240243022Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:38:24.240244064Z[0m [INFO] BACKTESTER-001.BacktestEngine: Balances starting:[0m
[1m2026-10-03T06:38:24.240254573Z[0m [INFO] BACKTESTER-001.BacktestEngine: 100_000.00000000 USDT[0m
[1m2026-10-03T06:38:24.240261794Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:38:24.240262632Z[0m [INFO] BACKTESTER-001.BacktestEngine: Balances ending:[0m
[1m2026-10-03T06:38:24.240268388Z[0m [INFO] BACKTESTER-001.BacktestEngine: 99_899.90000000 USDT[0m
[1m2026-10-03T06:38:24.240278076Z[0m [INFO] BACKTESTER-001.BacktestEngine: 1.00000000 BTC[0m
[1m2026-10-03T06:38:24.240279009Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:38:24.240279301Z[0m [INFO] BACKTESTER-001.BacktestEngine: Commissions:[0m
[1m2026-10-03T06:38:24.240290274Z[0m [INFO] BACKTESTER-001.BacktestEngine: -0.10000000 USDT[0m
[1m2026-10-03T06:38:24.240297465Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:38:24.240298706Z[0m [INFO] BACKTESTER-001.BacktestEngine: Unrealized PnLs (included in totals):[0m
[1m2026-10-03T06:38:24.240364883Z[0m [INFO] BACKTESTER-001.BacktestEngine: 0.00000000 USDT[0m
[1m2026-10-03T06:38:24.240378420Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:38:24.240379609Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m PORTFOLIO PERFORMANCE[0m
[1m2026-10-03T06:38:24.240380059Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m=================================================================[0m
[1m2026-10-03T06:38:24.241483500Z[0m [INFO] BACKTESTER-001.BacktestEngine:  PnL Statistics (BTC)[0m
[1m2026-10-03T06:38:24.241517763Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:38:24.241672433Z[0m [INFO] BACKTESTER-001.BacktestEngine: PnL (total):                    1.0[0m
[1m2026-10-03T06:38:24.241685874Z[0m [INFO] BACKTESTER-001.BacktestEngine: PnL% (total):                   0.0[0m
[1m2026-10-03T06:38:24.241686644Z[0m [INFO] BACKTESTER-001.BacktestEngine: Max Winner:                     nan[0m
[1m2026-10-03T06:38:24.241687204Z[0m [INFO] BACKTESTER-001.BacktestEngine: Avg Winner:                     nan[0m
[1m2026-10-03T06:38:24.241687451Z[0m [INFO] BACKTESTER-001.BacktestEngine: Min Winner:                     nan[0m
[1m2026-10-03T06:38:24.241687991Z[0m [INFO] BACKTESTER-001.BacktestEngine: Min Loser:                      nan[0m
[1m2026-10-03T06:38:24.241688284Z[0m [INFO] BACKTESTER-001.BacktestEngine: Avg Loser:                      nan[0m
[1m2026-10-03T06:38:24.241688647Z[0m [INFO] BACKTESTER-001.BacktestEngine: Max Loser:                      nan[0m
[1m2026-10-03T06:38:24.241688936Z[0m [INFO] BACKTESTER-001.BacktestEngine: Expectancy:                     nan[0m
[1m2026-10-03T06:38:24.241690516Z[0m [INFO] BACKTESTER-001.BacktestEngine: Win Rate:                       nan[0m
[1m2026-10-03T06:38:24.241691413Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:38:24.241692422Z[0m [INFO] BACKTESTER-001.BacktestEngine:  PnL Statistics (USDT)[0m
[1m2026-10-03T06:38:24.241692796Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:38:24.241877180Z[0m [INFO] BACKTESTER-001.BacktestEngine: PnL (total):                    -100.1[0m
[1m2026-10-03T06:38:24.241888780Z[0m [INFO] BACKTESTER-001.BacktestEngine: PnL% (total):                   -0.10009999999999128[0m
[1m2026-10-03T06:38:24.241890373Z[0m [INFO] BACKTESTER-001.BacktestEngine: Max Winner:                     nan[0m
[1m2026-10-03T06:38:24.241890580Z[0m [INFO] BACKTESTER-001.BacktestEngine: Avg Winner:                     nan[0m
[1m2026-10-03T06:38:24.241890889Z[0m [INFO] BACKTESTER-001.BacktestEngine: Min Winner:                     nan[0m
[1m2026-10-03T06:38:24.241891160Z[0m [INFO] BACKTESTER-001.BacktestEngine: Min Loser:                      -0.1[0m
[1m2026-10-03T06:38:24.241891380Z[0m [INFO] BACKTESTER-001.BacktestEngine: Avg Loser:                      -0.1[0m
[1m2026-10-03T06:38:24.241891558Z[0m [INFO] BACKTESTER-001.BacktestEngine: Max Loser:                      -0.1[0m
[1m2026-10-03T06:38:24.241891841Z[0m [INFO] BACKTESTER-001.BacktestEngine: Expectancy:                     -0.1[0m
[1m2026-10-03T06:38:24.241892060Z[0m [INFO] BACKTESTER-001.BacktestEngine: Win Rate:                       0.0[0m
[1m2026-10-03T06:38:24.241892760Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:38:24.241893693Z[0m [INFO] BACKTESTER-001.BacktestEngine:  Returns Statistics[0m
[1m2026-10-03T06:38:24.241894188Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:38:24.241952297Z[0m [INFO] BACKTESTER-001.BacktestEngine: Returns Volatility (252 days):  nan[0m
[1m2026-10-03T06:38:24.241960903Z[0m [INFO] BACKTESTER-001.BacktestEngine: Average (Return):               nan[0m
[1m2026-10-03T06:38:24.241961617Z[0m [INFO] BACKTESTER-001.BacktestEngine: Average Loss (Return):          nan[0m
[1m2026-10-03T06:38:24.241961885Z[0m [INFO] BACKTESTER-001.BacktestEngine: Average Win (Return):           nan[0m
[1m2026-10-03T06:38:24.241962139Z[0m [INFO] BACKTESTER-001.BacktestEngine: Sharpe Ratio (252 days):        nan[0m
[1m2026-10-03T06:38:24.241962387Z[0m [INFO] BACKTESTER-001.BacktestEngine: Sortino Ratio (252 days):       nan[0m
[1m2026-10-03T06:38:24.241962681Z[0m [INFO] BACKTESTER-001.BacktestEngine: Profit Factor:                  nan[0m
[1m2026-10-03T06:38:24.241963008Z[0m [INFO] BACKTESTER-001.BacktestEngine: Risk Return Ratio:              nan[0m
[1m2026-10-03T06:38:24.241963654Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:38:24.241964308Z[0m [INFO] BACKTESTER-001.BacktestEngine:  General Statistics[0m
[1m2026-10-03T06:38:24.241964635Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
[1m2026-10-03T06:38:24.241992991Z[0m [INFO] BACKTESTER-001.BacktestEngine: Long Ratio:                     1.0[0m
[1m2026-10-03T06:38:24.242001148Z[0m [INFO] BACKTESTER-001.BacktestEngine: [36m-----------------------------------------------------------------[0m
STATE QUERY postrun before disposal
CALL engine.cache.positions_open()
RETURN <class 'list'> count 1
ITEM <class 'nautilus_trader.model.position.Position'> Position(LONG 1.000000 BTCUSDT.BINANCE, id=BTCUSDT.BINANCE-TraceBuyHold-000)
FIELD id PositionId('BTCUSDT.BINANCE-TraceBuyHold-000') DOC The position ID.

:returns: `PositionId`
FIELD client_order_id ABSENT
FIELD instrument_id InstrumentId('BTCUSDT.BINANCE') DOC The position instrument ID.

:returns: `InstrumentId`
FIELD is_open True DOC Return whether the position side is **not** ``FLAT``.

Returns
-------
bool
FIELD is_closed False DOC Return whether the position side is ``FLAT``.

Returns
-------
bool
FIELD side <PositionSide.LONG: 2> DOC The current position side.

:returns: `PositionSide`
FIELD quantity Quantity(1.000000) DOC The current open quantity.

:returns: `Quantity`
FIELD signed_qty 1.0 DOC The current signed quantity (positive for position side ``LONG``, negative for ``SHORT``).

:returns: `double`
FIELD status ABSENT
CALL engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 1
ITEM <class 'nautilus_trader.model.position.Position'> Position(LONG 1.000000 BTCUSDT.BINANCE, id=BTCUSDT.BINANCE-TraceBuyHold-000)
FIELD id PositionId('BTCUSDT.BINANCE-TraceBuyHold-000') DOC The position ID.

:returns: `PositionId`
FIELD client_order_id ABSENT
FIELD instrument_id InstrumentId('BTCUSDT.BINANCE') DOC The position instrument ID.

:returns: `InstrumentId`
FIELD is_open True DOC Return whether the position side is **not** ``FLAT``.

Returns
-------
bool
FIELD is_closed False DOC Return whether the position side is ``FLAT``.

Returns
-------
bool
FIELD side <PositionSide.LONG: 2> DOC The current position side.

:returns: `PositionSide`
FIELD quantity Quantity(1.000000) DOC The current open quantity.

:returns: `Quantity`
FIELD signed_qty 1.0 DOC The current signed quantity (positive for position side ``LONG``, negative for ``SHORT``).

:returns: `double`
FIELD status ABSENT
CALL engine.cache.orders_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
CALL engine.cache.orders_inflight(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))
RETURN <class 'list'> count 0
FINAL equity_snapshots [(1735776000000, 99999.90000000001), (1735862400000, 99999.90000000001), (1735948800000, 99999.90000000001), (1736035200000, 99999.90000000001)]
ENTRY SUBMISSION TIMES [1735776000000] FILL TIMES [1735776000000]
REPORT fills class <class 'pandas.DataFrame'>
columns ['trader_id', 'strategy_id', 'instrument_id', 'venue_order_id', 'account_id', 'trade_id', 'position_id', 'order_side', 'order_type', 'last_qty', 'last_px', 'currency', 'commission', 'liquidity_side', 'event_id', 'ts_event', 'ts_init', 'info', 'reconciliation'] dtypes {'trader_id': <StringDtype(na_value=nan)>, 'strategy_id': <StringDtype(na_value=nan)>, 'instrument_id': <StringDtype(na_value=nan)>, 'venue_order_id': <StringDtype(na_value=nan)>, 'account_id': <StringDtype(na_value=nan)>, 'trade_id': <StringDtype(na_value=nan)>, 'position_id': <StringDtype(na_value=nan)>, 'order_side': <StringDtype(na_value=nan)>, 'order_type': <StringDtype(na_value=nan)>, 'last_qty': <StringDtype(na_value=nan)>, 'last_px': <StringDtype(na_value=nan)>, 'currency': <StringDtype(na_value=nan)>, 'commission': <StringDtype(na_value=nan)>, 'liquidity_side': <StringDtype(na_value=nan)>, 'event_id': <StringDtype(na_value=nan)>, 'ts_event': datetime64[ns, UTC], 'ts_init': datetime64[ns, UTC], 'info': dtype('O'), 'reconciliation': dtype('bool')}
index class <class 'pandas.Index'> index name 'client_order_id' index values ['O-20250102-000000-001-000-1']
FULL FRAME
                                  trader_id       strategy_id    instrument_id venue_order_id   account_id                trade_id                       position_id order_side order_type  last_qty last_px currency       commission liquidity_side                              event_id                  ts_event                   ts_init info  reconciliation
client_order_id                                                                                                                                                                                                                                                                                                                                                     
O-20250102-000000-001-000-1  BACKTESTER-001  TraceBuyHold-000  BTCUSDT.BINANCE  BINANCE-1-001  BINANCE-001  T-1e0a8050dcb6f2a1-005  BTCUSDT.BINANCE-TraceBuyHold-000        BUY     MARKET  1.000000  100.00     USDT  0.10000000 USDT          TAKER  511b2651-a52b-408e-97a7-24b48818f638 2025-01-02 00:00:00+00:00 2025-01-02 00:00:00+00:00   {}           False
FULL RECORDS (index retained)
[{'client_order_id': 'O-20250102-000000-001-000-1',
  'trader_id': 'BACKTESTER-001',
  'strategy_id': 'TraceBuyHold-000',
  'instrument_id': 'BTCUSDT.BINANCE',
  'venue_order_id': 'BINANCE-1-001',
  'account_id': 'BINANCE-001',
  'trade_id': 'T-1e0a8050dcb6f2a1-005',
  'position_id': 'BTCUSDT.BINANCE-TraceBuyHold-000',
  'order_side': 'BUY',
  'order_type': 'MARKET',
  'last_qty': '1.000000',
  'last_px': '100.00',
  'currency': 'USDT',
  'commission': '0.10000000 USDT',
  'liquidity_side': 'TAKER',
  'event_id': '511b2651-a52b-408e-97a7-24b48818f638',
  'ts_event': Timestamp('2025-01-02 00:00:00+0000', tz='UTC'),
  'ts_init': Timestamp('2025-01-02 00:00:00+0000', tz='UTC'),
  'info': {},
  'reconciliation': False}]
TIME ts_opened ABSENT
TIME ORIGINAL ts_event Timestamp('2025-01-02 00:00:00+0000', tz='UTC') type <class 'pandas.Timestamp'> ms 1735776000000
TIME ORIGINAL ts_init Timestamp('2025-01-02 00:00:00+0000', tz='UTC') type <class 'pandas.Timestamp'> ms 1735776000000
TIME ts_last ABSENT
REPORT positions class <class 'pandas.DataFrame'>
columns ['trader_id', 'strategy_id', 'instrument_id', 'account_id', 'opening_order_id', 'closing_order_id', 'entry', 'side', 'quantity', 'peak_qty', 'ts_init', 'ts_opened', 'ts_last', 'ts_closed', 'duration_ns', 'avg_px_open', 'avg_px_close', 'commissions', 'realized_return', 'realized_pnl', 'is_snapshot'] dtypes {'trader_id': <StringDtype(na_value=nan)>, 'strategy_id': <StringDtype(na_value=nan)>, 'instrument_id': <StringDtype(na_value=nan)>, 'account_id': <StringDtype(na_value=nan)>, 'opening_order_id': <StringDtype(na_value=nan)>, 'closing_order_id': dtype('O'), 'entry': <StringDtype(na_value=nan)>, 'side': <StringDtype(na_value=nan)>, 'quantity': <StringDtype(na_value=nan)>, 'peak_qty': <StringDtype(na_value=nan)>, 'ts_init': dtype('int64'), 'ts_opened': datetime64[ns, UTC], 'ts_last': dtype('int64'), 'ts_closed': dtype('O'), 'duration_ns': dtype('O'), 'avg_px_open': dtype('float64'), 'avg_px_close': dtype('O'), 'commissions': dtype('O'), 'realized_return': dtype('float64'), 'realized_pnl': <StringDtype(na_value=nan)>, 'is_snapshot': dtype('bool')}
index class <class 'pandas.Index'> index name 'position_id' index values ['BTCUSDT.BINANCE-TraceBuyHold-000']
FULL FRAME
                                       trader_id       strategy_id    instrument_id   account_id             opening_order_id closing_order_id entry  side  quantity  peak_qty              ts_init                 ts_opened              ts_last ts_closed duration_ns  avg_px_open avg_px_close        commissions  realized_return      realized_pnl  is_snapshot
position_id                                                                                                                                                                                                                                                                                                                                                          
BTCUSDT.BINANCE-TraceBuyHold-000  BACKTESTER-001  TraceBuyHold-000  BTCUSDT.BINANCE  BINANCE-001  O-20250102-000000-001-000-1             None   BUY  LONG  1.000000  1.000000  1735776000000000000 2025-01-02 00:00:00+00:00  1735776000000000000      <NA>        None        100.0         None  [0.10000000 USDT]              0.0  -0.10000000 USDT        False
FULL RECORDS (index retained)
[{'position_id': 'BTCUSDT.BINANCE-TraceBuyHold-000',
  'trader_id': 'BACKTESTER-001',
  'strategy_id': 'TraceBuyHold-000',
  'instrument_id': 'BTCUSDT.BINANCE',
  'account_id': 'BINANCE-001',
  'opening_order_id': 'O-20250102-000000-001-000-1',
  'closing_order_id': None,
  'entry': 'BUY',
  'side': 'LONG',
  'quantity': '1.000000',
  'peak_qty': '1.000000',
  'ts_init': 1735776000000000000,
  'ts_opened': Timestamp('2025-01-02 00:00:00+0000', tz='UTC'),
  'ts_last': 1735776000000000000,
  'ts_closed': None,
  'duration_ns': None,
  'avg_px_open': 100.0,
  'avg_px_close': None,
  'commissions': ['0.10000000 USDT'],
  'realized_return': 0.0,
  'realized_pnl': '-0.10000000 USDT',
  'is_snapshot': False}]
TIME ORIGINAL ts_opened Timestamp('2025-01-02 00:00:00+0000', tz='UTC') type <class 'pandas.Timestamp'> ms 1735776000000
TIME ts_event ABSENT
TIME ORIGINAL ts_init 1735776000000000000 type <class 'int'> ms 1735776000000
TIME ORIGINAL ts_last 1735776000000000000 type <class 'int'> ms 1735776000000
REPORT account class <class 'pandas.DataFrame'>
columns ['total', 'locked', 'free', 'currency', 'account_id', 'account_type', 'base_currency', 'margins', 'reported', 'info'] dtypes {'total': <StringDtype(na_value=nan)>, 'locked': <StringDtype(na_value=nan)>, 'free': <StringDtype(na_value=nan)>, 'currency': <StringDtype(na_value=nan)>, 'account_id': <StringDtype(na_value=nan)>, 'account_type': <StringDtype(na_value=nan)>, 'base_currency': dtype('O'), 'margins': dtype('O'), 'reported': dtype('bool'), 'info': dtype('O')}
index class <class 'pandas.DatetimeIndex'> index name None index values [Timestamp('2025-01-02 00:00:00+0000', tz='UTC'), Timestamp('2025-01-02 00:00:00+0000', tz='UTC'), Timestamp('2025-01-02 00:00:00+0000', tz='UTC')]
FULL FRAME
                                     total      locked             free currency   account_id account_type base_currency margins  reported info
2025-01-02 00:00:00+00:00  100000.00000000  0.00000000  100000.00000000     USDT  BINANCE-001         CASH          None      []      True   {}
2025-01-02 00:00:00+00:00   99899.90000000  0.00000000   99899.90000000     USDT  BINANCE-001         CASH          None      []     False   {}
2025-01-02 00:00:00+00:00       1.00000000  0.00000000       1.00000000      BTC  BINANCE-001         CASH          None      []     False   {}
FULL RECORDS (index retained)
[{'index': Timestamp('2025-01-02 00:00:00+0000', tz='UTC'),
  'total': '100000.00000000',
  'locked': '0.00000000',
  'free': '100000.00000000',
  'currency': 'USDT',
  'account_id': 'BINANCE-001',
  'account_type': 'CASH',
  'base_currency': None,
  'margins': [],
  'reported': True,
  'info': {}},
 {'index': Timestamp('2025-01-02 00:00:00+0000', tz='UTC'),
  'total': '99899.90000000',
  'locked': '0.00000000',
  'free': '99899.90000000',
  'currency': 'USDT',
  'account_id': 'BINANCE-001',
  'account_type': 'CASH',
  'base_currency': None,
  'margins': [],
  'reported': False,
  'info': {}},
 {'index': Timestamp('2025-01-02 00:00:00+0000', tz='UTC'),
  'total': '1.00000000',
  'locked': '0.00000000',
  'free': '1.00000000',
  'currency': 'BTC',
  'account_id': 'BINANCE-001',
  'account_type': 'CASH',
  'base_currency': None,
  'margins': [],
  'reported': False,
  'info': {}}]
TIME ts_opened ABSENT
TIME ts_event ABSENT
TIME ts_init ABSENT
TIME ts_last ABSENT
TIME ts_opened ABSENT
TIME ts_event ABSENT
TIME ts_init ABSENT
TIME ts_last ABSENT
TIME ts_opened ABSENT
TIME ts_event ABSENT
TIME ts_init ABSENT
TIME ts_last ABSENT
TERMINAL last report row per currency: cash USDT 99899.9 base BTC 1.0 last eligible close 1735948800000 last eligible price 100 cash + base * last eligible price 99999.9 NO liquidation; sentinel price equals eligible price but still reached matching/valuation
CALL engine.dispose()
[1m2026-10-03T06:38:24.271441287Z[0m [INFO] BACKTESTER-001.DataClient-BINANCE: DISPOSED[0m
[1m2026-10-03T06:38:24.271475897Z[0m [INFO] BACKTESTER-001.DataEngine: DISPOSED[0m
[1m2026-10-03T06:38:24.271484123Z[0m [INFO] BACKTESTER-001.RiskEngine: DISPOSED[0m
[1m2026-10-03T06:38:24.271496495Z[0m [INFO] BACKTESTER-001.ExecClient-BINANCE: DISPOSED[0m
[1m2026-10-03T06:38:24.271502054Z[0m [INFO] BACKTESTER-001.ExecEngine: DISPOSED[0m
[1m2026-10-03T06:38:24.271520099Z[0m [INFO] BACKTESTER-001.OrderEmulator: DISPOSED[0m
[1m2026-10-03T06:38:24.271529519Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: Cleared actors[0m
[1m2026-10-03T06:38:24.271583727Z[0m [INFO] BACKTESTER-001.TraceBuyHold: DISPOSED[0m
[1m2026-10-03T06:38:24.271599969Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: Cleared trading strategies[0m
[1m2026-10-03T06:38:24.271609556Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: Cleared execution algorithms[0m
[1m2026-10-03T06:38:24.271615989Z[0m [INFO] BACKTESTER-001.BACKTESTER-001: DISPOSED[0m
[1m2026-10-03T06:38:24.271655624Z[0m [INFO] BACKTESTER-001.Cache: Reset[0m
[1m2026-10-03T06:38:24.271680729Z[0m [INFO] BACKTESTER-001.MessageBus: Closed message bus[0m
Traceback (most recent call last):
  File "/tmp/phase18f-runtime-probe.py", line 234, in <module>
    main()
  File "/tmp/phase18f-runtime-probe.py", line 227, in main
    run_case(False)
  File "/tmp/phase18f-runtime-probe.py", line 210, in run_case
    assert strategy.equity_snapshots[0][1] == 99999.9
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError
PROBE STOP; failure retained; no silent substitution
```

## Whitespace verification and disclosed exception

The first staged `git diff --cached --check` exited 2. Its complete output
is retained below. Six flags are pandas index-header padding inside the
verbatim probe output fences. The authored extra blank line at EOF was
removed before the final check. Coordinator explicitly authorized preserving
transcript-inherent whitespace only; this is not a clean whitespace-check
claim. The final staged check must flag only raw transcript rows, including
reproduced diagnostic rows below. Source and prose have no trailing spaces.

```text
docs/specs/phase-18-runtime-probe.md:958: trailing whitespace.
+client_order_id                                                                                                                                                                                                                                                                                                                                                     
docs/specs/phase-18-runtime-probe.md:990: trailing whitespace.
+position_id                                                                                                                                                                                                                                                                                                                                                          
docs/specs/phase-18-runtime-probe.md:1585: trailing whitespace.
+client_order_id                                                                                                                                                                                                                                                                                                                                                     
docs/specs/phase-18-runtime-probe.md:1617: trailing whitespace.
+position_id                                                                                                                                                                                                                                                                                                                                                          
docs/specs/phase-18-runtime-probe.md:2507: trailing whitespace.
+client_order_id                                                                                                                                                                                                                                                                                                                                                     
docs/specs/phase-18-runtime-probe.md:2539: trailing whitespace.
+position_id                                                                                                                                                                                                                                                                                                                                                          
docs/specs/phase-18-runtime-probe.md:2648: new blank line at EOF.
```
