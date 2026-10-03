"""Tests for `quant.api.schemas` — the §4.4 wire-contract models."""

from __future__ import annotations

import json
import logging
import sqlite3
from collections import UserDict
from collections.abc import Iterator
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from quant.api.routers.runs import router
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
from quant.data.runs_store import init_runs_schema


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
        "experiment_id": "exp-001",
        "research_stage": "oos",
        "hypothesis_id": "hyp-007",
        "strategy_version": "momentum-v2",
        "in_sample_start_ts": 1_577_836_800_000,
        "in_sample_end_ts": 1_609_459_200_000,
        "validation_start_ts": 1_609_459_200_001,
        "validation_end_ts": 1_640_995_200_000,
        "oos_start_ts": 1_640_995_200_001,
        "oos_end_ts": 1_672_531_200_000,
        "trial_index": 3,
        "trial_count": 12,
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
    assert run.research_stage == "oos"
    assert run.hypothesis_id == "hyp-007"
    assert run.strategy_version == "momentum-v2"
    assert run.in_sample_start_ts == 1_577_836_800_000
    assert run.validation_start_ts == 1_609_459_200_001
    assert run.oos_start_ts == 1_640_995_200_001
    assert run.trial_index == 3
    assert run.trial_count == 12


def test_run_summary_nullable_fields_accept_none() -> None:
    data = _run_summary_dict()
    nullable_fields = (
        "git_sha",
        "sharpe",
        "cagr",
        "max_drawdown",
        "experiment_id",
        "research_stage",
        "hypothesis_id",
        "strategy_version",
        "in_sample_start_ts",
        "in_sample_end_ts",
        "validation_start_ts",
        "validation_end_ts",
        "oos_start_ts",
        "oos_end_ts",
        "trial_index",
        "trial_count",
    )
    data.update({field: None for field in nullable_fields})
    run = RunSummary(**data)
    assert all(getattr(run, field) is None for field in nullable_fields)


def test_run_summary_research_metadata_defaults_to_none() -> None:
    data = _run_summary_dict()
    research_fields = (
        "research_stage",
        "hypothesis_id",
        "strategy_version",
        "in_sample_start_ts",
        "in_sample_end_ts",
        "validation_start_ts",
        "validation_end_ts",
        "oos_start_ts",
        "oos_end_ts",
        "trial_index",
        "trial_count",
    )
    for field in research_fields:
        del data[field]

    run = RunSummary(**data)

    assert all(getattr(run, field) is None for field in research_fields)


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
    assert run_create.research_stage is None
    assert run_create.hypothesis_id is None
    assert run_create.strategy_version is None
    assert run_create.in_sample_start_ts is None
    assert run_create.in_sample_end_ts is None
    assert run_create.validation_start_ts is None
    assert run_create.validation_end_ts is None
    assert run_create.oos_start_ts is None
    assert run_create.oos_end_ts is None
    assert run_create.trial_index is None
    assert run_create.trial_count is None


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


def test_run_create_constructs_with_research_metadata() -> None:
    run_create = RunCreate(
        strategy="momentum",
        params={"lookback": 12},
        universe=["BTC/USDT"],
        start_ts=1_577_836_800_000,
        end_ts=1_672_531_200_000,
        experiment_id="exp-001",
        research_stage="validation",
        hypothesis_id="hyp-007",
        strategy_version="momentum-v2",
        in_sample_start_ts=1_577_836_800_000,
        in_sample_end_ts=1_609_459_200_000,
        validation_start_ts=1_609_459_200_001,
        validation_end_ts=1_640_995_200_000,
        oos_start_ts=1_640_995_200_001,
        oos_end_ts=1_672_531_200_000,
        trial_index=3,
        trial_count=12,
    )

    assert run_create.research_stage == "validation"
    assert run_create.hypothesis_id == "hyp-007"
    assert run_create.strategy_version == "momentum-v2"
    assert run_create.in_sample_start_ts == 1_577_836_800_000
    assert run_create.validation_start_ts == 1_609_459_200_001
    assert run_create.oos_start_ts == 1_640_995_200_001
    assert run_create.trial_index == 3
    assert run_create.trial_count == 12


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


@pytest.mark.parametrize("model_cls", [RunSummary, RunCreate])
def test_run_models_invalid_research_stage_raises(model_cls: type) -> None:
    if model_cls is RunSummary:
        data = _run_summary_dict()
    else:
        data = {
            "strategy": "momentum",
            "params": {},
            "universe": [],
            "start_ts": 0,
            "end_ts": 1,
        }
    data["research_stage"] = "holdout"

    with pytest.raises(ValidationError):
        model_cls(**data)


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


# Raw request admission is distinct from ordinary and historical metadata.
_RESEARCH_RANGES = {
    "in_sample_start_ts": -10,
    "in_sample_end_ts": 0,
    "validation_start_ts": 0,
    "validation_end_ts": 10,
    "oos_start_ts": 10,
    "oos_end_ts": 20,
}


def _research_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "strategy": "buy_hold",
        "params": {"trade_size": "1", "nested": {"research_stage": "holdout"}},
        "universe": ["BTC/USDT"],
        "start_ts": 100,
        "end_ts": 200,
        "research_stage": "oos",
        "hypothesis_id": "hyp-raw",
        "strategy_version": "v1",
        "trial_index": 0,
        "trial_count": 3,
        **_RESEARCH_RANGES,
    }
    payload.update(overrides)
    return payload


def _assert_declaration_error(
    error: ValidationError,
    message: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    errors = error.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ()
    assert errors[0]["type"] == "value_error"
    assert errors[0]["msg"] == "Value error, " + message
    records = [record for record in caplog.records if record.levelno >= logging.ERROR]
    assert [(record.name, record.getMessage()) for record in records] == [
        ("quant.engine.temporal", message),
    ]


@pytest.mark.parametrize("field", list(_RESEARCH_RANGES))
@pytest.mark.parametrize("raw", [True, "10", 10.0, Decimal("10")])
def test_designated_endpoints_reject_before_coercion(
    field: str,
    raw: object,
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = _research_payload(**{field: raw})
    original = deepcopy(payload)
    with pytest.raises(ValidationError) as caught:
        RunCreate(**payload)
    _assert_declaration_error(
        caught.value,
        f"{field} must be an integer UTC epoch-millisecond timestamp "
        "(bool is not allowed)",
        caplog,
    )
    assert payload == original


@pytest.mark.parametrize(
    "overrides, message",
    [
        (
            {"research_stage": "holdout", "in_sample_start_ts": True},
            "research_stage must be exploration, validation, oos, or None",
        ),
        (
            {
                "research_stage": "validation",
                "in_sample_start_ts": None,
                "in_sample_end_ts": None,
            },
            "validation research_stage requires in_sample range",
        ),
        (
            {
                "research_stage": "oos",
                "in_sample_start_ts": None,
                "in_sample_end_ts": None,
            },
            "oos research_stage requires in_sample range",
        ),
        (
            {
                "research_stage": "validation",
                "validation_start_ts": None,
                "validation_end_ts": None,
            },
            "validation research_stage requires validation range",
        ),
        (
            {"oos_start_ts": None, "oos_end_ts": None},
            "oos research_stage requires oos range",
        ),
        (
            {"in_sample_end_ts": None, "validation_start_ts": True},
            "in_sample_start_ts and in_sample_end_ts must be supplied together",
        ),
        (
            {"in_sample_end_ts": -10},
            "in_sample_start_ts must be less than in_sample_end_ts",
        ),
        (
            {"in_sample_end_ts": -11},
            "in_sample_start_ts must be less than in_sample_end_ts",
        ),
        (
            {"validation_start_ts": -1},
            "in_sample range must end at or before validation range starts",
        ),
        (
            {
                "validation_start_ts": None,
                "validation_end_ts": None,
                "oos_start_ts": -1,
            },
            "in_sample range must end at or before oos range starts",
        ),
        (
            {"research_stage": "exploration", "oos_end_ts": 10},
            "oos_start_ts must be less than oos_end_ts",
        ),
        (
            {"in_sample_start_ts": None, "in_sample_end_ts": None, "oos_end_ts": 10},
            "oos_start_ts must be less than oos_end_ts",
        ),
    ],
)
def test_designated_declaration_errors_and_precedence(
    overrides: dict[str, Any],
    message: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = _research_payload(**overrides)
    original = deepcopy(payload)
    for _ in range(2):
        caplog.clear()
        with pytest.raises(ValidationError) as caught:
            RunCreate.model_validate(UserDict(payload))
        _assert_declaration_error(caught.value, message, caplog)
        assert payload == original


@pytest.mark.parametrize(
    "metadata",
    [
        {"research_stage": "exploration"},
        {
            "research_stage": "exploration",
            "in_sample_start_ts": None,
            "in_sample_end_ts": None,
        },
        {
            "research_stage": "exploration",
            "in_sample_start_ts": -10,
            "in_sample_end_ts": 0,
        },
        {
            "research_stage": "validation",
            **{k: v for k, v in _RESEARCH_RANGES.items() if not k.startswith("oos")},
        },
        {
            "research_stage": "oos",
            **{
                k: v
                for k, v in _RESEARCH_RANGES.items()
                if not k.startswith("validation")
            },
        },
        {"research_stage": "oos", **_RESEARCH_RANGES},
        {"research_stage": "oos", **_RESEARCH_RANGES, "oos_end_ts": 10**100},
    ],
)
def test_valid_designated_paths_preserve_payload(
    metadata: dict[str, Any],
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = _research_payload()
    for field in ("research_stage", *_RESEARCH_RANGES):
        del payload[field]
    payload.update(metadata)
    original = deepcopy(payload)
    models = [
        RunCreate(**payload),
        RunCreate.model_validate(UserDict(payload)),
        RunCreate.model_validate_json(json.dumps(payload)),
    ]
    for model in models:
        dump = model.model_dump()
        assert {field: dump[field] for field in payload} == payload
        assert all(
            dump[field] is None for field in _RESEARCH_RANGES if field not in payload
        )
        assert dump["params"] == payload["params"]
        assert "hypothesis_id" not in dump["params"]
        assert model.start_ts == 100 and model.end_ts == 200
    assert models[0] == models[1] == models[2]
    assert payload == original
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_designated_accepts_integer_subclass() -> None:
    class Timestamp(int):
        pass

    model = RunCreate.model_validate(
        _research_payload(in_sample_start_ts=Timestamp(-10))
    )
    assert model.in_sample_start_ts == -10
    assert model.in_sample_end_ts == 0


@pytest.mark.parametrize("raw", ["10", True, 10.0])
def test_json_designated_endpoint_rejects_raw_values(
    raw: object,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with pytest.raises(ValidationError) as caught:
        RunCreate.model_validate_json(json.dumps(_research_payload(oos_start_ts=raw)))
    _assert_declaration_error(
        caught.value,
        "oos_start_ts must be an integer UTC epoch-millisecond timestamp "
        "(bool is not allowed)",
        caplog,
    )


@pytest.mark.parametrize("explicit_null", [False, True])
@pytest.mark.parametrize(
    "overrides",
    [
        {"in_sample_end_ts": None},
        {"in_sample_end_ts": -10},
        {"in_sample_end_ts": -11},
        {"validation_start_ts": -5},
        {"in_sample_start_ts": "-10", "validation_start_ts": True},
    ],
)
def test_ordinary_ranges_keep_semantics_and_coercion(
    explicit_null: bool,
    overrides: dict[str, Any],
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = _research_payload(**overrides)
    if explicit_null:
        payload["research_stage"] = None
    else:
        del payload["research_stage"]
    model = RunCreate.model_validate(payload)
    assert model.research_stage is None
    for field in _RESEARCH_RANGES:
        expected = payload[field]
        assert getattr(model, field) == (None if expected is None else int(expected))
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_ordinary_malformed_endpoint_keeps_field_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with pytest.raises(ValidationError) as caught:
        RunCreate.model_validate(
            _research_payload(research_stage=None, oos_start_ts="bad")
        )
    assert caught.value.errors()[0]["loc"] == ("oos_start_ts",)
    assert caught.value.errors()[0]["type"] == "int_parsing"
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


@pytest.mark.parametrize(
    "overrides",
    [
        {"in_sample_end_ts": None},
        {"in_sample_end_ts": -11},
        {"validation_start_ts": -5},
    ],
)
def test_historical_designated_summary_remains_permissive(
    overrides: dict[str, Any],
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = {**_run_summary_dict(), **_RESEARCH_RANGES, **overrides}
    assert RunSummary(**payload).model_dump() == payload
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_nonmapping_and_existing_model_use_pydantic_defaults() -> None:
    with pytest.raises(ValidationError) as caught:
        RunCreate.model_validate([("strategy", "buy_hold")])
    assert caught.value.errors()[0]["type"] == "model_type"
    assert caught.value.errors()[0]["loc"] == ()
    model = RunCreate(**_research_payload())
    assert RunCreate.model_validate(model) is model


@pytest.fixture
def research_client(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Iterator[tuple[TestClient, Path]]:
    path = tmp_path / "runs.sqlite"
    monkeypatch.setenv("QUANT_RUNS_DB", str(path))
    init_runs_schema(path)
    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as client:
        yield client, path


@pytest.mark.parametrize(
    "overrides, message",
    [
        (
            {"in_sample_end_ts": None},
            "in_sample_start_ts and in_sample_end_ts must be supplied together",
        ),
        (
            {"validation_start_ts": -1},
            "in_sample range must end at or before validation range starts",
        ),
        (
            {"oos_start_ts": "10"},
            "oos_start_ts must be an integer UTC epoch-millisecond timestamp "
            "(bool is not allowed)",
        ),
        (
            {"oos_start_ts": True},
            "oos_start_ts must be an integer UTC epoch-millisecond timestamp "
            "(bool is not allowed)",
        ),
    ],
)
def test_post_rejects_raw_designation_without_inserting(
    research_client: tuple[TestClient, Path],
    overrides: dict[str, Any],
    message: str,
) -> None:
    client, path = research_client
    response = client.post("/api/runs", json=_research_payload(**overrides))
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert len(detail) == 1
    assert detail[0]["loc"] == ["body"]
    assert detail[0]["type"] == "value_error"
    assert detail[0]["msg"] == "Value error, " + message
    with sqlite3.connect(path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM meta_runs").fetchone()[0] == 0


@pytest.mark.parametrize("ordinary", [False, True])
def test_post_preserves_designated_and_ordinary_metadata(
    research_client: tuple[TestClient, Path],
    ordinary: bool,
) -> None:
    client, path = research_client
    payload = _research_payload()
    if ordinary:
        payload.update(
            research_stage=None, in_sample_end_ts=-11, validation_start_ts=-5
        )
    response = client.post("/api/runs", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "queued"
    fields = (
        "research_stage",
        "hypothesis_id",
        "strategy_version",
        "trial_index",
        "trial_count",
        "start_ts",
        "end_ts",
        *_RESEARCH_RANGES,
    )
    assert {field: body[field] for field in fields} == {
        field: payload[field] for field in fields
    }
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM meta_runs WHERE run_id = ?", (body["run_id"],)
        ).fetchone()
        assert row is not None
        assert {field: row[field] for field in fields} == {
            field: payload[field] for field in fields
        }
        assert json.loads(row["params"]) == payload["params"]
