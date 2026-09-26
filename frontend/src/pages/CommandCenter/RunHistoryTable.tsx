import { useQuery } from '@tanstack/react-query'
import { AgGridReact } from 'ag-grid-react'
import type { ColDef, RowClickedEvent } from 'ag-grid-community'
import { useCallback, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'

import { listRuns } from '../../api/runs'
import type { RunSummary } from '../../api/types'
import '../../components/grid/agGridTheme.css'

const colDefs: ColDef<RunSummary>[] = [
  { field: 'name', headerName: 'Name', flex: 2, minWidth: 200 },
  { field: 'strategy', headerName: 'Strategy', flex: 1, minWidth: 120 },
  {
    field: 'created_at',
    headerName: 'Created',
    flex: 1,
    minWidth: 140,
    valueFormatter: (p) =>
      p.value ? new Date(p.value).toISOString().slice(0, 10) : '',
  },
  {
    field: 'sharpe',
    headerName: 'Sharpe',
    type: 'numericColumn',
    flex: 1,
    minWidth: 90,
    valueFormatter: (p) =>
      p.value == null ? '—' : p.value.toFixed(2),
  },
  {
    field: 'cagr',
    headerName: 'CAGR',
    type: 'numericColumn',
    flex: 1,
    minWidth: 90,
    valueFormatter: (p) =>
      p.value == null ? '—' : `${(p.value * 100).toFixed(1)}%`,
  },
  {
    field: 'max_drawdown',
    headerName: 'Max DD',
    type: 'numericColumn',
    flex: 1,
    minWidth: 90,
    valueFormatter: (p) =>
      p.value == null ? '—' : `${(p.value * 100).toFixed(1)}%`,
  },
  {
    field: 'status',
    headerName: 'Status',
    flex: 1,
    minWidth: 100,
  },
]

export function RunHistoryTable() {
  const navigate = useNavigate()

  const onRowClicked = useCallback(
    (event: RowClickedEvent<RunSummary>) => {
      const runId = event.data?.run_id
      if (runId) {
        navigate(`/runs/${runId}`)
      }
    },
    [navigate],
  )

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['runs'],
    queryFn: () => listRuns(),
    refetchInterval: (query) => {
      const data = query.state.data
      if (!data) return false
      const hasActive = data.items.some(
        (r) => r.status === 'queued' || r.status === 'running',
      )
      return hasActive ? 2000 : false
    },
  })

  const defaultColDef = useMemo<ColDef>(
    () => ({
      sortable: true,
      resizable: true,
      suppressMovable: true,
    }),
    [],
  )

  if (isLoading) {
    return <div className="run-history__state">Loading runs…</div>
  }

  if (isError) {
    return (
      <div className="run-history__state run-history__state--error">
        <span>Failed to load runs: {String(error)}</span>
        <button onClick={() => refetch()} type="button">
          Retry
        </button>
      </div>
    )
  }

  const rows = data?.items ?? []

  if (rows.length === 0) {
    return (
      <div className="run-history__state">
        No backtest runs yet.
      </div>
    )
  }

  return (
    <div className="ag-theme-quartz-dark run-history__grid">
      <AgGridReact<RunSummary>
        rowData={rows}
        columnDefs={colDefs}
        defaultColDef={defaultColDef}
        onRowClicked={onRowClicked}
        rowStyle={{ cursor: 'pointer' }}
        suppressCellFocus
      />
    </div>
  )
}
