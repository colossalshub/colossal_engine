"""FastAPI dependency providers for per-request database connections.

These are FastAPI generator dependencies. FastAPI calls them per request
and closes the connection when the response is sent.

No global connection objects. No singletons. §5 requires this.

SQLite WAL mode is applied by ``init_runs_schema`` at write time; this
module only sets ``busy_timeout``.

Paths are env-driven via ``QUANT_RUNS_DB`` and ``QUANT_BARS_DB``, with
defaults under ``<repo_root>/data/``.

The DuckDB connection is NOT marked ``read_only=True`` because DuckDB's
read-only mode raises if the file doesn't exist yet. The API layer only
runs SELECTs against ``curated_bars``; writes are enforced by convention
and code review, not by the DB engine.

This module does NOT call ``init_runs_schema`` or ``init_schema``. Callers
(routers) assume the schema exists. Scripts are responsible for creating
the schema.
"""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated

import duckdb
from fastapi import Depends


def _repo_root() -> Path:
    """Walk up from this file until we find pyproject.toml."""
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    msg = "cannot find repo root (pyproject.toml)"
    raise RuntimeError(msg)


def _default_data_dir() -> Path:
    return _repo_root() / "data"


def _runs_db_path() -> Path:
    default = str(_default_data_dir() / "quant.sqlite")
    return Path(os.environ.get("QUANT_RUNS_DB", default))


def _bars_db_path() -> Path:
    default = str(_default_data_dir() / "quant.duckdb")
    return Path(os.environ.get("QUANT_BARS_DB", default))


def get_artifacts_dir() -> Path:
    """Directory containing per-run parquet artifacts (`data/runs/`).

    Env-driven via ``QUANT_ARTIFACTS_DIR``, mirroring the ``_runs_db_path``/
    ``_bars_db_path`` pattern above. Public (unlike the two path helpers)
    because Phase 3.4's tearsheet router needs it and duplicating the
    `pyproject.toml` repo-root walk there would violate §5's no-premature-
    duplication rule.
    """
    default = str(_default_data_dir() / "runs")
    return Path(os.environ.get("QUANT_ARTIFACTS_DIR", default))


def get_runs_db() -> Iterator[sqlite3.Connection]:
    """Per-request SQLite connection. Caller must not close it — FastAPI does."""
    conn = sqlite3.connect(_runs_db_path())
    try:
        conn.execute("PRAGMA busy_timeout=5000")
        yield conn
    finally:
        conn.close()


def get_bars_db() -> Iterator[duckdb.DuckDBPyConnection]:
    """Per-request DuckDB connection. Read-only by convention — the API
    layer never writes to this DB. Do not hold this connection across
    requests."""
    conn = duckdb.connect(str(_bars_db_path()))
    try:
        yield conn
    finally:
        conn.close()


RunsDb = Annotated[sqlite3.Connection, Depends(get_runs_db)]
BarsDb = Annotated[duckdb.DuckDBPyConnection, Depends(get_bars_db)]
