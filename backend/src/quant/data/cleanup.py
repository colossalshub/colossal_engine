"""Purge parquet artifacts older than N days and archive their meta_runs rows."""

from __future__ import annotations

import logging
import shutil
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

_MS_PER_DAY = 86_400_000

_SELECT_ELIGIBLE_SQL = """
SELECT run_id, finished_at, artifacts
FROM meta_runs
WHERE status = 'done'
  AND finished_at IS NOT NULL
  AND finished_at < ?
"""

_UPDATE_ARCHIVED_SQL = """
UPDATE meta_runs
SET status = 'archived', artifacts = '{}'
WHERE run_id = ?
"""


@dataclass(frozen=True)
class CleanupResult:
    runs_scanned: int
    runs_archived: int
    dirs_deleted: int
    bytes_freed: int
    errors: list[str]


def _dir_size_bytes(path: Path) -> int:
    total = 0
    for child in path.rglob("*"):
        if child.is_file():
            try:
                total += child.stat().st_size
            except OSError as exc:
                msg = f"{path}: stat failed for {child}: {exc}"
                raise OSError(msg) from exc
    return total


def cleanup_old_artifacts(
    *,
    runs_db_path: Path,
    artifacts_dir: Path,
    older_than_days: int,
    dry_run: bool = False,
    now_ms: int | None = None,
) -> CleanupResult:
    """Delete parquet artifact directories older than ``older_than_days``.

    A run is eligible if its ``meta_runs`` row has ``status='done'`` and
    ``finished_at < now_ms - older_than_days * 86_400_000``. Eligible runs
    have their artifact directory removed and their row updated to
    ``status='archived'`` with ``artifacts='{}'``.

    Runs with status 'queued', 'running', 'failed', or already 'archived'
    are skipped.

    If ``dry_run`` is True, no filesystem or database changes are made; the
    result reports what WOULD have been done.
    """
    base_now = now_ms if now_ms is not None else int(time.time() * 1000)
    cutoff_ms = base_now - older_than_days * _MS_PER_DAY

    runs_scanned = 0
    runs_archived = 0
    dirs_deleted = 0
    bytes_freed = 0
    errors: list[str] = []

    conn = sqlite3.connect(runs_db_path)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA busy_timeout=5000")
        rows = conn.execute(_SELECT_ELIGIBLE_SQL, (cutoff_ms,)).fetchall()
        runs_scanned = len(rows)

        for row in rows:
            run_id = str(row["run_id"])
            run_dir = artifacts_dir / run_id
            size_bytes = 0
            delete_ok = True

            if run_dir.is_dir():
                try:
                    size_bytes = _dir_size_bytes(run_dir)
                except OSError as exc:
                    errors.append(str(exc))
                    delete_ok = False
                else:
                    if dry_run:
                        dirs_deleted += 1
                        bytes_freed += size_bytes
                    else:
                        try:
                            shutil.rmtree(run_dir)
                        except OSError as exc:
                            errors.append(
                                f"{run_id}: failed to remove {run_dir}: {exc}"
                            )
                            delete_ok = False
                        else:
                            dirs_deleted += 1
                            bytes_freed += size_bytes

            if not delete_ok and run_dir.is_dir():
                logger.info(
                    "skipped archive run_id=%s (artifact delete failed)", run_id
                )
                continue

            logger.info(
                "eligible run_id=%s finished_at=%s dry_run=%s dir_exists=%s",
                run_id,
                row["finished_at"],
                dry_run,
                run_dir.is_dir(),
            )

            if dry_run:
                runs_archived += 1
                continue

            conn.execute(_UPDATE_ARCHIVED_SQL, (run_id,))
            runs_archived += 1

        if not dry_run:
            conn.commit()
    finally:
        conn.close()

    return CleanupResult(
        runs_scanned=runs_scanned,
        runs_archived=runs_archived,
        dirs_deleted=dirs_deleted,
        bytes_freed=bytes_freed,
        errors=errors,
    )
