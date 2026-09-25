"""DuckDB schema initialization and curated bar persistence."""

from __future__ import annotations

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
