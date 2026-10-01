import type { KpiBlock } from '../../api/types'
import { KpiCard } from '../../components/ui/KpiCard'
import './kpiCards.css'

interface TradesSummaryProps {
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

export function TradesSummary({ kpis }: TradesSummaryProps) {
  return (
    <section className="tear-sheet-tab__section">
      <h2 className="tear-sheet-tab__heading">Closed trades</h2>
      <div className="kpi-cards">
        <KpiCard label="Trades" value={fmtInt(kpis.total_trades)} tone="neutral" />
        <KpiCard label="Win Rate" value={fmtPct(kpis.win_rate)} tone="neutral" />
        <KpiCard label="Profit Factor" value={fmtNum(kpis.profit_factor)} tone="neutral" />
        {kpis.avg_duration_days != null ? (
          <KpiCard
            label="Avg Duration"
            value={`${kpis.avg_duration_days.toFixed(1)}d`}
            tone="neutral"
          />
        ) : null}
      </div>
    </section>
  )
}
