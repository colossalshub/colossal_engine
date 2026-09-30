import { useQuery } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { Responsive, WidthProvider, type Layout } from 'react-grid-layout/legacy'
import { Link, useParams } from 'react-router-dom'

import { getTearsheet } from '../../api/runs'
import type { RunStatus, TearSheet as TearSheetData } from '../../api/types'
import { Badge } from '../../components/ui/Badge'
import { EmptyState } from '../../components/ui/EmptyState'
import { ErrorDisplay } from '../../components/ui/ErrorDisplay'
import { VerificationBadge } from '../../components/ui/VerificationBadge'
import { DrawdownChart } from './DrawdownChart'
import { EquityCurve } from './EquityCurve'
import { KpiCards } from './KpiCards'
import { MonthlyHeatmap } from './MonthlyHeatmap'
import { PriceChart } from './PriceChart'
import { TradeLedger } from './TradeLedger'
import {
  LAYOUT_SAVE_MS,
  LAYOUT_STORAGE_KEY,
  WIDGET_IDS,
  applyLayoutChange,
  readLayout,
  toggleWidget,
  type TearSheetLayoutConfig,
  type WidgetId,
} from './tearsheetLayout'
import './tearSheet.css'

const TearSheetGrid = WidthProvider(Responsive)

const WIDGET_TITLES: Record<WidgetId, string> = {
  kpis: 'KPIs',
  price: 'Price + Fills',
  equity: 'Equity',
  drawdown: 'Underwater',
  monthly: 'Monthly Returns',
  ledger: 'Trade Ledger',
}

/** Grid-unit floors so a widget cannot shrink below the §9.7 chart defaults. */
const WIDGET_MIN: Record<WidgetId, { minW: number; minH: number }> = {
  kpis: { minW: 4, minH: 4 },
  price: { minW: 6, minH: 11 },
  equity: { minW: 4, minH: 8 },
  drawdown: { minW: 4, minH: 8 },
  monthly: { minW: 6, minH: 4 },
  ledger: { minW: 6, minH: 8 },
}

const CHART_FALLBACK_PX: Partial<Record<WidgetId, number>> = {
  price: 420,
  equity: 280,
  drawdown: 280,
  ledger: 540,
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

function MeasuredSlot({
  fallback,
  children,
}: {
  fallback: number
  children: (height: number) => ReactNode
}) {
  const ref = useRef<HTMLDivElement>(null)
  const [height, setHeight] = useState(fallback)

  useEffect(() => {
    const el = ref.current
    if (!el || typeof ResizeObserver === 'undefined') return
    const apply = () => {
      const next = Math.floor(el.clientHeight)
      if (next > 0) setHeight((prev) => (prev === next ? prev : next))
    }
    apply()
    const observer = new ResizeObserver(apply)
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  return (
    <div ref={ref} className="tear-sheet__widget-slot">
      {children(height)}
    </div>
  )
}

function widgetBody(id: WidgetId, sheet: TearSheetData): ReactNode {
  switch (id) {
    case 'kpis':
      return <KpiCards kpis={sheet.kpis} />
    case 'price':
      return (
        <MeasuredSlot fallback={CHART_FALLBACK_PX.price ?? 420}>
          {(height) => (
            <PriceChart data={sheet.price} markers={sheet.markers} height={height} />
          )}
        </MeasuredSlot>
      )
    case 'equity':
      return (
        <MeasuredSlot fallback={CHART_FALLBACK_PX.equity ?? 280}>
          {(height) => <EquityCurve data={sheet.equity} height={height} />}
        </MeasuredSlot>
      )
    case 'drawdown':
      return (
        <MeasuredSlot fallback={CHART_FALLBACK_PX.drawdown ?? 280}>
          {(height) => <DrawdownChart data={sheet.drawdown} height={height} />}
        </MeasuredSlot>
      )
    case 'monthly':
      return <MonthlyHeatmap data={sheet.monthly_returns} />
    case 'ledger':
      return (
        <MeasuredSlot fallback={CHART_FALLBACK_PX.ledger ?? 540}>
          {(height) => <TradeLedger runId={sheet.run.run_id} height={height} />}
        </MeasuredSlot>
      )
  }
}

function WidgetPicker({
  config,
  onToggle,
}: {
  config: TearSheetLayoutConfig
  onToggle: (id: WidgetId) => void
}) {
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const onPointer = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', onPointer)
    return () => document.removeEventListener('mousedown', onPointer)
  }, [open])

  return (
    <div className="tear-sheet__picker" ref={rootRef}>
      <button
        type="button"
        className="tear-sheet__picker-button"
        aria-expanded={open}
        aria-haspopup="true"
        onClick={() => setOpen((value) => !value)}
      >
        Widgets ▾
      </button>
      {open ? (
        <div className="tear-sheet__picker-menu" role="group" aria-label="Tear sheet widgets">
          {WIDGET_IDS.map((id) => (
            <label key={id} className="tear-sheet__picker-option">
              <input
                type="checkbox"
                checked={config.widgets[id].visible}
                onChange={() => onToggle(id)}
              />
              {WIDGET_TITLES[id]}
            </label>
          ))}
        </div>
      ) : null}
    </div>
  )
}

export default function TearSheet() {
  const { id } = useParams<{ id: string }>()
  const runId = id ?? ''

  const [config, setConfig] = useState<TearSheetLayoutConfig>(() =>
    readLayout(localStorage.getItem(LAYOUT_STORAGE_KEY)),
  )
  const [canSave, setCanSave] = useState(false)

  useEffect(() => {
    setCanSave(true)
  }, [])

  useEffect(() => {
    if (!canSave) return
    const handle = window.setTimeout(() => {
      localStorage.setItem(LAYOUT_STORAGE_KEY, JSON.stringify(config))
    }, LAYOUT_SAVE_MS)
    return () => window.clearTimeout(handle)
  }, [config, canSave])

  const onLayoutChange = useCallback((next: Layout) => {
    setConfig((prev) => applyLayoutChange(prev, next))
  }, [])

  const onToggle = useCallback((widgetId: WidgetId) => {
    setConfig((prev) => toggleWidget(prev, widgetId))
  }, [])

  const rglLayout = useMemo(
    () =>
      WIDGET_IDS.filter((widgetId) => config.widgets[widgetId].visible).map((widgetId) => {
        const geom = config.widgets[widgetId]
        const min = WIDGET_MIN[widgetId]
        return {
          i: widgetId,
          x: geom.x,
          y: geom.y,
          w: geom.w,
          h: geom.h,
          minW: min.minW,
          minH: min.minH,
        }
      }),
    [config],
  )

  const layouts = useMemo(() => ({ lg: rglLayout }), [rglLayout])

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
          {showWorkspace ? (
            <div className="tear-sheet__header-actions">
              <WidgetPicker config={config} onToggle={onToggle} />
            </div>
          ) : null}
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
        <TearSheetGrid
          className="tear-sheet__grid"
          layouts={layouts}
          breakpoints={{ lg: 0 }}
          cols={{ lg: 12 }}
          rowHeight={40}
          margin={[8, 8]}
          containerPadding={[0, 0]}
          draggableHandle=".drag-handle"
          resizeHandles={['se', 'sw', 'ne', 'nw']}
          onLayoutChange={onLayoutChange}
        >
          {WIDGET_IDS.filter((widgetId) => config.widgets[widgetId].visible).map((widgetId) => (
            <div key={widgetId} className="tear-sheet__widget">
              <h2 className="tear-sheet__widget-header drag-handle">{WIDGET_TITLES[widgetId]}</h2>
              <div className="tear-sheet__widget-body">{widgetBody(widgetId, data)}</div>
            </div>
          ))}
        </TearSheetGrid>
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
