"""Tests for `GET /api/runs` (`quant.api.routers.runs.list_runs`)."""

from __future__ import annotations

import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from quant.api.routers.runs import router
from quant.data.runs_store import RunRecord, _now_ms, init_runs_schema, insert_run


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[TestClient]:
    db_path = tmp_path / "runs.sqlite"
    monkeypatch.setenv("QUANT_RUNS_DB", str(db_path))
    init_runs_schema(db_path)

    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "runs.sqlite"
    monkeypatch.setenv("QUANT_RUNS_DB", str(path))
    init_runs_schema(path)
    return path


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


def _insert_raw(db_path: Path, run_id: str, **column_overrides: Any) -> None:
    """Insert a row bypassing the store, for malformed-JSON scenarios."""
    record = _record(run_id=run_id)
    insert_run(db_path, record)
    if column_overrides:
        conn = sqlite3.connect(db_path)
        try:
            set_sql = ", ".join(f"{col} = ?" for col in column_overrides)
            conn.execute(
                f"UPDATE meta_runs SET {set_sql} WHERE run_id = ?",
                (*column_overrides.values(), run_id),
            )
            conn.commit()
        finally:
            conn.close()


def test_empty_db_returns_empty_list(client: TestClient) -> None:
    response = client.get("/api/runs")
    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "page": 1, "page_size": 50}


def test_one_run_all_fields_round_trip(client: TestClient, db_path: Path) -> None:
    record = _record()
    insert_run(db_path, record)

    response = client.get("/api/runs")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    item = body["items"][0]
    assert item["run_id"] == record.run_id
    assert item["name"] == record.name
    assert item["strategy"] == record.strategy
    assert item["universe"] == record.universe
    assert item["start_ts"] == record.start_ts
    assert item["end_ts"] == record.end_ts
    assert item["created_at"] == record.created_at
    assert item["git_sha"] == record.git_sha
    assert item["git_dirty"] is True
    assert item["status"] == record.status
    assert item["sharpe"] == 1.42
    assert item["cagr"] == 0.21
    assert item["max_drawdown"] == -0.18


def test_empty_metrics_yields_all_none(client: TestClient, db_path: Path) -> None:
    record = _record(metrics={})
    insert_run(db_path, record)

    response = client.get("/api/runs")
    item = response.json()["items"][0]
    assert item["sharpe"] is None
    assert item["cagr"] is None
    assert item["max_drawdown"] is None


def test_metrics_with_null_and_partial_values(
    client: TestClient, db_path: Path
) -> None:
    record = _record(metrics={"sharpe": None, "cagr": 0.15})
    insert_run(db_path, record)

    response = client.get("/api/runs")
    item = response.json()["items"][0]
    assert item["sharpe"] is None
    assert item["cagr"] == 0.15
    assert item["max_drawdown"] is None


def test_three_runs_ordered_by_created_at_desc(
    client: TestClient, db_path: Path
) -> None:
    base = _now_ms()
    r1 = _record(run_id="r1", created_at=base + 100)
    r2 = _record(run_id="r2", created_at=base)
    r3 = _record(run_id="r3", created_at=base + 200)
    # insert in an unsorted order
    insert_run(db_path, r2)
    insert_run(db_path, r1)
    insert_run(db_path, r3)

    response = client.get("/api/runs")
    items = response.json()["items"]
    assert [item["run_id"] for item in items] == ["r3", "r1", "r2"]
    assert items[0]["created_at"] >= items[1]["created_at"] >= items[2]["created_at"]


def test_filter_by_strategy(client: TestClient, db_path: Path) -> None:
    insert_run(db_path, _record(run_id="a1", strategy="momentum"))
    insert_run(db_path, _record(run_id="a2", strategy="momentum"))
    insert_run(db_path, _record(run_id="b1", strategy="mean_reversion"))

    response = client.get("/api/runs", params={"strategy": "momentum"})
    body = response.json()
    assert body["total"] == 2
    assert {item["strategy"] for item in body["items"]} == {"momentum"}


@pytest.mark.parametrize("target_status", ["done", "queued", "archived"])
def test_filter_by_status(
    client: TestClient, db_path: Path, target_status: str
) -> None:
    insert_run(db_path, _record(run_id="s1", status="done"))
    insert_run(db_path, _record(run_id="s2", status="queued"))
    insert_run(db_path, _record(run_id="s3", status="archived"))
    insert_run(db_path, _record(run_id="s4", status="running"))
    insert_run(db_path, _record(run_id="s5", status="failed"))

    response = client.get("/api/runs", params={"status": target_status})
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["status"] == target_status


def test_filter_by_strategy_and_status_intersection(
    client: TestClient, db_path: Path
) -> None:
    insert_run(db_path, _record(run_id="x1", strategy="momentum", status="done"))
    insert_run(db_path, _record(run_id="x2", strategy="momentum", status="queued"))
    insert_run(db_path, _record(run_id="x3", strategy="mean_reversion", status="done"))

    response = client.get(
        "/api/runs", params={"strategy": "momentum", "status": "done"}
    )
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["run_id"] == "x1"


@pytest.mark.parametrize(
    ("page", "page_size", "expected_count"),
    [(1, 2, 2), (2, 2, 2), (3, 2, 1), (4, 2, 0)],
)
def test_pagination(
    client: TestClient, db_path: Path, page: int, page_size: int, expected_count: int
) -> None:
    base = _now_ms()
    for i in range(5):
        insert_run(db_path, _record(run_id=f"p{i}", created_at=base + i))

    response = client.get("/api/runs", params={"page": page, "page_size": page_size})
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == expected_count
    assert body["total"] == 5
    assert body["page"] == page
    assert body["page_size"] == page_size


@pytest.mark.parametrize(
    "query",
    [
        {"page": 0},
        {"page_size": 0},
        {"page_size": 501},
    ],
)
def test_invalid_pagination_params_422(
    client: TestClient, query: dict[str, int]
) -> None:
    response = client.get("/api/runs", params=query)
    assert response.status_code == 422


def test_bad_status_filter_422(client: TestClient) -> None:
    response = client.get("/api/runs", params={"status": "bogus"})
    assert response.status_code == 422


def test_malformed_universe_json_coerces_to_empty_list(
    client: TestClient, db_path: Path
) -> None:
    _insert_raw(db_path, "malformed-universe", universe="{not valid json")

    response = client.get("/api/runs")
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["universe"] == []


def test_malformed_metrics_json_coerces_to_none(
    client: TestClient, db_path: Path
) -> None:
    _insert_raw(db_path, "malformed-metrics", metrics="{not valid json")

    response = client.get("/api/runs")
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["sharpe"] is None
    assert item["cagr"] is None
    assert item["max_drawdown"] is None
