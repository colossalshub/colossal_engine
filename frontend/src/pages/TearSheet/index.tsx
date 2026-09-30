import { useQuery } from '@tanstack/react-query'
import { Link, Outlet, useParams } from 'react-router-dom'

import { getTearsheet } from '../../api/runs'
import type { RunStatus, TearSheet as TearSheetData } from '../../api/types'
import { Badge } from '../../components/ui/Badge'
import { EmptyState } from '../../components/ui/EmptyState'
import { ErrorDisplay } from '../../components/ui/ErrorDisplay'
import { VerificationBadge } from '../../components/ui/VerificationBadge'
import { TearSheetNav } from './TearSheetNav'
import './tearSheet.css'

export interface TearSheetContext {
  data: TearSheetData
  runId: string
}

function formatDate(tsMs: number): string {
  return new Date(tsMs).toISOString().slice(0, 10)
}

function emptyStateForStatus(status: RunStatus): { icon: string; message: string } {
  switch (status) {
    case 'queued':
      return { icon: '⏳', message: 'Backtest in progress…' }
    case 'running':
      return { icon: '⏳', message: 'Backtest in progress…' }
    case 'failed':
      return { icon: '⚠', message: 'This backtest failed.' }
    case 'archived':
      return { icon: '📦', message: 'Artifacts expired.' }
    case 'done':
      return { icon: '', message: '' }
  }
}

export default function TearSheetLayout() {
  const { id } = useParams<{ id: string }>()
  const runId = id ?? ''

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['tearsheet', runId],
    queryFn: () => getTearsheet(runId),
    enabled: runId.length > 0,
    refetchInterval: (query) => {
      const sheet = query.state.data
      if (!sheet) return false
      const status = sheet.run.status
      if (status === 'queued' || status === 'running') return 2000
      return false
    },
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
      <div className="tear-sheet__error-wrap">
        <ErrorDisplay
          message={`Failed to load tear sheet: ${String(error)}`}
          onRetry={() => refetch()}
        />
        <Link to="/" className="tear-sheet__back">← Back to Command Center</Link>
      </div>
    )
  }

  if (!data) {
    return <div className="tear-sheet__state">No data.</div>
  }

  const { run } = data
  const showWorkspace = run.status === 'done'

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
          <span>{run.universe[0]}</span>
          {run.universe.length > 1 ? (
            <>
              <span className="tear-sheet__meta-sep">·</span>
              <span className="tear-sheet__meta-mono">
                only first symbol executed
              </span>
            </>
          ) : null}
          <span className="tear-sheet__meta-sep">·</span>
          <span>
            {formatDate(run.start_ts)} → {formatDate(run.end_ts)}
          </span>
          {typeof data.params.maker_fee === 'string' ? (
            <>
              <span className="tear-sheet__meta-sep">·</span>
              <span className="tear-sheet__meta-mono">
                fees {((parseFloat(data.params.maker_fee) || 0) * 100).toFixed(2)}%
              </span>
            </>
          ) : null}
          {typeof data.params.benchmark_symbol === 'string' &&
          data.params.benchmark_symbol ? (
            <>
              <span className="tear-sheet__meta-sep">·</span>
              <span className="tear-sheet__meta-mono">
                benchmark {data.params.benchmark_symbol}
              </span>
            </>
          ) : null}
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

      {showWorkspace ? (
        <div className="tear-sheet__body">
          <TearSheetNav />
          <div className="tear-sheet__content">
            <Outlet context={{ data, runId } satisfies TearSheetContext} />
          </div>
        </div>
      ) : (
        <section className="tear-sheet__section">
          <EmptyState
            icon={emptyStateForStatus(run.status).icon}
            message={emptyStateForStatus(run.status).message}
          />
        </section>
      )}
    </div>
  )
}
