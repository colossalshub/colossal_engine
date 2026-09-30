"""Background worker: poll meta_runs for queued jobs, execute them, update status.

Single-worker design (§4.5). Exit with Ctrl+C.
"""

from __future__ import annotations

import logging
import sqlite3
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

from quant import config
from quant.data.runs_store import (
    RunRecord,
    claim_next_queued,
    fail_stale_running,
    init_runs_schema,
    update_heartbeat,
    update_run_status,
)
from quant.engine.orchestrator import execute_run
from quant.logging_setup import configure_logging

logger = logging.getLogger(__name__)

_POLL_INTERVAL_S = 1.0
_HEARTBEAT_INTERVAL_S = 5.0


def _now_ms() -> int:
    return int(datetime.now(UTC).timestamp() * 1000)


def _heartbeat_loop(db_path: Path, run_id: str, stop_event: threading.Event) -> None:
    """Update heartbeat_ts every 5s until stop_event is set.

    Runs on its own thread with its own connection — sqlite3 connections
    are not safe to share across threads by default.
    """
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA busy_timeout=5000")
        while not stop_event.wait(_HEARTBEAT_INTERVAL_S):
            update_heartbeat(conn, run_id)
    finally:
        conn.close()


def _execute_claimed_run(
    conn: sqlite3.Connection,
    db_path: Path,
    record: RunRecord,
    bars_db_path: Path,
    artifacts_dir: Path,
) -> None:
    logger.info("claimed run_id=%s name=%s", record.run_id, record.name)

    stop_event = threading.Event()
    heartbeat_thread = threading.Thread(
        target=_heartbeat_loop,
        args=(db_path, record.run_id, stop_event),
        daemon=True,
    )
    heartbeat_thread.start()

    started = time.monotonic()
    try:
        starting_balance = record.params.get("starting_balance", 100_000.0)
        trade_size = record.params.get("trade_size", "1")
        updated = execute_run(
            record,
            bars_db_path=bars_db_path,
            artifacts_dir=artifacts_dir,
            starting_balance=starting_balance,
            trade_size=trade_size,
        )
    except Exception as exc:  # noqa: BLE001 - any failure must be persisted, then polling continues
        logger.exception("run_id=%s raised during execution", record.run_id)
        update_run_status(
            conn,
            record.run_id,
            status="failed",
            error=str(exc)[:2000],
            finished_at=_now_ms(),
        )
        logger.info("run_id=%s failed: %s", record.run_id, exc)
    else:
        update_run_status(
            conn,
            record.run_id,
            status="done",
            finished_at=_now_ms(),
            metrics=updated.metrics,
            artifacts=updated.artifacts,
            data_snapshot=updated.data_snapshot,
        )
        elapsed = time.monotonic() - started
        logger.info("run_id=%s done in %.1fs", record.run_id, elapsed)
    finally:
        stop_event.set()
        heartbeat_thread.join()


def main() -> None:
    configure_logging()

    db_path = config.runs_db_path()
    bars_db_path = config.bars_db_path()
    artifacts_dir = config.artifacts_dir()

    init_runs_schema(db_path)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA busy_timeout=5000")
        logger.info("worker started, polling every 1s")
        while True:
            stale_count = fail_stale_running(conn)
            if stale_count:
                logger.info("marked %d stale runs as failed", stale_count)

            record = claim_next_queued(conn)
            if record is None:
                time.sleep(_POLL_INTERVAL_S)
                continue

            _execute_claimed_run(conn, db_path, record, bars_db_path, artifacts_dir)
    except KeyboardInterrupt:
        logger.info("shutting down")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
