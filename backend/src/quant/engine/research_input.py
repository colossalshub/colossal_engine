"""Immutable supplied research evidence and exact research-input-v1 identity.

The factory accepts exactly contract_version, rule_id, venue, symbol, timeframe,
calendar, anchor_ts and observations. Supported tokens respectively are
research-input-v1, phase18-temporal-v1, binance, BTC/USDT, 1d and
continuous_utc_fixed. Observations are a nonempty list/tuple of mappings with
exactly ts, close_ts, available_ts, open, high, low, close, volume, source_id,
revision_id and provenance; provenance has exactly kind, reference, declared_by.
All fields, including explicit nulls, are required. Strings are not normalized.
Clocks are signed unbounded integers excluding bool, on the explicit daily grid;
close is open plus one day, known availability is at or after close. Unknown
availability stays None. OHLCV preserves finite positive int/float prices and
nonnegative volume without coercion, rounding or engine precision restrictions.
Rows are validated in supplied order, never filtered, sorted or deduplicated.

Provenance tokens are caller claims: unknown requires null reference, actor and
availability; researcher_attested requires reference and actor, with optional
availability; controlled_fixture requires reference, null actor and known
availability. No reference is fetched or authenticated. A future trusted fixture
importer must reproduce and bind rows before granting any fixture capability;
real historical publication/revision verification is separate work. This module
certifies neither source history, complete coverage, selection nor eligibility.
Direct construction of the frozen slots dataclasses is unvalidated.

Canonical identity contains the detached wire fields in supplied row order.
EVERY numeric field, including all clocks and anchor, becomes an object with
kind='int', value=hex(value), or kind='float', value=value.hex(). Null stays null.
Serialize with json.dumps(sort_keys=True, separators=(',', ':'),
ensure_ascii=False, allow_nan=False).encode('utf-8'), without newline or BOM.
snapshot_id is 'sha256:' plus the lowercase SHA-256 hex digest of those bytes.
This v1 typed hexadecimal convention preserves numeric kind, IEEE float values
and signed zero; it is not the existing bar fingerprint or an RFC convention.
Identity is not authentication or evidence of execution compatibility (the runner
separately interprets Decimal(str(value))). No global numeric settings change.
Mappings cannot reveal duplicate JSON keys already discarded by a parser; a
future JSON boundary must reject those keys before admission and preserve numbers.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, NoReturn, cast

logger = logging.getLogger(__name__)
_DAY_MS = 86_400_000
_TOKENS = {
    "contract_version": "research-input-v1",
    "rule_id": "phase18-temporal-v1",
    "venue": "binance",
    "symbol": "BTC/USDT",
    "timeframe": "1d",
    "calendar": "continuous_utc_fixed",
}
_DOCUMENT_FIELDS = frozenset((*_TOKENS, "anchor_ts", "observations"))
_ROW_FIELDS = frozenset(
    (
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
    )
)
_PROVENANCE_FIELDS = frozenset(("kind", "reference", "declared_by"))
_KINDS = ("controlled_fixture", "researcher_attested", "unknown")


@dataclass(frozen=True, slots=True)
class InputProvenance:
    """Supplied attribution claim, not an authenticated trust verdict."""

    kind: Literal["controlled_fixture", "researcher_attested", "unknown"]
    reference: str | None
    declared_by: str | None


@dataclass(frozen=True, slots=True)
class ResearchObservation:
    """Detached raw values; ts retains the bar-open meaning."""

    ts: int
    close_ts: int
    available_ts: int | None
    open: int | float
    high: int | float
    low: int | float
    close: int | float
    volume: int | float
    source_id: str
    revision_id: str
    provenance: InputProvenance


@dataclass(frozen=True, slots=True)
class ResearchInputSnapshot:
    """Exact immutable observed batch and content identity, without eligibility."""

    contract_version: str
    rule_id: str
    venue: str
    symbol: str
    timeframe: str
    calendar: str
    anchor_ts: int
    observations: tuple[ResearchObservation, ...]
    canonical_bytes: bytes
    snapshot_id: str


def _fail(message: str) -> NoReturn:
    logger.error(message)
    raise ValueError(message)


def _fields(value: object, fields: frozenset[str], path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or value.keys() != fields:
        _fail(f"{path} must contain exactly the declared fields")
    return cast(Mapping[str, object], value)


def _integer(value: object, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        _fail(f"{path} must be an integer excluding bool")
    return value


def _number(value: object, path: str, *, volume: bool = False) -> int | float:
    requirement = "nonnegative" if volume else "positive"
    if (
        not isinstance(value, int | float)
        or isinstance(value, bool)
        or (isinstance(value, float) and not math.isfinite(value))
        or value < 0
        or (not volume and value == 0)
    ):
        _fail(f"{path} must be a finite {requirement} int or float excluding bool")
    return value


def _text(value: object, path: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or "\x00" in value
        or any(0xD800 <= ord(character) <= 0xDFFF for character in value)
    ):
        _fail(f"{path} must be a nonempty UTF-8 string without NUL")
    return value


def _provenance(value: object, path: str, available: int | None) -> InputProvenance:
    data = _fields(value, _PROVENANCE_FIELDS, path)
    kind = data["kind"]
    if not isinstance(kind, str) or kind not in _KINDS:
        _fail(
            f"{path}.kind must be controlled_fixture, researcher_attested, or unknown"
        )
    reference = data["reference"]
    actor = data["declared_by"]
    if kind == "unknown":
        if reference is not None or actor is not None or available is not None:
            _fail(f"{path} must match the declared kind and availability")
        return InputProvenance("unknown", None, None)
    reference = _text(reference, f"{path}.reference")
    if kind == "researcher_attested":
        return InputProvenance(
            "researcher_attested",
            reference,
            _text(actor, f"{path}.declared_by"),
        )
    if actor is not None or available is None:
        _fail(f"{path} must match the declared kind and availability")
    return InputProvenance("controlled_fixture", reference, None)


def _observation(
    value: Mapping[str, object], path: str, anchor: int
) -> ResearchObservation:
    row = _fields(value, _ROW_FIELDS, path)
    ts = _integer(row["ts"], f"{path}.ts")
    close_ts = _integer(row["close_ts"], f"{path}.close_ts")
    raw_available = row["available_ts"]
    available = (
        None
        if raw_available is None
        else _integer(raw_available, f"{path}.available_ts")
    )
    if (ts - anchor) % _DAY_MS:
        _fail(f"{path}.ts must align with the declared daily grid")
    if close_ts != ts + _DAY_MS:
        _fail(f"{path}.close_ts must equal ts plus one day")
    if available is not None and available < close_ts:
        _fail(f"{path}.available_ts must be at or after close_ts")
    prices = {
        name: _number(row[name], f"{path}.{name}")
        for name in ("open", "high", "low", "close")
    }
    volume = _number(row["volume"], f"{path}.volume", volume=True)
    if (
        prices["high"] < max(prices["open"], prices["close"])
        or prices["low"] > min(prices["open"], prices["close"])
        or prices["high"] < prices["low"]
    ):
        _fail(f"{path} must have consistent OHLC bounds")
    source = _text(row["source_id"], f"{path}.source_id")
    revision = _text(row["revision_id"], f"{path}.revision_id")
    provenance = _provenance(row["provenance"], f"{path}.provenance", available)
    return ResearchObservation(
        ts,
        close_ts,
        available,
        prices["open"],
        prices["high"],
        prices["low"],
        prices["close"],
        volume,
        source,
        revision,
        provenance,
    )


def _typed_number(value: int | float | None) -> dict[str, str] | None:
    if value is None:
        return None
    if isinstance(value, int):
        return {"kind": "int", "value": hex(value)}
    return {"kind": "float", "value": value.hex()}


def create_research_input_snapshot(
    document: Mapping[str, object],
) -> ResearchInputSnapshot:
    """Validate, detach and bind every supplied row without granting trust."""
    data = _fields(document, _DOCUMENT_FIELDS, "document")
    metadata: dict[str, str] = {}
    for name, token in _TOKENS.items():
        value = data[name]
        if not isinstance(value, str) or value != token:
            _fail(f"{name} must be {token}")
        metadata[name] = value
    anchor = _integer(data["anchor_ts"], "anchor_ts")
    raw_rows = data["observations"]
    if not isinstance(raw_rows, list | tuple) or not raw_rows:
        _fail("observations must be a nonempty list or tuple of mappings")
    rows: list[ResearchObservation] = []
    seen: set[int] = set()
    previous: int | None = None
    for index, raw_row in enumerate(raw_rows):
        path = f"observations[{index}]"
        if not isinstance(raw_row, Mapping):
            _fail(f"{path} must be a mapping")
        row = _observation(raw_row, path, anchor)
        if row.ts in seen:
            _fail(f"{path}.ts duplicates an earlier observation")
        if previous is not None and row.ts <= previous:
            _fail("observations must be strictly chronological")
        seen.add(row.ts)
        previous = row.ts
        rows.append(row)
    identity_rows: list[dict[str, object]] = []
    for row in rows:
        identity_rows.append(
            {
                **{
                    name: _typed_number(getattr(row, name))
                    for name in (
                        "ts",
                        "close_ts",
                        "available_ts",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                    )
                },
                "source_id": row.source_id,
                "revision_id": row.revision_id,
                "provenance": {
                    "kind": row.provenance.kind,
                    "reference": row.provenance.reference,
                    "declared_by": row.provenance.declared_by,
                },
            }
        )
    identity = {
        **metadata,
        "anchor_ts": _typed_number(anchor),
        "observations": identity_rows,
    }
    canonical = json.dumps(
        identity,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return ResearchInputSnapshot(
        metadata["contract_version"],
        metadata["rule_id"],
        metadata["venue"],
        metadata["symbol"],
        metadata["timeframe"],
        metadata["calendar"],
        anchor,
        tuple(rows),
        canonical,
        "sha256:" + hashlib.sha256(canonical).hexdigest(),
    )
