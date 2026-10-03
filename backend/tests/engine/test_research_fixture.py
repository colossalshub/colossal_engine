from __future__ import annotations

import copy
import hashlib
import json
import logging
from dataclasses import asdict
from typing import Any

import pytest

from quant.engine.bar_coverage import BarClock
from quant.engine.research_fixture import (
    bind_controlled_fixture,
    create_controlled_fixture,
)
from quant.engine.research_input import create_research_input_snapshot
from quant.engine.research_runner import run_research_buy_hold
from quant.engine.temporal import ResearchInterval

D = 86_400_000
RID = "sha256:9ef687c70741b00dba743e2dbc8de911cd26b70392d837e5a21c224ca1b04c44"
SID = "sha256:468fd3da9955a653d0398d67c561f534bd36c6109322a707a730f86bd4e7739d"
MISMATCH = "document does not match the reproduced controlled fixture"


def recipe() -> dict[str, Any]:
    return dict(
        recipe_version="controlled-daily-linear-v1",
        rule_id="phase18-temporal-v1",
        anchor_ts=12345,
        start_open_ts=12345,
        observation_count=3,
        price_start=100,
        price_step=20,
        volume=1000,
    )


def wire() -> dict[str, Any]:
    # Independently hardcoded recipe result, without any production helper.
    return dict(
        contract_version="research-input-v1",
        rule_id="phase18-temporal-v1",
        venue="binance",
        symbol="BTC/USDT",
        timeframe="1d",
        calendar="continuous_utc_fixed",
        anchor_ts=12345,
        observations=[
            dict(
                ts=ts,
                close_ts=close,
                available_ts=close,
                open=price,
                high=price,
                low=price,
                close=price,
                volume=1000,
                source_id="controlled-fixture:controlled-daily-linear-v1",
                revision_id=RID,
                provenance=dict(
                    kind="controlled_fixture", reference=RID, declared_by=None
                ),
            )
            for ts, close, price in (
                (12345, 86412345, 100),
                (86412345, 172812345, 120),
                (172812345, 259212345, 140),
            )
        ],
    )


def typed(value: Any) -> Any:
    if isinstance(value, int):
        return {"kind": "int", "value": hex(value)}
    if isinstance(value, dict):
        return {key: typed(item) for key, item in value.items()}
    if isinstance(value, list):
        return [typed(item) for item in value]
    return value


def canonical(value: Any) -> bytes:
    return json.dumps(
        typed(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def assert_error(
    caplog: pytest.LogCaptureFixture, message: str, name: str, call: Any
) -> None:
    caplog.clear()
    with caplog.at_level(logging.ERROR), pytest.raises(ValueError) as error:
        call()
    assert str(error.value) == message
    assert [(r.name, r.levelno, r.getMessage()) for r in caplog.records] == [
        (name, logging.ERROR, message)
    ]


def test_hardcoded_rows_and_independent_complete_identities(
    caplog: pytest.LogCaptureFixture,
) -> None:
    assert "sha256:" + hashlib.sha256(canonical(recipe())).hexdigest() == RID
    expected = wire()
    snapshot = create_controlled_fixture(recipe())
    assert snapshot.snapshot_id == SID
    assert snapshot.canonical_bytes == canonical(expected)
    assert "sha256:" + hashlib.sha256(canonical(expected)).hexdigest() == SID
    assert [asdict(row) for row in snapshot.observations] == expected["observations"]
    assert all(row.available_ts == row.close_ts for row in snapshot.observations)
    assert not hasattr(snapshot, "eligible")
    assert not hasattr(snapshot, "source_verified")
    assert create_controlled_fixture(dict(reversed(list(recipe().items())))) == snapshot
    assert create_controlled_fixture(recipe()) == snapshot
    assert not caplog.records


def test_bind_returns_fresh_detached_reproduction() -> None:
    raw = wire()
    r = recipe()
    supplied = create_research_input_snapshot(raw)
    bound = bind_controlled_fixture(recipe=r, document=raw)
    assert bound == supplied
    assert bound is not supplied
    assert bound.observations[0] is not supplied.observations[0]
    raw["observations"][0]["provenance"]["reference"] = "mutated"
    raw["observations"].clear()
    r["price_start"] = 999
    assert bound.snapshot_id == SID
    assert bound.observations[0].provenance.reference == RID
    assert bound.observations[0].close == 100


@pytest.mark.parametrize("step,prices", [(0, [100, 100, 100]), (-20, [100, 80, 60])])
def test_signed_steps(step: int, prices: list[int]) -> None:
    r = recipe()
    r["price_step"] = step
    assert [row.close for row in create_controlled_fixture(r).observations] == prices


def test_shifted_and_unbounded_integer_recipe() -> None:
    huge = 10**5000
    r = recipe()
    r.update(
        anchor_ts=-huge,
        start_open_ts=-huge + D,
        price_start=huge,
        price_step=-1,
        volume=huge,
    )
    result = create_controlled_fixture(r)
    assert result.anchor_ts == -huge
    assert result.observations[0].ts == -huge + D
    assert result.observations[-1].close == huge - 2
    assert result.observations[-1].available_ts == -huge + 4 * D
    assert result.observations[-1].volume == huge
    assert hex(huge).encode() in result.canonical_bytes


@pytest.mark.parametrize(
    "field,value,message",
    [
        (
            "recipe_version",
            "opaque",
            "recipe_version must be controlled-daily-linear-v1",
        ),
        ("rule_id", "opaque", "rule_id must be phase18-temporal-v1"),
        ("anchor_ts", True, "anchor_ts must be an integer excluding bool"),
        ("start_open_ts", 12345.0, "start_open_ts must be an integer excluding bool"),
        ("observation_count", 0, "observation_count must be positive"),
        ("price_start", 0, "price_start must be positive"),
        ("price_step", None, "price_step must be an integer excluding bool"),
        ("volume", -1, "volume must be nonnegative"),
        (
            "start_open_ts",
            12346,
            "start_open_ts must align with the declared daily grid",
        ),
        ("price_step", -50, "generated prices must all be positive"),
    ],
)
def test_recipe_failures(
    caplog: pytest.LogCaptureFixture, field: str, value: object, message: str
) -> None:
    r = recipe()
    r[field] = value
    assert_error(
        caplog,
        message,
        "quant.engine.research_fixture",
        lambda: create_controlled_fixture(r),
    )


@pytest.mark.parametrize("extra", [False, True])
def test_exact_recipe_keys(caplog: pytest.LogCaptureFixture, extra: bool) -> None:
    r = recipe()
    if extra:
        r["eligible"] = True
    else:
        del r["volume"]
    assert_error(
        caplog,
        "recipe must contain exactly the declared fields",
        "quant.engine.research_fixture",
        lambda: create_controlled_fixture(r),
    )


def test_error_precedence_and_recipe_before_document(
    caplog: pytest.LogCaptureFixture,
) -> None:
    r = recipe()
    r.update(observation_count=-1, price_start=0, volume=False)
    assert_error(
        caplog,
        "volume must be an integer excluding bool",
        "quant.engine.research_fixture",
        lambda: bind_controlled_fixture(recipe=r, document={}),
    )
    r["volume"] = -1
    assert_error(
        caplog,
        "observation_count must be positive",
        "quant.engine.research_fixture",
        lambda: create_controlled_fixture(r),
    )
    r["recipe_version"] = "secret-payload"
    r["rule_id"] = "bad"
    assert_error(
        caplog,
        "recipe_version must be controlled-daily-linear-v1",
        "quant.engine.research_fixture",
        lambda: create_controlled_fixture(r),
    )


@pytest.mark.parametrize(
    "change",
    [
        "price",
        "source",
        "revision",
        "reference",
        "delay",
        "anchor",
        "rowcount",
        "numeric_kind",
    ],
)
def test_valid_tampering_and_recomputed_hash_cannot_bind(
    caplog: pytest.LogCaptureFixture,
    change: str,
) -> None:
    raw = wire()
    row = raw["observations"][0]
    if change == "price":
        row.update(open=101, high=101, low=101, close=101)
    elif change == "source":
        row["source_id"] = "historical-source"
    elif change == "revision":
        row["revision_id"] = "sha256:opaque"
    elif change == "reference":
        row["provenance"]["reference"] = "sha256:opaque"
    elif change == "delay":
        row["available_ts"] += 1
    elif change == "anchor":
        raw["anchor_ts"] += D
    elif change == "rowcount":
        raw["observations"].pop()
    else:
        row["volume"] = 1000.0
    forged = create_research_input_snapshot(raw)  # labels and recomputed identity valid
    assert forged.snapshot_id != SID
    assert_error(
        caplog,
        MISMATCH,
        "quant.engine.research_fixture",
        lambda: bind_controlled_fixture(recipe=recipe(), document=raw),
    )


@pytest.mark.parametrize(
    "change,message",
    [
        ("missing", "observations[0] must contain exactly the declared fields"),
        ("extra", "observations[0] must contain exactly the declared fields"),
        ("duplicate", "observations[1].ts duplicates an earlier observation"),
        ("order", "observations must be strictly chronological"),
    ],
)
def test_factory_failures_are_not_relogged(
    caplog: pytest.LogCaptureFixture,
    change: str,
    message: str,
) -> None:
    raw = wire()
    if change == "missing":
        del raw["observations"][0]["volume"]
    elif change == "extra":
        raw["observations"][0]["eligible"] = True
    elif change == "duplicate":
        raw["observations"][1] = copy.deepcopy(raw["observations"][0])
    else:
        raw["observations"].reverse()
    assert_error(
        caplog,
        message,
        "quant.engine.research_input",
        lambda: bind_controlled_fixture(recipe=recipe(), document=raw),
    )


def test_bound_fixture_actual_runner_fill_fee_and_last_eligible_valuation() -> None:
    fixture = bind_controlled_fixture(recipe=recipe(), document=wire())
    rows = [
        {
            name: getattr(row, name)
            for name in ("ts", "open", "high", "low", "close", "volume")
        }
        for row in fixture.observations
    ]
    clocks = tuple(
        BarClock(row.ts, row.close_ts, row.available_ts) for row in fixture.observations
    )
    result = run_research_buy_hold(
        active=ResearchInterval(12345 + D, 12345 + 3 * D),
        warmup=None,
        required_warmup_observations=0,
        timeframe=fixture.timeframe,
        calendar=fixture.calendar,
        anchor_ts=fixture.anchor_ts,
        clocks=clocks,
        rows=rows,
        starting_balance_usdt=100000.0,
        trade_size="1",
        deploy_pct="0",
        maker_fee="0.001",
        taker_fee="0.001",
    )
    (fill,) = result.fills_report
    assert fill["ts_event"].value == (12345 + D) * 1_000_000
    assert float(fill["last_px"]) == 100
    assert float(str(fill["commission"]).split()[0]) == pytest.approx(0.1)
    assert result.independent_ending_balance == pytest.approx(100019.9)
    assert result.ending_balance == pytest.approx(100019.9)
    assert [ts for ts, _ in result.portfolio_returns] == [12345 + D, 12345 + 2 * D]
