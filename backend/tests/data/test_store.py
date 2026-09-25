from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import duckdb
import pytest

from quant.data.store import ensure_canonical_bars, init_schema, upsert_bars

EXPECTED_COLUMNS: frozenset[str] = frozenset(
    {
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
    }
)

EXPECTED_TYPES: dict[str, str] = {
    "venue": "VARCHAR",
    "symbol": "VARCHAR",
    "asset_class": "VARCHAR",
    "timeframe": "VARCHAR",
    "ts": "BIGINT",
    "open": "DOUBLE",
    "high": "DOUBLE",
    "low": "DOUBLE",
    "close": "DOUBLE",
    "volume": "DOUBLE",
    "vwap": "DOUBLE",
    "trades": "BIGINT",
    "source": "VARCHAR",
    "ingested_at": "BIGINT",
}

PRIMARY_KEY_COLUMNS: frozenset[str] = frozenset(
    {"venue", "symbol", "timeframe", "ts"}
)


def _table_info(db_path: Path) -> list[tuple[Any, ...]]:
    conn = duckdb.connect(str(db_path))
    try:
        return conn.execute("PRAGMA table_info('curated_bars')").fetchall()
    finally:
        conn.close()


def _column_meta(db_path: Path) -> dict[str, tuple[str, bool]]:
    info = _table_info(db_path)
    return {str(row[1]): (str(row[2]), bool(row[5])) for row in info}


def _fetch_all_bars(db_path: Path) -> list[tuple[Any, ...]]:
    conn = duckdb.connect(str(db_path))
    try:
        return conn.execute(
            """
            SELECT venue, symbol, asset_class, timeframe, ts,
                   open, high, low, close, volume, vwap, trades, source, ingested_at
            FROM curated_bars
            ORDER BY ts ASC
            """
        ).fetchall()
    finally:
        conn.close()


def _minimal_row(**overrides: object) -> Mapping[str, object]:
    base: dict[str, object] = {
        "venue": "binance",
        "symbol": "BTC/USDT",
        "asset_class": "crypto",
        "timeframe": "1d",
        "ts": 1735689600000,
    }
    base.update(overrides)
    return base


def test_init_schema_creates_file_and_table(tmp_path: Path) -> None:
    db_path = tmp_path / "nested" / "bars.duckdb"
    init_schema(db_path)
    assert db_path.is_file()
    meta = _column_meta(db_path)
    assert set(meta) == EXPECTED_COLUMNS


@pytest.mark.parametrize("name,expected_type", list(EXPECTED_TYPES.items()))
def test_init_schema_column_types(
    tmp_path: Path, name: str, expected_type: str
) -> None:
    db_path = tmp_path / "bars.duckdb"
    init_schema(db_path)
    meta = _column_meta(db_path)
    assert meta[name][0] == expected_type


def test_init_schema_primary_key_columns(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    init_schema(db_path)
    meta = _column_meta(db_path)
    pk_names = {name for name, (_, is_pk) in meta.items() if is_pk}
    assert pk_names == PRIMARY_KEY_COLUMNS


def test_init_schema_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    init_schema(db_path)
    init_schema(db_path)
    assert set(_column_meta(db_path)) == EXPECTED_COLUMNS


def test_init_schema_creates_parent_directory(tmp_path: Path) -> None:
    db_path = tmp_path / "deep" / "dir" / "bars.duckdb"
    assert not db_path.parent.exists()
    init_schema(db_path)
    assert db_path.parent.is_dir()
    assert db_path.is_file()


def test_ensure_canonical_bars_fresh_path(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    ensure_canonical_bars(db_path)
    assert set(_column_meta(db_path)) == EXPECTED_COLUMNS


def test_ensure_canonical_bars_existing_valid_table(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "bars.duckdb"
    init_schema(db_path)
    ensure_canonical_bars(db_path)


def test_ensure_canonical_bars_missing_column_raises(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    conn = duckdb.connect(str(db_path))
    try:
        conn.execute(
            """
            CREATE TABLE curated_bars (
                venue VARCHAR NOT NULL,
                symbol VARCHAR NOT NULL,
                asset_class VARCHAR NOT NULL,
                timeframe VARCHAR NOT NULL,
                ts BIGINT NOT NULL,
                open DOUBLE,
                PRIMARY KEY (venue, symbol, timeframe, ts)
            )
            """
        )
    finally:
        conn.close()
    with pytest.raises(RuntimeError, match=r"missing required column: high"):
        ensure_canonical_bars(db_path)


def test_upsert_bars_complete_row_round_trips(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    ensure_canonical_bars(db_path)
    row = _minimal_row(
        open=100.0,
        high=110.0,
        low=90.0,
        close=105.0,
        volume=1234.5,
        vwap=102.0,
        trades=42,
        source="ccxt",
        ingested_at=1735689700000,
    )
    written = upsert_bars(db_path, [row])
    assert written == 1
    stored = _fetch_all_bars(db_path)
    assert len(stored) == 1
    assert stored[0] == (
        "binance",
        "BTC/USDT",
        "crypto",
        "1d",
        1735689600000,
        100.0,
        110.0,
        90.0,
        105.0,
        1234.5,
        102.0,
        42,
        "ccxt",
        1735689700000,
    )


def test_upsert_bars_three_rows_two_timeframes(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    ensure_canonical_bars(db_path)
    rows = [
        _minimal_row(timeframe="1h", ts=1, close=1.0),
        _minimal_row(timeframe="1h", ts=2, close=2.0),
        _minimal_row(timeframe="1d", ts=3, close=3.0),
    ]
    assert upsert_bars(db_path, rows) == 3
    assert len(_fetch_all_bars(db_path)) == 3


def test_upsert_bars_replaces_same_primary_key(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    ensure_canonical_bars(db_path)
    key = _minimal_row(close=10.0)
    upsert_bars(db_path, [key])
    upsert_bars(db_path, [_minimal_row(close=20.0)])
    bars = _fetch_all_bars(db_path)
    assert len(bars) == 1
    assert bars[0][8] == 20.0


def test_upsert_bars_partial_row_null_optionals(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "bars.duckdb"
    ensure_canonical_bars(db_path)
    upsert_bars(db_path, [_minimal_row()])
    row = _fetch_all_bars(db_path)[0]
    assert row[5:12] == (None, None, None, None, None, None, None)
    assert row[12:] == (None, None)


def test_upsert_bars_empty_input(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    ensure_canonical_bars(db_path)
    upsert_bars(db_path, [_minimal_row(close=1.0)])
    assert upsert_bars(db_path, []) == 0
    bars = _fetch_all_bars(db_path)
    assert len(bars) == 1
    assert bars[0][8] == 1.0


def test_upsert_bars_without_table_raises(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    with pytest.raises(duckdb.CatalogException):
        upsert_bars(db_path, [_minimal_row()])
