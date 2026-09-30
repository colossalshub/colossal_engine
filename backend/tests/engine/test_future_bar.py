from __future__ import annotations

import copy

from quant.engine.runner import run_backtest

_BAR_TYPE = "BTCUSDT.BINANCE-1-DAY-LAST-EXTERNAL"
_START_TS = 1_735_689_600_000
_DAY_MS = 86_400_000
_BAR_COUNT = 5


def _flat_bars() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for i in range(_BAR_COUNT):
        rows.append(
            {
                "ts": _START_TS + i * _DAY_MS,
                "open": 100.0,
                "high": 100.0,
                "low": 100.0,
                "close": 100.0,
                "volume": 1.0,
            }
        )
    return rows


def _project_fill(row: dict[str, object]) -> tuple[str, str, str, str, str]:
    return (
        str(row["order_side"]),
        str(row["last_px"]),
        str(row["last_qty"]),
        str(row["ts_event"]),
        str(row["commission"]),
    )


def _run(rows: list[dict[str, object]]):
    return run_backtest(
        venue="binance",
        symbol="BTC/USDT",
        bar_type_str=_BAR_TYPE,
        rows=rows,
        strategy="buy_hold",
        trade_size="1",
        deploy_pct="0",
        starting_balance_usdt=100_000.0,
    )


def test_mutating_last_bar_leaves_earlier_buy_hold_results_unchanged() -> None:
    flat_rows = _flat_bars()
    mutated_rows = copy.deepcopy(flat_rows)
    mutated_rows[-1] = {
        **mutated_rows[-1],
        "open": 100.0,
        "high": 510.0,
        "low": 90.0,
        "close": 500.0,
        "volume": 1.0,
    }

    run_a = _run(flat_rows)
    run_b = _run(mutated_rows)

    expected_fills = [
        (
            "BUY",
            "100.00",
            "0.250000",
            "2025-01-02 00:00:00+00:00",
            "0.02500000 USDT",
        ),
        (
            "BUY",
            "100.01",
            "0.750000",
            "2025-01-02 00:00:00+00:00",
            "0.07500750 USDT",
        ),
    ]

    fills_a = [_project_fill(row) for row in run_a.fills_report]
    fills_b = [_project_fill(row) for row in run_b.fills_report]
    assert fills_a == expected_fills
    assert fills_b == expected_fills

    assert (
        run_a.fills_report[0]["client_order_id"]
        == run_a.fills_report[1]["client_order_id"]
    )
    assert (
        run_b.fills_report[0]["client_order_id"]
        == run_b.fills_report[1]["client_order_id"]
    )
    assert (
        run_a.fills_report[0]["client_order_id"]
        == run_b.fills_report[0]["client_order_id"]
    )

    assert len(run_a.portfolio_returns) >= 2
    assert len(run_b.portfolio_returns) >= 2
    assert run_a.portfolio_returns[:-1] == run_b.portfolio_returns[:-1]

    assert run_a.ending_balance != run_b.ending_balance
    assert run_a.independent_ending_balance != run_b.independent_ending_balance
