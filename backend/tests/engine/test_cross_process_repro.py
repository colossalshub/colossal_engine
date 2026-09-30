"""Cross-process reproducibility: CLI backtest vs API queue + worker (Phase 14.4)."""

from __future__ import annotations

import importlib.util
import re
import sqlite3
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from quant import config
from quant.api.routers.runs import router
from quant.data.runs_store import claim_next_queued, init_runs_schema
from quant.data.store import ensure_canonical_bars, upsert_bars

_VENUE = "binance"
_SYMBOL = "BTC/USDT"
_DAY_MS = 86_400_000
_START_TS = 1_735_689_600_000
_END_TS = 1_736_467_200_000

_SHARED_PARAMS: dict[str, Any] = {
    "trade_size": "1",
    "deploy_pct": "1.0",
    "starting_balance": 100_000.0,
    "timeframe": "1d",
    "venue": _VENUE,
    "maker_fee": "0.001",
    "taker_fee": "0.001",
    "benchmark_symbol": "",
}


def _store_canonical_bars(db_path: Path) -> None:
    ensure_canonical_bars(db_path)
    rows: list[dict[str, object]] = []
    for i in range(10):
        ts = _START_TS + i * _DAY_MS
        rows.append(
            {
                "venue": _VENUE,
                "symbol": _SYMBOL,
                "asset_class": "crypto",
                "timeframe": "1d",
                "ts": ts,
                "open": 100.0,
                "high": 110.0,
                "low": 90.0,
                "close": 100.0,
                "volume": 1_000_000.0,
            }
        )
    upsert_bars(db_path, rows)


def _fetch_run(db_path: Path, run_id: str) -> dict[str, Any]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT status, data_snapshot FROM meta_runs WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        assert row is not None
        return {str(key): row[key] for key in row.keys()}
    finally:
        conn.close()


def _parse_run_id(stdout: str) -> str:
    for line in stdout.splitlines():
        if line.startswith("run_id="):
            return line.split("=", 1)[1].strip()
    raise AssertionError(f"run_id not found in stdout:\n{stdout}")


def _load_execute_claimed_run():
    script = config.repo_root() / "scripts" / "run_worker.py"
    spec = importlib.util.spec_from_file_location("run_worker_test", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._execute_claimed_run


@pytest.fixture
def api_runs_db(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "runs_api.sqlite"
    monkeypatch.setenv("QUANT_RUNS_DB", str(path))
    init_runs_schema(path)
    return path


@pytest.fixture
def api_client(api_runs_db: Path) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as test_client:
        yield test_client


def test_cli_and_worker_produce_identical_snapshot_and_equity(
    tmp_path: Path,
    api_client: TestClient,
    api_runs_db: Path,
) -> None:
    bars_db = tmp_path / "bars.duckdb"
    _store_canonical_bars(bars_db)

    cli_runs_db = tmp_path / "runs_cli.sqlite"
    cli_artifacts = tmp_path / "artifacts_cli"
    worker_artifacts = tmp_path / "artifacts_worker"

    repo_root = config.repo_root()
    script = repo_root / "scripts" / "run_backtest.py"
    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--venue",
            _VENUE,
            "--symbol",
            _SYMBOL,
            "--timeframe",
            "1d",
            "--start",
            "2025-01-01",
            "--end",
            "2025-01-10",
            "--strategy",
            "buy_hold",
            "--trade-size",
            "1",
            "--deploy-pct",
            "1.0",
            "--starting-balance",
            "100000",
            "--maker-fee",
            "0.001",
            "--taker-fee",
            "0.001",
            "--benchmark-symbol",
            "",
            "--db",
            str(bars_db),
            "--runs-db",
            str(cli_runs_db),
            "--artifacts-dir",
            str(cli_artifacts),
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(repo_root),
    )
    cli_run_id = _parse_run_id(proc.stdout)

    payload = {
        "strategy": "buy_hold",
        "params": _SHARED_PARAMS,
        "universe": [_SYMBOL],
        "start_ts": _START_TS,
        "end_ts": _END_TS,
    }
    response = api_client.post("/api/runs", json=payload)
    assert response.status_code == 201
    api_run_id = response.json()["run_id"]

    execute_claimed_run = _load_execute_claimed_run()
    conn = sqlite3.connect(api_runs_db)
    try:
        conn.execute("PRAGMA busy_timeout=5000")
        claimed = claim_next_queued(conn)
        assert claimed is not None
        assert claimed.run_id == api_run_id
        execute_claimed_run(
            conn,
            api_runs_db,
            claimed,
            bars_db,
            worker_artifacts,
        )
    finally:
        conn.close()

    cli_row = _fetch_run(cli_runs_db, cli_run_id)
    api_row = _fetch_run(api_runs_db, api_run_id)
    assert cli_row["status"] == "done"
    assert api_row["status"] == "done"

    cli_snap = cli_row["data_snapshot"]
    api_snap = api_row["data_snapshot"]
    assert cli_snap is not None and re.fullmatch(r"[0-9a-f]{64}", cli_snap)
    assert api_snap is not None and re.fullmatch(r"[0-9a-f]{64}", api_snap)
    assert cli_snap == api_snap

    cli_equity = cli_artifacts / cli_run_id / "equity.parquet"
    api_equity = worker_artifacts / api_run_id / "equity.parquet"
    cli_table = pq.read_table(cli_equity, columns=["ts", "equity", "benchmark"])
    api_table = pq.read_table(api_equity, columns=["ts", "equity", "benchmark"])
    assert cli_table.equals(api_table)

    cli_bytes = cli_equity.read_bytes()
    api_bytes = api_equity.read_bytes()
    assert cli_bytes == api_bytes
