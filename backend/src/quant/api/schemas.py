"""Pydantic v2 wire-contract models mirroring PROJECT.md §4.4 exactly.

This module is the single source of truth for the JSON shapes exchanged
between the backend and the frontend. Every router in `quant.api.routers`
imports its request/response models from here — never define an inline
dict or ad-hoc shape in a router.

Any change to a field name, type, or nesting here is a change to §4.4 and
requires a migration script and a project-version bump (PROJECT.md §7).

These are wire types only: never import ORM, DB (sqlite3/duckdb), or
NautilusTrader types into this module. Conversion from internal
representations to these models happens in the routers/deps layer, not here.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "ApiErrorDetail",
    "ApiError",
    "RunSummary",
    "RunList",
    "RunCreate",
    "KpiBlock",
    "EquityPoint",
    "DrawdownPoint",
    "OHLCV",
    "TradeMarker",
    "MonthlyReturns",
    "Verification",
    "ExecutionAssumptions",
    "TearSheet",
    "Trade",
    "TradePage",
    "CoverageCell",
    "CoverageRow",
    "CoverageResponse",
    "IngestRequest",
    "IngestResponse",
]


class ApiErrorDetail(BaseModel):
    """Body of the `error` key in an `ApiError` response (§4.4)."""

    model_config = ConfigDict(extra="ignore")

    code: str
    message: str
    details: Any | None = None


class ApiError(BaseModel):
    """Top-level error envelope returned on every non-2xx response (§4.4)."""

    model_config = ConfigDict(extra="ignore")

    error: ApiErrorDetail


class RunSummary(BaseModel):
    """One row of run metadata, in `RunList.items` and `TearSheet.run` (§4.4)."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    name: str
    strategy: str
    universe: list[str]
    start_ts: int
    end_ts: int
    created_at: int
    git_sha: str | None
    git_dirty: bool
    status: Literal["queued", "running", "done", "failed", "archived"]
    sharpe: float | None
    cagr: float | None
    max_drawdown: float | None
    experiment_id: str | None


class RunList(BaseModel):
    """Paginated response for `GET /api/runs` (§4.4)."""

    model_config = ConfigDict(extra="forbid")

    items: list[RunSummary]
    total: int
    page: int
    page_size: int


class RunCreate(BaseModel):
    """Request body for `POST /api/runs` (§4.4)."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    strategy: str
    params: dict[str, Any]
    universe: list[str]
    start_ts: int
    end_ts: int
    experiment_id: str | None = None


class KpiBlock(BaseModel):
    """Computed KPI block (§4.4).

    All fields are nullable: `quant.extract.metrics.extract_metrics` returns
    `None` for any metric that cannot be computed (e.g. a zero-trade run, or
    fewer than two return observations) rather than `NaN` or `inf`.
    """

    model_config = ConfigDict(extra="forbid")

    sharpe: float | None
    sortino: float | None
    cagr: float | None
    volatility: float | None
    max_drawdown: float | None
    calmar: float | None
    win_rate: float | None
    profit_factor: float | None
    turnover: float | None
    total_trades: float | None
    avg_duration_days: float | None


class EquityPoint(BaseModel):
    """One point of the reconstructed equity curve (§4.4)."""

    model_config = ConfigDict(extra="forbid")

    ts: int
    equity: float
    benchmark: float | None


class DrawdownPoint(BaseModel):
    """One point of the underwater/drawdown series; `dd` in [-1, 0] (§4.4)."""

    model_config = ConfigDict(extra="forbid")

    ts: int
    dd: float


class OHLCV(BaseModel):
    """One price bar fed into the engine, using full field names (§4.4)."""

    model_config = ConfigDict(extra="forbid")

    ts: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class TradeMarker(BaseModel):
    """One chart-plotting marker derived from fills, for the price chart (§4.4)."""

    model_config = ConfigDict(extra="forbid")

    ts: int
    side: Literal["buy", "sell"]
    price: float
    qty: float


class MonthlyReturns(BaseModel):
    """One calendar year of monthly returns; `months` has exactly 12 entries (§4.4)."""

    model_config = ConfigDict(extra="forbid")

    year: int
    months: list[float | None] = Field(min_length=12, max_length=12)


class Verification(BaseModel):
    """Equity-reconstruction verification block (§4.3, §4.4)."""

    model_config = ConfigDict(extra="forbid")

    verified: bool
    discrepancy_pct: float
    source: str


class ExecutionAssumptions(BaseModel):
    """Pinned execution assumptions surfaced on the tear sheet (Phase 15.2).

    Structural fields are copied verbatim from
    `quant.engine.assumptions.CURRENT_ASSUMPTIONS`. `maker_fee`/`taker_fee`
    are the effective fee rates for the specific run (its params, falling
    back to the pinned defaults).
    """

    model_config = ConfigDict(extra="forbid")

    bar_ts: str
    nautilus_bar_ts_event: str
    signal_and_order: str
    order_type: str
    sizing_price_when_deploy_pct_positive: str
    maker_fee_default: str
    taker_fee_default: str
    maker_fee: str
    taker_fee: str
    fill_model: str
    latency: str
    spread: str
    queue_model: str
    partial_fills: str
    equity_ts: str
    fill_ts: str
    marker_ts: str
    fill_included_in_equity: str


class TearSheet(BaseModel):
    """Full response for `GET /api/runs/{id}/tearsheet` (§4.4)."""

    model_config = ConfigDict(extra="forbid")

    run: RunSummary
    params: dict[str, Any]
    kpis: KpiBlock
    equity: list[EquityPoint]
    drawdown: list[DrawdownPoint]
    price: list[OHLCV]
    markers: list[TradeMarker]
    monthly_returns: list[MonthlyReturns]
    verification: Verification
    execution_assumptions: ExecutionAssumptions
    artifacts: dict[str, str]


class Trade(BaseModel):
    """One row of `GET /api/runs/{id}/trades` (§4.4)."""

    model_config = ConfigDict(extra="forbid")

    trade_id: str
    symbol: str
    side: Literal["long", "short"]
    entry_ts: int
    exit_ts: int | None
    entry_px: float
    exit_px: float | None
    qty: float
    pnl: float
    pnl_pct: float
    fees: float
    duration_s: float


class TradePage(BaseModel):
    """Paginated response for `GET /api/runs/{id}/trades` (§4.4)."""

    model_config = ConfigDict(extra="forbid")

    items: list[Trade]
    total: int
    page: int
    page_size: int


class CoverageCell(BaseModel):
    model_config = ConfigDict(extra="forbid")

    year: int
    month: Annotated[int, Field(ge=1, le=12)]
    bars: int
    expected: int
    coverage: Annotated[float, Field(ge=0.0, le=1.0)]


class CoverageRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    venue: str
    symbol: str
    timeframe: str
    cells: list[CoverageCell]


class CoverageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rows: list[CoverageRow]


class IngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    venue: str
    symbol: str
    timeframe: str
    start: str
    end: str


class IngestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    command: str
