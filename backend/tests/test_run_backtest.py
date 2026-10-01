"""Backtest CLI research metadata parsing and persistence."""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path
from types import ModuleType

import pytest

from quant.data.runs_store import RunRecord

_METADATA: dict[str, str | int] = {
    "experiment_id": "experiment-17",
    "research_stage": "oos",
    "hypothesis_id": "hypothesis-1",
    "strategy_version": "version-2",
    "in_sample_start_ts": 1704067200000,
    "in_sample_end_ts": 1704153600000,
    "validation_start_ts": 1704240000000,
    "validation_end_ts": 1704326400000,
    "oos_start_ts": 1704412800000,
    "oos_end_ts": 1704499200000,
    "trial_index": 2,
    "trial_count": 5,
}
_REQUIRED = [
    "--venue",
    "binance",
    "--symbol",
    "BTC/USDT",
    "--timeframe",
    "1d",
    "--start",
    "2024-01-06",
    "--end",
    "2024-01-07",
]


@pytest.fixture
def cli() -> ModuleType:
    path = Path(__file__).resolve().parents[2] / "scripts" / "run_backtest.py"
    spec = importlib.util.spec_from_file_location("run_backtest", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("with_metadata", [False, True])
def test_main_persists_research_metadata(
    cli: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    with_metadata: bool,
) -> None:
    runs_db = tmp_path / "runs.sqlite"
    argv = [
        "run_backtest",
        *_REQUIRED,
        "--runs-db",
        str(runs_db),
        "--db",
        str(tmp_path / "bars.duckdb"),
        "--artifacts-dir",
        str(tmp_path / "artifacts"),
    ]
    if with_metadata:
        for field, value in _METADATA.items():
            argv.extend([f"--{field.replace('_', '-')}", str(value)])
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(cli, "configure_logging", lambda: None)
    monkeypatch.setattr(cli, "capture_git_state", lambda _: ("test-sha", False))

    def execute(record: RunRecord, **kwargs: object) -> RunRecord:
        for field, value in _METADATA.items():
            assert getattr(record, field) == (value if with_metadata else None)
            assert field not in record.params
        return record

    monkeypatch.setattr(cli, "execute_run", execute)
    cli.main()
    with sqlite3.connect(runs_db) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM meta_runs").fetchone()
    assert row is not None
    for field, value in _METADATA.items():
        assert row[field] == (value if with_metadata else None)


@pytest.mark.parametrize("stage", ["exploration", "validation", "oos"])
def test_parser_accepts_research_stages(cli: ModuleType, stage: str) -> None:
    args = cli.build_arg_parser().parse_args([*_REQUIRED, "--research-stage", stage])
    assert args.research_stage == stage


@pytest.mark.parametrize(
    ("flag", "value"),
    [
        ("--research-stage", "holdout"),
        ("--trial-count", "many"),
        ("--oos-start-ts", "2024-01-06"),
    ],
)
def test_parser_rejects_invalid_metadata(
    cli: ModuleType,
    flag: str,
    value: str,
) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.build_arg_parser().parse_args([*_REQUIRED, flag, value])
    assert exc.value.code == 2
