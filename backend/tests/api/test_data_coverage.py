"""Tests for ``GET /api/data/coverage``."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import duckdb
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from quant.api.routers.data import router as data_router
from quant.data.store import init_schema, upsert_bars


def _ms(year: int, month: int, day: int) -> int:
    return int(datetime(year, month, day, tzinfo=UTC).timestamp() * 1000)


def _insert_daily_bars(
    db_path: Path,
    *,
    venue: str,
    symbol: str,
    timeframe: str,
    start: datetime,
    count: int,
) -> None:
    rows: list[dict[str, object]] = []
    for i in range(count):
        ts = int((start + timedelta(days=i)).timestamp() * 1000)
        rows.append(
            {
                "venue": venue,
                "symbol": symbol,
                "asset_class": "crypto",
                "timeframe": timeframe,
                "ts": ts,
            }
        )
    upsert_bars(db_path, rows)


@pytest.fixture
def coverage_client(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Iterator[tuple[TestClient, Path]]:
    bars_path = tmp_path / "bars.duckdb"
    monkeypatch.setenv("QUANT_BARS_DB", str(bars_path))
    init_schema(bars_path)

    app = FastAPI()
    app.include_router(data_router)
    with TestClient(app) as client:
        yield client, bars_path


def test_empty_db_returns_empty_rows(coverage_client: tuple[TestClient, Path]) -> None:
    client, _ = coverage_client
    response = client.get("/api/data/coverage")
    assert response.status_code == 200
    assert response.json() == {"rows": []}


def test_single_symbol_single_month(coverage_client: tuple[TestClient, Path]) -> None:
    client, db_path = coverage_client
    start = datetime(2024, 1, 1, tzinfo=UTC)
    _insert_daily_bars(
        db_path,
        venue="binance",
        symbol="BTC/USDT",
        timeframe="1d",
        start=start,
        count=10,
    )

    response = client.get("/api/data/coverage")
    assert response.status_code == 200
    body = response.json()
    assert len(body["rows"]) == 1
    row = body["rows"][0]
    assert row["venue"] == "binance"
    assert row["symbol"] == "BTC/USDT"
    assert row["timeframe"] == "1d"
    assert len(row["cells"]) == 1
    cell = row["cells"][0]
    assert cell["year"] == 2024
    assert cell["month"] == 1
    assert cell["bars"] == 10
    assert cell["expected"] == 31
    assert abs(cell["coverage"] - 10 / 31) < 1e-9


def test_multiple_months_one_row(coverage_client: tuple[TestClient, Path]) -> None:
    client, db_path = coverage_client
    jan_start = datetime(2024, 1, 1, tzinfo=UTC)
    feb_start = datetime(2024, 2, 1, tzinfo=UTC)
    _insert_daily_bars(
        db_path,
        venue="binance",
        symbol="BTC/USDT",
        timeframe="1d",
        start=jan_start,
        count=5,
    )
    _insert_daily_bars(
        db_path,
        venue="binance",
        symbol="BTC/USDT",
        timeframe="1d",
        start=feb_start,
        count=3,
    )

    response = client.get("/api/data/coverage")
    body = response.json()
    assert len(body["rows"]) == 1
    months = [(c["year"], c["month"]) for c in body["rows"][0]["cells"]]
    assert months == [(2024, 1), (2024, 2)]


def test_multiple_symbols_sorted(coverage_client: tuple[TestClient, Path]) -> None:
    client, db_path = coverage_client
    start = datetime(2024, 1, 1, tzinfo=UTC)
    _insert_daily_bars(
        db_path,
        venue="binance",
        symbol="ETH/USDT",
        timeframe="1d",
        start=start,
        count=1,
    )
    _insert_daily_bars(
        db_path,
        venue="binance",
        symbol="BTC/USDT",
        timeframe="1d",
        start=start,
        count=1,
    )

    response = client.get("/api/data/coverage")
    symbols = [r["symbol"] for r in response.json()["rows"]]
    assert symbols == ["BTC/USDT", "ETH/USDT"]


def test_multiple_timeframes_two_rows(coverage_client: tuple[TestClient, Path]) -> None:
    client, db_path = coverage_client
    day = datetime(2024, 1, 1, tzinfo=UTC)
    _insert_daily_bars(
        db_path,
        venue="binance",
        symbol="BTC/USDT",
        timeframe="1d",
        start=day,
        count=1,
    )
    upsert_bars(
        db_path,
        [
            {
                "venue": "binance",
                "symbol": "BTC/USDT",
                "asset_class": "crypto",
                "timeframe": "1h",
                "ts": _ms(2024, 1, 1),
            }
        ],
    )

    response = client.get("/api/data/coverage")
    timeframes = sorted(r["timeframe"] for r in response.json()["rows"])
    assert timeframes == ["1d", "1h"]


def test_coverage_capped_at_one(coverage_client: tuple[TestClient, Path]) -> None:
    client, db_path = coverage_client
    # Forty distinct 1d rows in January (intraday ts); expected stays 31 calendar days.
    base = datetime(2024, 1, 1, tzinfo=UTC)
    rows: list[dict[str, object]] = []
    for i in range(40):
        ts = int((base + timedelta(hours=i)).timestamp() * 1000)
        rows.append(
            {
                "venue": "binance",
                "symbol": "BTC/USDT",
                "asset_class": "crypto",
                "timeframe": "1d",
                "ts": ts,
            }
        )
    upsert_bars(db_path, rows)

    response = client.get("/api/data/coverage")
    cell = response.json()["rows"][0]["cells"][0]
    assert cell["bars"] == 40
    assert cell["expected"] == 31
    assert cell["coverage"] == 1.0


def test_unknown_timeframe_skipped(coverage_client: tuple[TestClient, Path]) -> None:
    client, db_path = coverage_client
    _insert_daily_bars(
        db_path,
        venue="binance",
        symbol="BTC/USDT",
        timeframe="1d",
        start=datetime(2024, 1, 1, tzinfo=UTC),
        count=1,
    )

    conn = duckdb.connect(str(db_path))
    try:
        conn.execute(
            """
            INSERT INTO curated_bars (
                venue, symbol, asset_class, timeframe, ts,
                open, high, low, close, volume, vwap, trades, source, ingested_at
            ) VALUES (
                'binance', 'BTC/USDT', 'crypto', 'banana', ?,
                NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
            )
            """,
            [_ms(2024, 1, 2)],
        )
    finally:
        conn.close()

    response = client.get("/api/data/coverage")
    assert response.status_code == 200
    assert len(response.json()["rows"]) == 1
    assert response.json()["rows"][0]["timeframe"] == "1d"


def test_expected_math_leap_and_hourly(
    coverage_client: tuple[TestClient, Path],
) -> None:
    client, db_path = coverage_client
    _insert_daily_bars(
        db_path,
        venue="binance",
        symbol="BTC/USDT",
        timeframe="1d",
        start=datetime(2024, 2, 1, tzinfo=UTC),
        count=1,
    )
    upsert_bars(
        db_path,
        [
            {
                "venue": "binance",
                "symbol": "BTC/USDT",
                "asset_class": "crypto",
                "timeframe": "1h",
                "ts": _ms(2024, 1, 1),
            }
        ],
    )

    response = client.get("/api/data/coverage")
    rows = response.json()["rows"]
    by_tf = {r["timeframe"]: r for r in rows}
    feb_cell = by_tf["1d"]["cells"][0]
    assert feb_cell["month"] == 2
    assert feb_cell["expected"] == 29

    jan_hour = by_tf["1h"]["cells"][0]
    assert jan_hour["month"] == 1
    assert jan_hour["expected"] == 744
