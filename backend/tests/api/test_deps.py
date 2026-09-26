"""Tests for FastAPI DB dependency providers in ``quant.api.deps``."""

from __future__ import annotations

import sqlite3

import duckdb
from fastapi import FastAPI
from fastapi.testclient import TestClient

from quant.api.deps import (
    BarsDb,
    RunsDb,
    _bars_db_path,
    _runs_db_path,
    get_bars_db,
    get_runs_db,
)
from quant.data.runs_store import init_runs_schema
from quant.data.store import init_schema


def test_sqlite_dependency_lifecycle(monkeypatch, tmp_path) -> None:
    runs_path = tmp_path / "runs.sqlite"
    monkeypatch.setenv("QUANT_RUNS_DB", str(runs_path))
    init_runs_schema(runs_path)

    app = FastAPI()

    @app.get("/t")
    def t(db: RunsDb) -> dict[str, int]:
        result = db.execute("SELECT 1").fetchone()
        return {"v": int(result[0])}

    client = TestClient(app)
    response = client.get("/t")
    assert response.status_code == 200
    assert response.json() == {"v": 1}


def test_duckdb_dependency_lifecycle(monkeypatch, tmp_path) -> None:
    bars_path = tmp_path / "bars.duckdb"
    monkeypatch.setenv("QUANT_BARS_DB", str(bars_path))
    init_schema(bars_path)

    app = FastAPI()

    @app.get("/t")
    def t(db: BarsDb) -> dict[str, int]:
        result = db.execute("SELECT 42").fetchone()
        return {"v": int(result[0])}

    client = TestClient(app)
    response = client.get("/t")
    assert response.status_code == 200
    assert response.json() == {"v": 42}


def test_runs_db_yields_sqlite_connection(monkeypatch, tmp_path) -> None:
    runs_path = tmp_path / "runs.sqlite"
    monkeypatch.setenv("QUANT_RUNS_DB", str(runs_path))
    gen = get_runs_db()
    conn = next(gen)
    assert isinstance(conn, sqlite3.Connection)
    gen.close()


def test_bars_db_yields_duckdb_connection(monkeypatch, tmp_path) -> None:
    bars_path = tmp_path / "bars.duckdb"
    monkeypatch.setenv("QUANT_BARS_DB", str(bars_path))
    init_schema(bars_path)

    gen = get_bars_db()
    conn = next(gen)
    assert isinstance(conn, duckdb.DuckDBPyConnection)
    gen.close()


def test_runs_db_path_env_override(monkeypatch, tmp_path) -> None:
    custom = tmp_path / "custom.sqlite"
    monkeypatch.setenv("QUANT_RUNS_DB", str(custom))
    assert _runs_db_path() == custom


def test_bars_db_path_env_override(monkeypatch, tmp_path) -> None:
    custom = tmp_path / "custom.duckdb"
    monkeypatch.setenv("QUANT_BARS_DB", str(custom))
    assert _bars_db_path() == custom
