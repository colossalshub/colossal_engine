import { useState } from 'react'

import type { KpiBlock } from '../../api/types'
import { KpiCard } from '../../components/ui/KpiCard'
import './kpiCards.css'

interface KpiCardsProps {
  kpis: KpiBlock
}

interface KpiGroup {
  id: 'returns' | 'risk' | 'trading' | 'portfolio'
  label: string
}

const GROUPS: KpiGroup[] = [
  { id: 'returns', label: 'Returns' },
  { id: 'risk', label: 'Risk' },
  { id: 'trading', label: 'Trading' },
  { id: 'portfolio', label: 'Portfolio' },
]

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

function groupCards(group: KpiGroup['id'], kpis: KpiBlock) {
  switch (group) {
    case 'returns':
      return <KpiCard label="CAGR" value={fmtPct(kpis.cagr)} tone={toneFrom(kpis.cagr)} />
    case 'risk':
      return (
        <>
          <KpiCard label="Sharpe" value={fmtNum(kpis.sharpe)} tone={toneFrom(kpis.sharpe)} />
          <KpiCard label="Sortino" value={fmtNum(kpis.sortino)} tone={toneFrom(kpis.sortino)} />
          <KpiCard label="Volatility" value={fmtPct(kpis.volatility)} tone="neutral" />
          <KpiCard label="Max DD" value={fmtPct(kpis.max_drawdown)} tone={toneFrom(kpis.max_drawdown)} />
          <KpiCard label="Calmar" value={fmtNum(kpis.calmar)} tone={toneFrom(kpis.calmar)} />
        </>
      )
    case 'trading':
      return (
        <>
          <KpiCard label="Win Rate" value={fmtPct(kpis.win_rate)} tone="neutral" />
          <KpiCard label="Profit Factor" value={fmtNum(kpis.profit_factor)} tone="neutral" />
          <KpiCard label="Trades" value={fmtInt(kpis.total_trades)} tone="neutral" />
          {kpis.avg_duration_days != null ? (
            <KpiCard
              label="Avg Duration"
              value={`${kpis.avg_duration_days.toFixed(1)}d`}
              tone="neutral"
            />
          ) : null}
        </>
      )
    case 'portfolio':
      return <KpiCard label="Turnover" value={fmtNum(kpis.turnover)} tone="neutral" />
  }
}

export function KpiCards({ kpis }: KpiCardsProps) {
  const [open, setOpen] = useState<KpiGroup['id']>('returns')

  return (
    <div className="kpi-groups">
      <div className="kpi-groups__tabs" role="tablist" aria-label="KPI groups">
        {GROUPS.map((group) => {
          const selected = group.id === open
          return (
            <button
              key={group.id}
              type="button"
              role="tab"
              id={`kpi-group-${group.id}`}
              className={
                selected ? 'kpi-groups__tab kpi-groups__tab--active' : 'kpi-groups__tab'
              }
              aria-selected={selected}
              aria-controls="kpi-group-panel"
              onClick={() => setOpen(group.id)}
            >
              {group.label}
            </button>
          )
        })}
      </div>
      <div
        id="kpi-group-panel"
        role="tabpanel"
        aria-labelledby={`kpi-group-${open}`}
        className="kpi-cards"
      >
        {groupCards(open, kpis)}
      </div>
    </div>
  )
}
