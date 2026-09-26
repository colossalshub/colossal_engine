"""`GET /api/data/coverage` — per-month bar coverage from curated_bars."""

from __future__ import annotations

import calendar
import math
import subprocess
import sys
from pathlib import Path

import duckdb
from fastapi import APIRouter, HTTPException, status

from quant.api.deps import BarsDb
from quant.api.schemas import (
    ApiError,
    CoverageCell,
    CoverageResponse,
    CoverageRow,
    IngestRequest,
    IngestResponse,
)

router = APIRouter(prefix="/api/data", tags=["data"])

_VALID_TIMEFRAMES = frozenset({"1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1mo"})


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    msg = "cannot find repo root (pyproject.toml)"
    raise RuntimeError(msg)


_TIMEFRAME_BARS_PER_DAY: dict[str, float] = {
    "1m": 1440.0,
    "5m": 288.0,
    "15m": 96.0,
    "30m": 48.0,
    "1h": 24.0,
    "4h": 6.0,
    "1d": 1.0,
    "1w": 1.0 / 7.0,
    "1mo": 1.0 / 30.0,
}

_COVERAGE_SQL = """
SELECT
    venue,
    symbol,
    timeframe,
    CAST(strftime(to_timestamp(ts / 1000.0), '%Y') AS INTEGER) AS year,
    CAST(strftime(to_timestamp(ts / 1000.0), '%m') AS INTEGER) AS month,
    COUNT(*) AS bars
FROM curated_bars
GROUP BY venue, symbol, timeframe, year, month
ORDER BY venue, symbol, timeframe, year, month
"""


def _expected_for_month(timeframe: str, year: int, month: int) -> int:
    multiplier = _TIMEFRAME_BARS_PER_DAY[timeframe]
    days = calendar.monthrange(year, month)[1]
    return max(1, math.ceil(days * multiplier))


@router.get(
    "/coverage",
    response_model=CoverageResponse,
    responses={500: {"model": ApiError}},
)
def get_coverage(bars_db: BarsDb) -> CoverageResponse:
    try:
        raw_rows = bars_db.execute(_COVERAGE_SQL).fetchall()
    except duckdb.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL",
                    "message": str(exc),
                    "details": None,
                }
            },
        ) from exc

    grouped: dict[tuple[str, str, str], list[CoverageCell]] = {}
    for venue, symbol, timeframe, year, month, bars in raw_rows:
        tf = str(timeframe)
        if tf not in _TIMEFRAME_BARS_PER_DAY:
            continue
        yr = int(year)
        mo = int(month)
        bar_count = int(bars)
        expected = _expected_for_month(tf, yr, mo)
        coverage = min(1.0, max(0.0, bar_count / expected))
        key = (str(venue), str(symbol), tf)
        cell = CoverageCell(
            year=yr,
            month=mo,
            bars=bar_count,
            expected=expected,
            coverage=coverage,
        )
        grouped.setdefault(key, []).append(cell)

    rows: list[CoverageRow] = []
    for venue, symbol, timeframe in sorted(grouped.keys()):
        cells = sorted(
            grouped[(venue, symbol, timeframe)],
            key=lambda c: (c.year, c.month),
        )
        rows.append(
            CoverageRow(
                venue=venue,
                symbol=symbol,
                timeframe=timeframe,
                cells=cells,
            )
        )

    return CoverageResponse(rows=rows)


@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=202,
    responses={422: {"model": ApiError}, 500: {"model": ApiError}},
)
def post_ingest(payload: IngestRequest) -> IngestResponse:
    if payload.timeframe not in _VALID_TIMEFRAMES:
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "VALIDATION",
                    "message": f"invalid timeframe: {payload.timeframe}",
                    "details": None,
                }
            },
        )
    if not payload.start or not payload.end:
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "VALIDATION",
                    "message": "start and end are required",
                    "details": None,
                }
            },
        )

    argv = [
        sys.executable,
        str(_repo_root() / "scripts" / "ingest_bars.py"),
        "--venue",
        payload.venue,
        "--symbol",
        payload.symbol,
        "--timeframe",
        payload.timeframe,
        "--start",
        payload.start,
        "--end",
        payload.end,
    ]

    try:
        subprocess.Popen(  # noqa: S603 — inputs are validated above
            argv,
            cwd=str(_repo_root()),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "INTERNAL",
                    "message": str(exc),
                    "details": None,
                }
            },
        ) from exc

    return IngestResponse(status="started", command=" ".join(argv))
