"""Tests for `GET /api/runs/{id}/trades` (`quant.api.routers.runs.get_trades`)."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pyarrow as pa  # type: ignore[import-untyped]  # pyarrow ships without py.typed
import pyarrow.parquet as pq  # type: ignore[import-untyped]  # pyarrow ships without py.typed
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from quant.api.routers.runs import router
from quant.data.runs_store import RunRecord, _now_ms, init_runs_schema, insert_run

_TRADES_TYPES: dict[str, pa.DataType] = {
    "trade_id": pa.string(),
    "symbol": pa.string(),
    "side": pa.string(),
    "entry_ts": pa.int64(),
    "exit_ts": pa.int64(),
    "entry_px": pa.float64(),
    "exit_px": pa.float64(),
    "qty": pa.float64(),
    "pnl": pa.float64(),
    "pnl_pct": pa.float64(),
    "fees": pa.float64(),
    "duration_s": pa.float64(),
}


def _write_trades_parquet(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = {
        name: pa.array([row.get(name) for row in rows], type=dtype)
        for name, dtype in _TRADES_TYPES.items()
    }
    pq.write_table(pa.table(columns), path)


def _trade_row(
    trade_id: str,
    entry_ts: int,
    *,
    symbol: str = "BTC/USDT",
    side: str = "long",
    **overrides: Any,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "trade_id": trade_id,
        "symbol": symbol,
        "side": side,
        "entry_ts": entry_ts,
        "exit_ts": entry_ts + 1000,
        "entry_px": 100.0,
        "exit_px": 110.0,
        "qty": 1.0,
        "pnl": 10.0,
        "pnl_pct": 0.1,
        "fees": 0.5,
        "duration_s": 100.0,
    }
    row.update(overrides)
    return row


def _five_trades() -> list[dict[str, Any]]:
    return [_trade_row(f"t{i}", 1_000 * i) for i in range(1, 6)]


@pytest.fixture
def artifacts_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "runs"
    path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("QUANT_ARTIFACTS_DIR", str(path))
    return path


@pytest.fixture
def db_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "runs.sqlite"
    monkeypatch.setenv("QUANT_RUNS_DB", str(path))
    init_runs_schema(path)
    return path


@pytest.fixture
def client(db_path: Path, artifacts_dir: Path) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as test_client:
        yield test_client


def _record(**overrides: Any) -> RunRecord:
    created = _now_ms()
    record = RunRecord(
        run_id=str(uuid.uuid4()),
        name="mom-12-1",
        strategy="momentum",
        params={"lookback": 12},
        universe=["BTC/USDT"],
        start_ts=1_577_836_800_000,
        end_ts=1_735_689_600_000,
        created_at=created,
        finished_at=created + 1000,
        heartbeat_ts=created + 500,
        status="done",
        error=None,
        git_sha="a" * 40,
        git_dirty=False,
        data_snapshot="snapshot-sha",
        seed=7,
        metrics={},
        artifacts={"trades": "trades.parquet"},
    )
    for key, value in overrides.items():
        setattr(record, key, value)
    return record


def test_not_found_404(client: TestClient) -> None:
    response = client.get("/api/runs/does-not-exist/trades")
    assert response.status_code == 404
    assert response.json()["detail"]["error"]["code"] == "NOT_FOUND"


@pytest.mark.parametrize("target_status", ["queued", "failed", "archived"])
def test_non_done_status_returns_empty_page(
    client: TestClient, db_path: Path, target_status: str
) -> None:
    record = _record(status=target_status)
    insert_run(db_path, record)

    response = client.get(f"/api/runs/{record.run_id}/trades?page=2&page_size=10")
    assert response.status_code == 200
    body = response.json()
    assert body == {"items": [], "total": 0, "page": 2, "page_size": 10}


def test_done_missing_trades_parquet_500(
    client: TestClient, db_path: Path, artifacts_dir: Path
) -> None:
    record = _record(status="done")
    insert_run(db_path, record)
    (artifacts_dir / record.run_id).mkdir(parents=True, exist_ok=True)

    response = client.get(f"/api/runs/{record.run_id}/trades")
    assert response.status_code == 500
    assert response.json()["detail"]["error"]["code"] == "INTERNAL"
    assert "trades.parquet missing" in response.json()["detail"]["error"]["message"]


def test_done_corrupt_parquet_500(
    client: TestClient, db_path: Path, artifacts_dir: Path
) -> None:
    record = _record(status="done")
    insert_run(db_path, record)
    run_dir = artifacts_dir / record.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "trades.parquet").write_text("not parquet", encoding="utf-8")

    response = client.get(f"/api/runs/{record.run_id}/trades")
    assert response.status_code == 500
    assert response.json()["detail"]["error"]["code"] == "INTERNAL"


def test_done_returns_all_trades_sorted(
    client: TestClient, db_path: Path, artifacts_dir: Path
) -> None:
    record = _record(status="done")
    insert_run(db_path, record)
    trades_path = artifacts_dir / record.run_id / "trades.parquet"
    _write_trades_parquet(trades_path, _five_trades())

    response = client.get(f"/api/runs/{record.run_id}/trades?page=1&page_size=100")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 5
    assert body["page"] == 1
    assert body["page_size"] == 100
    entry_ts = [item["entry_ts"] for item in body["items"]]
    assert entry_ts == [1000, 2000, 3000, 4000, 5000]
    trade_ids = [item["trade_id"] for item in body["items"]]
    assert trade_ids == ["t1", "t2", "t3", "t4", "t5"]


@pytest.mark.parametrize(
    ("page", "page_size", "expected_count"),
    [
        (1, 2, 2),
        (2, 2, 2),
        (3, 2, 1),
        (4, 2, 0),
    ],
)
def test_pagination_slices(
    client: TestClient,
    db_path: Path,
    artifacts_dir: Path,
    page: int,
    page_size: int,
    expected_count: int,
) -> None:
    record = _record(status="done")
    insert_run(db_path, record)
    trades_path = artifacts_dir / record.run_id / "trades.parquet"
    _write_trades_parquet(trades_path, _five_trades())

    response = client.get(
        f"/api/runs/{record.run_id}/trades?page={page}&page_size={page_size}"
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == expected_count
    assert body["total"] == 5
    assert body["page"] == page
    assert body["page_size"] == page_size


@pytest.mark.parametrize(
    ("query", "expected_status"),
    [
        ("page=0", 422),
        ("page_size=0", 422),
        ("page_size=501", 422),
    ],
)
def test_invalid_pagination_query_422(
    client: TestClient,
    db_path: Path,
    artifacts_dir: Path,
    query: str,
    expected_status: int,
) -> None:
    record = _record(status="done")
    insert_run(db_path, record)
    trades_path = artifacts_dir / record.run_id / "trades.parquet"
    _write_trades_parquet(trades_path, _five_trades())

    response = client.get(f"/api/runs/{record.run_id}/trades?{query}")
    assert response.status_code == expected_status


def test_open_position_null_exit_fields(
    client: TestClient, db_path: Path, artifacts_dir: Path
) -> None:
    record = _record(status="done")
    insert_run(db_path, record)
    rows = [
        _trade_row(
            "open-1",
            5_000,
            exit_ts=None,
            exit_px=None,
            pnl=0.0,
            pnl_pct=0.0,
            duration_s=0.0,
        )
    ]
    _write_trades_parquet(artifacts_dir / record.run_id / "trades.parquet", rows)

    response = client.get(f"/api/runs/{record.run_id}/trades")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    item = body["items"][0]
    assert item["exit_ts"] is None
    assert item["exit_px"] is None
    assert item["trade_id"] == "open-1"
    assert item["entry_ts"] == 5_000


def test_duplicate_trade_id_deduped(
    client: TestClient, db_path: Path, artifacts_dir: Path
) -> None:
    record = _record(status="done")
    insert_run(db_path, record)
    rows = [
        _trade_row("dup", 2_000, entry_px=100.0),
        _trade_row("dup", 1_000, entry_px=999.0),
    ]
    _write_trades_parquet(artifacts_dir / record.run_id / "trades.parquet", rows)

    response = client.get(f"/api/runs/{record.run_id}/trades")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["trade_id"] == "dup"
    assert body["items"][0]["entry_px"] == 999.0


def test_descending_parquet_order_returned_ascending(
    client: TestClient, db_path: Path, artifacts_dir: Path
) -> None:
    record = _record(status="done")
    insert_run(db_path, record)
    rows = list(reversed(_five_trades()))
    _write_trades_parquet(artifacts_dir / record.run_id / "trades.parquet", rows)

    response = client.get(f"/api/runs/{record.run_id}/trades")
    assert response.status_code == 200
    entry_ts_values = [item["entry_ts"] for item in response.json()["items"]]
    assert entry_ts_values == [1000, 2000, 3000, 4000, 5000]
