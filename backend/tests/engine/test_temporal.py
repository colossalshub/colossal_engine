from __future__ import annotations

import logging
from collections.abc import Iterator, Mapping
from copy import deepcopy
from dataclasses import FrozenInstanceError
from decimal import Decimal
from types import MappingProxyType

import pytest

from quant.engine.temporal import (
    ResearchDeclaration,
    ResearchInterval,
    ResearchStage,
    validate_research_declaration,
)

_NAMES = ("in_sample", "validation", "oos")
_FIELDS = tuple(
    f"{name}_{endpoint}_ts" for name in _NAMES for endpoint in ("start", "end")
)
_STAGE_ERROR = "research_stage must be exploration, validation, oos, or None"
_INVALID_POINTS = (True, False, 1.0, 1.5, "1", "", Decimal("1"), float("nan"),
                   float("inf"), object())


def _pair(name: str, start: object, end: object) -> dict[str, object]:
    return {f"{name}_start_ts": start, f"{name}_end_ts": end}


def _all_ranges(stage: ResearchStage = "exploration") -> dict[str, object]:
    return {
        "research_stage": stage,
        **_pair("in_sample", -10, 0),
        **_pair("validation", 0, 10),
        **_pair("oos", 10, 20),
    }


def _reject(
    metadata: dict[str, object], message: str, caplog: pytest.LogCaptureFixture,
) -> None:
    before = metadata.copy()
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger="quant.engine.temporal"):
        with pytest.raises(ValueError) as error:
            validate_research_declaration(metadata)
    assert str(error.value) == message
    assert caplog.record_tuples == [("quant.engine.temporal", logging.ERROR, message)]
    assert metadata == before


class StageOnlyMapping(Mapping[str, object]):
    """Any read except the null stage would violate ordinary compatibility."""

    def __init__(self, omitted: bool) -> None:
        self.omitted = omitted
        self.reads: list[str] = []

    def __getitem__(self, key: str) -> object:
        self.reads.append(key)
        if key != "research_stage":
            raise AssertionError(f"unexpected endpoint read: {key}")
        if self.omitted:
            raise KeyError(key)
        return None

    def __iter__(self) -> Iterator[str]:
        return iter(()) if self.omitted else iter(("research_stage",))

    def __len__(self) -> int:
        return 0 if self.omitted else 1


@pytest.mark.parametrize("omitted", [False, True])
def test_ordinary_exit_reads_only_stage(
    omitted: bool, caplog: pytest.LogCaptureFixture,
) -> None:
    metadata = StageOnlyMapping(omitted)
    with caplog.at_level(logging.DEBUG):
        assert validate_research_declaration(metadata) is None
    assert metadata.reads == ["research_stage"]
    assert not caplog.records


@pytest.mark.parametrize("omitted", [False, True])
@pytest.mark.parametrize("legacy", [
    {}, dict.fromkeys(_FIELDS), _pair("in_sample", 1, None),
    _pair("validation", 5, 5), _pair("oos", 9, -1),
    {**_pair("in_sample", 0, 20), **_pair("validation", 10, 30)},
    {**_pair("in_sample", True, False), **_pair("oos", "bad", "bad")},
])
def test_ordinary_ignores_malformed_legacy_ranges(
    omitted: bool, legacy: dict[str, object], caplog: pytest.LogCaptureFixture,
) -> None:
    metadata = dict(legacy)
    if not omitted:
        metadata["research_stage"] = None
    before = deepcopy(metadata)
    with caplog.at_level(logging.DEBUG):
        assert validate_research_declaration(metadata) is None
    assert metadata == before
    assert not caplog.records


@pytest.mark.parametrize("stage", [
    "", " exploration", "oos ", "Exploration", "OOS", "is", "walk_forward",
    "null", True, False, 1, 0, [], {}, object(),
])
def test_unsupported_stages_are_logged_value_errors(
    stage: object, caplog: pytest.LogCaptureFixture,
) -> None:
    _reject({"research_stage": stage}, _STAGE_ERROR, caplog)


@pytest.mark.parametrize("stage,names,active_name", [
    ("exploration", (), None),
    ("exploration", ("in_sample",), "in_sample"),
    ("exploration", ("validation",), None),
    ("exploration", ("oos",), None),
    ("exploration", ("validation", "oos"), None),
    ("exploration", _NAMES, "in_sample"),
    ("validation", ("in_sample", "validation"), "validation"),
    ("validation", _NAMES, "validation"),
    ("oos", ("in_sample", "oos"), "oos"),
    ("oos", _NAMES, "oos"),
])
def test_stage_applicability_and_exact_records(
    stage: ResearchStage, names: tuple[str, ...], active_name: str | None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    metadata: dict[str, object] = {"research_stage": stage}
    intervals = {"in_sample": ResearchInterval(-10, 0),
                 "validation": ResearchInterval(0, 10), "oos": ResearchInterval(10, 20)}
    for name in names:
        interval = intervals[name]
        metadata.update(_pair(name, interval.start_ts, interval.end_ts))
    before = metadata.copy()
    with caplog.at_level(logging.DEBUG):
        result = validate_research_declaration(MappingProxyType(metadata))
        repeated = validate_research_declaration(metadata)
    assert result == repeated == ResearchDeclaration(
        stage, *(intervals[name] if name in names else None for name in _NAMES),
    )
    assert result is not None
    assert result.active_range == (intervals[active_name] if active_name else None)
    assert metadata == before
    assert not caplog.records


@pytest.mark.parametrize("explicit_null", [False, True])
@pytest.mark.parametrize("stage,missing", [
    ("validation", "in_sample"), ("validation", "validation"),
    ("oos", "in_sample"), ("oos", "oos"),
])
def test_missing_required_ranges(
    explicit_null: bool, stage: ResearchStage, missing: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    metadata = _all_ranges(stage)
    for endpoint in ("start", "end"):
        field = f"{missing}_{endpoint}_ts"
        if explicit_null:
            metadata[field] = None
        else:
            del metadata[field]
    _reject(metadata, f"{stage} research_stage requires {missing} range", caplog)


@pytest.mark.parametrize("name", _NAMES)
@pytest.mark.parametrize("endpoint", ["start", "end"])
@pytest.mark.parametrize("absent", ["omitted", "null"])
def test_every_optional_pair_requires_both_endpoints(
    name: str, endpoint: str, absent: str, caplog: pytest.LogCaptureFixture,
) -> None:
    metadata: dict[str, object] = {"research_stage": "exploration"}
    metadata[f"{name}_{endpoint}_ts"] = 1
    other = "end" if endpoint == "start" else "start"
    if absent == "null":
        metadata[f"{name}_{other}_ts"] = None
    _reject(
        metadata,
        f"{name}_start_ts and {name}_end_ts must be supplied together",
        caplog,
    )


@pytest.mark.parametrize("name", _NAMES)
@pytest.mark.parametrize("start,end", [(1, 1), (2, 1)])
def test_every_optional_pair_requires_increasing_bounds(
    name: str, start: int, end: int, caplog: pytest.LogCaptureFixture,
) -> None:
    _reject({"research_stage": "exploration", **_pair(name, start, end)},
            f"{name}_start_ts must be less than {name}_end_ts", caplog)


@pytest.mark.parametrize("stage,name", [("validation", "oos"), ("oos", "validation")])
@pytest.mark.parametrize("start,end,suffix", [
    (1, None, "pair"), (2, 1, "order"), (True, 10, "type"),
])
def test_invalid_inactive_ranges_are_checked(
    stage: ResearchStage, name: str, start: object, end: object, suffix: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    metadata = _all_ranges(stage)
    metadata.update(_pair(name, start, end))
    messages = {
        "pair": f"{name}_start_ts and {name}_end_ts must be supplied together",
        "order": f"{name}_start_ts must be less than {name}_end_ts",
        "type": (f"{name}_start_ts must be an integer UTC epoch-millisecond timestamp "
                 "(bool is not allowed)"),
    }
    _reject(metadata, messages[suffix], caplog)


@pytest.mark.parametrize("field", _FIELDS)
@pytest.mark.parametrize("value", _INVALID_POINTS)
def test_each_endpoint_rejects_noninteger_without_coercion(
    field: str, value: object, caplog: pytest.LogCaptureFixture,
) -> None:
    metadata = _all_ranges()
    metadata[field] = value
    _reject(metadata, f"{field} must be an integer UTC epoch-millisecond timestamp "
            "(bool is not allowed)", caplog)


class IntegerSubclass(int):
    pass


@pytest.mark.parametrize("start,end", [(-10, 0), (0, 1), (-10**100, 10**100),
                                      (10**100, 10**100 + 1),
                                      (IntegerSubclass(-1), IntegerSubclass(0))])
def test_signed_zero_unbounded_and_subclass_integers_are_preserved(
    start: int, end: int,
) -> None:
    result = validate_research_declaration({
        "research_stage": "exploration", **_pair("in_sample", start, end),
    })
    assert result is not None
    assert result.in_sample == ResearchInterval(start, end)
    assert result.in_sample is not None
    assert result.in_sample.start_ts is start
    assert result.in_sample.end_ts is end
    assert result.in_sample.contains(start)
    assert not result.in_sample.contains(end)


@pytest.mark.parametrize("previous,following", [
    ("in_sample", "validation"), ("validation", "oos"), ("in_sample", "oos"),
])
@pytest.mark.parametrize("first,second", [
    ((0, 10), (9, 20)), ((0, 20), (5, 10)), ((0, 10), (0, 10)),
    ((20, 30), (0, 10)),
])
def test_present_ranges_reject_overlap_nesting_and_reverse_semantic_order(
    previous: str, following: str, first: tuple[int, int], second: tuple[int, int],
    caplog: pytest.LogCaptureFixture,
) -> None:
    _reject({"research_stage": "exploration", **_pair(previous, *first),
             **_pair(following, *second)},
            f"{previous} range must end at or before {following} range starts", caplog)


@pytest.mark.parametrize("previous,following", [
    ("in_sample", "validation"), ("validation", "oos"), ("in_sample", "oos"),
])
@pytest.mark.parametrize("next_start", [10, 11])
def test_touching_and_one_millisecond_separation_preserve_boundaries(
    previous: str, following: str, next_start: int,
) -> None:
    result = validate_research_declaration({"research_stage": "exploration",
                                          **_pair(previous, 0, 10),
                                          **_pair(following, next_start, 20)})
    assert result is not None
    assert getattr(result, previous) == ResearchInterval(0, 10)
    assert getattr(result, following) == ResearchInterval(next_start, 20)


@pytest.mark.parametrize("name", _NAMES)
def test_half_open_point_membership_at_every_interval_boundary(name: str) -> None:
    declaration = validate_research_declaration(_all_ranges("oos"))
    assert declaration is not None
    interval = getattr(declaration, name)
    assert isinstance(interval, ResearchInterval)
    points = (interval.start_ts - 1, interval.start_ts, interval.end_ts - 1,
              interval.end_ts, interval.end_ts + 1)
    assert [interval.contains(point) for point in points] == [
        False, True, True, False, False,
    ]
    assert [getattr(declaration, range_name).contains(0) for range_name in _NAMES] == [
        False, True, False,
    ]
    assert [getattr(declaration, range_name).contains(10) for range_name in _NAMES] == [
        False, False, True,
    ]


@pytest.mark.parametrize("value", _INVALID_POINTS)
def test_invalid_contains_argument_logs_once_and_raises(
    value: object, caplog: pytest.LogCaptureFixture,
) -> None:
    message = ("timestamp must be an integer UTC epoch-millisecond timestamp "
               "(bool is not allowed)")
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(ValueError) as error:
            ResearchInterval(-10, 20).contains(value)
    assert str(error.value) == message
    assert caplog.record_tuples == [("quant.engine.temporal", logging.ERROR, message)]


@pytest.mark.parametrize("metadata,message", [
    ({"research_stage": [], "in_sample_start_ts": True}, _STAGE_ERROR),
    ({"research_stage": "oos", "validation_start_ts": True},
     "validation_start_ts and validation_end_ts must be supplied together"),
    ({"research_stage": "validation", **_pair("oos", 2, 1)},
     "oos_start_ts must be less than oos_end_ts"),
    ({"research_stage": "oos"}, "oos research_stage requires in_sample range"),
    ({"research_stage": "oos", **_pair("in_sample", 20, 30),
      **_pair("validation", 0, 10)}, "oos research_stage requires oos range"),
    ({"research_stage": "exploration", **_pair("in_sample", 20, 30),
      **_pair("validation", 0, 10), **_pair("oos", -20, -10)},
     "in_sample range must end at or before validation range starts"),
])
def test_first_failure_precedence(
    metadata: dict[str, object], message: str, caplog: pytest.LogCaptureFixture,
) -> None:
    _reject(metadata, message, caplog)


@pytest.mark.parametrize("outcome", ["valid", "ordinary", "stage", "pair", "type",
                                      "bounds", "required", "order"])
def test_nested_unrelated_caller_data_remains_unchanged(
    outcome: str, caplog: pytest.LogCaptureFixture,
) -> None:
    metadata = _all_ranges("oos")
    extra = {"params": {"secret": ["caller-only-value"]}, "start_ts": -999,
             "end_ts": 999, "minimum_gap_ms": object(), "coverage": [],
             "selection": {"frozen": False}, "experiment_id": "untouched"}
    metadata.update(extra)
    messages = {
        "stage": _STAGE_ERROR,
        "pair": "oos_start_ts and oos_end_ts must be supplied together",
        "type": ("oos_start_ts must be an integer UTC epoch-millisecond timestamp "
                 "(bool is not allowed)"),
        "bounds": "oos_start_ts must be less than oos_end_ts",
        "required": "oos research_stage requires oos range",
        "order": "validation range must end at or before oos range starts",
    }
    changes: dict[str, dict[str, object]] = {
        "valid": {}, "ordinary": {"research_stage": None},
        "stage": {"research_stage": "bad"}, "pair": {"oos_end_ts": None},
        "type": {"oos_start_ts": True}, "bounds": _pair("oos", 20, 10),
        "required": _pair("oos", None, None), "order": _pair("oos", 9, 20),
    }
    metadata.update(changes[outcome])
    nested_before = deepcopy(metadata["params"])
    if outcome in messages:
        _reject(metadata, messages[outcome], caplog)
        assert "caller-only-value" not in caplog.text
    else:
        before = metadata.copy()
        with caplog.at_level(logging.DEBUG):
            result = validate_research_declaration(metadata)
        assert metadata == before
        assert not caplog.records
        if outcome == "valid":
            assert result == validate_research_declaration(_all_ranges("oos"))
        else:
            assert result is None
    assert metadata["params"] == nested_before
    for key, value in extra.items():
        assert metadata[key] is value


def test_returned_declaration_and_nested_intervals_are_frozen_and_detached() -> None:
    metadata = _all_ranges("validation")
    declaration = validate_research_declaration(metadata)
    assert declaration is not None
    with pytest.raises(FrozenInstanceError):
        declaration.research_stage = "oos"
    for name in _NAMES:
        interval = getattr(declaration, name)
        with pytest.raises(FrozenInstanceError):
            interval.start_ts = 100
    metadata.update(_pair("in_sample", 100, 200))
    assert declaration.in_sample == ResearchInterval(-10, 0)
    assert declaration.active_range is declaration.validation
