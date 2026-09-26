import type { KpiBlock } from '../../api/types'
import { KpiCard } from '../../components/ui/KpiCard'
import './kpiCards.css'

interface KpiCardsProps {
  kpis: KpiBlock
}

function fmtPct(v: number | null, digits = 1): string {
  if (v == null) return '—'
  return `${(v * 100).toFixed(digits)}%`
}

function fmtNum(v: number | null, digits = 2): string {
  if (v == null) return '—'
  return v.toFixed(digits)
}

function fmtInt(v: number | null): string {
  if (v == null) return '—'
  return Math.round(v).toString()
}

function toneFrom(v: number | null): 'pos' | 'neg' | 'neutral' {
  if (v == null) return 'neutral'
  if (v > 0) return 'pos'
  if (v < 0) return 'neg'
  return 'neutral'
}

export function KpiCards({ kpis }: KpiCardsProps) {
  return (
    <div className="kpi-cards">
      <KpiCard label="Sharpe" value={fmtNum(kpis.sharpe)} tone={toneFrom(kpis.sharpe)} />
      <KpiCard label="Sortino" value={fmtNum(kpis.sortino)} tone={toneFrom(kpis.sortino)} />
      <KpiCard label="CAGR" value={fmtPct(kpis.cagr)} tone={toneFrom(kpis.cagr)} />
      <KpiCard label="Volatility" value={fmtPct(kpis.volatility)} tone="neutral" />
      <KpiCard label="Max DD" value={fmtPct(kpis.max_drawdown)} tone={toneFrom(kpis.max_drawdown)} />
      <KpiCard label="Calmar" value={fmtNum(kpis.calmar)} tone={toneFrom(kpis.calmar)} />
      <KpiCard label="Win Rate" value={fmtPct(kpis.win_rate)} tone="neutral" />
      <KpiCard label="Profit Factor" value={fmtNum(kpis.profit_factor)} tone="neutral" />
      <KpiCard label="Turnover" value={fmtNum(kpis.turnover)} tone="neutral" />
      <KpiCard label="Trades" value={fmtInt(kpis.total_trades)} tone="neutral" />
      <KpiCard label="Avg Duration" value={kpis.avg_duration_days == null ? '—' : `${kpis.avg_duration_days.toFixed(1)}d`} tone="neutral" />
    </div>
  )
}
