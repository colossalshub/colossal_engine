"""SQLite schema initialization and meta_runs persistence."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_CREATE_META_RUNS_SQL = """
CREATE TABLE IF NOT EXISTS meta_runs (
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

_INSERT_RUN_SQL = """
INSERT INTO meta_runs (
    run_id,
    name,
    strategy,
    params,
    universe,
    start_ts,
    end_ts,
    created_at,
    finished_at,
    heartbeat_ts,
    status,
    error,
    git_sha,
    git_dirty,
    data_snapshot,
    seed,
    metrics,
    artifacts
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


@dataclass
class RunRecord:
    run_id: str
    name: str
    strategy: str
    params: dict[str, Any]
    universe: list[str]
    start_ts: int
    end_ts: int
    created_at: int
    finished_at: int | None = None
    heartbeat_ts: int | None = None
    status: str = "queued"
    error: str | None = None
    git_sha: str | None = None
    git_dirty: bool = False
    data_snapshot: str | None = None
    seed: int = 0
    metrics: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)


def _now_ms() -> int:
    return int(datetime.now(UTC).timestamp() * 1000)


def init_runs_schema(db_path: Path) -> None:
    """Create the SQLite file and meta_runs table if they do not exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute(_CREATE_META_RUNS_SQL)
        conn.commit()
    finally:
        conn.close()


def insert_run(db_path: Path, record: RunRecord) -> None:
    """Insert one meta_runs row. Caller must initialize the schema first."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute(
            _INSERT_RUN_SQL,
            (
                record.run_id,
                record.name,
                record.strategy,
                json.dumps(record.params, separators=(",", ":")),
                json.dumps(record.universe, separators=(",", ":")),
                record.start_ts,
                record.end_ts,
                record.created_at,
                record.finished_at,
                record.heartbeat_ts,
                record.status,
                record.error,
                record.git_sha,
                1 if record.git_dirty else 0,
                record.data_snapshot,
                record.seed,
                json.dumps(record.metrics, separators=(",", ":")),
                json.dumps(record.artifacts, separators=(",", ":")),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def insert_run_with_connection(conn: sqlite3.Connection, record: RunRecord) -> None:
    """Insert one meta_runs row using an existing connection.

    Caller owns schema setup and commit lifecycle (e.g. a FastAPI
    per-request connection from `quant.api.deps.get_runs_db`). Unlike
    `insert_run`, this does not open or close its own connection.
    """
    conn.execute(
        _INSERT_RUN_SQL,
        (
            record.run_id,
            record.name,
            record.strategy,
            json.dumps(record.params, separators=(",", ":")),
            json.dumps(record.universe, separators=(",", ":")),
            record.start_ts,
            record.end_ts,
            record.created_at,
            record.finished_at,
            record.heartbeat_ts,
            record.status,
            record.error,
            record.git_sha,
            1 if record.git_dirty else 0,
            record.data_snapshot,
            record.seed,
            json.dumps(record.metrics, separators=(",", ":")),
            json.dumps(record.artifacts, separators=(",", ":")),
        ),
    )
    conn.commit()


_CLAIM_NEXT_QUEUED_SELECT_SQL = """
SELECT run_id, name, strategy, params, universe, start_ts, end_ts,
       created_at, finished_at, heartbeat_ts, status, error, git_sha,
       git_dirty, data_snapshot, seed, metrics, artifacts
FROM meta_runs
WHERE status = 'queued'
ORDER BY created_at ASC, run_id ASC
LIMIT 1
"""


def claim_next_queued(conn: sqlite3.Connection) -> RunRecord | None:
    """Atomically claim the oldest queued run for the (single) worker.

    Uses `BEGIN IMMEDIATE` to take SQLite's exclusive write lock before
    reading, so two workers racing this call cannot both claim the same
    row (§4.5 — only one worker runs at a time, but this makes the claim
    itself safe regardless). Returns `None` if no queued rows exist.
    """
    conn.execute("BEGIN IMMEDIATE")
    row = conn.execute(_CLAIM_NEXT_QUEUED_SELECT_SQL).fetchone()

    if row is None:
        conn.commit()
        return None

    run_id = row[0]
    now = _now_ms()
    conn.execute(
        "UPDATE meta_runs SET status = 'running', heartbeat_ts = ? WHERE run_id = ?",
        (now, run_id),
    )
    conn.commit()

    return RunRecord(
        run_id=run_id,
        name=row[1],
        strategy=row[2],
        params=json.loads(row[3]),
        universe=json.loads(row[4]),
        start_ts=row[5],
        end_ts=row[6],
        created_at=row[7],
        finished_at=row[8],
        heartbeat_ts=now,
        status="running",
        error=row[11],
        git_sha=row[12],
        git_dirty=bool(row[13]),
        data_snapshot=row[14],
        seed=row[15],
        metrics=json.loads(row[16]),
        artifacts=json.loads(row[17]),
    )


def update_heartbeat(conn: sqlite3.Connection, run_id: str) -> None:
    """Bump `heartbeat_ts` to now for the given run. Caller owns the connection."""
    conn.execute(
        "UPDATE meta_runs SET heartbeat_ts = ? WHERE run_id = ?",
        (_now_ms(), run_id),
    )
    conn.commit()


def update_run_status(
    conn: sqlite3.Connection,
    run_id: str,
    *,
    status: str,
    error: str | None = None,
    finished_at: int | None = None,
    metrics: dict[str, Any] | None = None,
    artifacts: dict[str, Any] | None = None,
    git_sha: str | None = None,
    git_dirty: bool | None = None,
) -> None:
    """Update a run's terminal/transitional fields with a dynamic SET clause.

    `status` and `error` are always written (error explicitly, possibly to
    `None`, to clear a prior failure message). Every other column is only
    included when its kwarg is not `None`. `metrics` and `artifacts` are
    JSON-encoded; `git_dirty` is stored as 0/1. Caller owns the connection.
    """
    set_clauses: list[str] = ["status = ?", "error = ?"]
    values: list[Any] = [status, error]

    if finished_at is not None:
        set_clauses.append("finished_at = ?")
        values.append(finished_at)
    if metrics is not None:
        set_clauses.append("metrics = ?")
        values.append(json.dumps(metrics, separators=(",", ":")))
    if artifacts is not None:
        set_clauses.append("artifacts = ?")
        values.append(json.dumps(artifacts, separators=(",", ":")))
    if git_sha is not None:
        set_clauses.append("git_sha = ?")
        values.append(git_sha)
    if git_dirty is not None:
        set_clauses.append("git_dirty = ?")
        values.append(1 if git_dirty else 0)

    values.append(run_id)
    conn.execute(
        f"UPDATE meta_runs SET {', '.join(set_clauses)} WHERE run_id = ?",  # noqa: S608 - column list is a fixed internal allowlist, not user input
        values,
    )
    conn.commit()


def fail_stale_running(conn: sqlite3.Connection, *, stale_ms: int = 60_000) -> int:
    """Fail any `running` row whose heartbeat is older than `stale_ms` (§4.5).

    Called by both the worker (before claiming new work) and the API's
    `list_runs` (on every read), so a crashed worker self-heals without
    manual intervention. Returns the number of rows updated.
    """
    now = _now_ms()
    cursor = conn.execute(
        """
        UPDATE meta_runs
        SET status = 'failed', error = 'heartbeat timeout', finished_at = ?
        WHERE status = 'running' AND heartbeat_ts < ?
        """,
        (now, now - stale_ms),
    )
    conn.commit()
    return cursor.rowcount
