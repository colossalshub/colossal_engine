from __future__ import annotations

import copy
import logging
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pandas as pd
import pytest

from quant.engine import research_runner as module
from quant.engine.bar_coverage import BarClock
from quant.engine.runner import BacktestResult, run_backtest
from quant.engine.temporal import ResearchInterval
from quant.strategies.buy_hold import BuyHold

D = 86_400_000
T = 1_735_689_600_000 + 12_345  # shifted grid, not midnight
NS = 1_000_000


def _inputs(*, warmup: bool = False) -> dict[str, Any]:
    rows = [
        {
            "ts": T + i * D,
            "open": price,
            "high": price + 1,
            "low": price - 1,
            "close": price,
            "volume": 1000.0,
        }
        for i, price in enumerate((50.0, 100.0, 120.0, 9000.0, 8000.0))
    ]
    return dict(
        active=ResearchInterval(T + 2 * D, T + 4 * D),
        warmup=ResearchInterval(T + D, T + 2 * D) if warmup else None,
        required_warmup_observations=1 if warmup else 0,
        timeframe="1d",
        calendar="continuous_utc_fixed",
        anchor_ts=T,
        clocks=tuple(
            BarClock(T + i * D, T + (i + 1) * D, T + (i + 1) * D) for i in range(5)
        ),
        rows=rows,
        starting_balance_usdt=100_000.0,
        trade_size="1.0000000",
        deploy_pct="0",
        maker_fee="0.001",
        taker_fee="0.001",
    )


class _EngineWatch:
    """Delegate to a real engine; only observe data, calls and disposal."""

    def __init__(self, real: Any) -> None:
        self.real = real
        self.bars: list[Any] = []
        self.strategy: Any = None
        self.disposed = False
        self.swallow = False
        self.swallowed: Exception | None = None
        self.extractions = 0
        self.cache_override: Any = None

    def __getattr__(self, name: str) -> Any:
        return getattr(self.real, name)

    @property
    def cache(self) -> Any:
        return (
            self.cache_override if self.cache_override is not None else self.real.cache
        )

    @property
    def trader(self) -> Any:
        self.extractions += 1
        return self.real.trader

    def add_data(self, bars: list[Any]) -> None:
        self.bars.extend(bars)
        self.real.add_data(bars)

    def add_strategy(self, strategy: Any) -> None:
        self.strategy = strategy
        self.real.add_strategy(strategy)

    def run(self) -> None:
        try:
            self.real.run()
        except Exception as exc:
            if not self.swallow:
                raise
            self.swallowed = exc

    def dispose(self) -> None:
        self.disposed = True
        self.real.dispose()


class _CacheFault:
    """Inject a query result/error at a chosen actual adapter query."""

    def __init__(self, real: Any, method: str, at: int, failure: object) -> None:
        self.real = real
        self.method = method
        self.at = at
        self.failure = failure
        self.calls = 0

    def __getattr__(self, name: str) -> Any:
        query = getattr(self.real, name)
        if name != self.method:
            return query

        def call(*args: Any, **kwargs: Any) -> Any:
            self.calls += 1
            result = query(*args, **kwargs)  # real cache query still runs
            if self.calls == self.at:
                if isinstance(self.failure, Exception):
                    raise self.failure
                return self.failure
            return result

        return call


def _watch(monkeypatch: pytest.MonkeyPatch) -> list[_EngineWatch]:
    watches: list[_EngineWatch] = []
    real_factory = module.BacktestEngine

    def factory(**kwargs: Any) -> _EngineWatch:
        watch = _EngineWatch(real_factory(**kwargs))
        watches.append(watch)
        return watch

    monkeypatch.setattr(module, "BacktestEngine", factory)
    return watches


def _assert_result(result: BacktestResult) -> None:
    assert result.starting_balance == 100_000.0
    assert [ts for ts, _ in result.portfolio_returns] == [T + 2 * D, T + 3 * D]
    (fill,) = result.fills_report
    (position,) = result.position_report
    assert fill["ts_event"].value == (T + 2 * D) * NS
    assert fill["ts_init"].value == (T + 2 * D) * NS
    assert float(fill["last_px"]) == 100.0
    assert float(fill["last_qty"]) == 1.0
    assert float(str(fill["commission"]).split()[0]) == pytest.approx(0.1)
    assert str(fill["order_side"]) == "BUY"
    assert pd.isna(position["ts_closed"])
    assert position["ts_opened"].value == (T + 2 * D) * NS
    assert position["position_id"]
    assert position["side"] == "LONG"
    assert float(result.account_report["total"]) == pytest.approx(99899.9)
    # Independent expected base is the actual fill quantity; no liquidation.
    expected = float(result.account_report["total"]) + float(fill["last_qty"]) * 120
    assert result.independent_ending_balance == pytest.approx(expected)
    assert result.ending_balance == pytest.approx(expected)
    assert result.portfolio_returns[0][1] == pytest.approx(-0.1 / 100_000)
    assert result.portfolio_returns[1][1] == pytest.approx(20 / 99999.9)


@pytest.mark.parametrize("warmup", [False, True])
def test_real_boundary_fee_residual_and_fresh_repeat(
    monkeypatch: pytest.MonkeyPatch,
    warmup: bool,
) -> None:
    watches = _watch(monkeypatch)
    inputs = _inputs(warmup=warmup)
    before = copy.deepcopy(inputs)
    first = module.run_research_buy_hold(**inputs)
    _assert_result(first)
    inputs["clocks"] = tuple(reversed(inputs["clocks"]))
    inputs["rows"] = [inputs["rows"][i] for i in (4, 2, 0, 3, 1)]
    for row in inputs["rows"]:
        if row["ts"] == T:
            row.update(open=987654.0, high=987655.0, low=987653.0, close=987654.0)
        elif row["ts"] >= T + 3 * D:
            row.update(open="invalid excluded", high=float("nan"), low=-1, close=None)
    changed_before = copy.deepcopy(inputs)
    second = module.run_research_buy_hold(**inputs)
    _assert_result(second)
    assert second.portfolio_returns == first.portfolio_returns
    assert second.account_report == first.account_report
    assert inputs == changed_before
    assert before["rows"][0]["close"] == 50.0
    for watch in watches:
        assert watch.disposed
        expected = [T + D, T + 2 * D, T + 3 * D] if warmup else [T + 2 * D, T + 3 * D]
        assert [(b.ts_event, b.ts_init) for b in watch.bars] == [
            (t * NS, t * NS) for t in expected
        ]
        assert len(watch.strategy.equity_snapshots) == 2
        assert not watch.strategy.callback_error


def test_admitted_decimal_volume_reaches_actual_engine_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    watches = _watch(monkeypatch)
    inputs = _inputs()
    inputs["rows"][1]["volume"] = 1000000000000.0001
    before = copy.deepcopy(inputs)
    result = module.run_research_buy_hold(**inputs)
    _assert_result(result)
    (watch,) = watches
    assert str(watch.bars[0].volume) == "1000000000000.000100"
    assert Decimal(str(watch.bars[0].volume)) == Decimal(
        str(inputs["rows"][1]["volume"])
    )
    for bar, row in zip(watch.bars, inputs["rows"][1:3], strict=True):
        for field in ("open", "high", "low", "close", "volume"):
            assert Decimal(str(getattr(bar, field))) == Decimal(str(row[field]))
    assert inputs == before
    assert watch.disposed


def test_ordinary_daily_control_unchanged() -> None:
    inputs = _inputs()
    rows = inputs["rows"][1:3]
    control = run_backtest(
        venue="binance",
        symbol="BTC/USDT",
        bar_type_str="BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL",
        rows=rows,
        starting_balance_usdt=100_000.0,
        trade_size="1",
        deploy_pct="0",
        maker_fee="0.001",
        taker_fee="0.001",
    )
    research = module.run_research_buy_hold(**inputs)
    _assert_result(control)
    assert research.portfolio_returns == control.portfolio_returns
    assert research.ending_balance == pytest.approx(control.ending_balance)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("timeframe", "1h", "timeframe must be 1d"),
        ("calendar", "session", "calendar must be continuous_utc_fixed"),
        (
            "active",
            ResearchInterval(True, T + 4 * D),
            "active.start_ts must be an integer",
        ),
        ("active", ResearchInterval(T + 4 * D, T + 2 * D), "must be less than"),
        ("active", ResearchInterval(T + 2 * D + 1, T + 4 * D), "must align"),
        ("anchor_ts", False, "anchor_ts must be an integer"),
        ("required_warmup_observations", True, "must be an integer"),
        ("required_warmup_observations", -1, "must be nonnegative"),
        ("required_warmup_observations", 1, "absent warmup requires"),
        ("starting_balance_usdt", 100000.1, "whole-USDT float"),
        ("starting_balance_usdt", float("inf"), "whole-USDT float"),
        ("starting_balance_usdt", True, "whole-USDT float"),
        ("starting_balance_usdt", 100000, "whole-USDT float"),
        ("trade_size", "bad", "trade_size must be a finite decimal string"),
        ("trade_size", "NaN", "trade_size must be a finite decimal string"),
        ("trade_size", "0", "trade_size must be positive"),
        ("trade_size", "0.0000001", "6 decimal places"),
        ("deploy_pct", "Infinity", "deploy_pct must be a finite decimal string"),
        ("deploy_pct", "1.1", "deploy_pct must be between"),
        ("maker_fee", "bad", "maker_fee must be a finite decimal string"),
        ("taker_fee", "-0.1", "taker_fee must be nonnegative"),
        ("taker_fee", "NaN", "taker_fee must be a finite decimal string"),
    ],
)
def test_scalar_rejection_before_engine(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    field: str,
    value: object,
    message: str,
) -> None:
    inputs = _inputs()
    inputs[field] = value
    _reject_before_engine(monkeypatch, caplog, inputs, message)


def _reject_before_engine(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    inputs: dict[str, Any],
    message: str,
) -> None:
    def forbidden(**kwargs: Any) -> None:
        pytest.fail("engine constructed before admission completed")

    monkeypatch.setattr(module, "BacktestEngine", forbidden)
    before = copy.deepcopy(inputs)
    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(ValueError, match=message) as exc,
    ):
        module.run_research_buy_hold(**inputs)
    assert inputs == before
    errors = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert len(errors) == 1
    assert errors[0].getMessage() == str(exc.value)


@pytest.mark.parametrize(
    "case",
    [
        "missing_active",
        "missing_warmup",
        "insufficient_warmup",
        "zero_warmup",
        "overlap_warmup",
        "bool_clock",
        "delay",
        "wrong_close",
        "misaligned_clock",
        "missing_join",
        "extra_join",
        "duplicate_row",
        "duplicate_clock",
        "bool_row",
        "bad_ohlcv",
        "bool_ohlcv",
        "decimal_ohlcv",
        "negative_volume",
        "bad_bounds",
        "price_precision",
        "volume_precision",
        "negative_engine_open",
        "wide_engine_close",
    ],
)
def test_evidence_rejection_before_engine(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    case: str,
) -> None:
    inputs = _inputs(warmup=True)
    clocks = list(inputs["clocks"])
    message = ""
    if case in ("missing_active", "missing_warmup"):
        index = 2 if case == "missing_active" else 0
        del inputs["rows"][index]
        del clocks[index]
        message = "coverage|at least one stage observation"
    elif case == "insufficient_warmup":
        inputs["required_warmup_observations"] = 2
        message = "less than required"
    elif case == "zero_warmup":
        inputs["required_warmup_observations"] = 0
        message = "present warmup requires"
    elif case == "overlap_warmup":
        inputs["warmup"] = ResearchInterval(T + D, T + 3 * D)
        message = "warmup.end_ts must be at or before"
    elif case in ("bool_clock", "delay", "wrong_close", "misaligned_clock"):
        original = clocks[1]
        clocks[1] = BarClock(
            original.open_ts + (1 if case == "misaligned_clock" else 0),
            True
            if case == "bool_clock"
            else original.close_ts + (D if case == "wrong_close" else 0),
            original.available_ts + (1 if case == "delay" else 0),
        )
        message = {
            "bool_clock": "must be an integer",
            "delay": "available_ts must equal",
            "wrong_close": "close_ts must equal",
            "misaligned_clock": "must align",
        }[case]
    elif case == "missing_join":
        del inputs["rows"][1]
        message = "exactly matching"
    elif case == "extra_join":
        inputs["rows"].append(dict(inputs["rows"][0], ts=T - D))
        message = "exactly matching"
    elif case == "duplicate_row":
        inputs["rows"].append(dict(inputs["rows"][1]))
        message = "duplicates an earlier row"
    elif case == "duplicate_clock":
        clocks.append(clocks[1])
        message = "duplicates an earlier clock"
    elif case == "bool_row":
        inputs["rows"][1]["ts"] = False
        message = "rows.*ts must be an integer"
    elif case in ("negative_engine_open", "wide_engine_close"):
        shift = -T - D if case == "negative_engine_open" else (2**64 // NS // D + 1) * D
        inputs["anchor_ts"] += shift
        inputs["active"] = ResearchInterval(T + 2 * D + shift, T + 4 * D + shift)
        inputs["warmup"] = ResearchInterval(T + D + shift, T + 2 * D + shift)
        clocks = [
            BarClock(c.open_ts + shift, c.close_ts + shift, c.available_ts + shift)
            for c in clocks
        ]
        for row in inputs["rows"]:
            row["ts"] += shift
        message = "unsigned 64-bit"
    else:
        name, value, message = {
            "bad_ohlcv": ("close", float("nan"), "must be a finite int or float"),
            "bool_ohlcv": ("open", True, "must be a finite int or float"),
            "decimal_ohlcv": ("close", Decimal("100"), "must be a finite int or float"),
            "negative_volume": ("volume", -1, "must be nonnegative"),
            "bad_bounds": ("high", 99, "consistent OHLC bounds"),
            "price_precision": ("close", 100.001, "2 decimal places"),
            "volume_precision": ("volume", 0.0000001, "6 decimal places"),
        }[case]
        inputs["rows"][1][name] = value
    inputs["clocks"] = tuple(clocks)
    _reject_before_engine(monkeypatch, caplog, inputs, message)


@pytest.mark.parametrize(
    ("method", "at", "failure_kind"),
    [
        ("positions_open", 1, "nonempty"),
        ("positions_open", 3, "nonempty"),
        ("orders_open", 1, "nonempty"),
        ("orders_inflight", 2, "nonempty"),
        ("positions_open", 1, "query_error"),
        ("orders_open", 2, "query_error"),
    ],
)
def test_live_clean_state_failure_aborts_without_submission(
    monkeypatch: pytest.MonkeyPatch,
    method: str,
    at: int,
    failure_kind: str,
) -> None:
    watches = _watch(monkeypatch)
    real_init = _EngineWatch.__init__
    error = RuntimeError("injected actual query failure")

    def init(self: _EngineWatch, real: Any) -> None:
        real_init(self, real)
        self.cache_override = _CacheFault(
            real.cache,
            method,
            at,
            error if failure_kind == "query_error" else [object()],
        )

    monkeypatch.setattr(_EngineWatch, "__init__", init)
    submitted: list[int] = []
    original = BuyHold._submit_entry

    def submit(self: BuyHold, bar: Any, venue: Any) -> None:
        submitted.append(bar.ts_event)
        original(self, bar, venue)

    monkeypatch.setattr(BuyHold, "_submit_entry", submit)
    with pytest.raises(RuntimeError) as exc:
        module.run_research_buy_hold(**_inputs(warmup=True))
    if failure_kind == "query_error":
        assert exc.value is error
    else:
        assert "without positions or open/inflight orders" in str(exc.value)
    (watch,) = watches
    assert watch.strategy.callback_error is exc.value
    assert submitted == []
    assert watch.strategy.equity_snapshots == []
    assert watch.disposed
    assert watch.extractions == 0


def test_actual_fill_with_outside_clock_aborts(monkeypatch: pytest.MonkeyPatch) -> None:
    watches = _watch(monkeypatch)
    original = module._ResearchBuyHold.on_order_filled
    actual: list[int] = []

    def fill(self: Any, event: Any) -> None:
        actual.append(event.ts_event)
        original(self, SimpleNamespace(ts_event=(T + 4 * D) * NS))

    monkeypatch.setattr(module._ResearchBuyHold, "on_order_filled", fill)
    with pytest.raises(RuntimeError, match="fill ts_event must be inside") as exc:
        module.run_research_buy_hold(**_inputs())
    assert actual == [(T + 2 * D) * NS]
    (watch,) = watches
    assert watch.strategy.callback_error is exc.value
    assert watch.disposed and watch.extractions == 0


@pytest.mark.parametrize("callback", ["on_start", "on_bar", "on_order_filled"])
def test_retained_inherited_failure_prevents_swallowed_success(
    monkeypatch: pytest.MonkeyPatch,
    callback: str,
) -> None:
    watches = _watch(monkeypatch)
    error = RuntimeError(f"inherited {callback} failed")
    original = getattr(BuyHold, callback)
    calls: list[str] = []

    def fail(self: Any, *args: Any) -> None:
        original(self, *args)
        calls.append(callback)
        raise error

    monkeypatch.setattr(BuyHold, callback, fail)
    real_init = _EngineWatch.__init__

    def init(self: _EngineWatch, real: Any) -> None:
        real_init(self, real)
        self.swallow = True

    monkeypatch.setattr(_EngineWatch, "__init__", init)
    with pytest.raises(RuntimeError) as exc:
        module.run_research_buy_hold(**_inputs(warmup=True))
    assert exc.value is error
    (watch,) = watches
    assert calls == [callback]
    assert watch.strategy.callback_error is error
    assert watch.disposed and watch.extractions == 0
    # Later callbacks cannot act or replace the first failure.
    snapshots = list(watch.strategy.equity_snapshots)
    with pytest.raises(RuntimeError) as later:
        watch.strategy.on_bar(watch.bars[-1])
    assert later.value is error
    assert watch.strategy.equity_snapshots == snapshots


@pytest.mark.parametrize("method", ["orders_open", "orders_inflight"])
def test_actual_terminal_order_query_rejects_pending_orders(
    monkeypatch: pytest.MonkeyPatch,
    method: str,
) -> None:
    watches = _watch(monkeypatch)
    real_init = _EngineWatch.__init__

    def init(self: _EngineWatch, real: Any) -> None:
        real_init(self, real)
        self.cache_override = _CacheFault(real.cache, method, 3, [object()])

    monkeypatch.setattr(_EngineWatch, "__init__", init)
    with pytest.raises(RuntimeError, match="terminal open/inflight orders"):
        module.run_research_buy_hold(**_inputs())
    (watch,) = watches
    assert watch.strategy._entered
    assert watch.disposed and watch.extractions == 0


def test_missing_actual_account_currency_fails_loudly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    watches = _watch(monkeypatch)
    trader_property = _EngineWatch.trader

    def trader(self: _EngineWatch) -> Any:
        real_trader = trader_property.fget(self)

        def account(venue: Any) -> Any:
            frame = real_trader.generate_account_report(venue)
            return frame[frame["currency"] != "BTC"]

        return SimpleNamespace(generate_account_report=account)

    monkeypatch.setattr(_EngineWatch, "trader", property(trader))
    with pytest.raises(RuntimeError, match="latest USDT and BTC valuation rows"):
        module.run_research_buy_hold(**_inputs())
    assert watches[0].disposed
