"""Actual SQLite durability, replay, ordering and contender regressions."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from pathlib import Path
from threading import Barrier
from typing import cast

import pytest

from quant.data import research_store as store
from quant.engine.research_fixture import create_controlled_fixture

DAY = 86_400_000


def canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode()


def wire(recipe: dict[str, object]) -> dict[str, object]:
    """Independent raw recipe expansion with separately constructed provenance."""
    typed = {
        key: {"kind": "int", "value": hex(value)} if isinstance(value, int) else value
        for key, value in recipe.items()
    }
    revision = "sha256:" + hashlib.sha256(canonical(typed)).hexdigest()
    rows = []
    for index in range(cast(int, recipe["observation_count"])):
        ts = cast(int, recipe["start_open_ts"]) + index * DAY
        price = cast(int, recipe["price_start"]) + index * cast(
            int, recipe["price_step"]
        )
        rows.append(
            {
                "ts": ts,
                "close_ts": ts + DAY,
                "available_ts": ts + DAY,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": recipe["volume"],
                "source_id": "controlled-fixture:controlled-daily-linear-v1",
                "revision_id": revision,
                "provenance": {
                    "kind": "controlled_fixture",
                    "reference": revision,
                    "declared_by": None,
                },
            }
        )
    return {
        "contract_version": "research-input-v1",
        "rule_id": "phase18-temporal-v1",
        "venue": "binance",
        "symbol": "BTC/USDT",
        "timeframe": "1d",
        "calendar": "continuous_utc_fixed",
        "anchor_ts": recipe["anchor_ts"],
        "observations": rows,
    }


@pytest.fixture
def recipe() -> dict[str, object]:
    return {
        "recipe_version": "controlled-daily-linear-v1",
        "rule_id": "phase18-temporal-v1",
        "anchor_ts": 0,
        "start_open_ts": 0,
        "observation_count": 4,
        "price_start": 100,
        "price_step": 10,
        "volume": 2,
    }


@pytest.fixture
def db(tmp_path: Path) -> Path:
    return tmp_path / "nested" / "metadata.sqlite"


def capture(db: Path, recipe: dict[str, object]) -> store.StoredResearchEvent:
    return store.capture_fixture_input(db, recipe=recipe, document=wire(recipe))


def candidate(input_id: str) -> dict[str, object]:
    return {
        "contract_version": "research-candidate-v1",
        "rule_id": "phase18-temporal-v1",
        "experiment_id": "experiment",
        "hypothesis_id": "hypothesis",
        "candidate_revision": "r1",
        "parent_candidate_id": None,
        "strategy_version": "v1",
        "strategy": "buy_hold",
        "parameters": {
            "starting_balance_usdt": 100000.0,
            "trade_size": "1.0000000",
            "deploy_pct": "0",
            "maker_fee": "0.001",
            "taker_fee": "0.001",
        },
        "code_id": "a" * 40,
        "seed": None,
        "fitted_artifacts": (),
        "in_sample_input_id": input_id,
        "in_sample_start_ts": DAY,
        "in_sample_end_ts": 3 * DAY,
        "trial_index": 1,
        "trial_count": 3,
    }


def count(db: Path) -> int:
    with sqlite3.connect(db) as connection:
        return cast(
            int,
            connection.execute("SELECT count(*) FROM research_events_v1").fetchone()[0],
        )


def test_roundtrip_exact_identity_durable_and_idempotent(
    db: Path, recipe: dict[str, object]
) -> None:
    event = capture(db, recipe)
    expected_input = canonical(
        {
            "contract_version": "research-store-input-v1",
            "recipe": {
                key: {"kind": "int", "value": hex(value)}
                if isinstance(value, int)
                else value
                for key, value in recipe.items()
            },
            "snapshot": json.loads(create_controlled_fixture(recipe).canonical_bytes),
        }
    )
    assert event.canonical_bytes == expected_input
    assert event.event_id == "sha256:" + hashlib.sha256(expected_input).hexdigest()
    document = candidate(event.event_id)
    frozen = store.freeze_research_candidate(db, document=document)
    expected = {**document, "fitted_artifacts": []}
    for field in (
        "in_sample_start_ts",
        "in_sample_end_ts",
        "trial_index",
        "trial_count",
    ):
        expected[field] = {"kind": "int", "value": hex(cast(int, document[field]))}
    params = cast(dict[str, object], document["parameters"]).copy()
    params["starting_balance_usdt"] = {"kind": "float", "value": (100000.0).hex()}
    expected["parameters"] = params
    assert frozen.canonical_bytes == canonical(expected)
    assert (
        frozen.event_id == "sha256:" + hashlib.sha256(canonical(expected)).hexdigest()
    )
    assert event.seq == 1 and frozen.seq == 2
    store.init_research_schema(db)
    assert store._read_research_event(db, event_id=frozen.event_id) == frozen
    assert capture(db, recipe) == event
    assert store.freeze_research_candidate(db, document=document) == frozen
    assert count(db) == 2
    assert not hasattr(frozen, "eligible")
    with pytest.raises(FrozenInstanceError):
        frozen.__setattr__("seq", 10)
    assert store._read_research_event(db, event_id="missing") is None


@pytest.mark.parametrize("field", ["code_id", "parameters", "in_sample_input_id"])
def test_changed_content_same_revision_rejects_new_revision_preserved(
    db: Path,
    recipe: dict[str, object],
    field: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    source = capture(db, recipe)
    original = store.freeze_research_candidate(db, document=candidate(source.event_id))
    revised = candidate(source.event_id)
    if field == "code_id":
        revised[field] = "b" * 40
    elif field == "parameters":
        revised[field] = {**cast(dict[str, object], revised[field]), "trade_size": "2"}
    else:
        revised[field] = capture(db, {**recipe, "price_start": 200}).event_id
    caplog.clear()
    with pytest.raises(
        ValueError, match="^candidate revision already has different frozen content$"
    ):
        store.freeze_research_candidate(db, document=revised)
    assert [(record.name, record.message) for record in caplog.records] == [
        (
            "quant.data.research_store",
            "candidate revision already has different frozen content",
        )
    ]
    revised["candidate_revision"] = "r2"
    revised["parent_candidate_id"] = original.event_id
    second = store.freeze_research_candidate(db, document=revised)
    assert second.event_id != original.event_id
    assert store._read_research_event(db, event_id=original.event_id) == original
    assert store._read_research_event(db, event_id=second.event_id) == second


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"trial_index": True}, "trial_index must be an integer excluding bool"),
        ({"trial_count": 0}, "trial_count must be positive"),
        ({"trial_index": 4}, "trial_index must be between one and trial_count"),
        (
            {"seed": 1},
            "seed and fitted_artifacts must be explicitly absent for buy_hold",
        ),
        (
            {"fitted_artifacts": ["model"]},
            "seed and fitted_artifacts must be explicitly absent for buy_hold",
        ),
        (
            {"in_sample_start_ts": DAY + 1},
            "in_sample_start_ts must align with the declared daily grid",
        ),
        (
            {"in_sample_end_ts": 7 * DAY},
            "observations do not provide complete expected bar coverage",
        ),
        (
            {"in_sample_start_ts": 6 * DAY, "in_sample_end_ts": 7 * DAY},
            "observations must contain at least one stage observation",
        ),
        ({"in_sample_input_id": "missing"}, "candidate input event does not exist"),
        ({"parent_candidate_id": "missing"}, "parent candidate event does not exist"),
    ],
)
def test_candidate_rejection_has_no_insert(
    db: Path,
    recipe: dict[str, object],
    changes: dict[str, object],
    message: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    source = capture(db, recipe)
    caplog.clear()
    with pytest.raises(ValueError) as error:
        store.freeze_research_candidate(
            db, document={**candidate(source.event_id), **changes}
        )
    assert str(error.value) == message
    assert len(caplog.records) == 1 and caplog.records[0].message == message
    assert count(db) == 1


def test_parent_group_and_wrong_kinds(db: Path, recipe: dict[str, object]) -> None:
    source = capture(db, recipe)
    parent = store.freeze_research_candidate(db, document=candidate(source.event_id))
    data = {
        **candidate(source.event_id),
        "candidate_revision": "r2",
        "parent_candidate_id": parent.event_id,
        "hypothesis_id": "other",
    }
    with pytest.raises(
        ValueError, match="parent candidate does not match experiment and hypothesis"
    ):
        store.freeze_research_candidate(db, document=data)
    data["parent_candidate_id"] = source.event_id
    with pytest.raises(ValueError, match="parent candidate event does not exist"):
        store.freeze_research_candidate(db, document=data)
    data["in_sample_input_id"] = parent.event_id
    with pytest.raises(ValueError, match="candidate input event does not exist"):
        store.freeze_research_candidate(db, document=data)
    assert count(db) == 2


@pytest.mark.parametrize(
    "size", ["1", "1.0", "1.000000000000000000000", "1.234567000", "10e-7"]
)
def test_runner_equivalent_decimal_precision(
    db: Path, recipe: dict[str, object], size: str
) -> None:
    data = candidate(capture(db, recipe).event_id)
    cast(dict[str, object], data["parameters"])["trade_size"] = size
    frozen = store.freeze_research_candidate(db, document=data)
    assert json.loads(frozen.canonical_bytes)["parameters"]["trade_size"] == size
    assert store._read_research_event(db, event_id=frozen.event_id) == frozen


def test_validation_precedence_and_precision(
    db: Path, recipe: dict[str, object]
) -> None:
    data = candidate(capture(db, recipe).event_id)
    data.update(contract_version="wrong", rule_id="wrong", seed=1)
    with pytest.raises(
        ValueError, match="contract_version must be research-candidate-v1"
    ):
        store.freeze_research_candidate(db, document=data)
    data = candidate(capture(db, recipe).event_id)
    params = cast(dict[str, object], data["parameters"])
    params.update(trade_size="0.0000001", maker_fee=-1)
    with pytest.raises(
        ValueError, match="positive and exactly representable at 6 decimal places"
    ):
        store.freeze_research_candidate(db, document=data)
    params.update(trade_size="1", maker_fee=0)
    with pytest.raises(
        ValueError, match="parameters.maker_fee must be a finite decimal string"
    ):
        store.freeze_research_candidate(db, document=data)
    assert count(db) == 1


def test_huge_hex_and_tampered_source_binder(
    db: Path, recipe: dict[str, object], caplog: pytest.LogCaptureFixture
) -> None:
    huge = 1 << 16000
    recipe.update(anchor_ts=-huge, start_open_ts=-huge, price_start=huge, volume=huge)
    event = capture(db, recipe)
    assert store._read_research_event(db, event_id=event.event_id) == event
    assert json.loads(event.canonical_bytes)["recipe"]["anchor_ts"]["value"] == hex(
        -huge
    )
    document = wire(recipe)
    rows = cast(list[dict[str, object]], document["observations"])
    rows[0]["volume"] = huge + 1
    caplog.clear()
    with pytest.raises(
        ValueError, match="document does not match the reproduced controlled fixture"
    ):
        store.capture_fixture_input(db, recipe=recipe, document=document)
    assert len(caplog.records) == 1
    assert caplog.records[0].name == "quant.engine.research_fixture"
    assert count(db) == 1


def test_close_float_kind_cannot_collide(db: Path, recipe: dict[str, object]) -> None:
    document = wire(recipe)
    row = cast(list[dict[str, object]], document["observations"])[0]
    row["close"] = 100.000000001
    row["high"] = 100.000000001
    with pytest.raises(
        ValueError, match="document does not match the reproduced controlled fixture"
    ):
        store.capture_fixture_input(db, recipe=recipe, document=document)
    assert capture(db, recipe).seq == 1


def test_triggers_block_update_delete(db: Path, recipe: dict[str, object]) -> None:
    capture(db, recipe)
    with sqlite3.connect(db) as connection:
        for sql in (
            "UPDATE research_events_v1 SET recorded_at_ts=0",
            "DELETE FROM research_events_v1",
        ):
            with pytest.raises(
                sqlite3.IntegrityError, match="research events are append-only"
            ):
                connection.execute(sql)
    assert count(db) == 1


def corrupt(
    db: Path,
    event_id: str,
    *,
    payload: bytes | None = None,
    assignment: str | None = None,
) -> str:
    """Simulate a direct SQLite owner bypassing append-only application triggers."""
    with sqlite3.connect(db) as connection:
        connection.execute("DROP TRIGGER research_no_update")
        if payload is not None:
            new_id = "sha256:" + hashlib.sha256(payload).hexdigest()
            connection.execute(
                "UPDATE research_events_v1 SET event_id=?,payload=? WHERE event_id=?",
                (new_id, payload, event_id),
            )
            return new_id
        assert assignment is not None
        connection.execute(
            f"UPDATE research_events_v1 SET {assignment} WHERE event_id=?", (event_id,)
        )
    return event_id


@pytest.mark.parametrize(
    "change",
    [
        "digest",
        "kind",
        "input_index",
        "candidate_index",
        "whitespace",
        "duplicate",
        "hex",
        "tag",
    ],
)
def test_corruption_integrity_replay(
    db: Path, recipe: dict[str, object], change: str, caplog: pytest.LogCaptureFixture
) -> None:
    source = capture(db, recipe)
    frozen = store.freeze_research_candidate(db, document=candidate(source.event_id))
    event = frozen if change == "candidate_index" else source
    if change == "digest":
        identity = corrupt(db, event.event_id, assignment="payload=X'7B7D'")
    elif change == "kind":
        identity = corrupt(db, event.event_id, assignment="kind='candidate'")
    elif change in ("input_index", "candidate_index"):
        identity = corrupt(db, event.event_id, assignment="experiment_id='tampered'")
    else:
        payload = event.canonical_bytes
        if change == "whitespace":
            payload += b"\n"
        elif change == "duplicate":
            payload = b'{"contract_version":"research-store-input-v1",' + payload[1:]
        elif change == "hex":
            payload = payload.replace(b'"0x0"', b'"0X0"')
        else:
            payload = payload.replace(b'"kind":"int"', b'"kind":"unknown"', 1)
        identity = corrupt(db, event.event_id, payload=payload)
    caplog.clear()
    with pytest.raises(
        ValueError, match="^stored research event failed integrity validation$"
    ):
        store._read_research_event(db, event_id=identity)
    assert len(caplog.records) == 1
    assert count(db) == 2


def test_valid_encoding_binder_failure_propagates_once(
    db: Path, recipe: dict[str, object], caplog: pytest.LogCaptureFixture
) -> None:
    source = capture(db, recipe)
    payload = json.loads(source.canonical_bytes)
    payload["snapshot"]["observations"][0]["volume"]["value"] = "0x3"
    identity = corrupt(db, source.event_id, payload=canonical(payload))
    caplog.clear()
    with pytest.raises(
        ValueError, match="document does not match the reproduced controlled fixture"
    ):
        store._read_research_event(db, event_id=identity)
    assert [(record.name, record.message) for record in caplog.records] == [
        (
            "quant.engine.research_fixture",
            "document does not match the reproduced controlled fixture",
        )
    ]


def test_server_seq_and_original_timestamp(
    db: Path, recipe: dict[str, object], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(store.time, "time_ns", lambda: 900_000_000)
    source = capture(db, recipe)
    monkeypatch.setattr(store.time, "time_ns", lambda: 100_000_000)
    frozen = store.freeze_research_candidate(db, document=candidate(source.event_id))
    assert frozen.seq > source.seq and frozen.recorded_at_ts < source.recorded_at_ts
    assert capture(db, recipe) == source
    assert (
        store.freeze_research_candidate(db, document=candidate(source.event_id))
        == frozen
    )


@pytest.mark.parametrize("conflict", [False, True])
def test_concurrent_contenders(
    db: Path, recipe: dict[str, object], conflict: bool
) -> None:
    source = capture(db, recipe)
    barrier = Barrier(2)

    def contend(code: str) -> store.StoredResearchEvent | str:
        data = {**candidate(source.event_id), "code_id": code}
        barrier.wait()
        try:
            return store.freeze_research_candidate(db, document=data)
        except ValueError as error:
            return str(error)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(contend, "a" * 40),
            pool.submit(contend, ("b" if conflict else "a") * 40),
        ]
        results = [future.result() for future in futures]
    if conflict:
        assert (
            sum(isinstance(result, store.StoredResearchEvent) for result in results)
            == 1
        )
        assert "candidate revision already has different frozen content" in results
    else:
        assert results[0] == results[1]
    assert count(db) == 2


def test_sqlite_failure_rolls_back_and_surfaces(
    db: Path, recipe: dict[str, object], caplog: pytest.LogCaptureFixture
) -> None:
    source = capture(db, recipe)
    with sqlite3.connect(db) as connection:
        connection.execute("""CREATE TRIGGER fail_candidate
            BEFORE INSERT ON research_events_v1
            WHEN NEW.kind='candidate' BEGIN
            SELECT RAISE(ABORT,'injected insert failure'); END""")
    caplog.clear()
    with pytest.raises(sqlite3.IntegrityError, match="injected insert failure"):
        store.freeze_research_candidate(db, document=candidate(source.event_id))
    assert not caplog.records
    assert count(db) == 1
    with sqlite3.connect(db) as connection:
        connection.execute("DROP TRIGGER fail_candidate")
    assert (
        store.freeze_research_candidate(db, document=candidate(source.event_id)).seq
        == 2
    )


@pytest.mark.parametrize("raw", [b"NaN", b"Infinity", b"1.0", b"1" * 5000])
def test_bare_json_numbers_are_redacted_integrity_failures(
    db: Path,
    recipe: dict[str, object],
    caplog: pytest.LogCaptureFixture,
    raw: bytes,
) -> None:
    source = capture(db, recipe)
    payload = source.canonical_bytes.replace(
        b'"anchor_ts":{"kind":"int","value":"0x0"}', b'"anchor_ts":' + raw, 1
    )
    identity = corrupt(db, source.event_id, payload=payload)
    caplog.clear()
    with pytest.raises(
        ValueError, match="^stored research event failed integrity validation$"
    ):
        store._read_research_event(db, event_id=identity)
    assert len(caplog.records) == 1
    assert (
        caplog.records[0].message == "stored research event failed integrity validation"
    )


def test_commit_failure_rolls_back_original_exception(
    db: Path,
    recipe: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    source = capture(db, recipe)
    original_connect = sqlite3.connect
    failure = sqlite3.OperationalError("injected commit failure")

    class FailCommit(sqlite3.Connection):
        def commit(self) -> None:
            raise failure

    def connect(path: Path, *, isolation_level: None) -> sqlite3.Connection:
        return original_connect(
            path, isolation_level=isolation_level, factory=FailCommit
        )

    monkeypatch.setattr(store.sqlite3, "connect", connect)
    caplog.clear()
    with pytest.raises(sqlite3.OperationalError) as error:
        store.freeze_research_candidate(db, document=candidate(source.event_id))
    assert error.value is failure
    assert not caplog.records
    monkeypatch.setattr(store.sqlite3, "connect", original_connect)
    assert count(db) == 1
    assert (
        store.freeze_research_candidate(db, document=candidate(source.event_id)).seq
        == 2
    )


def test_failed_reference_revalidation_rolls_back(
    db: Path,
    recipe: dict[str, object],
    caplog: pytest.LogCaptureFixture,
) -> None:
    source = capture(db, recipe)
    payload = json.loads(source.canonical_bytes)
    payload["snapshot"]["observations"][0]["volume"]["value"] = "0x3"
    identity = corrupt(db, source.event_id, payload=canonical(payload))
    caplog.clear()
    with pytest.raises(
        ValueError, match="document does not match the reproduced controlled fixture"
    ):
        store.freeze_research_candidate(db, document=candidate(identity))
    assert count(db) == 1
    assert len(caplog.records) == 1


def test_replay_requires_earlier_committed_parent(
    db: Path, recipe: dict[str, object]
) -> None:
    source = capture(db, recipe)
    parent = store.freeze_research_candidate(db, document=candidate(source.event_id))
    child = store.freeze_research_candidate(
        db,
        document={
            **candidate(source.event_id),
            "candidate_revision": "r2",
            "parent_candidate_id": parent.event_id,
        },
    )
    corrupt(db, parent.event_id, assignment="seq=100")
    with pytest.raises(
        ValueError, match="^stored research event failed integrity validation$"
    ):
        store._read_research_event(db, event_id=child.event_id)


def test_read_initializes_missing_schema(db: Path) -> None:
    assert store._read_research_event(db, event_id="missing") is None
    assert count(db) == 0
