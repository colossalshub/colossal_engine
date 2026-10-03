"""Backtest CLI research metadata parsing and persistence."""

from __future__ import annotations

import importlib.util
import json
import logging
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


def _main_argv(tmp_path: Path, metadata: dict[str, str | int]) -> list[str]:
    argv = [
        "run_backtest", *_REQUIRED,
        "--runs-db", str(tmp_path / "runs.sqlite"),
        "--db", str(tmp_path / "bars.duckdb"),
        "--artifacts-dir", str(tmp_path / "artifacts"),
    ]
    for field, value in metadata.items():
        argv.extend([f"--{field.replace('_', '-')}", str(value)])
    return argv


def _forbid_run_side_effects(cli: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        pytest.fail("rejected CLI input reached run side effects")

    monkeypatch.setattr(cli, "configure_logging", lambda: None)
    monkeypatch.setattr(cli.uuid, "uuid4", forbidden)
    for name in ("capture_git_state", "init_runs_schema", "execute_run", "insert_run"):
        monkeypatch.setattr(cli, name, forbidden)


@pytest.mark.parametrize(
    ("metadata", "message"),
    [
        ({"research_stage": "validation"},
         "validation research_stage requires in_sample range"),
        ({"research_stage": "oos", "in_sample_start_ts": 0, "in_sample_end_ts": 10},
         "oos research_stage requires oos range"),
        ({"research_stage": "exploration", "oos_start_ts": 20},
         "oos_start_ts and oos_end_ts must be supplied together"),
        ({"research_stage": "exploration", "in_sample_start_ts": 10,
          "in_sample_end_ts": 10},
         "in_sample_start_ts must be less than in_sample_end_ts"),
        ({"research_stage": "exploration", "validation_start_ts": 20,
          "validation_end_ts": 10},
         "validation_start_ts must be less than validation_end_ts"),
        ({"research_stage": "oos", "in_sample_start_ts": 0,
          "in_sample_end_ts": 20, "oos_start_ts": 10, "oos_end_ts": 30},
         "in_sample range must end at or before oos range starts"),
        ({"research_stage": "validation", "validation_start_ts": 20,
          "oos_start_ts": 30, "oos_end_ts": 10},
         "validation_start_ts and validation_end_ts must be supplied together"),
    ],
)
def test_main_rejects_declarations_before_side_effects(
    cli: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
    metadata: dict[str, str | int],
    message: str,
) -> None:
    monkeypatch.setattr(sys, "argv", _main_argv(tmp_path, metadata))
    _forbid_run_side_effects(cli, monkeypatch)
    with caplog.at_level(logging.ERROR), pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 2
    output = capsys.readouterr()
    assert output.err == f"{message}\n"
    assert output.out == ""
    assert [(r.name, r.levelno, r.getMessage()) for r in caplog.records] == [
        ("quant.engine.temporal", logging.ERROR, message),
    ]
    assert not (tmp_path / "runs.sqlite").exists()
    assert not (tmp_path / "artifacts").exists()


@pytest.mark.parametrize(
    "metadata",
    [
        {"research_stage": "exploration"},
        {"research_stage": "validation", "in_sample_start_ts": -10,
         "in_sample_end_ts": 0, "validation_start_ts": 0, "validation_end_ts": 10},
        {"research_stage": "oos", "in_sample_start_ts": -10,
         "in_sample_end_ts": 0, "oos_start_ts": 0, "oos_end_ts": 10**18},
        {"research_stage": "oos", "in_sample_start_ts": -10,
         "in_sample_end_ts": 0, "validation_start_ts": 0, "validation_end_ts": 10,
         "oos_start_ts": 10, "oos_end_ts": 20},
        {"in_sample_start_ts": -10},
        {"in_sample_start_ts": 10, "in_sample_end_ts": 0},
        {"in_sample_start_ts": -10, "in_sample_end_ts": 20,
         "validation_start_ts": 0, "validation_end_ts": 10,
         "oos_start_ts": 5, "oos_end_ts": 10**18},
    ],
)
def test_main_preserves_admitted_and_ordinary_declarations(
    cli: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
    metadata: dict[str, str | int],
) -> None:
    metadata = {
        "experiment_id": "admission", "hypothesis_id": "hypothesis",
        "strategy_version": "v1", "trial_index": 2, "trial_count": 3, **metadata,
    }
    monkeypatch.setattr(sys, "argv", _main_argv(tmp_path, metadata))
    monkeypatch.setattr(cli, "configure_logging", lambda: None)
    monkeypatch.setattr(cli, "capture_git_state", lambda _: ("test-sha", False))
    expected_params = {
        "trade_size": "1", "deploy_pct": "1.0", "starting_balance": 100_000.0,
        "timeframe": "1d", "venue": "binance", "maker_fee": "0.001",
        "taker_fee": "0.001", "benchmark_symbol": "",
    }
    executed: list[RunRecord] = []

    def execute(record: RunRecord, **kwargs: object) -> RunRecord:
        executed.append(record)
        for field in _METADATA:
            assert getattr(record, field) == metadata.get(field)
        assert record.params == expected_params
        assert (record.start_ts, record.end_ts) == (1704499200000, 1704585600000)
        assert kwargs == {
            "bars_db_path": tmp_path / "bars.duckdb",
            "artifacts_dir": tmp_path / "artifacts",
            "starting_balance": 100_000.0, "trade_size": "1",
        }
        return record

    monkeypatch.setattr(cli, "execute_run", execute)
    cli.main()
    assert len(executed) == 1
    with sqlite3.connect(tmp_path / "runs.sqlite") as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM meta_runs").fetchall()
    assert len(rows) == 1
    for field in _METADATA:
        assert rows[0][field] == metadata.get(field)
    assert json.loads(rows[0]["params"]) == expected_params
    assert (rows[0]["start_ts"], rows[0]["end_ts"]) == (1704499200000, 1704585600000)
    assert rows[0]["status"] == "done"
    assert not [r for r in caplog.records if r.name == "quant.engine.temporal"]
    output = capsys.readouterr()
    assert output.err == ""
    assert output.out == (
        f"run_id={executed[0].run_id}\n"
        f"artifacts_dir={tmp_path / 'artifacts' / executed[0].run_id}\n"
        "sharpe=null  cagr=null  max_drawdown=null\n"
    )


@pytest.mark.parametrize(
    ("overrides", "error_fragment"),
    [
        (["--timeframe", "bad", "--start", "not-a-date"], "Invalid timeframe 'bad'"),
        (["--start", "not-a-date"], "not-a-date"),
        (["--end", "not-a-date"], "not-a-date"),
        (["--oos-start-ts", "1.5"], "invalid int value: '1.5'"),
    ],
)
def test_main_prior_errors_precede_research_admission(
    cli: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
    overrides: list[str],
    error_fragment: str,
) -> None:
    argv = _main_argv(tmp_path, {"research_stage": "oos"})
    monkeypatch.setattr(sys, "argv", [*argv, *overrides])
    _forbid_run_side_effects(cli, monkeypatch)
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 2
    output = capsys.readouterr()
    assert error_fragment in output.err
    assert output.out == ""
    assert not [r for r in caplog.records if r.name == "quant.engine.temporal"]
    assert not (tmp_path / "runs.sqlite").exists()
    assert not (tmp_path / "artifacts").exists()


def test_help_describes_declaration_only_admission(cli: ModuleType) -> None:
    help_text = " ".join(cli.build_arg_parser().format_help().split())
    assert "declaration checks only; runtime eligibility unverified" in help_text
    assert "ISO-8601 start (inclusive), UTC" in help_text
    assert "ISO-8601 end (inclusive), UTC" in help_text
