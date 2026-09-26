"""Tests for `GET /api/runs/{id}/tearsheet` (`quant.api.routers.runs.get_tearsheet`)."""

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

_EQUITY_TYPES: dict[str, pa.DataType] = {
    "ts": pa.int64(),
    "equity": pa.float64(),
    "benchmark": pa.float64(),
}
_DRAWDOWN_TYPES: dict[str, pa.DataType] = {"ts": pa.int64(), "dd": pa.float64()}
_PRICE_TYPES: dict[str, pa.DataType] = {
    "ts": pa.int64(),
    "open": pa.float64(),
    "high": pa.float64(),
    "low": pa.float64(),
    "close": pa.float64(),
    "volume": pa.float64(),
}
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
_FILLS_TYPES: dict[str, pa.DataType] = {
    "ts": pa.int64(),
    "order_side": pa.string(),
    "last_px": pa.float64(),
    "last_qty": pa.float64(),
    "commission": pa.float64(),
}


def _write_table(
    path: Path, rows: list[dict[str, Any]], types: dict[str, pa.DataType]
) -> None:
    columns = {
        name: pa.array([row.get(name) for row in rows], type=dtype)
        for name, dtype in types.items()
    }
    pq.write_table(pa.table(columns), path)


def _write_artifacts(
    run_dir: Path,
    *,
    equity: list[dict[str, Any]] | None = None,
    drawdown: list[dict[str, Any]] | None = None,
    price: list[dict[str, Any]] | None = None,
    trades: list[dict[str, Any]] | None = None,
    fills: list[dict[str, Any]] | None = None,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    _write_table(run_dir / "equity.parquet", equity or [], _EQUITY_TYPES)
    _write_table(run_dir / "drawdown.parquet", drawdown or [], _DRAWDOWN_TYPES)
    _write_table(run_dir / "price.parquet", price or [], _PRICE_TYPES)
    _write_table(run_dir / "trades.parquet", trades or [], _TRADES_TYPES)
    _write_table(run_dir / "fills.parquet", fills or [], _FILLS_TYPES)


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
def client(
    db_path: Path, artifacts_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
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
        universe=["BTC/USDT", "ETH/USDT"],
        start_ts=1_577_836_800_000,
        end_ts=1_735_689_600_000,
        created_at=created,
        finished_at=created + 1000,
        heartbeat_ts=created + 500,
        status="done",
        error=None,
        git_sha="a" * 40,
        git_dirty=True,
        data_snapshot="snapshot-sha",
        seed=7,
        metrics={"sharpe": 1.42, "cagr": 0.21, "max_drawdown": -0.18},
        artifacts={"equity": "equity.parquet"},
    )
    for key, value in overrides.items():
        setattr(record, key, value)
    return record


def test_not_found_404(client: TestClient) -> None:
    response = client.get("/api/runs/does-not-exist/tearsheet")
    assert response.status_code == 404
    assert response.json()["detail"]["error"]["code"] == "NOT_FOUND"


@pytest.mark.parametrize("target_status", ["queued", "running", "failed"])
def test_non_terminal_status_returns_empty_tearsheet(
    client: TestClient, db_path: Path, target_status: str
) -> None:
    record = _record(status=target_status, metrics={})
    insert_run(db_path, record)

    response = client.get(f"/api/runs/{record.run_id}/tearsheet")
    assert response.status_code == 200
    body = response.json()
    assert body["equity"] == []
    assert body["drawdown"] == []
    assert body["price"] == []
    assert body["markers"] == []
    assert body["monthly_returns"] == []
    assert body["verification"]["source"] == target_status
    assert body["verification"]["verified"] is True
    assert body["verification"]["discrepancy_pct"] == 0.0
    assert all(v is None for v in body["kpis"].values())
    assert body["artifacts"] == {}


def test_archived_status_returns_empty_artifacts(
    client: TestClient, db_path: Path
) -> None:
    record = _record(status="archived", artifacts={"equity": "equity.parquet"})
    insert_run(db_path, record)

    response = client.get(f"/api/runs/{record.run_id}/tearsheet")
    assert response.status_code == 200
    body = response.json()
    assert body["equity"] == []
    assert body["drawdown"] == []
    assert body["price"] == []
    assert body["artifacts"] == {}
    assert body["verification"]["source"] == "archived"
    assert all(v is None for v in body["kpis"].values())


def test_done_missing_artifacts_dir_500(client: TestClient, db_path: Path) -> None:
    record = _record(status="done")
    insert_run(db_path, record)

    response = client.get(f"/api/runs/{record.run_id}/tearsheet")
    assert response.status_code == 500
    assert response.json()["detail"]["error"]["code"] == "INTERNAL"


def test_done_corrupt_parquet_500(
    client: TestClient, db_path: Path, artifacts_dir: Path
) -> None:
    record = _record(status="done")
    insert_run(db_path, record)

    run_dir = artifacts_dir / record.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    _write_artifacts(run_dir)
    # Corrupt one of the parquet files.
    (run_dir / "equity.parquet").write_bytes(b"not a parquet file")

    response = client.get(f"/api/runs/{record.run_id}/tearsheet")
    assert response.status_code == 500
    assert response.json()["detail"]["error"]["code"] == "INTERNAL"


def test_happy_path(client: TestClient, db_path: Path, artifacts_dir: Path) -> None:
    record = _record(
        status="done", metrics={"sharpe": 1.23, "cagr": 0.15, "max_drawdown": -0.1}
    )
    insert_run(db_path, record)

    equity_rows = [
        {
            "ts": 1_600_000_000_000 + i * 86_400_000,
            "equity": 100_000.0 + i * 1_000.0,
            "benchmark": 99_000.0,
        }
        for i in range(5)
    ]
    drawdown_rows = [
        {"ts": 1_600_000_000_000 + i * 86_400_000, "dd": -0.01 * i} for i in range(3)
    ]
    price_rows = [
        {
            "ts": 1_600_000_000_000 + i * 86_400_000,
            "open": 100.0,
            "high": 110.0,
            "low": 90.0,
            "close": 105.0,
            "volume": 1_000.0,
        }
        for i in range(3)
    ]
    trades_rows = [
        {
            "trade_id": "t1",
            "symbol": "BTC/USDT",
            "side": "long",
            "entry_ts": 1_600_000_000_000,
            "exit_ts": 1_600_100_000_000,
            "entry_px": 100.0,
            "exit_px": 110.0,
            "qty": 1.0,
            "pnl": 10.0,
            "pnl_pct": 0.1,
            "fees": 0.5,
            "duration_s": 100.0,
        }
    ]
    fills_rows = [
        {
            "ts": 1_600_000_000_000,
            "order_side": "buy",
            "last_px": 100.0,
            "last_qty": 1.0,
            "commission": 0.5,
        }
    ]

    run_dir = artifacts_dir / record.run_id
    _write_artifacts(
        run_dir,
        equity=equity_rows,
        drawdown=drawdown_rows,
        price=price_rows,
        trades=trades_rows,
        fills=fills_rows,
    )

    response = client.get(f"/api/runs/{record.run_id}/tearsheet")
    assert response.status_code == 200
    body = response.json()

    assert len(body["equity"]) == 5
    assert len(body["drawdown"]) == 3
    assert len(body["price"]) == 3
    assert len(body["markers"]) == 2
    assert body["kpis"]["sharpe"] == 1.23
    assert body["verification"]["verified"] is True
    assert body["verification"]["discrepancy_pct"] < 0.001
    assert body["run"]["run_id"] == record.run_id


def test_equity_descending_order_is_sorted_ascending(
    client: TestClient, db_path: Path, artifacts_dir: Path
) -> None:
    record = _record(status="done")
    insert_run(db_path, record)

    equity_rows = [
        {"ts": 3_000, "equity": 103_000.0, "benchmark": None},
        {"ts": 2_000, "equity": 102_000.0, "benchmark": None},
        {"ts": 1_000, "equity": 101_000.0, "benchmark": None},
    ]
    run_dir = artifacts_dir / record.run_id
    _write_artifacts(run_dir, equity=equity_rows)

    response = client.get(f"/api/runs/{record.run_id}/tearsheet")
    assert response.status_code == 200
    ts_values = [pt["ts"] for pt in response.json()["equity"]]
    assert ts_values == [1_000, 2_000, 3_000]


def test_equity_duplicate_ts_keeps_first(
    client: TestClient, db_path: Path, artifacts_dir: Path
) -> None:
    record = _record(status="done")
    insert_run(db_path, record)

    equity_rows = [
        {"ts": 1_000, "equity": 101_000.0, "benchmark": None},
        {"ts": 1_000, "equity": 999_999.0, "benchmark": None},
        {"ts": 2_000, "equity": 102_000.0, "benchmark": None},
    ]
    run_dir = artifacts_dir / record.run_id
    _write_artifacts(run_dir, equity=equity_rows)

    response = client.get(f"/api/runs/{record.run_id}/tearsheet")
    assert response.status_code == 200
    equity_points = response.json()["equity"]
    assert len(equity_points) == 2
    assert equity_points[0]["ts"] == 1_000
    assert equity_points[0]["equity"] == 101_000.0


def test_monthly_returns_three_months(
    client: TestClient, db_path: Path, artifacts_dir: Path
) -> None:
    record = _record(status="done")
    insert_run(db_path, record)

    # 2024-01-01, 2024-02-01, 2024-03-01 (UTC midnight, epoch ms)
    equity_rows = [
        {"ts": 1_704_067_200_000, "equity": 100_000.0, "benchmark": None},  # Jan
        {"ts": 1_706_745_600_000, "equity": 110_000.0, "benchmark": None},  # Feb
        {"ts": 1_709_251_200_000, "equity": 121_000.0, "benchmark": None},  # Mar
    ]
    run_dir = artifacts_dir / record.run_id
    _write_artifacts(run_dir, equity=equity_rows)

    response = client.get(f"/api/runs/{record.run_id}/tearsheet")
    assert response.status_code == 200
    monthly_returns = response.json()["monthly_returns"]
    assert len(monthly_returns) == 1
    entry = monthly_returns[0]
    assert entry["year"] == 2024
    assert len(entry["months"]) == 12
    populated = [m for m in entry["months"] if m is not None]
    assert len(populated) == 3
    nulls = [m for m in entry["months"] if m is None]
    assert len(nulls) == 9
    assert entry["months"][0] == pytest.approx(0.0)  # Jan baseline == equity[0]
    assert entry["months"][1] == pytest.approx(0.1)  # Feb: (110k-100k)/100k
    assert entry["months"][2] == pytest.approx(0.1)  # Mar: (121k-110k)/110k


@pytest.mark.parametrize(
    ("side", "expected_entry_side", "expected_exit_side"),
    [("long", "buy", "sell"), ("short", "sell", "buy")],
)
def test_markers_side_mapping(
    client: TestClient,
    db_path: Path,
    artifacts_dir: Path,
    side: str,
    expected_entry_side: str,
    expected_exit_side: str,
) -> None:
    record = _record(status="done")
    insert_run(db_path, record)

    trades_rows = [
        {
            "trade_id": "t1",
            "symbol": "BTC/USDT",
            "side": side,
            "entry_ts": 1_000,
            "exit_ts": 2_000,
            "entry_px": 100.0,
            "exit_px": 110.0,
            "qty": 1.0,
            "pnl": 10.0,
            "pnl_pct": 0.1,
            "fees": 0.5,
            "duration_s": 100.0,
        }
    ]
    run_dir = artifacts_dir / record.run_id
    _write_artifacts(run_dir, trades=trades_rows)

    response = client.get(f"/api/runs/{record.run_id}/tearsheet")
    assert response.status_code == 200
    markers = response.json()["markers"]
    assert len(markers) == 2
    assert markers[0]["side"] == expected_entry_side
    assert markers[1]["side"] == expected_exit_side


def test_open_position_yields_single_entry_marker(
    client: TestClient, db_path: Path, artifacts_dir: Path
) -> None:
    record = _record(status="done")
    insert_run(db_path, record)

    trades_rows = [
        {
            "trade_id": "t1",
            "symbol": "BTC/USDT",
            "side": "long",
            "entry_ts": 1_000,
            "exit_ts": None,
            "entry_px": 100.0,
            "exit_px": None,
            "qty": 1.0,
            "pnl": 0.0,
            "pnl_pct": 0.0,
            "fees": 0.5,
            "duration_s": 0.0,
        }
    ]
    run_dir = artifacts_dir / record.run_id
    _write_artifacts(run_dir, trades=trades_rows)

    response = client.get(f"/api/runs/{record.run_id}/tearsheet")
    assert response.status_code == 200
    markers = response.json()["markers"]
    assert len(markers) == 1
    assert markers[0]["side"] == "buy"


def test_done_with_zero_row_parquets_returns_empty_lists(
    client: TestClient, db_path: Path, artifacts_dir: Path
) -> None:
    record = _record(status="done")
    insert_run(db_path, record)

    run_dir = artifacts_dir / record.run_id
    _write_artifacts(run_dir)

    response = client.get(f"/api/runs/{record.run_id}/tearsheet")
    assert response.status_code == 200
    body = response.json()
    assert body["equity"] == []
    assert body["drawdown"] == []
    assert body["price"] == []
    assert body["markers"] == []
    assert body["verification"]["verified"] is True
