"""Tests for ``POST /api/data/ingest``."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from quant.api.main import app


@pytest.fixture
def ingest_client() -> Iterator[TestClient]:
    with TestClient(app) as client:
        yield client


def test_valid_request_returns_202(
    ingest_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, Any] = {}

    class FakePopen:
        def __init__(self, argv: list[str], **kwargs: object) -> None:
            captured["argv"] = argv
            captured["kwargs"] = kwargs

    monkeypatch.setattr("quant.api.routers.data.subprocess.Popen", FakePopen)

    response = ingest_client.post(
        "/api/data/ingest",
        json={
            "venue": "binance",
            "symbol": "BTC/USDT",
            "timeframe": "1d",
            "start": "2024-02-01",
            "end": "2024-02-29",
        },
    )
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "started"
    assert "scripts/ingest_bars.py" in body["command"].replace("\\", "/")
    assert "--venue" in body["command"]
    assert "binance" in body["command"]
    assert "BTC/USDT" in body["command"]
    assert "2024-02-01" in body["command"]
    assert "2024-02-29" in body["command"]

    argv = captured["argv"]
    assert any("ingest_bars.py" in str(a) for a in argv)
    assert argv[-4:] == ["--start", "2024-02-01", "--end", "2024-02-29"]


def test_invalid_timeframe_returns_422(ingest_client: TestClient) -> None:
    response = ingest_client.post(
        "/api/data/ingest",
        json={
            "venue": "binance",
            "symbol": "BTC/USDT",
            "timeframe": "banana",
            "start": "2024-01-01",
            "end": "2024-01-31",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION"
    assert "invalid timeframe" in response.json()["error"]["message"]


def test_empty_start_returns_422(ingest_client: TestClient) -> None:
    response = ingest_client.post(
        "/api/data/ingest",
        json={
            "venue": "binance",
            "symbol": "BTC/USDT",
            "timeframe": "1d",
            "start": "",
            "end": "2024-01-31",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION"
    assert response.json()["error"]["message"] == "start and end are required"
