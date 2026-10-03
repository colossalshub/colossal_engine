from __future__ import annotations

import json
import logging
import math
import sys
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any

import pytest

from quant.engine.research_input import (
    InputProvenance,
    ResearchInputSnapshot,
    ResearchObservation,
    create_research_input_snapshot,
)

D = 86_400_000
LOGGER = "quant.engine.research_input"
# Independently written complete wire-identity bytes, not a production encoder.
CANONICAL = (
    b'{"anchor_ts":{"kind":"int","value":"0x0"},'
    b'"calendar":"continuous_utc_fixed","contract_version":"research-input-v1",'
    b'"observations":[{"available_ts":{"kind":"int","value":"0x5265c00"},'
    b'"close":{"kind":"float","value":"0x1.8000000000000p+0"},'
    b'"close_ts":{"kind":"int","value":"0x5265c00"},'
    b'"high":{"kind":"int","value":"0x2"},"low":{"kind":"int","value":"0x1"},'
    b'"open":{"kind":"int","value":"0x1"},"provenance":{"declared_by":null,'
    b'"kind":"controlled_fixture","reference":"r\xc3\xa9cipe"},'
    b'"revision_id":"r1","source_id":" source ","ts":{"kind":"int","value":"0x0"},'
    b'"volume":{"kind":"float","value":"-0x0.0p+0"}}],'
    b'"rule_id":"phase18-temporal-v1","symbol":"BTC/USDT",'
    b'"timeframe":"1d","venue":"binance"}'
)
SNAPSHOT_ID = "sha256:df720d027a740232c362fc02a800b717083bc93c8144e219ebcb07ffc4d774f6"


def _document() -> dict[str, Any]:
    return {
        "contract_version": "research-input-v1",
        "rule_id": "phase18-temporal-v1",
        "venue": "binance",
        "symbol": "BTC/USDT",
        "timeframe": "1d",
        "calendar": "continuous_utc_fixed",
        "anchor_ts": 0,
        "observations": [
            {
                "ts": 0,
                "close_ts": D,
                "available_ts": D,
                "open": 1,
                "high": 2,
                "low": 1,
                "close": 1.5,
                "volume": -0.0,
                "source_id": " source ",
                "revision_id": "r1",
                "provenance": {
                    "kind": "controlled_fixture",
                    "reference": "récipe",
                    "declared_by": None,
                },
            }
        ],
    }


def _reject(
    document: Mapping[str, object], message: str, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger=LOGGER):
        with pytest.raises(ValueError) as error:
            create_research_input_snapshot(document)
    assert str(error.value) == message
    assert caplog.record_tuples == [(LOGGER, logging.ERROR, message)]


def test_independent_canonical_bytes_digest_and_silent_repeat(
    caplog: pytest.LogCaptureFixture,
) -> None:
    doc = _document()
    with caplog.at_level(logging.DEBUG, logger=LOGGER):
        result = create_research_input_snapshot(doc)
        assert create_research_input_snapshot(doc) == result
    assert caplog.record_tuples == []
    assert result.canonical_bytes == CANONICAL
    assert result.snapshot_id == SNAPSHOT_ID
    assert result.observations == (
        ResearchObservation(
            0,
            D,
            D,
            1,
            2,
            1,
            1.5,
            -0.0,
            " source ",
            "r1",
            InputProvenance("controlled_fixture", "récipe", None),
        ),
    )
    assert math.copysign(1, result.observations[0].volume) == -1


def test_mapping_order_and_tuple_container_do_not_change_identity() -> None:
    doc = _document()
    row = dict(reversed(list(doc["observations"][0].items())))
    row["provenance"] = MappingProxyType(
        dict(reversed(list(row["provenance"].items())))
    )
    doc["observations"] = (MappingProxyType(row),)
    doc = dict(reversed(list(doc.items())))
    result = create_research_input_snapshot(MappingProxyType(doc))
    assert result.canonical_bytes == CANONICAL
    assert result.snapshot_id == SNAPSHOT_ID


def test_deep_mutation_isolation_and_frozen_slots() -> None:
    doc = _document()
    before = deepcopy(doc)
    result = create_research_input_snapshot(doc)
    assert doc == before
    doc["anchor_ts"] = 7
    doc["observations"][0]["close"] = 900
    doc["observations"][0]["provenance"]["reference"] = "changed"
    doc["observations"].append(deepcopy(doc["observations"][0]))
    assert result.canonical_bytes == CANONICAL
    assert result.snapshot_id == SNAPSHOT_ID
    assert result.observations[0].close == 1.5
    assert result.observations[0].provenance.reference == "récipe"
    for record, name, value in (
        (result, "anchor_ts", 1),
        (result.observations[0], "close", 2),
        (result.observations[0].provenance, "reference", "changed"),
    ):
        assert not hasattr(record, "__dict__")
        with pytest.raises(FrozenInstanceError):
            setattr(record, name, value)
    assert isinstance(result.observations, tuple)
    assert isinstance(result.canonical_bytes, bytes)
    with pytest.raises(TypeError):
        result.canonical_bytes[0] = 0


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("open", 1.1),
        ("high", 3),
        ("low", 0.5),
        ("close", 1.75),
        ("volume", 1),
        ("available_ts", D + 1),
        ("source_id", " source"),
        ("revision_id", "r2"),
    ],
)
def test_every_raw_value_and_label_binds_identity(field: str, value: object) -> None:
    doc = _document()
    doc["observations"][0][field] = value
    assert create_research_input_snapshot(doc).snapshot_id != SNAPSHOT_ID


def test_anchor_open_close_and_whole_later_context_bind_identity() -> None:
    doc = _document()
    doc["anchor_ts"] = D  # same grid, different explicit anchor
    assert create_research_input_snapshot(doc).snapshot_id != SNAPSHOT_ID
    doc = _document()
    row = doc["observations"][0]
    row.update(ts=D, close_ts=2 * D, available_ts=2 * D)
    assert create_research_input_snapshot(doc).snapshot_id != SNAPSHOT_ID
    doc = _document()
    later = deepcopy(doc["observations"][0])
    later.update(ts=3 * D, close_ts=4 * D, available_ts=4 * D)
    doc["observations"].append(later)  # raw batches need not be complete grids
    result = create_research_input_snapshot(doc)
    assert len(result.observations) == 2
    assert result.snapshot_id != SNAPSHOT_ID
    later["revision_id"] = "later-revision"
    assert create_research_input_snapshot(doc).snapshot_id != result.snapshot_id


@pytest.mark.parametrize(
    ("field", "first", "second"),
    [
        ("open", 1, 1.0),
        ("volume", 0, 0.0),
        ("volume", 0.0, -0.0),
        ("close", 1.2345678901, 1.23456789012),
    ],
)
def test_numeric_kind_signed_zero_and_precision_are_exact(
    field: str,
    first: int | float,
    second: int | float,
) -> None:
    if field == "close":
        assert format(first, ".10g") == format(second, ".10g")
    doc = _document()
    doc["observations"][0][field] = first
    before = create_research_input_snapshot(doc)
    doc["observations"][0][field] = second
    after = create_research_input_snapshot(doc)
    assert type(getattr(before.observations[0], field)) is type(first)
    assert type(getattr(after.observations[0], field)) is type(second)
    assert before.snapshot_id != after.snapshot_id


@pytest.mark.parametrize("sign", [1, -1])
def test_arithmetic_huge_integers_preserved_without_digit_limit_changes(
    sign: int,
) -> None:
    limit = sys.get_int_max_str_digits()
    huge = 10**4500 + 17  # no decimal parsing or str conversion
    assert huge > 10**4300
    doc = _document()
    anchor = sign * huge
    doc["anchor_ts"] = anchor
    row = doc["observations"][0]
    row.update(
        ts=anchor,
        close_ts=anchor + D,
        available_ts=anchor + D + 9,
        open=huge,
        high=huge + 3,
        low=huge - 1,
        close=huge + 1,
        volume=huge,
    )
    result = create_research_input_snapshot(doc)
    assert result.anchor_ts == anchor
    observation = result.observations[0]
    for name in (
        "ts",
        "close_ts",
        "available_ts",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ):
        assert getattr(observation, name) == row[name]
        assert type(getattr(observation, name)) is int
    identity = json.loads(result.canonical_bytes)
    assert identity["anchor_ts"] == {"kind": "int", "value": hex(anchor)}
    for name in (
        "ts",
        "close_ts",
        "available_ts",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ):
        assert identity["observations"][0][name] == {
            "kind": "int",
            "value": hex(row[name]),
        }
    assert sys.get_int_max_str_digits() == limit


@pytest.mark.parametrize(
    ("kind", "available", "reference", "actor"),
    [
        ("unknown", None, None, None),
        ("researcher_attested", None, "https://unfetched.invalid/声明", " Actor "),
        ("researcher_attested", D + 77, "claim:hash", "researcher"),
        ("controlled_fixture", D + 77, "unreproduced:recipe", None),
    ],
)
def test_provenance_is_only_a_claim_with_unknown_or_delayed_availability(
    kind: str,
    available: int | None,
    reference: str | None,
    actor: str | None,
) -> None:
    doc = _document()
    row = doc["observations"][0]
    row["available_ts"] = available
    row["provenance"] = {"kind": kind, "reference": reference, "declared_by": actor}
    result = create_research_input_snapshot(doc)
    assert result.observations[0].available_ts == available
    provenance = result.observations[0].provenance
    assert (provenance.kind, provenance.reference, provenance.declared_by) == (
        kind,
        reference,
        actor,
    )
    assert json.loads(result.canonical_bytes)["observations"][0]["available_ts"] == (
        None if available is None else {"kind": "int", "value": hex(available)}
    )
    for record in (result, result.observations[0], provenance):
        assert all(
            not hasattr(record, name) for name in ("verified", "eligible", "frozen")
        )


def test_provenance_reference_actor_and_unicode_are_identity_inputs() -> None:
    doc = _document()
    ids = {SNAPSHOT_ID}
    row = doc["observations"][0]
    row["provenance"]["reference"] = "re\u0301cipe"
    ids.add(create_research_input_snapshot(doc).snapshot_id)
    row["provenance"].update(kind="researcher_attested", declared_by="A")
    ids.add(create_research_input_snapshot(doc).snapshot_id)
    row["provenance"]["declared_by"] = "B"
    ids.add(create_research_input_snapshot(doc).snapshot_id)
    row["available_ts"] = None
    ids.add(create_research_input_snapshot(doc).snapshot_id)
    row["provenance"].update(kind="unknown", reference=None, declared_by=None)
    ids.add(create_research_input_snapshot(doc).snapshot_id)
    assert len(ids) == 6


@pytest.mark.parametrize("level", ["document", "row", "provenance"])
@pytest.mark.parametrize("operation", ["missing", "extra"])
def test_exact_fields_every_level(
    level: str,
    operation: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    doc = _document()
    target = doc if level == "document" else doc["observations"][0]
    path = "document" if level == "document" else "observations[0]"
    if level == "provenance":
        target = target["provenance"]
        path += ".provenance"
    if operation == "missing":
        target.pop(next(iter(target)))
    else:
        target["sensitive-unknown-key"] = "secret"
    _reject(doc, f"{path} must contain exactly the declared fields", caplog)


@pytest.mark.parametrize(
    "field",
    [
        "contract_version",
        "rule_id",
        "venue",
        "symbol",
        "timeframe",
        "calendar",
    ],
)
@pytest.mark.parametrize("value", [None, True, "unsupported"])
def test_exact_fixed_tokens(
    field: str, value: object, caplog: pytest.LogCaptureFixture
) -> None:
    doc = _document()
    token = doc[field]
    doc[field] = value
    _reject(doc, f"{field} must be {token}", caplog)


@pytest.mark.parametrize("rows", [None, [], (), {}, "rows", iter([{}])])
def test_observations_container(rows: object, caplog: pytest.LogCaptureFixture) -> None:
    doc = _document()
    doc["observations"] = rows
    _reject(doc, "observations must be a nonempty list or tuple of mappings", caplog)


@pytest.mark.parametrize("row", [None, [], "secret"])
def test_row_mapping(row: object, caplog: pytest.LogCaptureFixture) -> None:
    doc = _document()
    doc["observations"] = [row]
    _reject(doc, "observations[0] must be a mapping", caplog)


@pytest.mark.parametrize("field", ["anchor_ts", "ts", "close_ts"])
def test_clock_null_rejected(field: str, caplog: pytest.LogCaptureFixture) -> None:
    doc = _document()
    target = doc if field == "anchor_ts" else doc["observations"][0]
    target[field] = None
    path = field if field == "anchor_ts" else f"observations[0].{field}"
    _reject(doc, f"{path} must be an integer excluding bool", caplog)


@pytest.mark.parametrize("level", ["document", "row", "provenance"])
def test_required_nullable_fields_cannot_be_omitted(
    level: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    doc = _document()
    target = doc if level == "document" else doc["observations"][0]
    path = "document" if level == "document" else "observations[0]"
    field = "anchor_ts" if level == "document" else "available_ts"
    if level == "provenance":
        target = target["provenance"]
        field = "declared_by"
        path += ".provenance"
    target.pop(field)
    _reject(doc, f"{path} must contain exactly the declared fields", caplog)


@pytest.mark.parametrize("value", [None, [], "secret"])
def test_provenance_requires_mapping(
    value: object, caplog: pytest.LogCaptureFixture
) -> None:
    doc = _document()
    doc["observations"][0]["provenance"] = value
    _reject(
        doc,
        "observations[0].provenance must contain exactly the declared fields",
        caplog,
    )


@pytest.mark.parametrize("field", ["anchor_ts", "ts", "close_ts", "available_ts"])
@pytest.mark.parametrize("value", [True, False, 1.0, "0", Decimal(0)])
def test_clock_types(
    field: str, value: object, caplog: pytest.LogCaptureFixture
) -> None:
    doc = _document()
    target = doc if field == "anchor_ts" else doc["observations"][0]
    target[field] = value
    path = field if field == "anchor_ts" else f"observations[0].{field}"
    _reject(doc, f"{path} must be an integer excluding bool", caplog)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("ts", 1, "ts must align with the declared daily grid"),
        ("close_ts", D + 1, "close_ts must equal ts plus one day"),
        ("available_ts", D - 1, "available_ts must be at or after close_ts"),
    ],
)
def test_clock_consistency(
    field: str, value: int, message: str, caplog: pytest.LogCaptureFixture
) -> None:
    doc = _document()
    doc["observations"][0][field] = value
    _reject(doc, f"observations[0].{message}", caplog)


@pytest.mark.parametrize("field", ["open", "high", "low", "close", "volume"])
@pytest.mark.parametrize(
    "value",
    [True, None, "secret", Decimal(1), float("nan"), float("inf"), float("-inf"), -1],
)
def test_numeric_types_finiteness_and_sign(
    field: str,
    value: object,
    caplog: pytest.LogCaptureFixture,
) -> None:
    doc = _document()
    doc["observations"][0][field] = value
    sign = "nonnegative" if field == "volume" else "positive"
    _reject(
        doc,
        f"observations[0].{field} must be a finite {sign} int or float excluding bool",
        caplog,
    )


@pytest.mark.parametrize("field", ["open", "high", "low", "close"])
def test_zero_prices_rejected(field: str, caplog: pytest.LogCaptureFixture) -> None:
    doc = _document()
    doc["observations"][0][field] = 0
    _reject(
        doc,
        f"observations[0].{field} must be a finite positive "
        "int or float excluding bool",
        caplog,
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"high": 1},
        {"low": 1.25},
        {"high": 1.25, "low": 1.5},
    ],
)
def test_ohlc_bounds(
    changes: dict[str, object], caplog: pytest.LogCaptureFixture
) -> None:
    doc = _document()
    doc["observations"][0].update(changes)
    _reject(doc, "observations[0] must have consistent OHLC bounds", caplog)


@pytest.mark.parametrize(
    "field", ["source_id", "revision_id", "reference", "declared_by"]
)
@pytest.mark.parametrize(
    "value", [None, "", 7, "secret\x00actor", "secret\ud800", "\udfff"]
)
def test_required_text_utf8_nul_and_nonempty(
    field: str,
    value: object,
    caplog: pytest.LogCaptureFixture,
) -> None:
    doc = _document()
    row = doc["observations"][0]
    path = f"observations[0].{field}"
    target = row
    if field in ("reference", "declared_by"):
        target = row["provenance"]
        target.update(kind="researcher_attested", declared_by="actor")
        path = f"observations[0].provenance.{field}"
    target[field] = value
    _reject(doc, f"{path} must be a nonempty UTF-8 string without NUL", caplog)


@pytest.mark.parametrize("value", [None, True, "source_verified", "UNKNOWN"])
def test_exact_provenance_kind(value: object, caplog: pytest.LogCaptureFixture) -> None:
    doc = _document()
    doc["observations"][0]["provenance"]["kind"] = value
    _reject(
        doc,
        "observations[0].provenance.kind must be controlled_fixture, "
        "researcher_attested, or unknown",
        caplog,
    )


@pytest.mark.parametrize(
    ("kind", "available", "reference", "actor"),
    [
        ("unknown", D, None, None),
        ("unknown", None, "secret-reference", None),
        ("unknown", None, None, "secret-actor"),
        ("controlled_fixture", None, "recipe", None),
        ("controlled_fixture", D, "recipe", "secret-actor"),
    ],
)
def test_provenance_conditional_nulls(
    kind: str,
    available: int | None,
    reference: str | None,
    actor: str | None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    doc = _document()
    row = doc["observations"][0]
    row["available_ts"] = available
    row["provenance"] = {"kind": kind, "reference": reference, "declared_by": actor}
    _reject(
        doc,
        "observations[0].provenance must match the declared kind and availability",
        caplog,
    )


@pytest.mark.parametrize("revision", ["r1", "conflicting-revision"])
def test_duplicate_opens_even_equal_or_different_revision(
    revision: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    doc = _document()
    other = deepcopy(doc["observations"][0])
    other["revision_id"] = revision
    doc["observations"].append(other)
    _reject(doc, "observations[1].ts duplicates an earlier observation", caplog)


def test_out_of_order_never_sorted(caplog: pytest.LogCaptureFixture) -> None:
    doc = _document()
    earlier = deepcopy(doc["observations"][0])
    earlier.update(ts=-D, close_ts=0, available_ts=0)
    doc["observations"].append(earlier)
    _reject(doc, "observations must be strictly chronological", caplog)


def test_competing_invalid_order_and_redacted_single_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    doc = _document()
    row = doc["observations"][0]
    doc.update(contract_version="secret-version", rule_id="secret-rule", anchor_ts=True)
    row.update(
        ts=True,
        close_ts=True,
        available_ts=True,
        open=False,
        high=False,
        volume=False,
        source_id="secret\x00source",
    )
    row["provenance"].update(kind="secret-kind", reference="secret-reference")
    _reject(doc, "contract_version must be research-input-v1", caplog)
    doc["contract_version"] = "research-input-v1"
    _reject(doc, "rule_id must be phase18-temporal-v1", caplog)
    doc["rule_id"] = "phase18-temporal-v1"
    _reject(doc, "anchor_ts must be an integer excluding bool", caplog)
    doc["anchor_ts"] = 0
    _reject(doc, "observations[0].ts must be an integer excluding bool", caplog)
    row["ts"] = 1
    _reject(doc, "observations[0].close_ts must be an integer excluding bool", caplog)
    row["close_ts"] = D
    _reject(
        doc, "observations[0].available_ts must be an integer excluding bool", caplog
    )
    row["available_ts"] = D - 1
    _reject(doc, "observations[0].ts must align with the declared daily grid", caplog)
    row["ts"] = 0
    row["close_ts"] = D + 1
    _reject(doc, "observations[0].close_ts must equal ts plus one day", caplog)
    row["close_ts"] = D
    _reject(doc, "observations[0].available_ts must be at or after close_ts", caplog)
    row["available_ts"] = D
    _reject(
        doc,
        "observations[0].open must be a finite positive int or float excluding bool",
        caplog,
    )
    row.update(open=1, high=2, volume=0)
    _reject(
        doc,
        "observations[0].source_id must be a nonempty UTF-8 string without NUL",
        caplog,
    )
    row["source_id"] = "source"
    _reject(
        doc,
        "observations[0].provenance.kind must be controlled_fixture, "
        "researcher_attested, or unknown",
        caplog,
    )
    # A later duplicate is fully validated before duplicate/order rejection.
    doc = _document()
    other = deepcopy(doc["observations"][0])
    other["provenance"]["reference"] = None
    doc["observations"].append(other)
    _reject(
        doc,
        "observations[1].provenance.reference must be a nonempty "
        "UTF-8 string without NUL",
        caplog,
    )


def test_direct_dataclasses_are_unvalidated_without_extra_fields() -> None:
    provenance = InputProvenance("controlled_fixture", None, None)
    row = ResearchObservation(1, 1, None, -1, -1, -1, -1, -1, "", "", provenance)
    snapshot = ResearchInputSnapshot("", "", "", "", "", "", 1, (row,), b"", "")
    assert snapshot.observations == (row,)
    assert [field.name for field in fields(InputProvenance)] == [
        "kind",
        "reference",
        "declared_by",
    ]
    assert [field.name for field in fields(ResearchObservation)] == [
        "ts",
        "close_ts",
        "available_ts",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "source_id",
        "revision_id",
        "provenance",
    ]
    assert [field.name for field in fields(ResearchInputSnapshot)] == [
        "contract_version",
        "rule_id",
        "venue",
        "symbol",
        "timeframe",
        "calendar",
        "anchor_ts",
        "observations",
        "canonical_bytes",
        "snapshot_id",
    ]
