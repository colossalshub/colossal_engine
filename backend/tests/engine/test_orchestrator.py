from __future__ import annotations

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
