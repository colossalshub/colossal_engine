from __future__ import annotations

from pathlib import Path
from typing import cast

import pandas as pd  # type: ignore[import-untyped]  # stubs not in dev deps; pandas via nautilus_trader
import pyarrow as pa  # type: ignore[import-untyped]  # pyarrow ships without py.typed
import pyarrow.parquet as pq  # type: ignore[import-untyped]  # pyarrow ships without py.typed
from pandas import Timestamp

from quant.extract.equity import EquityExtraction

_ARTIFACT_FILENAMES: dict[str, str] = {
    "equity": "equity.parquet",
    "drawdown": "drawdown.parquet",
    "price": "price.parquet",
    "trades": "trades.parquet",
    "fills": "fills.parquet",
}

_TRADES_SCHEMA = pa.schema(
    [
        ("trade_id", pa.string()),
        ("symbol", pa.string()),
        ("side", pa.string()),
        ("entry_ts", pa.int64()),
        ("exit_ts", pa.int64()),
        ("entry_px", pa.float64()),
        ("exit_px", pa.float64()),
        ("qty", pa.float64()),
        ("pnl", pa.float64()),
        ("pnl_pct", pa.float64()),
        ("fees", pa.float64()),
        ("duration_s", pa.float64()),
    ]
)

_FILLS_SCHEMA = pa.schema(
    [
        ("ts", pa.int64()),
        ("order_side", pa.string()),
        ("last_px", pa.float64()),
        ("last_qty", pa.float64()),
        ("commission", pa.float64()),
    ]
)


def _numeric(value: object) -> float:
    if isinstance(value, (int, float, str)):
        return float(value)
    msg = f"expected numeric value, got {type(value).__name__}"
    raise TypeError(msg)


def _money_str_to_float(value: object) -> float:
    if isinstance(value, str):
        return float(value.split()[0])
    msg = f"expected money string, got {type(value).__name__}"
    raise TypeError(msg)


def _ts_to_ms(value: object) -> int:
    if isinstance(value, Timestamp):
        return int(value.value // 1_000_000)
    msg = f"expected pandas Timestamp, got {type(value).__name__}"
    raise TypeError(msg)


def _optional_ts_to_ms(value: object) -> int | None:
    if value is None:
        return None
    if pd.isna(value):
        return None
    return _ts_to_ms(value)


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    if pd.isna(value):
        return None
    return _numeric(value)


def _map_position_row(row: dict[str, object]) -> dict[str, object]:
    commissions_raw = row.get("commissions")
    fees = 0.0
    if isinstance(commissions_raw, list):
        fees = sum(_money_str_to_float(item) for item in commissions_raw)

    duration_ns = row.get("duration_ns")
    duration_s = 0.0
    if duration_ns is not None and not pd.isna(duration_ns):
        duration_s = _numeric(duration_ns) / 1e9

    realized_return = row.get("realized_return")
    pnl_pct = 0.0 if realized_return is None else _numeric(realized_return)

    side_raw = row["side"]
    if side_raw == "LONG":
        side = "long"
    elif side_raw == "SHORT":
        side = "short"
    else:
        msg = f"unexpected position side: {side_raw!r}"
        raise ValueError(msg)

    return {
        "trade_id": str(row["position_id"]),
        "symbol": str(row["instrument_id"]),
        "side": side,
        "entry_ts": _ts_to_ms(row["ts_opened"]),
        "exit_ts": _optional_ts_to_ms(row.get("ts_closed")),
        "entry_px": _numeric(row["avg_px_open"]),
        "exit_px": _optional_float(row.get("avg_px_close")),
        "qty": _numeric(row["quantity"]),
        "pnl": _money_str_to_float(row["realized_pnl"]),
        "pnl_pct": pnl_pct,
        "fees": fees,
        "duration_s": duration_s,
    }


def _map_fill_row(row: dict[str, object]) -> dict[str, object]:
    order_side = str(row["order_side"]).lower()
    return {
        "ts": _ts_to_ms(row["ts_event"]),
        "order_side": order_side,
        "last_px": _numeric(row["last_px"]),
        "last_qty": _numeric(row["last_qty"]),
        "commission": _money_str_to_float(row["commission"]),
    }


def _empty_table(schema: pa.Schema) -> pa.Table:
    arrays = [pa.array([], type=field.type) for field in schema]
    return pa.table({field.name: arrays[i] for i, field in enumerate(schema)})


def write_artifacts(
    run_id: str,
    *,
    base_dir: Path,
    extraction: EquityExtraction,
    price_bars: list[dict[str, object]],
    position_report: list[dict[str, object]],
    fills_report: list[dict[str, object]],
) -> dict[str, str]:
    out_dir = base_dir / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    equity_table = pa.table(
        {
            "ts": pa.array([p.ts for p in extraction.equity], type=pa.int64()),
            "equity": pa.array(
                [p.equity for p in extraction.equity], type=pa.float64()
            ),
            "benchmark": pa.array(
                [p.benchmark for p in extraction.equity], type=pa.float64()
            ),
        }
    )
    pq.write_table(equity_table, out_dir / _ARTIFACT_FILENAMES["equity"])

    drawdown_table = pa.table(
        {
            "ts": pa.array([p.ts for p in extraction.drawdown], type=pa.int64()),
            "dd": pa.array([p.dd for p in extraction.drawdown], type=pa.float64()),
        }
    )
    pq.write_table(drawdown_table, out_dir / _ARTIFACT_FILENAMES["drawdown"])

    price_table = pa.table(
        {
            "ts": pa.array(
                [cast(int, bar["ts"]) for bar in price_bars], type=pa.int64()
            ),
            "open": pa.array(
                [_numeric(bar["open"]) for bar in price_bars], type=pa.float64()
            ),
            "high": pa.array(
                [_numeric(bar["high"]) for bar in price_bars], type=pa.float64()
            ),
            "low": pa.array(
                [_numeric(bar["low"]) for bar in price_bars], type=pa.float64()
            ),
            "close": pa.array(
                [_numeric(bar["close"]) for bar in price_bars], type=pa.float64()
            ),
            "volume": pa.array(
                [_numeric(bar["volume"]) for bar in price_bars], type=pa.float64()
            ),
        }
    )
    pq.write_table(price_table, out_dir / _ARTIFACT_FILENAMES["price"])

    if position_report:
        trades_table = pa.Table.from_pylist(
            [_map_position_row(row) for row in position_report],
            schema=_TRADES_SCHEMA,
        )
    else:
        trades_table = _empty_table(_TRADES_SCHEMA)
    pq.write_table(trades_table, out_dir / _ARTIFACT_FILENAMES["trades"])

    if fills_report:
        fills_table = pa.Table.from_pylist(
            [_map_fill_row(row) for row in fills_report],
            schema=_FILLS_SCHEMA,
        )
    else:
        fills_table = _empty_table(_FILLS_SCHEMA)
    pq.write_table(fills_table, out_dir / _ARTIFACT_FILENAMES["fills"])

    return dict(_ARTIFACT_FILENAMES)
