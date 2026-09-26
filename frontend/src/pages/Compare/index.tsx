import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'

import { getTearsheet } from '../../api/runs'
import { KpiCards } from '../TearSheet/KpiCards'
import './compare.css'

export default function Compare() {
  const [params] = useSearchParams()
  const idsParam = params.get('ids') ?? ''
  const runIds = idsParam.split(',').map((s) => s.trim()).filter(Boolean)

  const queries = useQuery({
    queryKey: ['compare', runIds],
    queryFn: async () => {
      const results = await Promise.all(runIds.map((id) => getTearsheet(id)))
      return results
    },
    enabled: runIds.length >= 2,
  })

  if (runIds.length < 2) {
    return (
      <div className="compare">
        <div className="compare__state">
          Select at least 2 runs to compare. <Link to="/">Back</Link>
        </div>
      </div>
    )
  }

  if (queries.isLoading) {
    return <div className="compare__state">Loading comparison…</div>
  }

  if (queries.isError) {
    return (
      <div className="compare__state compare__state--error">
        Failed to load comparison: {String(queries.error)}
        <Link to="/">Back</Link>
      </div>
    )
  }

  const sheets = queries.data ?? []

  return (
    <div className="compare">
      <header className="compare__header">
        <Link to="/" className="compare__back">← Back</Link>
        <h1 className="compare__title">Compare {sheets.length} runs</h1>
      </header>
      <div
        className="compare__grid"
        style={{ gridTemplateColumns: `repeat(${sheets.length}, minmax(0, 1fr))` }}
      >
        {sheets.map((sheet) => (
          <div key={sheet.run.run_id} className="compare__column">
            <div className="compare__run-name">{sheet.run.name}</div>
            <div className="compare__run-meta">
              {sheet.run.universe.join(' · ')} ·{' '}
              {new Date(sheet.run.start_ts).toISOString().slice(0, 10)} →{' '}
              {new Date(sheet.run.end_ts).toISOString().slice(0, 10)}
            </div>
            <KpiCards kpis={sheet.kpis} />
          </div>
        ))}
      </div>
    </div>
  )
}
