"""Read curated bars from DuckDB as JSON-serializable dicts."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import duckdb

_SELECT_COLUMNS: tuple[str, ...] = (
    "venue",
    "symbol",
    "asset_class",
    "timeframe",
    "ts",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "vwap",
    "trades",
    "source",
    "ingested_at",
)

_INT_COLUMNS: frozenset[str] = frozenset({"ts", "trades", "ingested_at"})
_FLOAT_COLUMNS: frozenset[str] = frozenset(
    {"open", "high", "low", "close", "volume", "vwap"}
)
_STR_COLUMNS: frozenset[str] = frozenset(
    {"venue", "symbol", "asset_class", "timeframe", "source"}
)


def _json_cell(column: str, value: object) -> object:
    if value is None:
        return None
    if column in _INT_COLUMNS:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, Decimal):
            return int(value)
        if isinstance(value, datetime):
            return int(value.timestamp() * 1000)
        if isinstance(value, date):
            return int(datetime(value.year, value.month, value.day).timestamp() * 1000)
        if isinstance(value, str):
            return int(value)
        msg = f"cannot convert {column} value to int: {type(value)!r}"
        raise TypeError(msg)
    if column in _FLOAT_COLUMNS:
        if isinstance(value, float):
            return value
        if isinstance(value, int) and not isinstance(value, bool):
            return float(value)
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, str):
            return float(value)
        msg = f"cannot convert {column} value to float: {type(value)!r}"
        raise TypeError(msg)
    if column in _STR_COLUMNS:
        if isinstance(value, str):
            return value
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)
    msg = f"unexpected column for JSON conversion: {column}"
    raise ValueError(msg)


def read_bars_json(
    db_path: Path,
    *,
    venue: str,
    symbol: str,
    timeframe: str,
    start_ts: int | None = None,
    end_ts: int | None = None,
) -> list[dict[str, object]]:
    """Return curated bars matching the filter, sorted by ts ascending."""
    if not db_path.is_file():
        return []

    columns_sql = ", ".join(_SELECT_COLUMNS)
    sql = (
        f"SELECT {columns_sql} FROM curated_bars "
        "WHERE venue = ? AND symbol = ? AND timeframe = ?"
    )
    params: list[object] = [venue, symbol, timeframe]
    if start_ts is not None:
        sql += " AND ts >= ?"
        params.append(start_ts)
    if end_ts is not None:
        sql += " AND ts <= ?"
        params.append(end_ts)
    sql += " ORDER BY ts ASC"

    conn = duckdb.connect(str(db_path))
    try:
        try:
            raw_rows = conn.execute(sql, params).fetchall()
        except duckdb.CatalogException:
            return []
    finally:
        conn.close()

    ts_index = _SELECT_COLUMNS.index("ts")
    seen_ts: set[int] = set()
    result: list[dict[str, object]] = []
    for row in raw_rows:
        ts_val = row[ts_index]
        if ts_val is None:
            continue
        ts_key_obj = _json_cell("ts", ts_val)
        if not isinstance(ts_key_obj, int):
            continue
        ts_key = ts_key_obj
        if ts_key in seen_ts:
            continue
        seen_ts.add(ts_key)
        bar = {
            col: _json_cell(col, val)
            for col, val in zip(_SELECT_COLUMNS, row, strict=True)
        }
        result.append(bar)
    return result
