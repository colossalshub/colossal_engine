from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

import duckdb
import pytest

from quant.data.read import read_bars_json
from quant.data.store import init_schema, upsert_bars

EXPECTED_KEYS: frozenset[str] = frozenset(
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


def _minimal_row(**overrides: object) -> Mapping[str, object]:
    base: dict[str, object] = {
        "venue": "binance",
        "symbol": "BTC/USDT",
        "asset_class": "crypto",
        "timeframe": "1d",
        "ts": 1000,
        "open": 1.0,
        "high": 2.0,
        "low": 0.5,
        "close": 1.5,
        "volume": 100.0,
    }
    base.update(overrides)
    return base


def _read(
    db_path: Path,
    *,
    venue: str = "binance",
    symbol: str = "BTC/USDT",
    timeframe: str = "1d",
    start_ts: int | None = None,
    end_ts: int | None = None,
) -> list[dict[str, object]]:
    return read_bars_json(
        db_path,
        venue=venue,
        symbol=symbol,
        timeframe=timeframe,
        start_ts=start_ts,
        end_ts=end_ts,
    )


def test_missing_db_path_returns_empty(tmp_path: Path) -> None:
    assert _read(tmp_path / "missing.duckdb") == []


def test_db_without_curated_bars_table_returns_empty(tmp_path: Path) -> None:
    db_path = tmp_path / "empty.duckdb"
    conn = duckdb.connect(str(db_path))
    conn.close()
    assert _read(db_path) == []


def test_empty_table_returns_empty(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    init_schema(db_path)
    assert _read(db_path) == []


def test_wrong_symbol_returns_empty(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    init_schema(db_path)
    upsert_bars(db_path, [_minimal_row()])
    assert _read(db_path, symbol="ETH/USDT") == []


def test_basic_read_three_bars(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    init_schema(db_path)
    rows = [
        _minimal_row(ts=1000, close=10.0, source="ccxt", ingested_at=9000),
        _minimal_row(ts=2000, close=20.0, source="ccxt", ingested_at=9001),
        _minimal_row(ts=3000, close=30.0, source="ccxt", ingested_at=9002),
    ]
    upsert_bars(db_path, rows)
    out = _read(db_path)
    assert len(out) == 3
    assert [r["ts"] for r in out] == [1000, 2000, 3000]
    for bar in out:
        assert set(bar) == EXPECTED_KEYS
    assert out[0]["close"] == 10.0
    assert out[1]["close"] == 20.0
    assert out[2]["close"] == 30.0
    assert out[0]["venue"] == "binance"
    assert out[0]["symbol"] == "BTC/USDT"
    assert out[0]["timeframe"] == "1d"
    assert out[0]["asset_class"] == "crypto"


@pytest.mark.parametrize(
    ("start_ts", "end_ts", "expected_ts"),
    [
        (2000, None, [2000, 3000]),
        (None, 2000, [1000, 2000]),
        (2000, 2000, [2000]),
        (9999, None, []),
    ],
)
def test_range_filters(
    tmp_path: Path,
    start_ts: int | None,
    end_ts: int | None,
    expected_ts: list[int],
) -> None:
    db_path = tmp_path / "bars.duckdb"
    init_schema(db_path)
    upsert_bars(
        db_path,
        [
            _minimal_row(ts=1000),
            _minimal_row(ts=2000),
            _minimal_row(ts=3000),
        ],
    )
    out = _read(db_path, start_ts=start_ts, end_ts=end_ts)
    assert [r["ts"] for r in out] == expected_ts


def test_read_returns_ascending_ts_when_inserted_descending(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    init_schema(db_path)
    upsert_bars(
        db_path,
        [
            _minimal_row(ts=3000, close=3.0),
            _minimal_row(ts=1000, close=1.0),
            _minimal_row(ts=2000, close=2.0),
        ],
    )
    out = _read(db_path)
    assert [r["ts"] for r in out] == [1000, 2000, 3000]
    assert [r["close"] for r in out] == [1.0, 2.0, 3.0]


@pytest.mark.parametrize(
    ("field", "other_value", "query_kw"),
    [
        ("symbol", "ETH/USDT", {"symbol": "BTC/USDT"}),
        ("venue", "yahoo", {"venue": "binance"}),
        ("timeframe", "1h", {"timeframe": "1d"}),
    ],
)
def test_filter_by_dimension(
    tmp_path: Path,
    field: str,
    other_value: str,
    query_kw: dict[str, str],
) -> None:
    db_path = tmp_path / "bars.duckdb"
    init_schema(db_path)
    primary = _minimal_row(ts=1000, close=1.0)
    other = _minimal_row(ts=2000, close=2.0, **{field: other_value})
    upsert_bars(db_path, [primary, other])
    out = _read(db_path, **query_kw)
    assert len(out) == 1
    assert out[0]["ts"] == 1000
    assert out[0]["close"] == 1.0


def test_null_optional_fields_round_trip(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    init_schema(db_path)
    upsert_bars(
        db_path,
        [
            _minimal_row(
                ts=1000,
                vwap=None,
                trades=None,
                source=None,
                ingested_at=None,
            ),
        ],
    )
    bar = _read(db_path)[0]
    assert bar["vwap"] is None
    assert bar["trades"] is None
    assert bar["source"] is None
    assert bar["ingested_at"] is None


def test_populated_optional_fields_round_trip(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    init_schema(db_path)
    upsert_bars(
        db_path,
        [
            _minimal_row(
                ts=1000,
                vwap=101.5,
                trades=99,
                source="ccxt",
                ingested_at=5000,
            ),
        ],
    )
    bar = _read(db_path)[0]
    assert bar["vwap"] == 101.5
    assert bar["trades"] == 99
    assert bar["source"] == "ccxt"
    assert bar["ingested_at"] == 5000


def test_result_is_json_serializable(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    init_schema(db_path)
    upsert_bars(
        db_path,
        [
            _minimal_row(
                ts=1000,
                vwap=1.1,
                trades=1,
                source="ccxt",
                ingested_at=1,
            ),
            _minimal_row(ts=2000, close=2.0),
        ],
    )
    out = _read(db_path)
    serialized = json.dumps(out)
    assert json.loads(serialized) == out
