"""Tests for ``quant.api.main`` — router wiring, ApiError handlers, health."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from quant.api.main import app
from quant.data.runs_store import init_runs_schema


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[TestClient]:
    db_path = tmp_path / "runs.sqlite"
    monkeypatch.setenv("QUANT_RUNS_DB", str(db_path))
    init_runs_schema(db_path)
    with TestClient(app) as test_client:
        yield test_client


def test_runs_list_wired(client: TestClient) -> None:
    response = client.get("/api/runs")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "page_size" in body


def test_tearsheet_not_found_api_error_shape(client: TestClient) -> None:
    response = client.get("/api/runs/does-not-exist/tearsheet")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"
    assert "message" in body["error"]


def test_trades_not_found_api_error_shape(client: TestClient) -> None:
    response = client.get("/api/runs/does-not-exist/trades")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"
    assert "message" in body["error"]


def test_validation_page_zero(client: TestClient) -> None:
    response = client.get("/api/runs?page=0")
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION"
    assert body["error"]["message"] == "request validation failed"
    assert body["error"]["details"] is not None


def test_validation_page_size_too_large(client: TestClient) -> None:
    response = client.get("/api/runs?page_size=999")
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION"


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
