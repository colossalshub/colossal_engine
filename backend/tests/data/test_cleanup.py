"""Tests for artifact cleanup and meta_runs archival."""

from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path

import pytest

from quant.data.cleanup import cleanup_old_artifacts
from quant.data.runs_store import RunRecord, init_runs_schema, insert_run

_MS_PER_DAY = 86_400_000


def _now_ms() -> int:
    return 1_700_000_000_000


def _insert_done_run(
    db_path: Path,
    *,
    run_id: str,
    finished_at: int,
    status: str = "done",
) -> None:
    init_runs_schema(db_path)
    record = RunRecord(
        run_id=run_id,
        name="test",
        strategy="buy_hold",
        params={},
        universe=["BTC/USDT"],
        start_ts=finished_at - _MS_PER_DAY,
        end_ts=finished_at,
        created_at=finished_at - _MS_PER_DAY,
        finished_at=finished_at,
        status=status,
        artifacts={"equity": f"runs/{run_id}/equity.parquet"},
    )
    insert_run(db_path, record)


def _fetch_status(db_path: Path, run_id: str) -> tuple[str, str]:
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT status, artifacts FROM meta_runs WHERE run_id = ?",
            (run_id,),
        ).fetchone()
    finally:
        conn.close()
    assert row is not None
    return str(row[0]), str(row[1])


def _make_artifact_dir(artifacts_root: Path, run_id: str) -> Path:
    run_dir = artifacts_root / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "a.bin").write_bytes(b"x" * 100)
    (run_dir / "b.bin").write_bytes(b"y" * 50)
    return run_dir


def test_no_eligible_runs(tmp_path: Path) -> None:
    db = tmp_path / "quant.sqlite"
    artifacts = tmp_path / "runs"
    now = _now_ms()
    _insert_done_run(db, run_id="recent", finished_at=now - 5 * _MS_PER_DAY)

    result = cleanup_old_artifacts(
        runs_db_path=db,
        artifacts_dir=artifacts,
        older_than_days=30,
        now_ms=now,
    )

    assert result.runs_scanned == 0
    assert result.runs_archived == 0
    assert result.dirs_deleted == 0
    assert result.bytes_freed == 0
    assert result.errors == []
    status, artifacts = _fetch_status(db, "recent")
    assert status == "done"
    assert artifacts == '{"equity":"runs/recent/equity.parquet"}'


def test_one_eligible_run_deletes_and_archives(tmp_path: Path) -> None:
    db = tmp_path / "quant.sqlite"
    artifacts = tmp_path / "runs"
    now = _now_ms()
    run_id = str(uuid.uuid4())
    _insert_done_run(db, run_id=run_id, finished_at=now - 40 * _MS_PER_DAY)
    run_dir = _make_artifact_dir(artifacts, run_id)

    result = cleanup_old_artifacts(
        runs_db_path=db,
        artifacts_dir=artifacts,
        older_than_days=30,
        now_ms=now,
    )

    assert result.runs_scanned == 1
    assert result.runs_archived == 1
    assert result.dirs_deleted == 1
    assert result.bytes_freed == 150
    assert not run_dir.exists()
    assert _fetch_status(db, run_id) == ("archived", "{}")


def test_dry_run_leaves_files_and_rows(tmp_path: Path) -> None:
    db = tmp_path / "quant.sqlite"
    artifacts = tmp_path / "runs"
    now = _now_ms()
    run_id = str(uuid.uuid4())
    _insert_done_run(db, run_id=run_id, finished_at=now - 40 * _MS_PER_DAY)
    run_dir = _make_artifact_dir(artifacts, run_id)

    result = cleanup_old_artifacts(
        runs_db_path=db,
        artifacts_dir=artifacts,
        older_than_days=30,
        dry_run=True,
        now_ms=now,
    )

    assert result.runs_archived == 1
    assert result.dirs_deleted == 1
    assert result.bytes_freed == 150
    assert run_dir.is_dir()
    assert _fetch_status(db, run_id)[0] == "done"


@pytest.mark.parametrize("status", ["queued", "running", "failed", "archived"])
def test_skipped_statuses_not_touched(tmp_path: Path, status: str) -> None:
    db = tmp_path / "quant.sqlite"
    artifacts = tmp_path / "runs"
    now = _now_ms()
    run_id = str(uuid.uuid4())
    _insert_done_run(
        db,
        run_id=run_id,
        finished_at=now - 100 * _MS_PER_DAY,
        status=status,
    )
    _make_artifact_dir(artifacts, run_id)

    result = cleanup_old_artifacts(
        runs_db_path=db,
        artifacts_dir=artifacts,
        older_than_days=30,
        now_ms=now,
    )

    assert result.runs_scanned == 0
    assert result.runs_archived == 0
    assert (artifacts / run_id).is_dir()
    assert _fetch_status(db, run_id)[0] == status


def test_boundary_29_days_untouched_31_days_archived(tmp_path: Path) -> None:
    db = tmp_path / "quant.sqlite"
    artifacts = tmp_path / "runs"
    now = _now_ms()
    young_id = str(uuid.uuid4())
    old_id = str(uuid.uuid4())
    _insert_done_run(db, run_id=young_id, finished_at=now - 29 * _MS_PER_DAY)
    _insert_done_run(db, run_id=old_id, finished_at=now - 31 * _MS_PER_DAY)
    _make_artifact_dir(artifacts, young_id)
    _make_artifact_dir(artifacts, old_id)

    result = cleanup_old_artifacts(
        runs_db_path=db,
        artifacts_dir=artifacts,
        older_than_days=30,
        now_ms=now,
    )

    assert result.runs_scanned == 1
    assert result.runs_archived == 1
    assert (artifacts / young_id).is_dir()
    assert not (artifacts / old_id).exists()
    assert _fetch_status(db, young_id)[0] == "done"
    assert _fetch_status(db, old_id) == ("archived", "{}")


def test_missing_artifacts_dir_still_archives_row(tmp_path: Path) -> None:
    db = tmp_path / "quant.sqlite"
    artifacts = tmp_path / "runs"
    now = _now_ms()
    run_id = str(uuid.uuid4())
    _insert_done_run(db, run_id=run_id, finished_at=now - 40 * _MS_PER_DAY)

    result = cleanup_old_artifacts(
        runs_db_path=db,
        artifacts_dir=artifacts,
        older_than_days=30,
        now_ms=now,
    )

    assert result.runs_archived == 1
    assert result.dirs_deleted == 0
    assert result.bytes_freed == 0
    assert result.errors == []
    assert _fetch_status(db, run_id) == ("archived", "{}")


def test_custom_now_ms_controls_cutoff(tmp_path: Path) -> None:
    db = tmp_path / "quant.sqlite"
    artifacts = tmp_path / "runs"
    fixed_now = 2_000_000_000_000
    run_id = str(uuid.uuid4())
    finished_at = fixed_now - 35 * _MS_PER_DAY
    _insert_done_run(db, run_id=run_id, finished_at=finished_at)
    _make_artifact_dir(artifacts, run_id)

    result = cleanup_old_artifacts(
        runs_db_path=db,
        artifacts_dir=artifacts,
        older_than_days=30,
        now_ms=fixed_now,
    )

    assert result.runs_archived == 1
    assert _fetch_status(db, run_id)[0] == "archived"


def test_nonexistent_artifacts_dir_no_error(tmp_path: Path) -> None:
    db = tmp_path / "quant.sqlite"
    artifacts = tmp_path / "does_not_exist" / "runs"
    now = _now_ms()
    run_id = str(uuid.uuid4())
    _insert_done_run(db, run_id=run_id, finished_at=now - 40 * _MS_PER_DAY)

    result = cleanup_old_artifacts(
        runs_db_path=db,
        artifacts_dir=artifacts,
        older_than_days=30,
        now_ms=now,
    )

    assert result.errors == []
    assert result.runs_archived == 1
