from __future__ import annotations

from pathlib import Path

import pytest

from quant.data.runs_store import RunRecord
from quant.data.store import ensure_canonical_bars, upsert_bars
from quant.engine.orchestrator import execute_run

_VENUE = "binance"
_SYMBOL = "BTC/USDT"
_DAY_MS = 86_400_000
_START_TS = 1_735_689_600_000


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
                "volume": 1.0,
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
