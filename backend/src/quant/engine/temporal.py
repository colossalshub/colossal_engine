"""Pure research-range declarations, without runtime eligibility guarantees.

The factory validates declarations only. Direct value-record construction does
not perform admission validation. No caller is wired to this helper yet.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, NoReturn, cast

logger = logging.getLogger(__name__)

ResearchStage = Literal["exploration", "validation", "oos"]


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


@dataclass(frozen=True)
class ResearchInterval:
    """Immutable [start,end) declaration; construction itself is unvalidated."""

    start_ts: int
    end_ts: int

    def contains(self, timestamp: object) -> bool:
        """Check integer point membership, not event or bar availability."""
        point = _integer_timestamp(timestamp, "timestamp")
        return self.start_ts <= point < self.end_ts


@dataclass(frozen=True)
class ResearchDeclaration:
    """Immutable declared ranges, not proof of execution or research validity."""

    research_stage: ResearchStage
    in_sample: ResearchInterval | None
    validation: ResearchInterval | None
    oos: ResearchInterval | None

    @property
    def active_range(self) -> ResearchInterval | None:
        """Return the stage's declared range without inferring a missing IS."""
        if self.research_stage == "exploration":
            return self.in_sample
        if self.research_stage == "validation":
            return self.validation
        return self.oos


def _read_interval(
    metadata: Mapping[str, object], range_name: str,
) -> ResearchInterval | None:
    start_field = f"{range_name}_start_ts"
    end_field = f"{range_name}_end_ts"
    start = metadata.get(start_field)
    end = metadata.get(end_field)
    if start is None and end is None:
        return None
    if start is None or end is None:
        _fail(f"{start_field} and {end_field} must be supplied together")
    start_ts = _integer_timestamp(start, start_field)
    end_ts = _integer_timestamp(end, end_field)
    if start_ts >= end_ts:
        _fail(f"{start_field} must be less than {end_field}")
    return ResearchInterval(start_ts, end_ts)


def validate_research_declaration(
    metadata: Mapping[str, object],
) -> ResearchDeclaration | None:
    """Validate only stage applicability, pairs and chronological nonoverlap.

    Missing and null stages are ordinary runs, returned before reading endpoints.
    Missing endpoints equal explicit nulls. Unrelated metadata is ignored. All
    supplied ranges are checked in IS, validation, OOS order without repair or
    sorting. Touching endpoints imply no gap or execution eligibility guarantee.
    """
    stage = metadata.get("research_stage")
    if stage is None:
        return None
    if not isinstance(stage, str) or stage not in ("exploration", "validation", "oos"):
        _fail("research_stage must be exploration, validation, oos, or None")
    research_stage = cast(ResearchStage, stage)

    in_sample = _read_interval(metadata, "in_sample")
    validation = _read_interval(metadata, "validation")
    oos = _read_interval(metadata, "oos")

    if research_stage in ("validation", "oos") and in_sample is None:
        _fail(f"{research_stage} research_stage requires in_sample range")
    if research_stage == "validation" and validation is None:
        _fail("validation research_stage requires validation range")
    if research_stage == "oos" and oos is None:
        _fail("oos research_stage requires oos range")

    previous: tuple[str, ResearchInterval] | None = None
    for name, interval in (
        ("in_sample", in_sample), ("validation", validation), ("oos", oos),
    ):
        if interval is None:
            continue
        if previous is not None and previous[1].end_ts > interval.start_ts:
            _fail(f"{previous[0]} range must end at or before {name} range starts")
        previous = (name, interval)

    return ResearchDeclaration(research_stage, in_sample, validation, oos)
