from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import FrozenInstanceError
from decimal import Decimal
from types import MappingProxyType
from typing import cast

import pytest

from quant.engine.bar_coverage import BarClock, validate_bar_coverage
from quant.engine.temporal import ResearchInterval

_CALENDAR = "continuous_utc_fixed"
_CALENDAR_ERROR = "calendar must be continuous_utc_fixed"
_TIMEFRAME_ERROR = "timeframe must be one of 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w"
_COUNT_ERROR = "observations do not provide complete expected bar coverage"
_INTERVAL = ResearchInterval(0, 180_000)
_INVALID_TIMESTAMPS = (
    True, False, 1.0, 1.5, "60000", "", Decimal("60000"), None,
    float("nan"), float("inf"), object(),
)
# Independent exact unit fixtures, not an import of the production table.
_DURATIONS = (
    ("1m", 60_000), ("5m", 300_000), ("15m", 900_000),
    ("30m", 1_800_000), ("1h", 3_600_000), ("4h", 14_400_000),
    ("1d", 86_400_000), ("1w", 604_800_000),
)


def _row(open_ts: object, close_ts: object) -> dict[str, object]:
    return {"ts": open_ts, "close_ts": close_ts, "available_ts": close_ts}


def _rows() -> list[dict[str, object]]:
    return [_row(-60_000, 0), _row(0, 60_000), _row(60_000, 120_000)]


def _validate(
    observations: Sequence[Mapping[str, object]],
    *,
    interval: ResearchInterval = _INTERVAL,
    calendar: object = _CALENDAR,
    timeframe: object = "1m",
    anchor_ts: object = 0,
) -> tuple[BarClock, ...]:
    return validate_bar_coverage(
        interval, timeframe=timeframe, calendar=calendar,
        anchor_ts=anchor_ts, observations=observations,
    )


def _reject(
    observations: Sequence[Mapping[str, object]], message: str,
    caplog: pytest.LogCaptureFixture, *,
    interval: ResearchInterval = _INTERVAL,
    calendar: object = _CALENDAR, timeframe: object = "1m", anchor_ts: object = 0,
) -> None:
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger="quant.engine.bar_coverage"):
        with pytest.raises(ValueError) as error:
            _validate(
                observations, interval=interval, calendar=calendar,
                timeframe=timeframe, anchor_ts=anchor_ts,
            )
    assert str(error.value) == message
    assert caplog.record_tuples == [
        ("quant.engine.bar_coverage", logging.ERROR, message)
    ]


def _type_error(field: str) -> str:
    return (
        f"{field} must be an integer UTC epoch-millisecond timestamp "
        "(bool is not allowed)"
    )


@pytest.mark.parametrize(("timeframe", "duration"), _DURATIONS)
def test_canonical_units_with_explicit_shifted_anchor(
    timeframe: str, duration: int, caplog: pytest.LogCaptureFixture,
) -> None:
    anchor = 12_345
    start = anchor + duration
    end = anchor + 4 * duration
    rows = [
        _row(anchor, start),
        _row(start, anchor + 2 * duration),
        _row(anchor + 2 * duration, anchor + 3 * duration),
    ]
    with caplog.at_level(logging.DEBUG):
        result = _validate(
            rows, interval=ResearchInterval(start, end), timeframe=timeframe,
            anchor_ts=anchor,
        )
    assert result == (
        BarClock(anchor, start, start),
        BarClock(start, anchor + 2 * duration, anchor + 2 * duration),
        BarClock(anchor + 2 * duration, anchor + 3 * duration, anchor + 3 * duration),
    )
    assert not caplog.records


@pytest.mark.parametrize("anchor", [-120_001, -60_000, 0, 1, 10**100])
def test_signed_zero_and_unbounded_timestamps(anchor: int) -> None:
    assert _validate(
        [_row(anchor - 60_000, anchor)],
        interval=ResearchInterval(anchor, anchor + 60_000), anchor_ts=anchor,
    ) == (BarClock(anchor - 60_000, anchor, anchor),)


class Milliseconds(int):
    """A benign timestamp subclass with unchanged integer behavior."""


def test_benign_integer_subclass_preserved() -> None:
    anchor = Milliseconds(7)
    start = Milliseconds(7)
    end = Milliseconds(60_007)
    open_ts = Milliseconds(-59_993)
    close_ts = Milliseconds(7)
    available_ts = Milliseconds(7)
    result = _validate(
        [{"ts": open_ts, "close_ts": close_ts, "available_ts": available_ts}],
        interval=ResearchInterval(start, end), anchor_ts=anchor,
    )
    assert result == (BarClock(-59_993, 7, 7),)
    assert result[0].open_ts is open_ts
    assert result[0].close_ts is close_ts
    assert result[0].available_ts is available_ts


def test_one_duration_stage_includes_close_at_start_with_prior_open() -> None:
    assert _validate(
        [_row(-60_000, 0)], interval=ResearchInterval(0, 60_000),
    ) == (BarClock(-60_000, 0, 0),)


@pytest.mark.parametrize("close_ts", [-60_000, 180_000, 240_000])
def test_outside_close_rejects_without_filtering(
    close_ts: int, caplog: pytest.LogCaptureFixture,
) -> None:
    _reject(
        [_row(close_ts - 60_000, close_ts)],
        "observations[0].close_ts must be inside the half-open interval", caplog,
    )


def test_shared_boundary_close_belongs_only_to_touching_later_stage(
    caplog: pytest.LogCaptureFixture,
) -> None:
    rows = [_row(0, 60_000)]
    _reject(
        rows, "observations[0].close_ts must be inside the half-open interval",
        caplog, interval=ResearchInterval(0, 60_000),
    )
    caplog.clear()
    assert _validate(rows, interval=ResearchInterval(60_000, 120_000)) == (
        BarClock(0, 60_000, 60_000),
    )
    assert not caplog.records


@pytest.mark.parametrize("calendar", [
    None, "", " continuous_utc_fixed", "continuous_utc_fixed ",
    "CONTINUOUS_UTC_FIXED", "session", "monthly", True, 0, [], {}, object(),
])
def test_unsupported_calendars(
    calendar: object, caplog: pytest.LogCaptureFixture,
) -> None:
    _reject(_rows(), _CALENDAR_ERROR, caplog, calendar=calendar)


@pytest.mark.parametrize("timeframe", [
    None, "", "1mo", "1M", "1MO", "1m ", " 1m", "1H", "1wk", "2m",
    True, 1, [], {}, object(),
])
def test_unsupported_timeframes(
    timeframe: object, caplog: pytest.LogCaptureFixture,
) -> None:
    _reject(_rows(), _TIMEFRAME_ERROR, caplog, timeframe=timeframe)


@pytest.mark.parametrize("field", [
    "anchor_ts", "interval.start_ts", "interval.end_ts",
    "observations[0].ts", "observations[0].close_ts",
    "observations[0].available_ts",
])
@pytest.mark.parametrize("value", _INVALID_TIMESTAMPS)
def test_all_timestamp_slots_require_integer_not_bool(
    field: str, value: object, caplog: pytest.LogCaptureFixture,
) -> None:
    rows = _rows()
    start: object = 0
    end: object = 180_000
    anchor: object = 0
    if field == "anchor_ts":
        anchor = value
    elif field == "interval.start_ts":
        start = value
    elif field == "interval.end_ts":
        end = value
    else:
        rows[0][field.rsplit(".", 1)[1]] = value
    # Direct construction is unvalidated; deliberately malformed typed payloads.
    interval = ResearchInterval(cast(int, start), cast(int, end))
    _reject(rows, _type_error(field), caplog, interval=interval, anchor_ts=anchor)


@pytest.mark.parametrize("field", ["ts", "close_ts", "available_ts"])
def test_missing_row_evidence_is_not_inferred(
    field: str, caplog: pytest.LogCaptureFixture,
) -> None:
    rows = _rows()
    del rows[0][field]
    rows[0]["ingested_at"] = 0
    _reject(rows, _type_error(f"observations[0].{field}"), caplog)


@pytest.mark.parametrize(("start", "end"), [(0, 0), (60_000, 0), (1, -1)])
def test_equal_or_reversed_interval(
    start: int, end: int, caplog: pytest.LogCaptureFixture,
) -> None:
    _reject(
        _rows(), "interval.start_ts must be less than interval.end_ts", caplog,
        interval=ResearchInterval(start, end),
    )


@pytest.mark.parametrize(("start", "end", "message"), [
    (0, 180_007, "interval.start_ts must align with the declared bar grid"),
    (7, 180_000, "interval.end_ts must align with the declared bar grid"),
    (8, 180_008, "interval.start_ts must align with the declared bar grid"),
])
def test_endpoints_align_with_declared_anchor_not_epoch_zero(
    start: int, end: int, message: str, caplog: pytest.LogCaptureFixture,
) -> None:
    _reject(_rows(), message, caplog, interval=ResearchInterval(start, end),
            anchor_ts=7)


def test_misaligned_open(caplog: pytest.LogCaptureFixture) -> None:
    _reject(
        [_row(-59_999, 1)],
        "observations[0].ts must align with the declared bar grid", caplog,
    )


@pytest.mark.parametrize("close_ts", [-120_000, -60_000, -1, 60_000, 120_000])
def test_wrong_or_stretched_close_is_not_next_stored_open(
    close_ts: int, caplog: pytest.LogCaptureFixture,
) -> None:
    _reject(
        [_row(-60_000, close_ts)],
        "observations[0].close_ts must equal ts plus the declared timeframe duration",
        caplog,
    )


@pytest.mark.parametrize("available_ts", [-60_000, -1, 1, 60_000, 240_000])
def test_early_and_delayed_availability_unsupported_not_shifted(
    available_ts: int, caplog: pytest.LogCaptureFixture,
) -> None:
    row = _row(-60_000, 0)
    row["available_ts"] = available_ts
    _reject(
        [row],
        "observations[0].available_ts must equal close_ts for the supported clock",
        caplog,
    )


def test_empty_batch(caplog: pytest.LogCaptureFixture) -> None:
    _reject([], "observations must contain at least one stage observation", caplog)


@pytest.mark.parametrize("kept_indices", [(1, 2), (0, 2), (0, 1), (0,), (2,)])
def test_missing_first_middle_last_and_partial_batch(
    kept_indices: tuple[int, ...], caplog: pytest.LogCaptureFixture,
) -> None:
    rows = _rows()
    _reject([rows[index] for index in kept_indices], _COUNT_ERROR, caplog)


@pytest.mark.parametrize("conflicting", [False, True])
def test_all_duplicates_reject_including_conflicting_ohlcv(
    conflicting: bool, caplog: pytest.LogCaptureFixture,
) -> None:
    rows = _rows()
    duplicate = rows[0].copy()
    rows[0]["close"] = "10"
    duplicate["close"] = "20" if conflicting else "10"
    _reject(
        [rows[0], rows[1], duplicate],
        "observations[2].ts duplicates an earlier observation", caplog,
    )


@pytest.mark.parametrize("indices", [(2, 1, 0), (0, 2, 1), (1, 0, 2)])
def test_unsorted_batch_rejected_without_sorting(
    indices: tuple[int, ...], caplog: pytest.LogCaptureFixture,
) -> None:
    rows = _rows()
    _reject([rows[index] for index in indices],
            "observations must be strictly chronological", caplog)


@pytest.mark.parametrize(("rows", "index"), [
    ([_row(-120_000, -60_000), *_rows()], 0),
    ([*_rows(), _row(120_000, 180_000)], 3),
    ([*_rows(), _row(180_000, 240_000)], 3),
])
def test_context_warmup_and_later_rows_not_filtered(
    rows: list[dict[str, object]], index: int, caplog: pytest.LogCaptureFixture,
) -> None:
    before = deepcopy(rows)
    _reject(
        rows, f"observations[{index}].close_ts must be inside the half-open interval",
        caplog,
    )
    assert rows == before


def test_february_march_monthly_30_day_guess_rejected(
    caplog: pytest.LogCaptureFixture,
) -> None:
    february = 1_706_745_600_000  # 2024-02-01 UTC
    march = 1_709_251_200_000  # 2024-03-01 UTC
    guessed_close = february + 30 * 86_400_000
    _reject(
        [_row(february, guessed_close)], _TIMEFRAME_ERROR, caplog,
        interval=ResearchInterval(february, march), timeframe="1mo",
        anchor_ts=february,
    )


def test_enormous_interval_small_batch_uses_arithmetic_count(
    caplog: pytest.LogCaptureFixture,
) -> None:
    _reject(
        [_row(-60_000, 0)], _COUNT_ERROR, caplog,
        interval=ResearchInterval(0, 60_000 * 10**100),
    )


def test_detached_frozen_output_repeatability_and_ignored_extras(
    caplog: pytest.LogCaptureFixture,
) -> None:
    sentinel = object()
    nested = {"payload": [sentinel]}
    originals = _rows()
    originals[0]["extra"] = nested
    proxies = [MappingProxyType(row) for row in originals]
    with caplog.at_level(logging.DEBUG):
        result = _validate(proxies)
        assert _validate(proxies) == result
    assert result == (
        BarClock(-60_000, 0, 0), BarClock(0, 60_000, 60_000),
        BarClock(60_000, 120_000, 120_000),
    )
    assert originals[0]["extra"] is nested
    assert nested == {"payload": [sentinel]}
    assert not caplog.records
    originals[0]["ts"] = 999
    nested["payload"].clear()
    proxies.clear()
    originals.clear()
    assert result[0] == BarClock(-60_000, 0, 0)
    with pytest.raises(FrozenInstanceError):
        result[0].open_ts = 123
    with pytest.raises(FrozenInstanceError):
        result[0].close_ts = 123
    with pytest.raises(FrozenInstanceError):
        result[0].available_ts = 123
    assert isinstance(result, tuple)
    with pytest.raises(TypeError):
        result[0] = BarClock(1, 2, 2)  # type: ignore[index] - exercise tuple immutability


class Unprintable:
    """Error construction must not stringify untrusted payloads."""

    def __repr__(self) -> str:
        raise AssertionError("payload was serialized")

    def __str__(self) -> str:
        raise AssertionError("payload was serialized")


def test_no_invalid_payload_serialization(caplog: pytest.LogCaptureFixture) -> None:
    row = _row(Unprintable(), 0)
    row["private"] = Unprintable()
    _reject([row], _type_error("observations[0].ts"), caplog)


@pytest.mark.parametrize(("field", "value", "message"), [
    ("ts", None, _type_error("observations[1].ts")),
    ("close_ts", None, _type_error("observations[1].close_ts")),
    ("available_ts", None, _type_error("observations[1].available_ts")),
    ("close_ts", 60_000,
     "observations[1].close_ts must equal ts plus the declared timeframe duration"),
    ("available_ts", 1,
     "observations[1].available_ts must equal close_ts for the supported clock"),
])
def test_row_local_evidence_precedes_duplicate_and_missing_count(
    field: str, value: object, message: str, caplog: pytest.LogCaptureFixture,
) -> None:
    rows = [_rows()[0], _rows()[0].copy()]
    rows[1][field] = value
    _reject(rows, message, caplog)


@pytest.mark.parametrize(("calendar", "timeframe", "anchor", "message"), [
    (None, None, None, _CALENDAR_ERROR),
    (_CALENDAR, None, None, _TIMEFRAME_ERROR),
    (_CALENDAR, "1m", None, _type_error("anchor_ts")),
])
def test_top_level_failure_precedence(
    calendar: object, timeframe: object, anchor: object, message: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    _reject(
        [], message, caplog, calendar=calendar, timeframe=timeframe,
        anchor_ts=anchor, interval=ResearchInterval(True, False),
    )


@pytest.mark.parametrize(("start", "end", "message"), [
    (True, False, _type_error("interval.start_ts")),
    (0, False, _type_error("interval.end_ts")),
    (1, 1, "interval.start_ts must be less than interval.end_ts"),
    (1, 180_001, "interval.start_ts must align with the declared bar grid"),
])
def test_interval_failure_precedence(
    start: int, end: int, message: str, caplog: pytest.LogCaptureFixture,
) -> None:
    _reject([], message, caplog, interval=ResearchInterval(start, end))


def test_later_malformed_row_precedes_coverage_count(
    caplog: pytest.LogCaptureFixture,
) -> None:
    _reject(
        [_rows()[0], {"ts": None}], _type_error("observations[1].ts"), caplog,
    )


def test_row_type_order_and_open_alignment_precedence(
    caplog: pytest.LogCaptureFixture,
) -> None:
    _reject(
        [{"ts": 1, "close_ts": False, "available_ts": None}],
        _type_error("observations[0].close_ts"), caplog,
    )
    _reject(
        [{"ts": 1, "close_ts": 2, "available_ts": 3}],
        "observations[0].ts must align with the declared bar grid", caplog,
    )
