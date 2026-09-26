"""Environment-driven configuration for the quant backend.

Load order:
1. Process environment (highest priority)
2. ``<repo_root>/.env`` if it exists
3. Hardcoded defaults (below)

Call ``_load_dotenv()`` once at import. All other modules read from this
module, not from ``os.environ`` directly.

The ``.env`` parser handles simple ``KEY=value`` lines only. It does NOT
handle inline comments after values, multi-line values, or shell expansion.
"""

from __future__ import annotations

import os
from pathlib import Path


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    msg = "cannot find repo root (pyproject.toml)"
    raise RuntimeError(msg)


def _load_dotenv() -> None:
    """Populate os.environ from ``<repo_root>/.env`` if it exists. Does NOT
    override existing env vars."""
    env_path = _repo_root() / ".env"
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


_load_dotenv()


def _data_dir() -> Path:
    return Path(os.environ.get("QUANT_DATA_DIR", str(_repo_root() / "data")))


def runs_db_path() -> Path:
    return Path(os.environ.get("QUANT_RUNS_DB", str(_data_dir() / "quant.sqlite")))


def bars_db_path() -> Path:
    return Path(os.environ.get("QUANT_BARS_DB", str(_data_dir() / "quant.duckdb")))


def artifacts_dir() -> Path:
    return Path(os.environ.get("QUANT_ARTIFACTS_DIR", str(_data_dir() / "runs")))


def cors_origins() -> list[str]:
    raw = os.environ.get("QUANT_CORS_ORIGINS", "*")
    return [o.strip() for o in raw.split(",") if o.strip()]


def log_level() -> str:
    return os.environ.get("QUANT_LOG_LEVEL", "INFO").upper()


def log_json() -> bool:
    return os.environ.get("QUANT_LOG_JSON") == "1"


def repo_root() -> Path:
    return _repo_root()
