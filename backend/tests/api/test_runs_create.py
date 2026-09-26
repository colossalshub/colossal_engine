"""Tests for `POST /api/runs` (`quant.api.routers.runs.create_run`)."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from quant.api.routers.runs import router
from quant.data.runs_store import init_runs_schema


@pytest.fixture
def db_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "runs.sqlite"
    monkeypatch.setenv("QUANT_RUNS_DB", str(path))
    init_runs_schema(path)
    return path


@pytest.fixture
def client(db_path: Path) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as test_client:
        yield test_client


def _fetch_run(db_path: Path, run_id: str) -> dict[str, Any]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM meta_runs WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        assert row is not None
        return {str(key): row[key] for key in row.keys()}
    finally:
        conn.close()


def _valid_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "strategy": "buy_hold",
        "params": {"trade_size": "1"},
        "universe": ["BTC/USDT"],
        "start_ts": 1_704_067_200_000,
        "end_ts": 1_706_659_200_000,
    }
    payload.update(overrides)
    return payload


def test_happy_path_returns_201_and_queued_summary(
    client: TestClient, db_path: Path
) -> None:
    response = client.post("/api/runs", json=_valid_payload())
    assert response.status_code == 201
    body = response.json()

    assert body["status"] == "queued"
    assert body["strategy"] == "buy_hold"
    assert body["universe"] == ["BTC/USDT"]
    assert body["start_ts"] == 1_704_067_200_000
    assert body["end_ts"] == 1_706_659_200_000
    assert body["git_sha"] is None
    assert body["git_dirty"] is False
    assert body["sharpe"] is None
    assert body["cagr"] is None
    assert body["max_drawdown"] is None
    assert isinstance(body["run_id"], str) and body["run_id"]
    assert isinstance(body["created_at"], int)

    row = _fetch_run(db_path, body["run_id"])
    assert row["run_id"] == body["run_id"]
    assert row["status"] == "queued"


def test_universe_empty_422(client: TestClient) -> None:
    response = client.post("/api/runs", json=_valid_payload(universe=[]))
    assert response.status_code == 422
    assert response.json()["detail"]["error"]["code"] == "VALIDATION"


def test_start_ts_after_end_ts_422(client: TestClient) -> None:
    response = client.post(
        "/api/runs",
        json=_valid_payload(start_ts=1_706_659_200_000, end_ts=1_704_067_200_000),
    )
    assert response.status_code == 422
    assert response.json()["detail"]["error"]["code"] == "VALIDATION"


def test_start_ts_equal_end_ts_422(client: TestClient) -> None:
    response = client.post(
        "/api/runs",
        json=_valid_payload(start_ts=1_704_067_200_000, end_ts=1_704_067_200_000),
    )
    assert response.status_code == 422
    assert response.json()["detail"]["error"]["code"] == "VALIDATION"


def test_unknown_strategy_422(client: TestClient) -> None:
    response = client.post("/api/runs", json=_valid_payload(strategy="momentum"))
    assert response.status_code == 422
    body = response.json()
    assert body["detail"]["error"]["code"] == "VALIDATION"
    assert "momentum" in body["detail"]["error"]["message"]


def test_missing_strategy_field_422(client: TestClient) -> None:
    payload = _valid_payload()
    del payload["strategy"]
    response = client.post("/api/runs", json=payload)
    assert response.status_code == 422
    # FastAPI's Pydantic error handler produces the default `detail` list
    # shape (not our `{"error": {...}}` envelope) for missing-field errors.
    assert "detail" in response.json()


def test_default_name_generation_single_symbol(
    client: TestClient, db_path: Path
) -> None:
    response = client.post("/api/runs", json=_valid_payload())
    assert response.status_code == 201
    run_id = response.json()["run_id"]
    row = _fetch_run(db_path, run_id)
    assert row["name"] == "buy_hold BTC/USDT"


def test_default_name_generation_multi_symbol(
    client: TestClient, db_path: Path
) -> None:
    response = client.post(
        "/api/runs",
        json=_valid_payload(universe=["BTC/USDT", "ETH/USDT"]),
    )
    assert response.status_code == 201
    run_id = response.json()["run_id"]
    row = _fetch_run(db_path, run_id)
    assert row["name"] == "buy_hold BTC/USDT,ETH/USDT"


def test_explicit_name_is_preserved(client: TestClient, db_path: Path) -> None:
    response = client.post("/api/runs", json=_valid_payload(name="my custom run"))
    assert response.status_code == 201
    run_id = response.json()["run_id"]
    row = _fetch_run(db_path, run_id)
    assert row["name"] == "my custom run"


def test_params_round_trip(client: TestClient, db_path: Path) -> None:
    params = {"trade_size": "2", "starting_balance": 50000}
    response = client.post("/api/runs", json=_valid_payload(params=params))
    assert response.status_code == 201
    run_id = response.json()["run_id"]
    row = _fetch_run(db_path, run_id)
    assert json.loads(row["params"]) == params


def test_universe_round_trip_preserves_order(
    client: TestClient, db_path: Path
) -> None:
    universe = ["BTC/USDT", "ETH/USDT"]
    response = client.post("/api/runs", json=_valid_payload(universe=universe))
    assert response.status_code == 201
    run_id = response.json()["run_id"]
    row = _fetch_run(db_path, run_id)
    assert json.loads(row["universe"]) == universe
