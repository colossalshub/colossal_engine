"""Tests for `runs_store.py`, including Phase 7.3b's worker-support functions.

Note (Phase 7.3b): `scripts/run_worker.py` has no dedicated test file by
design. Its behavior is fully covered here by testing `claim_next_queued`,
`update_heartbeat`, `update_run_status`, and `fail_stale_running` in
isolation — those are exactly the DB-touching pieces of the worker's
contract. The remaining glue in the script (a `time.sleep(1)` poll loop
and a daemon heartbeat thread) is orchestration, not logic; mocking
`threading`/`time` to "test" it would just re-assert the mock's own
behavior and wouldn't catch real regressions.
"""

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
    claim_next_queued,
    fail_stale_running,
    init_runs_schema,
    insert_run,
    insert_run_with_connection,
    update_heartbeat,
    update_run_status,
)

RESEARCH_METADATA_COLUMNS: frozenset[str] = frozenset(
    {
        "experiment_id",
        "research_stage",
        "hypothesis_id",
        "strategy_version",
        "in_sample_start_ts",
        "in_sample_end_ts",
        "validation_start_ts",
        "validation_end_ts",
        "oos_start_ts",
        "oos_end_ts",
        "trial_index",
        "trial_count",
    }
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
) | RESEARCH_METADATA_COLUMNS


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
    assert row["experiment_id"] == record.experiment_id
    assert row["research_stage"] == record.research_stage
    assert row["hypothesis_id"] == record.hypothesis_id
    assert row["strategy_version"] == record.strategy_version
    assert row["in_sample_start_ts"] == record.in_sample_start_ts
    assert row["in_sample_end_ts"] == record.in_sample_end_ts
    assert row["validation_start_ts"] == record.validation_start_ts
    assert row["validation_end_ts"] == record.validation_end_ts
    assert row["oos_start_ts"] == record.oos_start_ts
    assert row["oos_end_ts"] == record.oos_end_ts
    assert row["trial_index"] == record.trial_index
    assert row["trial_count"] == record.trial_count
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


# --- claim_next_queued -------------------------------------------------


def test_claim_next_queued_empty_table_returns_none(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    conn = sqlite3.connect(db_path)
    try:
        assert claim_next_queued(conn) is None
    finally:
        conn.close()


def test_claim_next_queued_one_row_claims_it(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    record = _record(run_id="run-a", status="queued", heartbeat_ts=None)
    insert_run(db_path, record)

    conn = sqlite3.connect(db_path)
    try:
        claimed = claim_next_queued(conn)
    finally:
        conn.close()

    assert claimed is not None
    assert claimed.run_id == "run-a"
    assert claimed.status == "running"
    assert claimed.heartbeat_ts is not None

    row = _fetch_run(db_path, "run-a")
    assert row["status"] == "running"
    assert row["heartbeat_ts"] == claimed.heartbeat_ts


def test_claim_next_queued_claims_the_older_row(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    older = _record(run_id="run-old", status="queued", created_at=1000)
    newer = _record(run_id="run-new", status="queued", created_at=2000)
    insert_run(db_path, newer)
    insert_run(db_path, older)

    conn = sqlite3.connect(db_path)
    try:
        claimed = claim_next_queued(conn)
    finally:
        conn.close()

    assert claimed is not None
    assert claimed.run_id == "run-old"
    assert _fetch_run(db_path, "run-new")["status"] == "queued"


def test_claim_next_queued_ignores_running_rows(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    running = _record(run_id="run-running", status="running", created_at=500)
    queued = _record(run_id="run-queued", status="queued", created_at=1500)
    insert_run(db_path, running)
    insert_run(db_path, queued)

    conn = sqlite3.connect(db_path)
    try:
        claimed = claim_next_queued(conn)
    finally:
        conn.close()

    assert claimed is not None
    assert claimed.run_id == "run-queued"
    assert _fetch_run(db_path, "run-running")["status"] == "running"


# --- update_heartbeat ----------------------------------------------------


def test_update_heartbeat_sets_new_value(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    record = _record(run_id="run-hb", heartbeat_ts=1)
    insert_run(db_path, record)

    conn = sqlite3.connect(db_path)
    try:
        update_heartbeat(conn, "run-hb")
    finally:
        conn.close()

    row = _fetch_run(db_path, "run-hb")
    assert row["heartbeat_ts"] is not None
    assert row["heartbeat_ts"] > 1


# --- update_run_status -----------------------------------------------------


def test_update_run_status_done_with_metrics_and_artifacts(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    record = _record(run_id="run-done", status="running", metrics={}, artifacts={})
    insert_run(db_path, record)

    metrics = {"sharpe": 1.1, "cagr": 0.15}
    artifacts = {"equity": "equity.parquet"}

    conn = sqlite3.connect(db_path)
    try:
        update_run_status(
            conn,
            "run-done",
            status="done",
            metrics=metrics,
            artifacts=artifacts,
        )
    finally:
        conn.close()

    row = _fetch_run(db_path, "run-done")
    assert row["status"] == "done"
    assert json.loads(row["metrics"]) == metrics
    assert json.loads(row["artifacts"]) == artifacts


def test_update_run_status_failed_with_error(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    record = _record(run_id="run-fail", status="running", error=None)
    insert_run(db_path, record)

    conn = sqlite3.connect(db_path)
    try:
        update_run_status(conn, "run-fail", status="failed", error="boom")
    finally:
        conn.close()

    row = _fetch_run(db_path, "run-fail")
    assert row["status"] == "failed"
    assert row["error"] == "boom"


def test_update_run_status_data_snapshot_optional(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    record = _record(
        run_id="run-snapshot",
        status="running",
        data_snapshot="original-sha",
    )
    insert_run(db_path, record)

    conn = sqlite3.connect(db_path)
    try:
        update_run_status(conn, "run-snapshot", status="running")
        assert _fetch_run(db_path, "run-snapshot")["data_snapshot"] == "original-sha"

        update_run_status(
            conn,
            "run-snapshot",
            status="done",
            data_snapshot="f" * 64,
        )
    finally:
        conn.close()

    row = _fetch_run(db_path, "run-snapshot")
    assert row["status"] == "done"
    assert row["data_snapshot"] == "f" * 64


def test_update_run_status_sets_finished_at(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    record = _record(run_id="run-finished", status="running", finished_at=None)
    insert_run(db_path, record)

    conn = sqlite3.connect(db_path)
    try:
        update_run_status(conn, "run-finished", status="done", finished_at=12345)
    finally:
        conn.close()

    row = _fetch_run(db_path, "run-finished")
    assert row["status"] == "done"
    assert row["finished_at"] == 12345


# --- fail_stale_running ------------------------------------------------


def test_fail_stale_running_marks_old_heartbeat_as_failed(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    now = _now_ms()
    record = _record(run_id="run-stale", status="running", heartbeat_ts=now - 61_000)
    insert_run(db_path, record)

    conn = sqlite3.connect(db_path)
    try:
        count = fail_stale_running(conn, stale_ms=60_000)
    finally:
        conn.close()

    assert count == 1
    row = _fetch_run(db_path, "run-stale")
    assert row["status"] == "failed"
    assert row["error"] == "heartbeat timeout"


def test_fail_stale_running_leaves_fresh_heartbeat_unchanged(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    now = _now_ms()
    record = _record(run_id="run-fresh", status="running", heartbeat_ts=now)
    insert_run(db_path, record)

    conn = sqlite3.connect(db_path)
    try:
        count = fail_stale_running(conn, stale_ms=60_000)
    finally:
        conn.close()

    assert count == 0
    row = _fetch_run(db_path, "run-fresh")
    assert row["status"] == "running"


def test_fail_stale_running_ignores_queued_rows(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    now = _now_ms()
    record = _record(run_id="run-queued", status="queued", heartbeat_ts=now - 61_000)
    insert_run(db_path, record)

    conn = sqlite3.connect(db_path)
    try:
        count = fail_stale_running(conn, stale_ms=60_000)
    finally:
        conn.close()

    assert count == 0
    row = _fetch_run(db_path, "run-queued")
    assert row["status"] == "queued"


def test_fail_stale_running_multiple_rows(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    now = _now_ms()
    stale_a = _record(
        run_id="run-stale-a", status="running", heartbeat_ts=now - 100_000
    )
    stale_b = _record(
        run_id="run-stale-b", status="running", heartbeat_ts=now - 200_000
    )
    fresh = _record(run_id="run-stale-c", status="running", heartbeat_ts=now)
    insert_run(db_path, stale_a)
    insert_run(db_path, stale_b)
    insert_run(db_path, fresh)

    conn = sqlite3.connect(db_path)
    try:
        count = fail_stale_running(conn, stale_ms=60_000)
    finally:
        conn.close()

    assert count == 2
    assert _fetch_run(db_path, "run-stale-a")["status"] == "failed"
    assert _fetch_run(db_path, "run-stale-b")["status"] == "failed"
    assert _fetch_run(db_path, "run-stale-c")["status"] == "running"


def test_init_runs_schema_fresh_db_has_experiment_id(tmp_path: Path) -> None:
    db_path = _init(tmp_path)

    assert "experiment_id" in _column_names(db_path)


def test_init_runs_schema_twice_is_idempotent(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    init_runs_schema(db_path)

    assert "experiment_id" in _column_names(db_path)


def test_insert_run_experiment_id_none_stores_null(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    insert_run(db_path, _record(run_id="exp-none"))

    assert _fetch_run(db_path, "exp-none")["experiment_id"] is None


def test_insert_run_experiment_id_round_trips(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    insert_run(db_path, _record(run_id="exp-set", experiment_id="exp-001"))

    assert _fetch_run(db_path, "exp-set")["experiment_id"] == "exp-001"


def test_insert_run_research_metadata_round_trips(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    record = _record(
        run_id="research-set",
        experiment_id="exp-001",
        research_stage="oos",
        hypothesis_id="hyp-007",
        strategy_version="ema-cross-v2",
        in_sample_start_ts=1_577_836_800_000,
        in_sample_end_ts=1_609_459_200_000,
        validation_start_ts=1_609_459_200_001,
        validation_end_ts=1_640_995_200_000,
        oos_start_ts=1_640_995_200_001,
        oos_end_ts=1_672_531_200_000,
        trial_index=3,
        trial_count=12,
    )

    insert_run(db_path, record)

    row = _fetch_run(db_path, "research-set")
    for field in (
        "experiment_id",
        "research_stage",
        "hypothesis_id",
        "strategy_version",
        "in_sample_start_ts",
        "in_sample_end_ts",
        "validation_start_ts",
        "validation_end_ts",
        "oos_start_ts",
        "oos_end_ts",
        "trial_index",
        "trial_count",
    ):
        assert row[field] == getattr(record, field)


def test_insert_run_with_connection_research_metadata_round_trips(
    tmp_path: Path,
) -> None:
    db_path = _init(tmp_path)
    record = _record(
        run_id="exp-conn",
        experiment_id="exp-002",
        research_stage="validation",
        hypothesis_id="hyp-002",
        strategy_version="buy-hold-v2",
        in_sample_start_ts=100,
        in_sample_end_ts=200,
        validation_start_ts=201,
        validation_end_ts=300,
        oos_start_ts=301,
        oos_end_ts=400,
        trial_index=1,
        trial_count=4,
    )
    conn = sqlite3.connect(db_path)
    try:
        insert_run_with_connection(conn, record)
    finally:
        conn.close()

    row = _fetch_run(db_path, "exp-conn")
    for field in RESEARCH_METADATA_COLUMNS:
        assert row[field] == getattr(record, field)


def test_insert_run_seed_none_stores_null(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    insert_run(db_path, _record(run_id="seed-none", seed=None))

    assert _fetch_run(db_path, "seed-none")["seed"] is None


def test_init_runs_schema_adds_research_columns_to_legacy_db(tmp_path: Path) -> None:
    db_path = tmp_path / "legacy.sqlite"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE meta_runs (
                run_id        TEXT PRIMARY KEY,
                name          TEXT NOT NULL,
                strategy      TEXT NOT NULL,
                params        TEXT NOT NULL DEFAULT '{}',
                universe      TEXT NOT NULL DEFAULT '[]',
                start_ts      INTEGER NOT NULL,
                end_ts        INTEGER NOT NULL,
                created_at    INTEGER NOT NULL,
                finished_at   INTEGER,
                heartbeat_ts  INTEGER,
                status        TEXT NOT NULL DEFAULT 'queued',
                error         TEXT,
                git_sha       TEXT,
                git_dirty     INTEGER DEFAULT 0,
                data_snapshot TEXT,
                seed          INTEGER DEFAULT 0,
                metrics       TEXT DEFAULT '{}',
                artifacts     TEXT DEFAULT '{}'
            )
            """
        )
        conn.execute(
            "INSERT INTO meta_runs (run_id, name, strategy, start_ts, end_ts, "
            "created_at) VALUES ('old', 'old', 'buy_hold', 1, 2, 3)"
        )
        conn.commit()
    finally:
        conn.close()
    assert RESEARCH_METADATA_COLUMNS.isdisjoint(_column_names(db_path))

    init_runs_schema(db_path)

    assert _column_names(db_path) == META_RUNS_COLUMNS
    legacy_row = _fetch_run(db_path, "old")
    for field in (
        "experiment_id",
        "research_stage",
        "hypothesis_id",
        "strategy_version",
        "in_sample_start_ts",
        "in_sample_end_ts",
        "validation_start_ts",
        "validation_end_ts",
        "oos_start_ts",
        "oos_end_ts",
        "trial_index",
        "trial_count",
    ):
        assert legacy_row[field] is None
    assert legacy_row["seed"] == 0
    insert_run(db_path, _record(run_id="new", experiment_id="exp-003"))
    assert _fetch_run(db_path, "new")["experiment_id"] == "exp-003"


def test_claim_next_queued_preserves_research_metadata(tmp_path: Path) -> None:
    db_path = _init(tmp_path)
    record = _record(
        run_id="research-queued",
        status="queued",
        experiment_id="exp-queued",
        research_stage="exploration",
        hypothesis_id="hyp-queued",
        strategy_version="buy-hold-v1",
        in_sample_start_ts=100,
        in_sample_end_ts=200,
        validation_start_ts=201,
        validation_end_ts=300,
        oos_start_ts=301,
        oos_end_ts=400,
        trial_index=2,
        trial_count=5,
    )
    insert_run(db_path, record)

    conn = sqlite3.connect(db_path)
    try:
        claimed = claim_next_queued(conn)
    finally:
        conn.close()

    assert claimed is not None
    for field in (
        "experiment_id",
        "research_stage",
        "hypothesis_id",
        "strategy_version",
        "in_sample_start_ts",
        "in_sample_end_ts",
        "validation_start_ts",
        "validation_end_ts",
        "oos_start_ts",
        "oos_end_ts",
        "trial_index",
        "trial_count",
    ):
        assert getattr(claimed, field) == getattr(record, field)
