import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'

import { getTearsheet } from '../../api/runs'
import { Badge } from '../../components/ui/Badge'
import { VerificationBadge } from '../../components/ui/VerificationBadge'
import { DrawdownChart } from './DrawdownChart'
import { EquityCurve } from './EquityCurve'
import { KpiCards } from './KpiCards'
import { MonthlyHeatmap } from './MonthlyHeatmap'
import { PriceChart } from './PriceChart'
import { TradeLedger } from './TradeLedger'
import './tearSheet.css'

function formatDate(tsMs: number): string {
  return new Date(tsMs).toISOString().slice(0, 10)
}

export default function TearSheet() {
  const { id } = useParams<{ id: string }>()
  const runId = id ?? ''

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['tearsheet', runId],
    queryFn: () => getTearsheet(runId),
    enabled: runId.length > 0,
  })

  if (!runId) {
    return (
      <div className="tear-sheet__state tear-sheet__state--error">
        <span>No run id in the URL.</span>
        <Link to="/">Back to Command Center</Link>
      </div>
    )
  }

  if (isLoading) {
    return <div className="tear-sheet__state">Loading tear sheet…</div>
  }

  if (isError) {
    return (
      <div className="tear-sheet__state tear-sheet__state--error">
        <span>Failed to load tear sheet: {String(error)}</span>
        <div className="tear-sheet__actions">
          <button onClick={() => refetch()} type="button">Retry</button>
          <Link to="/">Back to Command Center</Link>
        </div>
      </div>
    )
  }

  if (!data) {
    return <div className="tear-sheet__state">No data.</div>
  }

  const { run } = data

  return (
    <div className="tear-sheet">
      <header className="tear-sheet__header">
        <div className="tear-sheet__header-row">
          <Link to="/" className="tear-sheet__back">← Back</Link>
          <h1 className="tear-sheet__name">{run.name}</h1>
          <Badge status={run.status} />
          <VerificationBadge verification={data.verification} />
        </div>
        <div className="tear-sheet__meta">
          <span>{run.universe.join(' · ')}</span>
          <span className="tear-sheet__meta-sep">·</span>
          <span>
            {formatDate(run.start_ts)} → {formatDate(run.end_ts)}
          </span>
          {run.git_sha ? (
            <>
              <span className="tear-sheet__meta-sep">·</span>
              <span className="tear-sheet__meta-mono">
                git {run.git_sha.slice(0, 7)}
                {run.git_dirty ? ' (dirty)' : ''}
              </span>
            </>
          ) : null}
        </div>
      </header>

      <section className="tear-sheet__section">
        <h2 className="tear-sheet__section-heading">KPIs</h2>
        <KpiCards kpis={data.kpis} />
      </section>

      <section className="tear-sheet__section">
        <h2 className="tear-sheet__section-heading">Price + Fills</h2>
        <PriceChart data={data.price} markers={data.markers} />
      </section>

      <section className="tear-sheet__grid-2">
        <div className="tear-sheet__section">
          <h2 className="tear-sheet__section-heading">Equity</h2>
          <EquityCurve data={data.equity} />
        </div>
        <div className="tear-sheet__section">
          <h2 className="tear-sheet__section-heading">Underwater</h2>
          <DrawdownChart data={data.drawdown} />
        </div>
      </section>

      <section className="tear-sheet__section">
        <h2 className="tear-sheet__section-heading">Monthly Returns</h2>
        <MonthlyHeatmap data={data.monthly_returns} />
      </section>

      <section className="tear-sheet__section">
        <h2 className="tear-sheet__section-heading">Trade Ledger</h2>
        <TradeLedger runId={data.run.run_id} />
      </section>
    </div>
  )
}
