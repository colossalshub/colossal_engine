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
