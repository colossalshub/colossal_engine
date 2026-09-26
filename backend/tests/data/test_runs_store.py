from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

import pytest

from quant.data.runs_store import (
    RunRecord,
    _now_ms,
    init_runs_schema,
    insert_run,
    insert_run_with_connection,
)

META_RUNS_COLUMNS: frozenset[str] = frozenset(
    {
        "run_id",
        "name",
        "strategy",
        "params",
        "universe",
        "start_ts",
        "end_ts",
        "created_at",
        "finished_at",
        "heartbeat_ts",
        "status",
        "error",
        "git_sha",
        "git_dirty",
        "data_snapshot",
        "seed",
        "metrics",
        "artifacts",
    }
)


def _column_names(db_path: Path) -> set[str]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("PRAGMA table_info('meta_runs')").fetchall()
    finally:
        conn.close()
    return {str(row[1]) for row in rows}


def _table_exists(db_path: Path) -> bool:
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'meta_runs'"
        ).fetchone()
    finally:
        conn.close()
    return row is not None


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


def _count_runs(db_path: Path) -> int:
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute("SELECT COUNT(*) FROM meta_runs").fetchone()
    finally:
        conn.close()
    assert row is not None
    return int(row[0])


def _record(**overrides: Any) -> RunRecord:
    created = _now_ms()
    record = RunRecord(
        run_id=str(uuid.uuid4()),
        name="mom-12-1",
        strategy="buy_hold",
        params={"lookback": 12, "skip": 1},
        universe=["BTC/USDT", "ETH/USDT"],
        start_ts=1577836800000,
        end_ts=1767225600000,
        created_at=created,
        finished_at=created + 1000,
        heartbeat_ts=created + 500,
        status="done",
        error="none",
        git_sha="a" * 40,
        git_dirty=True,
        data_snapshot="snapshot-sha",
        seed=7,
        metrics={"sharpe": 1.42, "cagr": 0.21},
        artifacts={"equity": "equity.parquet", "trades": "trades.parquet"},
    )
    for key, value in overrides.items():
        setattr(record, key, value)
    return record


def _init(tmp_path: Path) -> Path:
    db_path = tmp_path / "runs.sqlite"
    init_runs_schema(db_path)
    return db_path


def test_init_runs_schema_creates_file_and_table(tmp_path: Path) -> None:
    db_path = tmp_path / "runs.sqlite"
    init_runs_schema(db_path)
    assert db_path.is_file()
    assert _table_exists(db_path)


def test_init_runs_schema_column_names(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    assert _column_names(db_path) == META_RUNS_COLUMNS


def test_init_runs_schema_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "runs.sqlite"
    init_runs_schema(db_path)
    init_runs_schema(db_path)
    assert _table_exists(db_path)
    assert _column_names(db_path) == META_RUNS_COLUMNS


def test_init_runs_schema_creates_missing_parent(tmp_path: Path) -> None:
    db_path = tmp_path / "missing" / "nested" / "runs.sqlite"
    assert not db_path.parent.exists()
    init_runs_schema(db_path)
    assert db_path.parent.is_dir()
    assert db_path.is_file()
    assert _table_exists(db_path)


def test_init_runs_schema_journal_mode_wal(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute("PRAGMA journal_mode").fetchone()
    finally:
        conn.close()
    assert row is not None
    assert row[0] == "wal"


def test_insert_run_round_trip(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    record = _record()
    insert_run(db_path, record)

    row = _fetch_run(db_path, record.run_id)
    assert row["run_id"] == record.run_id
    assert row["name"] == record.name
    assert row["strategy"] == record.strategy
    assert json.loads(row["params"]) == record.params
    assert json.loads(row["universe"]) == record.universe
    assert row["start_ts"] == record.start_ts
    assert row["end_ts"] == record.end_ts
    assert row["created_at"] == record.created_at
    assert row["finished_at"] == record.finished_at
    assert row["heartbeat_ts"] == record.heartbeat_ts
    assert row["status"] == record.status
    assert row["error"] == record.error
    assert row["git_sha"] == record.git_sha
    assert row["git_dirty"] == 1
    assert row["data_snapshot"] == record.data_snapshot
    assert row["seed"] == record.seed
    assert json.loads(row["metrics"]) == record.metrics
    assert json.loads(row["artifacts"]) == record.artifacts


@pytest.mark.parametrize(("git_dirty", "stored"), [(True, 1), (False, 0)])
def test_insert_run_git_dirty_as_int(
    tmp_path: Path, git_dirty: bool, stored: int
) -> None:
    db_path = _init(tmp_path)
    record = _record(git_dirty=git_dirty)
    insert_run(db_path, record)
    row = _fetch_run(db_path, record.run_id)
    assert row["git_dirty"] == stored


def test_insert_run_empty_json_shapes(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    record = _record(params={}, universe=[], metrics={}, artifacts={})
    insert_run(db_path, record)
    row = _fetch_run(db_path, record.run_id)
    assert row["params"] == "{}"
    assert row["universe"] == "[]"
    assert row["metrics"] == "{}"
    assert row["artifacts"] == "{}"


def test_insert_run_null_optionals(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    record = _record(
        finished_at=None,
        heartbeat_ts=None,
        error=None,
        git_sha=None,
        data_snapshot=None,
    )
    insert_run(db_path, record)
    row = _fetch_run(db_path, record.run_id)
    assert row["finished_at"] is None
    assert row["heartbeat_ts"] is None
    assert row["error"] is None
    assert row["git_sha"] is None
    assert row["data_snapshot"] is None


def test_insert_run_two_distinct_ids(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    first = _record(run_id="run-a")
    second = _record(run_id="run-b")
    insert_run(db_path, first)
    insert_run(db_path, second)
    assert _count_runs(db_path) == 2
    assert _fetch_run(db_path, "run-a")["name"] == first.name
    assert _fetch_run(db_path, "run-b")["name"] == second.name


def test_insert_run_duplicate_run_id_raises(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    record = _record(run_id="same-id")
    insert_run(db_path, record)
    with pytest.raises(sqlite3.IntegrityError):
        insert_run(db_path, record)
    assert _count_runs(db_path) == 1


def test_insert_run_without_schema_raises(tmp_path: Path) -> None:
    db_path = tmp_path / "runs.sqlite"
    with pytest.raises(sqlite3.OperationalError):
        insert_run(db_path, _record())


def test_insert_run_json_is_compact(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    record = _record(params={"a": 1, "b": 2})
    insert_run(db_path, record)
    row = _fetch_run(db_path, record.run_id)
    assert row["params"] == '{"a":1,"b":2}'


def test_insert_run_with_connection_round_trip(tmp_path: Path) -> None:
    """Insert via an existing connection, close it, then read back the row
    through a fresh connection (mirrors the FastAPI per-request pattern)."""
    db_path = _init(tmp_path)
    record = _record()

    conn = sqlite3.connect(db_path)
    try:
        insert_run_with_connection(conn, record)
    finally:
        conn.close()

    row = _fetch_run(db_path, record.run_id)
    assert row["run_id"] == record.run_id
    assert row["name"] == record.name
    assert row["strategy"] == record.strategy
    assert json.loads(row["params"]) == record.params
    assert json.loads(row["universe"]) == record.universe
    assert row["status"] == record.status
    assert row["git_dirty"] == 1
    assert json.loads(row["metrics"]) == record.metrics
    assert json.loads(row["artifacts"]) == record.artifacts
    assert _count_runs(db_path) == 1
