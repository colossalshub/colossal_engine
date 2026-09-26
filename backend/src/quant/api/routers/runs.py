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

Note on `get_tearsheet`'s `verification` block (§4.3): the discrepancy is
recomputed here directly from `equity.parquet`'s own `equity` column (see
`_build_verification`). This is trivially self-consistent because that
parquet was written from the same reconstructed snapshot series produced
by Phase 2.2.2/2.3 (`extract.equity.extract_equity`) — it proves the
parquet is internally coherent, not that it independently matches
Nautilus's account balance. The authoritative discrepancy check against
`ending_balance` happens once, at extraction time; this endpoint does not
have access to `ending_balance` and does not attempt to re-derive it.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from typing import Annotated, Any, Literal, cast

import pyarrow.parquet as pq  # type: ignore[import-untyped]  # pyarrow ships without py.typed
from fastapi import APIRouter, HTTPException, Query, status
from fastapi import Path as PathParam

from quant.api.deps import RunsDb, get_artifacts_dir
from quant.api.schemas import (
    OHLCV,
    ApiError,
    DrawdownPoint,
    EquityPoint,
    KpiBlock,
    MonthlyReturns,
    RunList,
    RunSummary,
    TearSheet,
    Trade,
    TradeMarker,
    TradePage,
    Verification,
)

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


def _kpi_block_from_metrics(metrics_dict: dict[str, Any]) -> KpiBlock:
    return KpiBlock(
        sharpe=_numeric_or_none(metrics_dict.get("sharpe")),
        sortino=_numeric_or_none(metrics_dict.get("sortino")),
        cagr=_numeric_or_none(metrics_dict.get("cagr")),
        volatility=_numeric_or_none(metrics_dict.get("volatility")),
        max_drawdown=_numeric_or_none(metrics_dict.get("max_drawdown")),
        calmar=_numeric_or_none(metrics_dict.get("calmar")),
        win_rate=_numeric_or_none(metrics_dict.get("win_rate")),
        profit_factor=_numeric_or_none(metrics_dict.get("profit_factor")),
        turnover=_numeric_or_none(metrics_dict.get("turnover")),
        total_trades=_numeric_or_none(metrics_dict.get("total_trades")),
        avg_duration_days=_numeric_or_none(metrics_dict.get("avg_duration_days")),
    )


def _sorted_dedup(
    rows: list[dict[str, Any]], ts_key: str = "ts"
) -> list[dict[str, Any]]:
    """Sort by `ts_key` ascending, keeping the first row for each duplicate ts."""
    seen: set[int] = set()
    result: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda r: r[ts_key]):
        ts = int(row[ts_key])
        if ts in seen:
            continue
        seen.add(ts)
        result.append(row)
    return result


def _build_markers(trades_rows: list[dict[str, Any]]) -> list[TradeMarker]:
    markers: list[TradeMarker] = []
    for trade in trades_rows:
        side = trade["side"]
        entry_side: Literal["buy", "sell"] = "buy" if side == "long" else "sell"
        markers.append(
            TradeMarker(
                ts=int(trade["entry_ts"]),
                side=entry_side,
                price=float(trade["entry_px"]),
                qty=float(trade["qty"]),
            )
        )
        exit_ts = trade.get("exit_ts")
        exit_px = trade.get("exit_px")
        if exit_ts is not None and exit_px is not None:
            exit_side: Literal["buy", "sell"] = "sell" if side == "long" else "buy"
            markers.append(
                TradeMarker(
                    ts=int(exit_ts),
                    side=exit_side,
                    price=float(exit_px),
                    qty=float(trade["qty"]),
                )
            )
    markers.sort(key=lambda m: m.ts)
    return markers


def _build_monthly_returns(equity_points: list[EquityPoint]) -> list[MonthlyReturns]:
    if not equity_points:
        return []

    by_month: dict[tuple[int, int], float] = {}
    for point in equity_points:
        dt = datetime.fromtimestamp(point.ts / 1000, tz=UTC)
        by_month[(dt.year, dt.month)] = point.equity

    first_equity = equity_points[0].equity
    monthly: dict[tuple[int, int], float | None] = {}
    prev_equity: float | None = None
    for i, key in enumerate(sorted(by_month.keys())):
        curr = by_month[key]
        baseline = first_equity if i == 0 else prev_equity
        if baseline is not None and baseline > 0:
            monthly[key] = (curr - baseline) / baseline
        else:
            monthly[key] = None
        prev_equity = curr

    years = sorted({key[0] for key in by_month})
    return [
        MonthlyReturns(
            year=year,
            months=[monthly.get((year, month)) for month in range(1, 13)],
        )
        for year in years
    ]


def _build_verification(equity_points: list[EquityPoint]) -> Verification:
    """Recompute the pairwise-return reconstruction from `equity.parquet`.

    This recompute is trivially self-consistent because the equity parquet
    was written from the same snapshot series used to build this
    reconstruction. It proves the parquet is internally coherent; it is
    not an independent verification of Nautilus's account balance.
    """
    if not equity_points:
        return Verification(
            verified=True,
            discrepancy_pct=0.0,
            source="reconstructed_from_portfolio_returns",
        )

    starting = equity_points[0].equity
    reconstructed = starting
    for i in range(1, len(equity_points)):
        prev = equity_points[i - 1].equity
        if prev == 0:
            continue
        r = (equity_points[i].equity - prev) / prev
        reconstructed *= 1 + r

    ending = equity_points[-1].equity
    discrepancy = 0.0 if ending == 0 else abs(reconstructed - ending) / ending

    return Verification(
        verified=discrepancy < 0.005,
        discrepancy_pct=discrepancy * 100.0,
        source="reconstructed_from_portfolio_returns",
    )


def _empty_tearsheet(
    summary: RunSummary,
    params: dict[str, Any],
    kpi_block: KpiBlock,
    artifacts_dict: dict[str, Any],
    source: str,
) -> TearSheet:
    return TearSheet(
        run=summary,
        params=params,
        kpis=kpi_block,
        equity=[],
        drawdown=[],
        price=[],
        markers=[],
        monthly_returns=[],
        verification=Verification(
            verified=True,
            discrepancy_pct=0.0,
            source=source,
        ),
        artifacts=artifacts_dict if isinstance(artifacts_dict, dict) else {},
    )


@router.get(
    "/{run_id}/tearsheet",
    response_model=TearSheet,
    responses={404: {"model": ApiError}, 500: {"model": ApiError}},
)
def get_tearsheet(
    db: RunsDb,
    run_id: Annotated[str, PathParam()],
) -> TearSheet:
    db.row_factory = sqlite3.Row
    row = db.execute(
        """
        SELECT run_id, name, strategy, universe, start_ts, end_ts, created_at,
               git_sha, git_dirty, status, params, metrics, artifacts
        FROM meta_runs
        WHERE run_id = ?
        """,
        (run_id,),
    ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"run {run_id} not found",
                    "details": None,
                }
            },
        )

    summary = _row_to_summary(row)
    params = _parse_json_or({}, row["params"])
    metrics_dict = _parse_json_or({}, row["metrics"])
    artifacts_dict = _parse_json_or({}, row["artifacts"])
    params_dict = params if isinstance(params, dict) else {}
    kpi_block = _kpi_block_from_metrics(
        metrics_dict if isinstance(metrics_dict, dict) else {}
    )

    run_status = row["status"]
    if run_status in ("queued", "running", "failed"):
        return _empty_tearsheet(summary, params_dict, kpi_block, {}, run_status)
    if run_status == "archived":
        return _empty_tearsheet(summary, params_dict, kpi_block, {}, run_status)

    # run_status == "done" — proceed to load parquets.
    run_dir = get_artifacts_dir() / run_id
    if not run_dir.is_dir():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL",
                    "message": f"artifacts directory missing for run {run_id}",
                    "details": None,
                }
            },
        )

    try:
        equity_rows = pq.read_table(run_dir / "equity.parquet").to_pylist()
        drawdown_rows = pq.read_table(run_dir / "drawdown.parquet").to_pylist()
        price_rows = pq.read_table(run_dir / "price.parquet").to_pylist()
        trades_rows = pq.read_table(run_dir / "trades.parquet").to_pylist()
        pq.read_table(run_dir / "fills.parquet").to_pylist()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {"code": "INTERNAL", "message": str(exc), "details": None}
            },
        ) from exc

    equity_points = [EquityPoint(**r) for r in _sorted_dedup(equity_rows)]
    drawdown_points = [DrawdownPoint(**r) for r in _sorted_dedup(drawdown_rows)]
    price_points = [OHLCV(**r) for r in _sorted_dedup(price_rows)]
    markers = _build_markers(trades_rows)
    monthly_returns = _build_monthly_returns(equity_points)
    verification = _build_verification(equity_points)

    return TearSheet(
        run=summary,
        params=params_dict,
        kpis=kpi_block,
        equity=equity_points,
        drawdown=drawdown_points,
        price=price_points,
        markers=markers,
        monthly_returns=monthly_returns,
        verification=verification,
        artifacts=artifacts_dict if isinstance(artifacts_dict, dict) else {},
    )


def _trade_from_parquet_row(row: dict[str, Any]) -> Trade:
    side_raw = str(row["side"])
    if side_raw not in ("long", "short"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL",
                    "message": (
                        f"invalid trade side {side_raw!r} "
                        f"for trade {row.get('trade_id')!r}"
                    ),
                    "details": None,
                }
            },
        )
    side = cast(Literal["long", "short"], side_raw)
    exit_ts_raw = row.get("exit_ts")
    exit_px_raw = row.get("exit_px")
    return Trade(
        trade_id=str(row["trade_id"]),
        symbol=str(row["symbol"]),
        side=side,
        entry_ts=int(row["entry_ts"]),
        exit_ts=int(exit_ts_raw) if exit_ts_raw is not None else None,
        entry_px=float(row["entry_px"]),
        exit_px=float(exit_px_raw) if exit_px_raw is not None else None,
        qty=float(row["qty"]),
        pnl=float(row["pnl"]),
        pnl_pct=float(row["pnl_pct"]),
        fees=float(row["fees"]),
        duration_s=float(row["duration_s"]),
    )


@router.get(
    "/{run_id}/trades",
    response_model=TradePage,
    responses={404: {"model": ApiError}, 500: {"model": ApiError}},
)
def get_trades(
    db: RunsDb,
    run_id: Annotated[str, PathParam()],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=500)] = 100,
) -> TradePage:
    db.row_factory = sqlite3.Row
    row = db.execute(
        "SELECT run_id, status FROM meta_runs WHERE run_id = ?",
        (run_id,),
    ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"run {run_id} not found",
                    "details": None,
                }
            },
        )

    run_status = row["status"]
    if run_status != "done":
        return TradePage(items=[], total=0, page=page, page_size=page_size)

    run_dir = get_artifacts_dir() / run_id
    parquet_path = run_dir / "trades.parquet"

    if not parquet_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL",
                    "message": f"trades.parquet missing for run {run_id}",
                    "details": None,
                }
            },
        )

    try:
        table = pq.read_table(parquet_path)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {"code": "INTERNAL", "message": str(exc), "details": None}
            },
        ) from exc

    rows = table.to_pylist()
    sorted_rows = sorted(rows, key=lambda r: int(r["entry_ts"]))
    seen_ids: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for r in sorted_rows:
        tid = str(r["trade_id"])
        if tid in seen_ids:
            continue
        seen_ids.add(tid)
        deduped.append(r)
    total = len(deduped)

    offset = (page - 1) * page_size
    paged = deduped[offset : offset + page_size]

    trade_items = [_trade_from_parquet_row(r) for r in paged]

    return TradePage(
        items=trade_items,
        total=total,
        page=page,
        page_size=page_size,
    )
