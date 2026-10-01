import { useQuery } from '@tanstack/react-query'
import { Link, Outlet, useParams } from 'react-router-dom'

import { getTearsheet } from '../../api/runs'
import type { RunStatus, TearSheet as TearSheetData } from '../../api/types'
import { EmptyState } from '../../components/ui/EmptyState'
import { ErrorDisplay } from '../../components/ui/ErrorDisplay'
import { ExperimentHeader } from './ExperimentHeader'
import { TearSheetNav } from './TearSheetNav'
import './tearSheet.css'

export interface TearSheetContext {
  data: TearSheetData
  runId: string
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
      <ExperimentHeader
        run={run}
        params={data.params}
        verification={data.verification}
      />

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
