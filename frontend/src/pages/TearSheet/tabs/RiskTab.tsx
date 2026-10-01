import { useOutletContext } from 'react-router-dom'

import { KpiCard } from '../../../components/ui/KpiCard'
import { DrawdownChart } from '../DrawdownChart'
import type { TearSheetContext } from '../index'
import '../kpiCards.css'

function fmtPct(value: number | null): string {
  if (value == null) return '—'
  return `${(value * 100).toFixed(1)}%`
}

function fmtNum(value: number | null): string {
  if (value == null) return '—'
  return value.toFixed(2)
}

function toneFrom(value: number | null): 'pos' | 'neg' | 'neutral' {
  if (value == null) return 'neutral'
  if (value > 0) return 'pos'
  if (value < 0) return 'neg'
  return 'neutral'
}

export default function RiskTab() {
  const { data } = useOutletContext<TearSheetContext>()
  const { kpis } = data

  return (
    <div className="tear-sheet-tab">
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">Risk metrics</h2>
        <div className="kpi-cards">
          <KpiCard label="Sharpe" value={fmtNum(kpis.sharpe)} tone={toneFrom(kpis.sharpe)} />
          <KpiCard label="Sortino" value={fmtNum(kpis.sortino)} tone={toneFrom(kpis.sortino)} />
          <KpiCard label="Volatility" value={fmtPct(kpis.volatility)} tone="neutral" />
          <KpiCard
            label="Max DD"
            value={fmtPct(kpis.max_drawdown)}
            tone={toneFrom(kpis.max_drawdown)}
          />
          <KpiCard label="Calmar" value={fmtNum(kpis.calmar)} tone={toneFrom(kpis.calmar)} />
        </div>
      </section>
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">Underwater</h2>
        <DrawdownChart data={data.drawdown} />
      </section>
    </div>
  )
}
