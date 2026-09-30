"""DuckDB schema initialization and curated bar persistence."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from pathlib import Path

import duckdb

_CURATED_BARS_COLUMNS: tuple[str, ...] = (
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

_CREATE_CURATED_BARS_SQL = """
CREATE TABLE IF NOT EXISTS curated_bars (
    venue        VARCHAR NOT NULL,
    symbol       VARCHAR NOT NULL,
    asset_class  VARCHAR NOT NULL,
    timeframe    VARCHAR NOT NULL,
    ts           BIGINT NOT NULL,
    open  DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE,
    volume DOUBLE, vwap DOUBLE, trades BIGINT,
    source VARCHAR,
    ingested_at  BIGINT,
    PRIMARY KEY (venue, symbol, timeframe, ts)
)
"""

_UPSERT_BARS_SQL = """
INSERT OR REPLACE INTO curated_bars (
    venue,
    symbol,
    asset_class,
    timeframe,
    ts,
    open,
    high,
    low,
    close,
    volume,
    vwap,
    trades,
    source,
    ingested_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

_REQUIRED_STRING_FIELDS: tuple[str, ...] = (
    "venue",
    "symbol",
    "asset_class",
    "timeframe",
)
_PRICE_FIELDS: tuple[str, ...] = ("open", "high", "low", "close")


def _is_finite_number(value: object) -> bool:
    return _to_finite_float(value) is not None


def _to_finite_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float) and math.isfinite(float(value)):
        return float(value)
    return None


def _validate_bars(rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        return None
    failures: list[tuple[int, str, str]] = []
    for row_index, row in enumerate(rows):
        for field in _REQUIRED_STRING_FIELDS:
            value = row.get(field)
            if not isinstance(value, str) or not value:
                failures.append((row_index, "missing_field", field))

        ts = row.get("ts")
        if isinstance(ts, bool) or not isinstance(ts, int) or ts <= 0:
            failures.append((row_index, "invalid_ts", "ts"))

        prices: dict[str, float] = {}
        prices_valid = True
        for field in _PRICE_FIELDS:
            price = row.get(field)
            price_f = _to_finite_float(price) if price is not None else None
            if price_f is None or price_f <= 0:
                failures.append((row_index, "invalid_price", field))
                prices_valid = False
            else:
                prices[field] = price_f

        if prices_valid:
            o = prices["open"]
            h = prices["high"]
            low = prices["low"]
            c = prices["close"]
            if h < max(o, c, low) or low > min(o, c, h):
                failures.append((row_index, "ohlc_invariant", "high/low"))

        volume = row.get("volume")
        if volume is not None:
            volume_f = _to_finite_float(volume)
            if volume_f is None or volume_f < 0:
                failures.append((row_index, "invalid_volume", "volume"))

    if not failures:
        return None

    failed_rows: dict[int, list[str]] = {}
    for row_index, rule, detail in failures:
        failed_rows.setdefault(row_index, []).append(f"{rule}({detail})")

    total = len(rows)
    failed_count = len(failed_rows)
    detail_parts: list[str] = []
    for row_index in sorted(failed_rows.keys())[:5]:
        rules = ", ".join(failed_rows[row_index])
        detail_parts.append(f"row {row_index}: {rules}")
    details = "; ".join(detail_parts)
    if failed_count > 5:
        details = f"{details}; ... and {failed_count - 5} more"
    msg = (
        f"invalid bars: {failed_count} of {total} rows failed validation: {details}"
    )
    raise ValueError(msg)


def init_schema(db_path: Path) -> None:
    """Create the DuckDB file and curated_bars table if they do not exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(db_path))
    try:
        conn.execute(_CREATE_CURATED_BARS_SQL)
        conn.commit()
    finally:
        conn.close()


def _curated_bars_column_names(conn: duckdb.DuckDBPyConnection) -> set[str]:
    rows = conn.execute("PRAGMA table_info('curated_bars')").fetchall()
    return {str(row[1]) for row in rows}


def ensure_canonical_bars(db_path: Path) -> None:
    """Ensure curated_bars exists with the expected column set."""
    init_schema(db_path)
    conn = duckdb.connect(str(db_path))
    try:
        columns = _curated_bars_column_names(conn)
        for name in _CURATED_BARS_COLUMNS:
            if name not in columns:
                msg = f"curated_bars missing required column: {name}"
                raise RuntimeError(msg)
    finally:
        conn.close()


def upsert_bars(db_path: Path, rows: Sequence[Mapping[str, object]]) -> int:
    """Insert or replace curated bar rows; returns the number of rows written."""
    if not rows:
        return 0
    _validate_bars(rows)
    payload = [
        (
            row["venue"],
            row["symbol"],
            row["asset_class"],
            row["timeframe"],
            row["ts"],
            row.get("open"),
            row.get("high"),
            row.get("low"),
            row.get("close"),
            row.get("volume"),
            row.get("vwap"),
            row.get("trades"),
            row.get("source"),
            row.get("ingested_at"),
        )
        for row in rows
    ]
    conn = duckdb.connect(str(db_path))
    try:
        conn.executemany(_UPSERT_BARS_SQL, payload)
        conn.commit()
    finally:
        conn.close()
    return len(rows)
