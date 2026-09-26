"""Tests for ``quant.config`` env-driven settings."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from quant import config

_QUANT_ENV_KEYS = (
    "QUANT_DATA_DIR",
    "QUANT_RUNS_DB",
    "QUANT_BARS_DB",
    "QUANT_ARTIFACTS_DIR",
    "QUANT_CORS_ORIGINS",
    "QUANT_LOG_LEVEL",
    "QUANT_LOG_JSON",
)


@pytest.fixture(autouse=True)
def _clear_quant_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _QUANT_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_defaults_runs_db_under_data_dir() -> None:
    path = config.runs_db_path()
    assert path.name == "quant.sqlite"
    assert path.parent.name == "data"


def test_env_override_runs_db(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    custom = tmp_path / "custom.sqlite"
    monkeypatch.setenv("QUANT_RUNS_DB", str(custom))
    assert config.runs_db_path() == custom


def test_quant_data_dir_cascades(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "alt-data"
    monkeypatch.setenv("QUANT_DATA_DIR", str(data_dir))
    assert config.runs_db_path() == data_dir / "quant.sqlite"
    assert config.bars_db_path() == data_dir / "quant.duckdb"
    assert config.artifacts_dir() == data_dir / "runs"


def test_full_path_override_wins_over_data_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    runs_override = tmp_path / "runs.sqlite"
    monkeypatch.setenv("QUANT_DATA_DIR", str(data_dir))
    monkeypatch.setenv("QUANT_RUNS_DB", str(runs_override))
    assert config.runs_db_path() == runs_override


def test_cors_origins_parsing(monkeypatch: pytest.MonkeyPatch) -> None:
    assert config.cors_origins() == ["*"]
    monkeypatch.setenv("QUANT_CORS_ORIGINS", "a,b")
    assert config.cors_origins() == ["a", "b"]


def test_dotenv_loading(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    env_file = config.repo_root() / ".env"
    had_file = env_file.is_file()
    previous = env_file.read_text(encoding="utf-8") if had_file else None
    dotenv_path = tmp_path / "from-dotenv.sqlite"
    monkeypatch.delenv("QUANT_RUNS_DB", raising=False)
    try:
        env_file.write_text(f"QUANT_RUNS_DB={dotenv_path}\n", encoding="utf-8")
        importlib.reload(config)
        assert config.runs_db_path() == dotenv_path
    finally:
        if had_file and previous is not None:
            env_file.write_text(previous, encoding="utf-8")
        elif env_file.is_file():
            env_file.unlink()
        importlib.reload(config)


def test_env_var_beats_dotenv(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    env_file = config.repo_root() / ".env"
    had_file = env_file.is_file()
    previous = env_file.read_text(encoding="utf-8") if had_file else None
    from_dotenv = tmp_path / "dotenv.sqlite"
    from_env = tmp_path / "process.sqlite"
    try:
        env_file.write_text(f"QUANT_RUNS_DB={from_dotenv}\n", encoding="utf-8")
        monkeypatch.setenv("QUANT_RUNS_DB", str(from_env))
        importlib.reload(config)
        assert config.runs_db_path() == from_env
    finally:
        if had_file and previous is not None:
            env_file.write_text(previous, encoding="utf-8")
        elif env_file.is_file():
            env_file.unlink()
        monkeypatch.delenv("QUANT_RUNS_DB", raising=False)
        importlib.reload(config)
