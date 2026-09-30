from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq
import pytest

from quant.data.read import read_bars_json
from quant.data.runs_store import RunRecord
from quant.data.store import ensure_canonical_bars, upsert_bars
from quant.engine.orchestrator import execute_run

_VENUE = "binance"
_SYMBOL = "BTC/USDT"
_BENCH_SYMBOL = "BENCH/USDT"
_DAY_MS = 86_400_000
_START_TS = 1_735_689_600_000
_BAR_COUNT = 5


def _store_bars(
    db_path: Path,
    symbol: str,
    *,
    flat_close: bool,
) -> None:
    ensure_canonical_bars(db_path)
    rows: list[dict[str, object]] = []
    for i in range(_BAR_COUNT):
        if flat_close:
            close = 100.0
        else:
            close = 100.0 + float(i)
        rows.append(
            {
                "venue": _VENUE,
                "symbol": symbol,
                "asset_class": "crypto",
                "timeframe": "1d",
                "ts": _START_TS + i * _DAY_MS,
                "open": close,
                "high": close,
                "low": close,
                "close": close,
                "volume": 1.0,
            }
        )
    upsert_bars(db_path, rows)


def _make_record(*, start_ts: int, end_ts: int) -> RunRecord:
    return RunRecord(
        run_id="test-run-id",
        name="test run",
        strategy="buy_hold",
        params={
            "timeframe": "1d",
            "trade_size": "1",
            "deploy_pct": "0",
            "benchmark_symbol": _BENCH_SYMBOL,
        },
        universe=[_SYMBOL],
        start_ts=start_ts,
        end_ts=end_ts,
        created_at=start_ts,
    )


def test_benchmark_last_point_is_last_close_on_the_equity_clock(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "bars.duckdb"
    _store_bars(db_path, _SYMBOL, flat_close=True)
    _store_bars(db_path, _BENCH_SYMBOL, flat_close=False)

    last_stored_open = _START_TS + (_BAR_COUNT - 1) * _DAY_MS
    expected_opens = [_START_TS + i * _DAY_MS for i in range(_BAR_COUNT)]

    artifacts_dir = tmp_path / "artifacts"
    record = _make_record(start_ts=_START_TS, end_ts=last_stored_open)

    updated = execute_run(
        record,
        bars_db_path=db_path,
        artifacts_dir=artifacts_dir,
    )

    bench_rows = read_bars_json(
        db_path,
        venue=_VENUE,
        symbol=_BENCH_SYMBOL,
        timeframe="1d",
        start_ts=_START_TS,
        end_ts=last_stored_open,
    )
    assert len(bench_rows) == _BAR_COUNT
    bench_ts = [int(row["ts"]) for row in bench_rows]
    assert bench_ts == expected_opens
    assert bench_ts[-1] == last_stored_open

    first_stored_close = float(bench_rows[0]["close"])
    last_stored_close = float(bench_rows[-1]["close"])

    table = pq.read_table(artifacts_dir / updated.run_id / "equity.parquet")
    ts_values = [int(v) for v in table.column("ts").to_pylist()]
    equity_values = [float(v) for v in table.column("equity").to_pylist()]
    benchmark_values = table.column("benchmark").to_pylist()

    for i in range(1, len(ts_values)):
        assert ts_values[i] > ts_values[i - 1]
    assert len(ts_values) >= 2
    assert ts_values[-1] == _START_TS + _BAR_COUNT * _DAY_MS
    assert ts_values[-1] not in bench_ts

    last_benchmark = benchmark_values[-1]
    assert last_benchmark is not None
    assert last_benchmark == pytest.approx(
        equity_values[0] * last_stored_close / first_stored_close
    )

    assert all(b is not None for b in benchmark_values)
