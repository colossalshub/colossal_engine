"""Reproduce and bind controlled-daily-linear-v1 synthetic research inputs.

Recipe fields are exactly recipe_version, rule_id, anchor_ts, start_open_ts,
observation_count, price_start, price_step and volume; every field is required.
Tokens are controlled-daily-linear-v1 and phase18-temporal-v1. Remaining values
are signed unbounded integers excluding bool: count and starting price positive,
volume nonnegative, start on the declared 86400000 ms daily grid, and final
linear price positive. There are no defaults, count caps or numeric coercions.
Generation costs O(count); this pure layer promises no execution compatibility.

Recipe identity preserves tokens and replaces EVERY integer with
{'kind':'int','value':hex(value)}. Serialize json.dumps(sort_keys=True,
separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8'),
without BOM/newline; recipe_id is 'sha256:' plus lowercase SHA-256 digest.
Change recipe_version if generation semantics change. Identity is not authenticity.

For index i, ts=start_open_ts+i*86400000, close_ts=ts+86400000,
available_ts=close_ts, OHLC=price_start+i*price_step, volume=recipe volume.
These zero-delay clocks are synthetic DEFINITIONS, never inferred real-market
publication history. Raw values remain integers (100 differs from float 100.0).
The exact research-input-v1 document uses phase18-temporal-v1, binance, BTC/USDT,
1d, continuous_utc_fixed, explicit anchor and these ordered observations.
Each source_id is controlled-fixture:controlled-daily-linear-v1, revision_id is
recipe_id, provenance is kind=controlled_fixture, reference=recipe_id,
declared_by=None. Generated range is complete on its own grid, with no stage or
window coverage claim. No randomness, files, network or historical data is used.

Create validates generated raw rows through the accepted snapshot factory.
Bind regenerates FIRST, independently validates supplied raw document SECOND,
compares canonical_bytes AND snapshot_id THIRD, then returns only the fresh
expected snapshot. Direct records, labels, opaque hashes, references and flags
are never trust shortcuts. A future runtime gateway must CALL this binder on
raw recipe+document at execution rather than trust a transported type/hash/flag.
Different explicit recipes legitimately create different synthetic datasets;
historical-looking prices do not certify historical origin or revision history.
This certifies reproduced synthetic contents/clocks only: no source history,
selection/OOS inspection, causal dependencies, research eligibility, realistic
execution, runtime wiring or completion of Phase18. Own failures log one redacted
ERROR and raise identical ValueError; factory errors propagate without relogging.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Mapping
from typing import NoReturn

from quant.engine.research_input import (
    ResearchInputSnapshot,
    create_research_input_snapshot,
)

logger = logging.getLogger(__name__)
_DAY_MS = 86_400_000
_VERSION = "controlled-daily-linear-v1"
_RULE = "phase18-temporal-v1"
_INTEGERS = (
    "anchor_ts",
    "start_open_ts",
    "observation_count",
    "price_start",
    "price_step",
    "volume",
)
_FIELDS = frozenset(("recipe_version", "rule_id", *_INTEGERS))


def _fail(message: str) -> NoReturn:
    logger.error(message)
    raise ValueError(message)


def create_controlled_fixture(recipe: Mapping[str, object]) -> ResearchInputSnapshot:
    """Validate an explicit recipe and reproduce its immutable synthetic batch."""
    if not isinstance(recipe, Mapping) or recipe.keys() != _FIELDS:
        _fail("recipe must contain exactly the declared fields")
    for field, token in (("recipe_version", _VERSION), ("rule_id", _RULE)):
        if not isinstance(recipe[field], str) or recipe[field] != token:
            _fail(f"{field} must be {token}")
    numbers: dict[str, int] = {}
    for field in _INTEGERS:
        value = recipe[field]
        if not isinstance(value, int) or isinstance(value, bool):
            _fail(f"{field} must be an integer excluding bool")
        numbers[field] = value
    anchor = numbers["anchor_ts"]
    start = numbers["start_open_ts"]
    count = numbers["observation_count"]
    price = numbers["price_start"]
    step = numbers["price_step"]
    volume = numbers["volume"]
    if count <= 0:
        _fail("observation_count must be positive")
    if price <= 0:
        _fail("price_start must be positive")
    if volume < 0:
        _fail("volume must be nonnegative")
    if (start - anchor) % _DAY_MS:
        _fail("start_open_ts must align with the declared daily grid")
    if price + (count - 1) * step <= 0:
        _fail("generated prices must all be positive")
    identity = {
        "recipe_version": _VERSION,
        "rule_id": _RULE,
        **{
            name: {"kind": "int", "value": hex(value)}
            for name, value in numbers.items()
        },
    }
    canonical = json.dumps(
        identity,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    recipe_id = "sha256:" + hashlib.sha256(canonical).hexdigest()
    rows: list[dict[str, object]] = []
    for index in range(count):
        ts = start + index * _DAY_MS
        value = price + index * step
        rows.append(
            {
                "ts": ts,
                "close_ts": ts + _DAY_MS,
                "available_ts": ts + _DAY_MS,
                "open": value,
                "high": value,
                "low": value,
                "close": value,
                "volume": volume,
                "source_id": "controlled-fixture:" + _VERSION,
                "revision_id": recipe_id,
                "provenance": {
                    "kind": "controlled_fixture",
                    "reference": recipe_id,
                    "declared_by": None,
                },
            }
        )
    return create_research_input_snapshot(
        {
            "contract_version": "research-input-v1",
            "rule_id": _RULE,
            "venue": "binance",
            "symbol": "BTC/USDT",
            "timeframe": "1d",
            "calendar": "continuous_utc_fixed",
            "anchor_ts": anchor,
            "observations": rows,
        }
    )


def bind_controlled_fixture(
    *, recipe: Mapping[str, object], document: Mapping[str, object]
) -> ResearchInputSnapshot:
    """Reproduce before validating raw evidence, then require both exact identities."""
    expected = create_controlled_fixture(recipe)
    supplied = create_research_input_snapshot(document)
    if (
        supplied.canonical_bytes != expected.canonical_bytes
        or supplied.snapshot_id != expected.snapshot_id
    ):
        _fail("document does not match the reproduced controlled fixture")
    return expected
