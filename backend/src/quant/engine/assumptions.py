from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionAssumptions:
    """Pinned record of execution behavior ``runner.py`` uses today."""

    bar_ts: str
    nautilus_bar_ts_event: str
    signal_and_order: str
    order_type: str
    sizing_price_when_deploy_pct_positive: str
    maker_fee_default: str
    taker_fee_default: str
    fill_model: str
    latency: str
    spread: str
    queue_model: str
    partial_fills: str
    equity_ts: str
    fill_ts: str
    marker_ts: str
    fill_included_in_equity: str


CURRENT_ASSUMPTIONS = ExecutionAssumptions(
    bar_ts="open",
    nautilus_bar_ts_event="close",
    signal_and_order="on_bar",
    order_type="market",
    sizing_price_when_deploy_pct_positive="bar.close",
    maker_fee_default="0.001",
    taker_fee_default="0.001",
    fill_model="not_passed",
    latency="not_passed",
    spread="not_passed",
    queue_model="not_passed",
    partial_fills="not_passed",
    equity_ts="open_then_each_close",
    fill_ts="bar_close",
    marker_ts="fill",
    fill_included_in_equity="same_timestamp",
)
