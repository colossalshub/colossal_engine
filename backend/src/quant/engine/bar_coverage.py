"""Check supplied fixed-grid clocks and coverage, without runtime certification.

Caller declarations do not establish actual historical publication or calendar
truth. No execution caller is wired here. Direct BarClock construction does not
perform validation. Delayed, session and monthly clocks are unsupported.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import NoReturn

from quant.engine.temporal import ResearchInterval

logger = logging.getLogger(__name__)

# Established elapsed units; avoid importing execution/third-party dependencies.
_DURATION_MS = {
    "1m": 60_000,
    "5m": 300_000,
    "15m": 900_000,
    "30m": 1_800_000,
    "1h": 3_600_000,
    "4h": 14_400_000,
    "1d": 86_400_000,
    "1w": 604_800_000,
}


@dataclass(frozen=True)
class BarClock:
    """Detached supplied timestamps, not a source-history or eligibility flag."""

    open_ts: int
    close_ts: int
    available_ts: int


def _fail(message: str) -> NoReturn:
    logger.error(message)
    raise ValueError(message)


def _integer_timestamp(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        _fail(
            f"{field} must be an integer UTC epoch-millisecond timestamp "
            "(bool is not allowed)"
        )
    return value


def validate_bar_coverage(
    interval: ResearchInterval,
    *,
    timeframe: object,
    calendar: object,
    anchor_ts: object,
    observations: Sequence[Mapping[str, object]],
) -> tuple[BarClock, ...]:
    """Validate the exact ordered active-stage batch on an explicit UTC grid.

    Close and availability must be explicitly supplied and equal for this
    supported zero-delay clock. Half-open close membership permits a prior-open
    first bar, but certifies no preboundary exposure, scoring or causal warmup.
    Never filter, sort, repair, infer missing evidence or build an expected
    schedule: actual-row validation and arithmetic count use O(n) work/memory.
    """
    if not isinstance(calendar, str) or calendar != "continuous_utc_fixed":
        _fail("calendar must be continuous_utc_fixed")
    if not isinstance(timeframe, str) or timeframe not in _DURATION_MS:
        _fail("timeframe must be one of 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w")
    duration = _DURATION_MS[timeframe]
    anchor = _integer_timestamp(anchor_ts, "anchor_ts")
    start = _integer_timestamp(interval.start_ts, "interval.start_ts")
    end = _integer_timestamp(interval.end_ts, "interval.end_ts")
    if start >= end:
        _fail("interval.start_ts must be less than interval.end_ts")
    if (start - anchor) % duration:
        _fail("interval.start_ts must align with the declared bar grid")
    if (end - anchor) % duration:
        _fail("interval.end_ts must align with the declared bar grid")

    clocks: list[BarClock] = []
    seen_opens: set[int] = set()
    previous_open: int | None = None
    for index, row in enumerate(observations):
        field = f"observations[{index}]"
        open_ts = _integer_timestamp(row.get("ts"), f"{field}.ts")
        close_ts = _integer_timestamp(row.get("close_ts"), f"{field}.close_ts")
        available_ts = _integer_timestamp(
            row.get("available_ts"), f"{field}.available_ts"
        )
        if (open_ts - anchor) % duration:
            _fail(f"{field}.ts must align with the declared bar grid")
        if close_ts != open_ts + duration:
            _fail(
                f"{field}.close_ts must equal ts plus the declared timeframe duration"
            )
        if available_ts != close_ts:
            _fail(f"{field}.available_ts must equal close_ts for the supported clock")
        if not start <= close_ts < end:
            _fail(f"{field}.close_ts must be inside the half-open interval")
        if open_ts in seen_opens:
            _fail(f"{field}.ts duplicates an earlier observation")
        if previous_open is not None and open_ts <= previous_open:
            _fail("observations must be strictly chronological")
        seen_opens.add(open_ts)
        previous_open = open_ts
        clocks.append(BarClock(open_ts, close_ts, available_ts))

    if not clocks:
        _fail("observations must contain at least one stage observation")
    # Aligned, unique in-range closes plus this count prove the complete grid.
    if len(clocks) != (end - start) // duration:
        _fail("observations do not provide complete expected bar coverage")
    return tuple(clocks)
