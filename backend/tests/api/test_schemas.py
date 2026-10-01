"""Tests for `quant.api.schemas` — the §4.4 wire-contract models."""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import ValidationError

from quant.api.schemas import (
    OHLCV,
    ApiError,
    ApiErrorDetail,
    CoverageCell,
    CoverageResponse,
    DrawdownPoint,
    EquityPoint,
    ExecutionAssumptions,
    KpiBlock,
    MonthlyReturns,
    RunCreate,
    RunList,
    RunSummary,
    TearSheet,
    Trade,
    TradeMarker,
    TradePage,
    Verification,
)


def _run_summary_dict() -> dict[str, Any]:
    return {
        "run_id": "run-1",
        "name": "mom-12-1",
        "strategy": "momentum",
        "universe": ["BTC/USDT", "ETH/USDT"],
        "start_ts": 1_577_836_800_000,
        "end_ts": 1_735_689_600_000,
        "created_at": 1_735_689_600_000,
        "git_sha": "7a3f9c1",
        "git_dirty": False,
        "status": "done",
        "sharpe": 1.42,
        "cagr": 0.214,
        "max_drawdown": -0.183,
        "experiment_id": None,
    }


def _kpi_block_dict() -> dict[str, Any]:
    return {
        "sharpe": 1.42,
        "sortino": 1.9,
        "cagr": 0.214,
        "volatility": 0.151,
        "max_drawdown": -0.183,
        "calmar": 1.17,
        "win_rate": 0.55,
        "profit_factor": 1.8,
        "turnover": 0.3,
        "total_trades": 142.0,
        "avg_duration_days": 3.5,
    }


def _trade_dict() -> dict[str, Any]:
    return {
        "trade_id": "t-1",
        "symbol": "BTC/USDT",
        "side": "long",
        "entry_ts": 1_577_836_800_000,
        "exit_ts": 1_577_923_200_000,
        "entry_px": 30000.0,
        "exit_px": 30500.0,
        "qty": 0.5,
        "pnl": 250.0,
        "pnl_pct": 0.0167,
        "fees": 1.5,
        "duration_s": 86400.0,
    }


def _tear_sheet_dict() -> dict[str, Any]:
    return {
        "run": _run_summary_dict(),
        "params": {"lookback": 12, "skip": 1},
        "kpis": _kpi_block_dict(),
        "equity": [
            {"ts": 1_577_836_800_000, "equity": 100_000.0, "benchmark": 100_000.0},
            {"ts": 1_577_923_200_000, "equity": 101_000.0, "benchmark": None},
        ],
        "drawdown": [
            {"ts": 1_577_836_800_000, "dd": 0.0},
            {"ts": 1_577_923_200_000, "dd": -0.02},
        ],
        "price": [
            {
                "ts": 1_577_836_800_000,
                "open": 100.0,
                "high": 105.0,
                "low": 95.0,
                "close": 101.0,
                "volume": 1234.5,
            }
        ],
        "markers": [
            {"ts": 1_577_836_800_000, "side": "buy", "price": 100.0, "qty": 1.0}
        ],
        "monthly_returns": [
            {
                "year": 2020,
                "months": [
                    0.01, -0.02, None, 0.03, 0.0, 0.01,
                    -0.01, 0.02, None, 0.0, 0.01, -0.03,
                ],
            }
        ],
        "verification": {
            "verified": True,
            "discrepancy_pct": 0.12,
            "source": "reconstructed_from_portfolio_returns",
        },
        "execution_assumptions": _execution_assumptions_dict(),
        "artifacts": {"equity": "equity.parquet", "drawdown": "drawdown.parquet"},
    }


def _execution_assumptions_dict() -> dict[str, Any]:
    return {
        "bar_ts": "open",
        "nautilus_bar_ts_event": "close",
        "signal_and_order": "on_bar",
        "order_type": "market",
        "sizing_price_when_deploy_pct_positive": "bar.close",
        "maker_fee_default": "0.001",
        "taker_fee_default": "0.001",
        "maker_fee": "0.001",
        "taker_fee": "0.001",
        "fill_model": "not_passed",
        "latency": "not_passed",
        "spread": "not_passed",
        "queue_model": "not_passed",
        "partial_fills": "not_passed",
        "equity_ts": "open_then_each_close",
        "fill_ts": "bar_close",
        "marker_ts": "fill",
        "fill_included_in_equity": "same_timestamp",
    }


# ---------------------------------------------------------------------------
# Construction from valid §4.4 shapes
# ---------------------------------------------------------------------------


def test_api_error_detail_constructs() -> None:
    detail = ApiErrorDetail(code="NOT_FOUND", message="run not found")
    assert detail.details is None


def test_api_error_constructs() -> None:
    err = ApiError(
        error={
            "code": "VALIDATION",
            "message": "bad input",
            "details": {"field": "start_ts"},
        }
    )
    assert err.error.code == "VALIDATION"
    assert err.error.details == {"field": "start_ts"}


def test_run_summary_constructs() -> None:
    run = RunSummary(**_run_summary_dict())
    assert run.status == "done"
    assert run.git_sha == "7a3f9c1"


def test_run_summary_nullable_fields_accept_none() -> None:
    data = _run_summary_dict()
    data.update(git_sha=None, sharpe=None, cagr=None, max_drawdown=None)
    run = RunSummary(**data)
    assert run.git_sha is None
    assert run.sharpe is None


def test_run_list_constructs() -> None:
    run_list = RunList(items=[_run_summary_dict()], total=1, page=1, page_size=50)
    assert run_list.total == 1
    assert len(run_list.items) == 1


def test_run_list_empty_items() -> None:
    run_list = RunList(items=[], total=0, page=2, page_size=50)
    assert run_list.items == []


def test_run_create_constructs_without_name() -> None:
    run_create = RunCreate(
        strategy="momentum",
        params={"lookback": 12},
        universe=["BTC/USDT"],
        start_ts=1_577_836_800_000,
        end_ts=1_735_689_600_000,
    )
    assert run_create.name is None


def test_run_create_constructs_with_name() -> None:
    run_create = RunCreate(
        name="mom-12-1",
        strategy="momentum",
        params={},
        universe=[],
        start_ts=0,
        end_ts=1,
    )
    assert run_create.name == "mom-12-1"


def test_kpi_block_constructs_all_present() -> None:
    kpis = KpiBlock(**_kpi_block_dict())
    assert kpis.sharpe == 1.42


def test_kpi_block_constructs_all_none() -> None:
    data = {k: None for k in _kpi_block_dict()}
    kpis = KpiBlock(**data)
    assert all(getattr(kpis, k) is None for k in data)


def test_equity_point_benchmark_none() -> None:
    point = EquityPoint(ts=1, equity=100.0, benchmark=None)
    assert point.benchmark is None


def test_drawdown_point_constructs() -> None:
    point = DrawdownPoint(ts=1, dd=-0.5)
    assert point.dd == -0.5


def test_ohlcv_constructs() -> None:
    bar = OHLCV(ts=1, open=1.0, high=2.0, low=0.5, close=1.5, volume=100.0)
    assert bar.close == 1.5


def test_trade_marker_constructs() -> None:
    marker = TradeMarker(ts=1, side="buy", price=100.0, qty=1.0)
    assert marker.side == "buy"


def test_monthly_returns_constructs_with_12_entries() -> None:
    months: list[float | None] = [0.0] * 11 + [None]
    mr = MonthlyReturns(year=2020, months=months)
    assert len(mr.months) == 12


def test_verification_constructs() -> None:
    v = Verification(
        verified=True,
        discrepancy_pct=0.12,
        source="reconstructed_from_portfolio_returns",
    )
    assert v.verified is True


def test_trade_constructs() -> None:
    trade = Trade(**_trade_dict())
    assert trade.side == "long"


def test_trade_nullable_exit_fields() -> None:
    data = _trade_dict()
    data.update(exit_ts=None, exit_px=None)
    trade = Trade(**data)
    assert trade.exit_ts is None
    assert trade.exit_px is None


def test_trade_page_constructs() -> None:
    page = TradePage(items=[_trade_dict()], total=1, page=1, page_size=100)
    assert page.total == 1


def test_tear_sheet_constructs() -> None:
    sheet = TearSheet(**_tear_sheet_dict())
    assert sheet.run.status == "done"
    assert sheet.kpis.sharpe == 1.42
    assert len(sheet.monthly_returns[0].months) == 12
    assert sheet.execution_assumptions.maker_fee == "0.001"
    assert sheet.execution_assumptions.bar_ts == "open"
    assert sheet.execution_assumptions.equity_ts == "open_then_each_close"
    assert sheet.execution_assumptions.fill_ts == "bar_close"
    assert sheet.execution_assumptions.marker_ts == "fill"
    assert sheet.execution_assumptions.fill_included_in_equity == "same_timestamp"


def test_execution_assumptions_extra_field_forbidden_raises() -> None:
    with pytest.raises(ValidationError):
        ExecutionAssumptions(**_execution_assumptions_dict(), extra_field="nope")


def test_tear_sheet_with_empty_artifacts() -> None:
    data = _tear_sheet_dict()
    data["artifacts"] = {}
    sheet = TearSheet(**data)
    assert sheet.artifacts == {}


def test_tear_sheet_equity_point_benchmark_none() -> None:
    data = _tear_sheet_dict()
    data["equity"] = [{"ts": 1, "equity": 100.0, "benchmark": None}]
    sheet = TearSheet(**data)
    assert sheet.equity[0].benchmark is None


# ---------------------------------------------------------------------------
# Invalid values fail as expected
# ---------------------------------------------------------------------------


def test_run_summary_invalid_status_raises() -> None:
    data = _run_summary_dict()
    data["status"] = "paused"
    with pytest.raises(ValidationError):
        RunSummary(**data)


@pytest.mark.parametrize("bad_side", ["long", "short", "BUY", "", "hold"])
def test_trade_marker_invalid_side_raises(bad_side: str) -> None:
    with pytest.raises(ValidationError):
        TradeMarker(ts=1, side=bad_side, price=1.0, qty=1.0)  # type: ignore[arg-type]


@pytest.mark.parametrize("bad_side", ["buy", "sell", "LONG", "", "flat"])
def test_trade_invalid_side_raises(bad_side: str) -> None:
    data = _trade_dict()
    data["side"] = bad_side
    with pytest.raises(ValidationError):
        Trade(**data)


@pytest.mark.parametrize("n_months", [11, 13])
def test_monthly_returns_wrong_length_raises(n_months: int) -> None:
    with pytest.raises(ValidationError):
        MonthlyReturns(year=2020, months=[0.0] * n_months)


@pytest.mark.parametrize(
    "model_cls, valid_kwargs",
    [
        (RunSummary, _run_summary_dict()),
        (KpiBlock, _kpi_block_dict()),
        (EquityPoint, {"ts": 1, "equity": 1.0, "benchmark": None}),
        (DrawdownPoint, {"ts": 1, "dd": 0.0}),
        (
            OHLCV,
            {
                "ts": 1,
                "open": 1.0,
                "high": 1.0,
                "low": 1.0,
                "close": 1.0,
                "volume": 1.0,
            },
        ),
        (TradeMarker, {"ts": 1, "side": "buy", "price": 1.0, "qty": 1.0}),
        (Verification, {"verified": True, "discrepancy_pct": 0.0, "source": "x"}),
        (Trade, _trade_dict()),
        (
            RunCreate,
            {"strategy": "s", "params": {}, "universe": [], "start_ts": 0, "end_ts": 1},
        ),
    ],
)
def test_extra_field_forbidden_raises(
    model_cls: type, valid_kwargs: dict[str, Any]
) -> None:
    with pytest.raises(ValidationError):
        model_cls(**valid_kwargs, extra_unexpected_field="nope")


def test_tear_sheet_extra_field_forbidden_raises() -> None:
    data = _tear_sheet_dict()
    data["unexpected"] = "nope"
    with pytest.raises(ValidationError):
        TearSheet(**data)


# ---------------------------------------------------------------------------
# Round-trip and JSON-serializability
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "model_cls, kwargs",
    [
        (RunSummary, _run_summary_dict()),
        (KpiBlock, _kpi_block_dict()),
        (Trade, _trade_dict()),
        (TearSheet, _tear_sheet_dict()),
    ],
)
def test_model_dump_round_trips(model_cls: type, kwargs: dict[str, Any]) -> None:
    instance = model_cls(**kwargs)
    dumped = instance.model_dump()
    rebuilt = model_cls(**dumped)
    assert rebuilt == instance


def test_tear_sheet_model_dump_json_mode_is_json_serializable() -> None:
    sheet = TearSheet(**_tear_sheet_dict())
    dumped = sheet.model_dump(mode="json")
    # Must not raise: proves no Decimal/datetime/non-JSON types leaked in.
    serialized = json.dumps(dumped)
    reparsed = json.loads(serialized)
    assert reparsed["run"]["status"] == "done"
    assert reparsed["equity"][1]["benchmark"] is None


def test_coverage_cell_rejects_month_13() -> None:
    with pytest.raises(ValidationError):
        CoverageCell(
            year=2024,
            month=13,
            bars=1,
            expected=31,
            coverage=0.5,
        )


def test_coverage_cell_accepts_coverage_bounds() -> None:
    low = CoverageCell(year=2024, month=1, bars=0, expected=31, coverage=0.0)
    high = CoverageCell(year=2024, month=1, bars=31, expected=31, coverage=1.0)
    assert low.coverage == 0.0
    assert high.coverage == 1.0


def test_coverage_response_empty_rows_round_trips() -> None:
    resp = CoverageResponse(rows=[])
    rebuilt = CoverageResponse(**resp.model_dump())
    assert rebuilt.rows == []
