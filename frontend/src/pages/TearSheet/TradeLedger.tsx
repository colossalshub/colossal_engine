import { useQuery } from '@tanstack/react-query'
import { AgGridReact } from 'ag-grid-react'
import type { ColDef } from 'ag-grid-community'
import { useMemo, useState } from 'react'

import { getTrades } from '../../api/runs'
import type { Trade } from '../../api/types'
import '../../components/grid/agGridTheme.css'
import './tradeLedger.css'

interface TradeLedgerProps {
  runId: string
  pageSize?: number
}

function fmtTs(tsMs: number | null): string {
  if (tsMs == null) return '—'
  return new Date(tsMs).toISOString().slice(0, 16).replace('T', ' ')
}

function fmtNum(v: number | null, digits = 2): string {
  if (v == null) return '—'
  return v.toFixed(digits)
}

function fmtPct(v: number | null): string {
  if (v == null) return '—'
  return `${(v * 100).toFixed(2)}%`
}

const colDefs: ColDef<Trade>[] = [
  { field: 'trade_id', headerName: 'Trade', flex: 2, minWidth: 180 },
  { field: 'symbol', headerName: 'Symbol', flex: 1, minWidth: 120 },
  {
    field: 'side',
    headerName: 'Side',
    width: 80,
  },
  {
    field: 'entry_ts',
    headerName: 'Entry',
    flex: 1,
    minWidth: 140,
    valueFormatter: (p) => fmtTs(p.value),
  },
  {
    field: 'exit_ts',
    headerName: 'Exit',
    flex: 1,
    minWidth: 140,
    valueFormatter: (p) => fmtTs(p.value),
  },
  {
    field: 'entry_px',
    headerName: 'Entry Px',
    type: 'numericColumn',
    flex: 1,
    minWidth: 100,
    valueFormatter: (p) => fmtNum(p.value),
  },
  {
    field: 'exit_px',
    headerName: 'Exit Px',
    type: 'numericColumn',
    flex: 1,
    minWidth: 100,
    valueFormatter: (p) => fmtNum(p.value),
  },
  {
    field: 'qty',
    headerName: 'Qty',
    type: 'numericColumn',
    flex: 1,
    minWidth: 80,
    valueFormatter: (p) => fmtNum(p.value, 4),
  },
  {
    field: 'pnl',
    headerName: 'PnL',
    type: 'numericColumn',
    flex: 1,
    minWidth: 100,
    cellStyle: (p) => {
      if (p.value == null) return null
      if (p.value > 0) return { color: '#22c55e' }
      if (p.value < 0) return { color: '#ef4444' }
      return null
    },
    valueFormatter: (p) => fmtNum(p.value),
  },
  {
    field: 'pnl_pct',
    headerName: 'PnL %',
    type: 'numericColumn',
    flex: 1,
    minWidth: 90,
    cellStyle: (p) => {
      if (p.value == null) return null
      if (p.value > 0) return { color: '#22c55e' }
      if (p.value < 0) return { color: '#ef4444' }
      return null
    },
    valueFormatter: (p) => fmtPct(p.value),
  },
  {
    field: 'fees',
    headerName: 'Fees',
    type: 'numericColumn',
    flex: 1,
    minWidth: 90,
    valueFormatter: (p) => fmtNum(p.value),
  },
  {
    field: 'duration_s',
    headerName: 'Duration',
    type: 'numericColumn',
    flex: 1,
    minWidth: 100,
    valueFormatter: (p) => {
      if (p.value == null || p.value === 0) return '—'
      const days = p.value / 86400
      return days < 1 ? `${(p.value / 3600).toFixed(1)}h` : `${days.toFixed(1)}d`
    },
  },
]

export function TradeLedger({ runId, pageSize = 50 }: TradeLedgerProps) {
  const [page, setPage] = useState(1)

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['trades', runId, page, pageSize],
    queryFn: () => getTrades(runId, { page, page_size: pageSize }),
    enabled: runId.length > 0,
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
    return <div className="trade-ledger__state">Loading trades…</div>
  }

  if (isError) {
    return (
      <div className="trade-ledger__state trade-ledger__state--error">
        <span>Failed to load trades: {String(error)}</span>
        <button onClick={() => refetch()} type="button">
          Retry
        </button>
      </div>
    )
  }

  const trades = data?.items ?? []
  const total = data?.total ?? 0

  if (total === 0) {
    return <div className="trade-ledger__state">No trades generated for this period.</div>
  }

  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const rangeStart = (page - 1) * pageSize + 1
  const rangeEnd = Math.min(page * pageSize, total)

  return (
    <div className="trade-ledger">
      <div className="ag-theme-quartz-dark trade-ledger__grid">
        <AgGridReact<Trade>
          rowData={trades}
          columnDefs={colDefs}
          defaultColDef={defaultColDef}
          suppressCellFocus
          suppressPaginationPanel
        />
      </div>
      <div className="trade-ledger__footer">
        <span className="trade-ledger__range">
          Showing {rangeStart}–{rangeEnd} of {total}
        </span>
        <div className="trade-ledger__pager">
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            ← Prev
          </button>
          <span className="trade-ledger__page-label">
            Page {page} of {totalPages}
          </span>
          <button
            type="button"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  )
}
