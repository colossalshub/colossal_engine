"""Append-only synthetic source and immutable BuyHold candidate capture.

Identity uses sorted compact UTF-8 JSON and exact typed hexadecimal numbers.
Server sequence records application commit order; wall time may go backwards.
Code/source identities are assertions, not authentication. Direct record
construction is unvalidated. This is internal persistence replay: no public raw
observation read path is integrated. Capture records must not become unlogged
API dumps. Future external access requires the transactional inspection gateway.
Frozen capture does not authorize selection, validation or OOS access, certify
an unseen holdout, outside inspection, historical data or research eligibility.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import re
import sqlite3
import time
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Literal, NoReturn, cast

from quant.engine.bar_coverage import validate_bar_coverage
from quant.engine.research_fixture import bind_controlled_fixture
from quant.engine.research_input import ResearchInputSnapshot
from quant.engine.temporal import ResearchInterval

logger = logging.getLogger(__name__)
_DAY = 86_400_000
_INTS = ("in_sample_start_ts", "in_sample_end_ts", "trial_index", "trial_count")
_RECIPE_INTS = (
    "anchor_ts",
    "start_open_ts",
    "observation_count",
    "price_start",
    "price_step",
    "volume",
)
_INDEX = ("experiment_id", "hypothesis_id", "candidate_revision")
_FIELDS = frozenset(
    (
        "contract_version",
        "rule_id",
        *_INDEX,
        "parent_candidate_id",
        "strategy_version",
        "strategy",
        "parameters",
        "code_id",
        "seed",
        "fitted_artifacts",
        "in_sample_input_id",
        *_INTS,
    )
)
_PARAMS = frozenset(
    ("starting_balance_usdt", "trade_size", "deploy_pct", "maker_fee", "taker_fee")
)
_INTEGRITY = "stored research event failed integrity validation"


@dataclass(frozen=True, slots=True)
class StoredResearchEvent:
    """Internal immutable persistence record, without an eligibility flag."""

    seq: int
    event_id: str
    kind: Literal["input", "candidate"]
    recorded_at_ts: int
    canonical_bytes: bytes


def _fail(message: str) -> NoReturn:
    logger.error(message)
    raise ValueError(message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _identity(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _typed(value: int | float) -> dict[str, str]:
    return (
        {"kind": "int", "value": hex(value)}
        if isinstance(value, int)
        else {"kind": "float", "value": value.hex()}
    )


def _decode_number(value: object, kinds: tuple[str, ...]) -> int | float:
    if not isinstance(value, dict) or value.keys() != {"kind", "value"}:
        _fail(_INTEGRITY)
    kind, spelling = value["kind"], value["value"]
    if kind not in kinds or not isinstance(spelling, str):
        _fail(_INTEGRITY)
    try:
        number = int(spelling, 16) if kind == "int" else float.fromhex(spelling)
    except (ValueError, OverflowError):
        _fail(_INTEGRITY)
    if _typed(number) != value:
        _fail(_INTEGRITY)
    return number


def _pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            _fail(_INTEGRITY)
        result[key] = value
    return result


def _reject_json_number(value: str) -> NoReturn:
    _fail(_INTEGRITY)


def _parse(payload: bytes) -> dict[str, object]:
    try:
        value: object = json.loads(
            payload,
            object_pairs_hook=_pairs,
            parse_int=_reject_json_number,
            parse_float=_reject_json_number,
            parse_constant=_reject_json_number,
        )
        if not isinstance(value, dict) or _canonical(value) != payload:
            _fail(_INTEGRITY)
    except (UnicodeError, json.JSONDecodeError, OverflowError):
        _fail(_INTEGRITY)
    return cast(dict[str, object], value)


def _mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        _fail(_INTEGRITY)
    return cast(dict[str, object], value).copy()


def _decode_input(
    value: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    if (
        value.keys() != {"contract_version", "recipe", "snapshot"}
        or value.get("contract_version") != "research-store-input-v1"
    ):
        _fail(_INTEGRITY)
    recipe = _mapping(value["recipe"])
    snapshot = _mapping(value["snapshot"])
    try:
        for field in _RECIPE_INTS:
            recipe[field] = _decode_number(recipe[field], ("int",))
        snapshot["anchor_ts"] = _decode_number(snapshot["anchor_ts"], ("int",))
        rows = snapshot["observations"]
        if not isinstance(rows, list):
            _fail(_INTEGRITY)
        decoded: list[dict[str, object]] = []
        for raw in rows:
            row = _mapping(raw)
            for field in (
                "ts",
                "close_ts",
                "available_ts",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ):
                if field == "available_ts" and row[field] is None:
                    continue
                kinds = ("int",) if field.endswith("ts") else ("int", "float")
                row[field] = _decode_number(row[field], kinds)
            decoded.append(row)
        snapshot["observations"] = decoded
    except KeyError:
        _fail(_INTEGRITY)
    return recipe, snapshot


def _input_payload(
    recipe: Mapping[str, object], snapshot: ResearchInputSnapshot
) -> bytes:
    encoded_recipe = {
        key: _typed(cast(int, val)) if key in _RECIPE_INTS else val
        for key, val in recipe.items()
    }
    return _canonical(
        {
            "contract_version": "research-store-input-v1",
            "recipe": encoded_recipe,
            "snapshot": json.loads(snapshot.canonical_bytes),
        }
    )


def _text(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and "\x00" not in value
        and not any(0xD800 <= ord(char) <= 0xDFFF for char in value)
    )


def _integer(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        _fail(f"{field} must be an integer excluding bool")
    return value


def _candidate(document: Mapping[str, object]) -> dict[str, object]:
    if not isinstance(document, Mapping) or document.keys() != _FIELDS:
        _fail("candidate must contain exactly the declared fields")
    data = dict(document)
    for field, token in (
        ("contract_version", "research-candidate-v1"),
        ("rule_id", "phase18-temporal-v1"),
        ("strategy", "buy_hold"),
    ):
        if not isinstance(data[field], str) or data[field] != token:
            _fail(f"{field} must be {token}")
    for field in (*_INDEX, "strategy_version", "in_sample_input_id"):
        if not _text(data[field]):
            _fail(f"{field} must be a nonempty UTF-8 string without NUL")
    if data["parent_candidate_id"] is not None and not _text(
        data["parent_candidate_id"]
    ):
        _fail("parent_candidate_id must be null or a nonempty UTF-8 string without NUL")
    code = data["code_id"]
    if not isinstance(code, str) or re.fullmatch("[0-9a-f]{40}", code) is None:
        _fail("code_id must be a 40-character lowercase hexadecimal git commit ID")
    params = data["parameters"]
    if not isinstance(params, Mapping) or params.keys() != _PARAMS:
        _fail("parameters must contain exactly the declared fields")
    cash = params["starting_balance_usdt"]
    if (
        not isinstance(cash, float)
        or not math.isfinite(cash)
        or cash <= 0
        or not cash.is_integer()
    ):
        _fail(
            "parameters.starting_balance_usdt must be a finite positive "
            "whole-USDT float"
        )
    for field in ("trade_size", "deploy_pct", "maker_fee", "taker_fee"):
        raw = params[field]
        if not isinstance(raw, str):
            _fail(f"parameters.{field} must be a finite decimal string")
        try:
            number = Decimal(raw)
        except InvalidOperation:
            _fail(f"parameters.{field} must be a finite decimal string")
        if not number.is_finite():
            _fail(f"parameters.{field} must be a finite decimal string")
        if field == "trade_size":
            _, digits, exponent = number.as_tuple()
            assert isinstance(exponent, int)
            trailing = 0
            for digit in reversed(digits):
                if digit:
                    break
                trailing += 1
            if number <= 0 or exponent + trailing < -6:
                _fail(
                    "parameters.trade_size must be positive and exactly representable "
                    "at 6 decimal places"
                )
        elif field == "deploy_pct" and not 0 <= number <= 1:
            _fail("parameters.deploy_pct must be between zero and one")
        elif field in ("maker_fee", "taker_fee") and number < 0:
            _fail(f"parameters.{field} must be nonnegative")
    if (
        data["seed"] is not None
        or not isinstance(data["fitted_artifacts"], list | tuple)
        or data["fitted_artifacts"]
    ):
        _fail("seed and fitted_artifacts must be explicitly absent for buy_hold")
    data["fitted_artifacts"] = []
    start = _integer(data["in_sample_start_ts"], "in_sample_start_ts")
    end = _integer(data["in_sample_end_ts"], "in_sample_end_ts")
    if start >= end:
        _fail("in_sample_start_ts must be less than in_sample_end_ts")
    index = _integer(data["trial_index"], "trial_index")
    count = _integer(data["trial_count"], "trial_count")
    if count <= 0:
        _fail("trial_count must be positive")
    if not 1 <= index <= count:
        _fail("trial_index must be between one and trial_count")
    data["parameters"] = dict(params)
    return data


def _candidate_payload(data: dict[str, object]) -> bytes:
    encoded = data.copy()
    for field in _INTS:
        encoded[field] = _typed(cast(int, data[field]))
    params = cast(dict[str, object], data["parameters"]).copy()
    params["starting_balance_usdt"] = _typed(
        cast(float, params["starting_balance_usdt"])
    )
    encoded["parameters"] = params
    return _canonical(encoded)


@contextmanager
def _connection(db_path: Path) -> Iterator[sqlite3.Connection]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, isolation_level=None)
    try:
        connection.execute("PRAGMA busy_timeout=5000")
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("""CREATE TABLE IF NOT EXISTS research_events_v1 (
            seq INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE,
            kind TEXT NOT NULL CHECK(kind IN ('input','candidate')),
            recorded_at_ts INTEGER NOT NULL, payload BLOB NOT NULL,
            experiment_id TEXT, hypothesis_id TEXT, candidate_revision TEXT,
            UNIQUE(experiment_id,hypothesis_id,candidate_revision))""")
        for operation in ("UPDATE", "DELETE"):
            connection.execute(f"""CREATE TRIGGER IF NOT EXISTS
                research_no_{operation.lower()}
                BEFORE {operation} ON research_events_v1 BEGIN
                SELECT RAISE(ABORT, 'research events are append-only'); END""")
        yield connection
    finally:
        connection.close()


def init_research_schema(db_path: Path) -> None:
    """Idempotently initialize the supplied metadata database."""
    with _connection(db_path):
        pass


def _references(
    connection: sqlite3.Connection,
    data: dict[str, object],
    seen: frozenset[str],
    seq: int | None = None,
) -> None:
    source = _replay(connection, cast(str, data["in_sample_input_id"]), seen)
    if source is None or source.kind != "input":
        _fail("candidate input event does not exist")
    recipe, document = _decode_input(_parse(source.canonical_bytes))
    snapshot = bind_controlled_fixture(recipe=recipe, document=document)
    start, end = (cast(int, data[field]) for field in _INTS[:2])
    for field, number in zip(_INTS[:2], (start, end), strict=True):
        if (number - snapshot.anchor_ts) % _DAY:
            _fail(f"{field} must align with the declared daily grid")
    validate_bar_coverage(
        ResearchInterval(start, end),
        timeframe=snapshot.timeframe,
        calendar=snapshot.calendar,
        anchor_ts=snapshot.anchor_ts,
        observations=[
            {"ts": row.ts, "close_ts": row.close_ts, "available_ts": row.available_ts}
            for row in snapshot.observations
            if start <= row.close_ts < end
        ],
    )
    parent_id = data["parent_candidate_id"]
    if parent_id is not None:
        parent = _replay(connection, cast(str, parent_id), seen)
        if parent is None or parent.kind != "candidate":
            _fail("parent candidate event does not exist")
        parent_data = _parse(parent.canonical_bytes)
        if any(parent_data[field] != data[field] for field in _INDEX[:2]):
            _fail("parent candidate does not match experiment and hypothesis")
        if seq is not None and parent.seq >= seq:
            _fail(_INTEGRITY)
    if seq is not None and source.seq >= seq:
        _fail(_INTEGRITY)


def _replay(
    connection: sqlite3.Connection, event_id: str, seen: frozenset[str] = frozenset()
) -> StoredResearchEvent | None:
    if event_id in seen:
        _fail(_INTEGRITY)
    row = connection.execute(
        """SELECT seq,event_id,kind,recorded_at_ts,payload,
        experiment_id,hypothesis_id,candidate_revision FROM research_events_v1
        WHERE event_id=?""",
        (event_id,),
    ).fetchone()
    if row is None:
        return None
    seq, identity, kind, timestamp, payload, *indexed = row
    if (
        not isinstance(payload, bytes)
        or _identity(payload) != identity
        or kind not in ("input", "candidate")
    ):
        _fail(_INTEGRITY)
    data = _parse(payload)
    if kind == "input":
        if indexed != [None, None, None]:
            _fail(_INTEGRITY)
        recipe, document = _decode_input(data)
        snapshot = bind_controlled_fixture(recipe=recipe, document=document)
        if _input_payload(recipe, snapshot) != payload:
            _fail(_INTEGRITY)
    else:
        if data.keys() != _FIELDS or indexed != [data[field] for field in _INDEX]:
            _fail(_INTEGRITY)
        try:
            for field in _INTS:
                data[field] = _decode_number(data[field], ("int",))
            params = _mapping(data["parameters"])
            params["starting_balance_usdt"] = _decode_number(
                params["starting_balance_usdt"], ("float",)
            )
            data["parameters"] = params
        except KeyError:
            _fail(_INTEGRITY)
        data = _candidate(data)
        if _candidate_payload(data) != payload:
            _fail(_INTEGRITY)
        _references(connection, data, seen | {event_id}, seq)
    return StoredResearchEvent(seq, identity, kind, timestamp, payload)


def _read_research_event(db_path: Path, *, event_id: str) -> StoredResearchEvent | None:
    """Private integrity replay only; future researcher access must be guarded."""
    with _connection(db_path) as connection:
        connection.execute("BEGIN")
        return _replay(connection, event_id)


def _capture(
    db_path: Path,
    kind: Literal["input", "candidate"],
    payload: bytes,
    data: dict[str, object] | None,
) -> StoredResearchEvent:
    identity = _identity(payload)
    with _connection(db_path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            if data is not None:
                _references(connection, data, frozenset())
                prior = connection.execute(
                    """SELECT event_id FROM research_events_v1
                    WHERE experiment_id=? AND hypothesis_id=?
                    AND candidate_revision=?""",
                    tuple(data[field] for field in _INDEX),
                ).fetchone()
                if prior is not None:
                    original = _replay(connection, prior[0])
                    if original is None or original.event_id != identity:
                        _fail("candidate revision already has different frozen content")
                    connection.commit()
                    return original
            original = _replay(connection, identity)
            if original is not None:
                if original.kind != kind or original.canonical_bytes != payload:
                    _fail(_INTEGRITY)
                connection.commit()
                return original
            timestamp = time.time_ns() // 1_000_000
            cursor = connection.execute(
                """INSERT INTO research_events_v1
                (event_id,kind,recorded_at_ts,payload,experiment_id,hypothesis_id,
                 candidate_revision) VALUES (?,?,?,?,?,?,?)""",
                (
                    identity,
                    kind,
                    timestamp,
                    payload,
                    *(data[field] if data is not None else None for field in _INDEX),
                ),
            )
            assert cursor.lastrowid is not None
            result = StoredResearchEvent(
                cursor.lastrowid, identity, kind, timestamp, payload
            )
            connection.commit()
            return result
        except BaseException:
            connection.rollback()
            raise


def capture_fixture_input(
    db_path: Path, *, recipe: Mapping[str, object], document: Mapping[str, object]
) -> StoredResearchEvent:
    """Reproduce raw synthetic evidence before persisting full immutable content."""
    snapshot = bind_controlled_fixture(recipe=recipe, document=document)
    return _capture(db_path, "input", _input_payload(recipe, snapshot), None)


def freeze_research_candidate(
    db_path: Path, *, document: Mapping[str, object]
) -> StoredResearchEvent:
    """Freeze exact declared BuyHold inputs; this grants no selection authorization."""
    data = _candidate(document)
    return _capture(db_path, "candidate", _candidate_payload(data), data)
