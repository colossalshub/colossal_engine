"""`GET /api/data/coverage` — per-month bar coverage from curated_bars."""

from __future__ import annotations

import calendar
import math

import duckdb
from fastapi import APIRouter, HTTPException, status

from quant.api.deps import BarsDb
from quant.api.schemas import ApiError, CoverageCell, CoverageResponse, CoverageRow

router = APIRouter(prefix="/api/data", tags=["data"])

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
