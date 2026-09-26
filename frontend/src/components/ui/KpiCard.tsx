import './kpiCard.css'

interface KpiCardProps {
  label: string
  value: string
  tone?: 'pos' | 'neg' | 'neutral'
}

export function KpiCard({ label, value, tone = 'neutral' }: KpiCardProps) {
  return (
    <div className="kpi-card">
      <div className="kpi-card__label">{label}</div>
      <div className={`kpi-card__value kpi-card__value--${tone}`}>{value}</div>
    </div>
  )
}
