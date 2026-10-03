from __future__ import annotations

import copy
import dataclasses
import logging
import re
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from quant.data.runs_store import RunRecord
from quant.data.store import ensure_canonical_bars, upsert_bars
from quant.engine.orchestrator import execute_run

_VENUE = "binance"
_SYMBOL = "BTC/USDT"
_BENCH_SYMBOL = "BENCH/USDT"
_DAY_MS = 86_400_000
_START_TS = 1_735_689_600_000


def _equity_benchmark_null_count(
    artifacts_dir: Path,
    run_id: str,
) -> tuple[int, int]:
    table = pq.read_table(artifacts_dir / run_id / "equity.parquet")
    benchmark_col = table.column("benchmark")
    return table.num_rows, benchmark_col.null_count


def _store_daily_bars_for_symbol(
    db_path: Path,
    symbol: str,
    *,
    start_ts: int,
    count: int = 10,
) -> int:
    ensure_canonical_bars(db_path)
    rows: list[dict[str, object]] = []
    for i in range(count):
        ts = start_ts + i * _DAY_MS
        rows.append(
            {
                "venue": _VENUE,
                "symbol": symbol,
                "asset_class": "crypto",
                "timeframe": "1d",
                "ts": ts,
                "open": 100.0,
                "high": 110.0,
                "low": 90.0,
                "close": 100.0 + float(i),
                "volume": 1.0,
            }
        )
    upsert_bars(db_path, rows)
    return start_ts + (count - 1) * _DAY_MS


def _store_daily_bars(db_path: Path, *, start_ts: int, count: int = 10) -> int:
    ensure_canonical_bars(db_path)
    rows: list[dict[str, object]] = []
    for i in range(count):
        ts = start_ts + i * _DAY_MS
        rows.append(
            {
                "venue": _VENUE,
                "symbol": _SYMBOL,
                "asset_class": "crypto",
                "timeframe": "1d",
                "ts": ts,
                "open": 100.0,
                "high": 110.0,
                "low": 90.0,
                "close": 100.0,
                "volume": 1_000_000.0,
            }
        )
    upsert_bars(db_path, rows)
    return start_ts + (count - 1) * _DAY_MS


def _make_record(
    *,
    universe: list[str] | None = None,
    params: dict[str, object] | None = None,
    start_ts: int = _START_TS,
    end_ts: int | None = None,
) -> RunRecord:
    return RunRecord(
        run_id="test-run-id",
        name="test run",
        strategy="buy_hold",
        params={"timeframe": "1d", "trade_size": "1"} if params is None else params,
        universe=["BTC/USDT"] if universe is None else universe,
        start_ts=start_ts,
        end_ts=end_ts if end_ts is not None else start_ts + 9 * _DAY_MS,
        created_at=start_ts,
    )


def test_execute_run_happy_path(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(start_ts=_START_TS, end_ts=end_ts)

    updated = execute_run(
        record,
        bars_db_path=db_path,
        artifacts_dir=artifacts_dir,
    )

    assert updated.metrics
    for key in ("sharpe", "cagr", "max_drawdown"):
        assert key in updated.metrics

    assert set(updated.artifacts) == {"equity", "drawdown", "price", "trades", "fills"}
    for rel_path in updated.artifacts.values():
        assert (artifacts_dir / updated.run_id / Path(rel_path).name).is_file()


def _snapshot_for(db_path: Path, artifacts_dir: Path, end_ts: int) -> str | None:
    record = _make_record(start_ts=_START_TS, end_ts=end_ts)
    return execute_run(
        record, bars_db_path=db_path, artifacts_dir=artifacts_dir
    ).data_snapshot


def test_execute_run_populates_data_snapshot(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)

    snapshot = _snapshot_for(db_path, tmp_path / "artifacts", end_ts)

    assert snapshot is not None
    assert re.fullmatch(r"[0-9a-f]{64}", snapshot)


def test_execute_run_same_bars_same_fingerprint(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)

    first = _snapshot_for(db_path, tmp_path / "a1", end_ts)
    second = _snapshot_for(db_path, tmp_path / "a2", end_ts)

    assert first is not None
    assert first == second


def test_execute_run_changed_historical_bar_changes_fingerprint(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    before = _snapshot_for(db_path, tmp_path / "a1", end_ts)

    upsert_bars(
        db_path,
        [
            {
                "venue": _VENUE,
                "symbol": _SYMBOL,
                "asset_class": "crypto",
                "timeframe": "1d",
                "ts": _START_TS + 3 * _DAY_MS,
                "open": 100.0,
                "high": 110.0,
                "low": 90.0,
                "close": 100.0 + 1e-6,
                "volume": 1_000_000.0,
            }
        ],
    )
    after = _snapshot_for(db_path, tmp_path / "a2", end_ts)

    assert before is not None
    assert after is not None
    assert before != after


def test_execute_run_does_not_mutate_input_record(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(start_ts=_START_TS, end_ts=end_ts)

    execute_run(record, bars_db_path=db_path, artifacts_dir=artifacts_dir)

    assert record.metrics == {}
    assert record.artifacts == {}


def test_execute_run_missing_timeframe_raises(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    ensure_canonical_bars(db_path)
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(params={})

    with pytest.raises(ValueError, match="timeframe"):
        execute_run(record, bars_db_path=db_path, artifacts_dir=artifacts_dir)


def test_execute_run_invalid_timeframe_raises(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    ensure_canonical_bars(db_path)
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(params={"timeframe": "banana"})

    with pytest.raises(ValueError):
        execute_run(record, bars_db_path=db_path, artifacts_dir=artifacts_dir)


def test_execute_run_empty_universe_raises(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    ensure_canonical_bars(db_path)
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(universe=[])

    with pytest.raises(ValueError, match="universe"):
        execute_run(record, bars_db_path=db_path, artifacts_dir=artifacts_dir)


def test_execute_run_no_bars_in_range_raises(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    artifacts_dir = tmp_path / "artifacts"

    out_of_range_start = _START_TS + 100 * _DAY_MS
    record = _make_record(
        start_ts=out_of_range_start,
        end_ts=out_of_range_start + 9 * _DAY_MS,
    )

    with pytest.raises(ValueError, match="no bars"):
        execute_run(record, bars_db_path=db_path, artifacts_dir=artifacts_dir)


def test_execute_run_venue_from_params(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(
        start_ts=_START_TS,
        end_ts=end_ts,
        params={"timeframe": "1d", "trade_size": "1", "venue": "kraken"},
    )

    with pytest.raises(ValueError, match="no bars in range for kraken"):
        execute_run(record, bars_db_path=db_path, artifacts_dir=artifacts_dir)


def test_execute_run_params_fees_flow_through(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(
        start_ts=_START_TS,
        end_ts=end_ts,
        params={
            "timeframe": "1d",
            "trade_size": "1",
            "deploy_pct": "0",
            "maker_fee": "0.01",
            "taker_fee": "0.01",
        },
    )

    updated = execute_run(
        record,
        bars_db_path=db_path,
        artifacts_dir=artifacts_dir,
    )

    assert updated.metrics
    for key in ("sharpe", "cagr", "max_drawdown"):
        assert key in updated.metrics


def test_execute_run_non_string_maker_fee_raises(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(
        start_ts=_START_TS,
        end_ts=end_ts,
        params={
            "timeframe": "1d",
            "trade_size": "1",
            "maker_fee": 0.001,
        },
    )

    with pytest.raises(ValueError, match="maker_fee"):
        execute_run(record, bars_db_path=db_path, artifacts_dir=artifacts_dir)


def test_execute_run_missing_venue_defaults_to_binance(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(
        start_ts=_START_TS,
        end_ts=end_ts,
        params={"timeframe": "1d", "trade_size": "1"},
    )

    updated = execute_run(
        record,
        bars_db_path=db_path,
        artifacts_dir=artifacts_dir,
    )

    assert updated.metrics
    for key in ("sharpe", "cagr", "max_drawdown"):
        assert key in updated.metrics


def test_execute_run_benchmark_bars_flow_through(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    _store_daily_bars_for_symbol(
        db_path, _BENCH_SYMBOL, start_ts=_START_TS, count=10
    )
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(
        start_ts=_START_TS,
        end_ts=end_ts,
        params={
            "timeframe": "1d",
            "trade_size": "1",
            "benchmark_symbol": _BENCH_SYMBOL,
        },
    )

    updated = execute_run(
        record,
        bars_db_path=db_path,
        artifacts_dir=artifacts_dir,
    )

    assert updated.metrics
    rows, nulls = _equity_benchmark_null_count(artifacts_dir, updated.run_id)
    assert rows > 0
    assert nulls == 0


def test_execute_run_benchmark_short_of_close_is_skipped(tmp_path: Path) -> None:
    """A benchmark that ends more than one bar before the equity close is dropped."""
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    _store_daily_bars_for_symbol(
        db_path, _BENCH_SYMBOL, start_ts=_START_TS, count=8
    )
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(
        start_ts=_START_TS,
        end_ts=end_ts,
        params={
            "timeframe": "1d",
            "trade_size": "1",
            "benchmark_symbol": _BENCH_SYMBOL,
        },
    )

    updated = execute_run(
        record,
        bars_db_path=db_path,
        artifacts_dir=artifacts_dir,
    )

    assert updated.metrics
    rows, nulls = _equity_benchmark_null_count(artifacts_dir, updated.run_id)
    assert rows > 0
    assert nulls == rows


def test_execute_run_missing_benchmark_bars_graceful(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(
        start_ts=_START_TS,
        end_ts=end_ts,
        params={
            "timeframe": "1d",
            "trade_size": "1",
            "benchmark_symbol": "GHOST/USDT",
        },
    )

    updated = execute_run(
        record,
        bars_db_path=db_path,
        artifacts_dir=artifacts_dir,
    )

    assert updated.metrics
    rows, nulls = _equity_benchmark_null_count(artifacts_dir, updated.run_id)
    assert rows > 0
    assert nulls == rows


def test_execute_run_buyhold_open_position_closed_trade_metrics_none(
    tmp_path: Path,
) -> None:
    """BuyHold with full deploy leaves one open position; closed-trade KPIs are null."""
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(
        start_ts=_START_TS,
        end_ts=end_ts,
        params={
            "timeframe": "1d",
            "trade_size": "1",
            "deploy_pct": "1.0",
        },
    )

    updated = execute_run(
        record,
        bars_db_path=db_path,
        artifacts_dir=artifacts_dir,
    )

    assert updated.metrics is not None
    assert updated.metrics["win_rate"] is None
    assert updated.metrics["profit_factor"] is None
    assert updated.metrics["avg_duration_days"] is None
    assert updated.metrics["total_trades"] == 1.0


def test_execute_run_params_deploy_pct_flows_through(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(
        start_ts=_START_TS,
        end_ts=end_ts,
        params={
            "timeframe": "1d",
            "trade_size": "1",
            "deploy_pct": "1.0",
        },
    )

    updated = execute_run(
        record,
        bars_db_path=db_path,
        artifacts_dir=artifacts_dir,
    )

    assert updated.metrics
    for key in ("sharpe", "cagr", "max_drawdown"):
        assert key in updated.metrics


def test_execute_run_non_string_deploy_pct_raises(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(
        start_ts=_START_TS,
        end_ts=end_ts,
        params={
            "timeframe": "1d",
            "trade_size": "1",
            "deploy_pct": 1.0,
        },
    )

    with pytest.raises(ValueError, match="deploy_pct"):
        execute_run(record, bars_db_path=db_path, artifacts_dir=artifacts_dir)


def test_execute_run_empty_benchmark_symbol_disables(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    artifacts_dir = tmp_path / "artifacts"

    record = _make_record(
        start_ts=_START_TS,
        end_ts=end_ts,
        params={
            "timeframe": "1d",
            "trade_size": "1",
            "benchmark_symbol": "",
        },
    )

    updated = execute_run(
        record,
        bars_db_path=db_path,
        artifacts_dir=artifacts_dir,
    )

    rows, nulls = _equity_benchmark_null_count(artifacts_dir, updated.run_id)
    assert rows > 0
    assert nulls == rows


def test_execute_run_buy_hold_seed_is_none(tmp_path: Path) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    record = _make_record(start_ts=_START_TS, end_ts=end_ts)
    assert record.seed == 0

    updated = execute_run(
        record, bars_db_path=db_path, artifacts_dir=tmp_path / "artifacts"
    )

    assert updated.seed is None


@pytest.mark.parametrize(
    ("metadata", "message"),
    [
        ({"research_stage": "validation"},
         "validation research_stage requires in_sample range"),
        ({"research_stage": "oos", "in_sample_start_ts": 0,
          "in_sample_end_ts": 10}, "oos research_stage requires oos range"),
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
        ({"research_stage": "exploration", "in_sample_start_ts": True,
          "in_sample_end_ts": 10},
         "in_sample_start_ts must be an integer UTC epoch-millisecond timestamp "
         "(bool is not allowed)"),
        ({"research_stage": "exploration", "in_sample_start_ts": 0,
          "in_sample_end_ts": "10"},
         "in_sample_end_ts must be an integer UTC epoch-millisecond timestamp "
         "(bool is not allowed)"),
        ({"research_stage": "IS"},
         "research_stage must be exploration, validation, oos, or None"),
    ],
)
def test_execute_run_rejects_raw_declaration_before_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    metadata: dict[str, object],
    message: str,
) -> None:
    # Competing venue/timeframe/universe errors must lose to declaration errors.
    record = dataclasses.replace(
        _make_record(params={"venue": 42, "timeframe": "banana"}, universe=[]),
        **metadata,
    )
    before = copy.deepcopy(record)
    artifacts_dir = tmp_path / "artifacts"

    def unexpected(*args: object, **kwargs: object) -> None:
        pytest.fail("execution action reached before declaration rejection")

    for name in (
        "read_bars_json", "fingerprint_bars", "run_backtest", "extract_equity",
        "extract_metrics", "write_artifacts",
    ):
        monkeypatch.setattr(f"quant.engine.orchestrator.{name}", unexpected)

    with caplog.at_level(logging.ERROR), pytest.raises(ValueError) as exc:
        execute_run(
            record, bars_db_path=tmp_path / "bars.duckdb",
            artifacts_dir=artifacts_dir,
        )

    assert str(exc.value) == message
    assert [(entry.name, entry.levelno, entry.getMessage())
            for entry in caplog.records] == [
        ("quant.engine.temporal", logging.ERROR, message),
    ]
    assert record == before
    assert not artifacts_dir.exists()
    assert not (tmp_path / "bars.duckdb").exists()


@pytest.mark.parametrize("stage", [None, "exploration"])
@pytest.mark.parametrize(
    ("params", "universe", "message"),
    [
        ({"venue": 42, "timeframe": "banana"}, [],
         "record.params['venue'] must be a string, got <class 'int'>"),
        ({"timeframe": "banana"}, [],
         "record.params['timeframe'] must be one of "
         "['15m', '1d', '1h', '1m', '1mo', '1w', '30m', '4h', '5m'], "
         "got 'banana'"),
        ({"timeframe": "1d"}, [],
         "record.universe must contain at least one symbol"),
    ],
)
def test_execute_run_preserves_existing_failure_priority(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    stage: str | None,
    params: dict[str, object],
    universe: list[str],
    message: str,
) -> None:
    record = dataclasses.replace(
        _make_record(params=params, universe=universe), research_stage=stage,
    )
    with caplog.at_level(logging.ERROR), pytest.raises(ValueError) as exc:
        execute_run(
            record, bars_db_path=tmp_path / "bars.duckdb",
            artifacts_dir=tmp_path / "artifacts",
        )
    assert str(exc.value) == message
    assert caplog.records == []
    assert not (tmp_path / "artifacts").exists()


@pytest.mark.parametrize(
    "metadata",
    [
        {"research_stage": "exploration"},
        {"research_stage": "validation", "in_sample_start_ts": 0,
         "in_sample_end_ts": 10, "validation_start_ts": 10,
         "validation_end_ts": 20},
        {"research_stage": "oos", "in_sample_start_ts": 0,
         "in_sample_end_ts": 10, "oos_start_ts": 10, "oos_end_ts": 20},
        {"research_stage": "oos", "in_sample_start_ts": 0,
         "in_sample_end_ts": 10, "validation_start_ts": 10,
         "validation_end_ts": 20, "oos_start_ts": 20, "oos_end_ts": 30},
        {"research_stage": None, "in_sample_start_ts": 0,
         "validation_start_ts": 20, "validation_end_ts": 10,
         "oos_start_ts": 5, "oos_end_ts": 25},
    ],
)
def test_execute_run_preserves_metadata_through_actual_engine(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    metadata: dict[str, object],
) -> None:
    db_path = tmp_path / "bars.duckdb"
    end_ts = _store_daily_bars(db_path, start_ts=_START_TS, count=10)
    artifacts_dir = tmp_path / "artifacts"
    # Research bounds deliberately differ from execution: declaration checks
    # alone do not certify containment or any other runtime eligibility.
    record = dataclasses.replace(
        _make_record(end_ts=end_ts),
        experiment_id="experiment", hypothesis_id="hypothesis",
        strategy_version="v1", trial_index=0, trial_count=2, **metadata,
    )
    before = copy.deepcopy(record)
    with caplog.at_level(logging.ERROR):
        updated = execute_run(
            record, bars_db_path=db_path, artifacts_dir=artifacts_dir,
        )

    for field in (
        "research_stage", "in_sample_start_ts", "in_sample_end_ts",
        "validation_start_ts", "validation_end_ts", "oos_start_ts",
        "oos_end_ts", "experiment_id", "hypothesis_id", "strategy_version",
        "trial_index", "trial_count", "params", "start_ts", "end_ts",
    ):
        assert getattr(updated, field) == getattr(before, field)
    assert updated.start_ts == _START_TS
    assert updated.end_ts == end_ts
    assert updated.params == {"timeframe": "1d", "trade_size": "1"}
    assert updated.metrics
    assert set(updated.artifacts) == {"equity", "drawdown", "price", "trades", "fills"}
    for rel_path in updated.artifacts.values():
        assert (artifacts_dir / updated.run_id / Path(rel_path).name).is_file()
    price = pq.read_table(artifacts_dir / updated.run_id / "price.parquet")
    assert price.column("ts").to_pylist() == [
        _START_TS + i * _DAY_MS for i in range(10)
    ]
    equity = pq.read_table(artifacts_dir / updated.run_id / "equity.parquet")
    assert equity.column("ts").to_pylist() == [
        _START_TS + i * _DAY_MS for i in range(11)
    ]
    assert record == before
    assert caplog.records == []
