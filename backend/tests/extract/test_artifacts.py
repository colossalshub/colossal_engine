from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from pandas import Timestamp

from quant.extract.artifacts import write_artifacts
from quant.extract.equity import (
    DrawdownPoint,
    EquityExtraction,
    EquityPoint,
    Verification,
)

_VERIFICATION = Verification(
    verified=True,
    discrepancy_pct=0.0,
    source="reconstructed_from_portfolio_returns",
)

_EXPECTED_ARTIFACT_KEYS = frozenset(
    {"equity", "drawdown", "price", "trades", "fills"}
)

_EQUITY_COLUMNS = ("ts", "equity", "benchmark")
_DRAWDOWN_COLUMNS = ("ts", "dd")
_PRICE_COLUMNS = ("ts", "open", "high", "low", "close", "volume")
_TRADES_COLUMNS = (
    "trade_id",
    "symbol",
    "side",
    "entry_ts",
    "exit_ts",
    "entry_px",
    "exit_px",
    "qty",
    "pnl",
    "pnl_pct",
    "fees",
    "duration_s",
)
_FILLS_COLUMNS = ("ts", "order_side", "last_px", "last_qty", "commission")


def _extraction(
    *,
    benchmark: float | None = 1000.0,
) -> EquityExtraction:
    return EquityExtraction(
        equity=[
            EquityPoint(ts=1000, equity=1000.0, benchmark=benchmark),
            EquityPoint(ts=2000, equity=1050.0, benchmark=benchmark),
        ],
        drawdown=[
            DrawdownPoint(ts=1000, dd=0.0),
            DrawdownPoint(ts=2000, dd=-0.01),
        ],
        verification=_VERIFICATION,
    )


def _price_bar(ts: int) -> dict[str, object]:
    return {
        "ts": ts,
        "open": 1.0 + ts / 10000,
        "high": 2.0,
        "low": 0.5,
        "close": 1.5,
        "volume": 100.0,
        "venue": "binance",
        "symbol": "BTC/USDT",
        "asset_class": "crypto",
        "timeframe": "1d",
        "vwap": None,
        "trades": None,
        "source": "test",
        "ingested_at": 0,
    }


def _position_row() -> dict[str, object]:
    return {
        "position_id": "BTCUSDT.BINANCE-BuyHold-000",
        "instrument_id": "BTCUSDT.BINANCE",
        "side": "LONG",
        "ts_opened": Timestamp("2024-01-01 00:00:00+0000", tz="UTC"),
        "ts_closed": None,
        "avg_px_open": 44179.55,
        "avg_px_close": None,
        "quantity": "1.000000",
        "realized_pnl": "-4.41795500 USDT",
        "realized_return": 0.0,
        "commissions": ["4.41795500 USDT"],
        "duration_ns": None,
    }


def _fill_row() -> dict[str, object]:
    return {
        "ts_event": Timestamp("2024-01-01 00:00:00+0000", tz="UTC"),
        "order_side": "BUY",
        "last_px": "44179.55",
        "last_qty": "1.000000",
        "commission": "4.41795500 USDT",
    }


def test_basic_write(tmp_path: Path) -> None:
    run_dir = tmp_path / "run-1"
    arts = write_artifacts(
        "run-1",
        base_dir=tmp_path,
        extraction=_extraction(),
        price_bars=[_price_bar(1000), _price_bar(2000), _price_bar(3000)],
        position_report=[_position_row()],
        fills_report=[_fill_row()],
    )
    assert set(arts.keys()) == _EXPECTED_ARTIFACT_KEYS
    assert arts["equity"] == "equity.parquet"
    for fname in arts.values():
        assert (run_dir / fname).is_file()

    equity = pq.read_table(run_dir / "equity.parquet")
    assert equity.column_names == list(_EQUITY_COLUMNS)
    assert equity.schema.field("ts").type == pa.int64()
    assert equity.schema.field("equity").type == pa.float64()

    trades = pq.read_table(run_dir / "trades.parquet")
    assert trades.column_names == list(_TRADES_COLUMNS)
    assert trades.num_rows == 1
    assert trades.column("trade_id")[0].as_py() == "BTCUSDT.BINANCE-BuyHold-000"

    fills = pq.read_table(run_dir / "fills.parquet")
    assert fills.column_names == list(_FILLS_COLUMNS)
    assert fills.num_rows == 1


@pytest.mark.parametrize(
    ("position_report", "fills_report"),
    [
        ([], []),
    ],
)
def test_empty_trades_and_fills(
    tmp_path: Path,
    position_report: list[dict[str, object]],
    fills_report: list[dict[str, object]],
) -> None:
    write_artifacts(
        "empty",
        base_dir=tmp_path,
        extraction=_extraction(),
        price_bars=[_price_bar(1000)],
        position_report=position_report,
        fills_report=fills_report,
    )
    run_dir = tmp_path / "empty"
    trades = pq.read_table(run_dir / "trades.parquet")
    fills = pq.read_table(run_dir / "fills.parquet")
    assert trades.column_names == list(_TRADES_COLUMNS)
    assert fills.column_names == list(_FILLS_COLUMNS)
    assert trades.num_rows == 0
    assert fills.num_rows == 0


def test_benchmark_nulls(tmp_path: Path) -> None:
    write_artifacts(
        "null-bench",
        base_dir=tmp_path,
        extraction=_extraction(benchmark=None),
        price_bars=[_price_bar(1000)],
        position_report=[],
        fills_report=[],
    )
    equity = pq.read_table(tmp_path / "null-bench" / "equity.parquet")
    benchmark_col = equity.column("benchmark")
    assert benchmark_col.null_count == equity.num_rows
    assert all(v is None for v in benchmark_col.to_pylist())


def test_price_bar_order_preserved(tmp_path: Path) -> None:
    bars = [_price_bar(3000), _price_bar(1000), _price_bar(2000)]
    write_artifacts(
        "order",
        base_dir=tmp_path,
        extraction=_extraction(),
        price_bars=bars,
        position_report=[],
        fills_report=[],
    )
    price = pq.read_table(tmp_path / "order" / "price.parquet")
    assert price.column("ts").to_pylist() == [3000, 1000, 2000]


def test_fresh_directory_creation(tmp_path: Path) -> None:
    run_dir = tmp_path / "new-run"
    assert not run_dir.exists()
    write_artifacts(
        "new-run",
        base_dir=tmp_path,
        extraction=_extraction(),
        price_bars=[_price_bar(1000)],
        position_report=[],
        fills_report=[],
    )
    assert run_dir.is_dir()

    write_artifacts(
        "new-run",
        base_dir=tmp_path,
        extraction=_extraction(),
        price_bars=[_price_bar(1000), _price_bar(2000)],
        position_report=[],
        fills_report=[],
    )
    price = pq.read_table(run_dir / "price.parquet")
    assert price.num_rows == 2
