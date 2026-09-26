"""`GET /api/runs` — paginated, filterable run history (PROJECT.md §4.4).

This is the first real router and the template for Phase 3.4
(`get_tearsheet`) and 3.5 (`get_trades`).

Note on error shape: this module raises `HTTPException` with a `detail`
dict shaped like `ApiErrorDetail` (i.e. `{"error": {"code", "message",
"details"}}`). FastAPI's default `HTTPException` handler serializes that
dict verbatim under the top-level `detail` key, which does not yet match
§4.4's flat `ApiError` envelope. Phase 3.6's `main.py` is responsible for
installing a global exception handler that unwraps `exc.detail` into a
proper `ApiError` response. Until then, callers of this router directly
(as in this phase's tests) will see the `{"detail": {"error": {...}}}`
shape on 4xx/5xx responses.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Annotated, Any, Literal

from fastapi import APIRouter, HTTPException, Query, status

from quant.api.deps import RunsDb
from quant.api.schemas import ApiError, RunList, RunSummary

router = APIRouter(prefix="/api/runs", tags=["runs"])

_VALID_STATUSES: frozenset[str] = frozenset(
    {"queued", "running", "done", "failed", "archived"}
)


def _parse_json_or(default: Any, value: str | None) -> Any:
    if value is None:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


def _extract_universe(raw: str | None) -> list[str]:
    parsed = _parse_json_or([], raw)
    if not isinstance(parsed, list):
        return []
    return [item for item in parsed if isinstance(item, str)]


def _numeric_or_none(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def _extract_metrics(
    raw: str | None,
) -> tuple[float | None, float | None, float | None]:
    parsed = _parse_json_or({}, raw)
    if not isinstance(parsed, dict):
        return None, None, None
    sharpe = _numeric_or_none(parsed.get("sharpe"))
    cagr = _numeric_or_none(parsed.get("cagr"))
    max_drawdown = _numeric_or_none(parsed.get("max_drawdown"))
    return sharpe, cagr, max_drawdown


def _row_to_summary(row: sqlite3.Row) -> RunSummary:
    raw_status = row["status"]
    if raw_status not in _VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL",
                    "message": f"meta_runs contains invalid status {raw_status!r}",
                    "details": None,
                }
            },
        )
    valid_status: Literal["queued", "running", "done", "failed", "archived"] = (
        raw_status
    )

    sharpe, cagr, max_drawdown = _extract_metrics(row["metrics"])

    return RunSummary(
        run_id=row["run_id"],
        name=row["name"],
        strategy=row["strategy"],
        universe=_extract_universe(row["universe"]),
        start_ts=row["start_ts"],
        end_ts=row["end_ts"],
        created_at=row["created_at"],
        git_sha=row["git_sha"],
        git_dirty=bool(row["git_dirty"]),
        status=valid_status,
        sharpe=sharpe,
        cagr=cagr,
        max_drawdown=max_drawdown,
    )


@router.get(
    "",
    response_model=RunList,
    responses={500: {"model": ApiError}},
)
def list_runs(
    db: RunsDb,
    strategy: Annotated[str | None, Query()] = None,
    status_: Annotated[
        Literal["queued", "running", "done", "failed", "archived"] | None,
        Query(alias="status"),
    ] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=500)] = 50,
) -> RunList:
    db.row_factory = sqlite3.Row

    where_clauses: list[str] = []
    params: list[str] = []
    if strategy is not None:
        where_clauses.append("strategy = ?")
        params.append(strategy)
    if status_ is not None:
        where_clauses.append("status = ?")
        params.append(status_)
    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    try:
        count_row = db.execute(
            f"SELECT COUNT(*) FROM meta_runs{where_sql}", params
        ).fetchone()
        total = int(count_row[0]) if count_row else 0

        offset = (page - 1) * page_size
        rows = db.execute(
            f"""
            SELECT run_id, name, strategy, universe, start_ts, end_ts, created_at,
                   git_sha, git_dirty, status, metrics
            FROM meta_runs{where_sql}
            ORDER BY created_at DESC, run_id ASC
            LIMIT ? OFFSET ?
            """,
            [*params, page_size, offset],
        ).fetchall()
    except sqlite3.DatabaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {"code": "INTERNAL", "message": str(exc), "details": None}
            },
        ) from exc

    summaries = [_row_to_summary(row) for row in rows]

    return RunList(
        items=summaries,
        total=total,
        page=page,
        page_size=page_size,
    )
