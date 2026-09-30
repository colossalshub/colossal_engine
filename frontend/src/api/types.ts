// Mirrors PROJECT.md §4.4. Any change here requires a matching change in
// backend/src/quant/api/schemas.py and a project-version bump (§7).

// ---------------------------------------------------------------------
// Errors and pagination
// ---------------------------------------------------------------------

export interface ApiErrorDetail {
  code: string;
  message: string;
  details?: unknown;
}

export interface ApiError {
  error: ApiErrorDetail;
}

// ---------------------------------------------------------------------
// Runs
// ---------------------------------------------------------------------

export type RunStatus = 'queued' | 'running' | 'done' | 'failed' | 'archived';

export interface RunSummary {
  run_id: string;
  name: string;
  strategy: string;
  universe: string[];
  start_ts: number;
  end_ts: number;
  created_at: number;
  git_sha: string | null;
  git_dirty: boolean;
  experiment_id: string | null;
  status: RunStatus;
  sharpe: number | null;
  cagr: number | null;
  max_drawdown: number | null;
}

export interface RunList {
  items: RunSummary[];
  total: number;
  page: number;
  page_size: number;
}

export interface RunCreate {
  name?: string;
  strategy: string;
  params: Record<string, unknown>;
  universe: string[];
  start_ts: number;
  end_ts: number;
}

// ---------------------------------------------------------------------
// KPIs
// ---------------------------------------------------------------------

export interface KpiBlock {
  sharpe: number | null;
  sortino: number | null;
  cagr: number | null;
  volatility: number | null;
  max_drawdown: number | null;
  calmar: number | null;
  win_rate: number | null;
  profit_factor: number | null;
  turnover: number | null;
  total_trades: number | null;
  avg_duration_days: number | null;
}

// ---------------------------------------------------------------------
// Time series
// ---------------------------------------------------------------------

export interface EquityPoint {
  ts: number;
  equity: number;
  benchmark: number | null;
}

export interface DrawdownPoint {
  ts: number;
  dd: number;
}

export interface OHLCV {
  ts: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface TradeMarker {
  ts: number;
  side: 'buy' | 'sell';
  price: number;
  qty: number;
}

export interface MonthlyReturns {
  year: number;
  months: (number | null)[]; // length 12
}

export interface Verification {
  verified: boolean;
  discrepancy_pct: number;
  source: string;
}

export interface ExecutionAssumptions {
  bar_ts: string;
  nautilus_bar_ts_event: string;
  signal_and_order: string;
  order_type: string;
  sizing_price_when_deploy_pct_positive: string;
  maker_fee_default: string;
  taker_fee_default: string;
  maker_fee: string;
  taker_fee: string;
  fill_model: string;
  latency: string;
  spread: string;
  queue_model: string;
  partial_fills: string;
}

// ---------------------------------------------------------------------
// Tear sheet
// ---------------------------------------------------------------------

export interface TearSheet {
  run: RunSummary;
  params: Record<string, unknown>;
  kpis: KpiBlock;
  equity: EquityPoint[];
  drawdown: DrawdownPoint[];
  price: OHLCV[];
  markers: TradeMarker[];
  monthly_returns: MonthlyReturns[];
  verification: Verification;
  execution_assumptions: ExecutionAssumptions;
  artifacts: Record<string, string>;
}

// ---------------------------------------------------------------------
// Trades
// ---------------------------------------------------------------------

export interface Trade {
  trade_id: string;
  symbol: string;
  side: 'long' | 'short';
  entry_ts: number;
  exit_ts: number | null;
  entry_px: number;
  exit_px: number | null;
  qty: number;
  pnl: number;
  pnl_pct: number;
  fees: number;
  duration_s: number;
}

export interface TradePage {
  items: Trade[];
  total: number;
  page: number;
  page_size: number;
}

export interface CoverageCell {
  year: number;
  month: number;
  bars: number;
  expected: number;
  coverage: number;
}

export interface CoverageRow {
  venue: string;
  symbol: string;
  timeframe: string;
  cells: CoverageCell[];
}

export interface CoverageResponse {
  rows: CoverageRow[];
}

export interface IngestRequest {
  venue: string;
  symbol: string;
  timeframe: string;
  start: string;
  end: string;
}

export interface IngestResponse {
  status: string;
  command: string;
}
