import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'

import { getCoverage } from '../../api/data'
import type { CoverageCell, CoverageRow } from '../../api/types'
import { ErrorDisplay } from '../../components/ui/ErrorDisplay'
import './coverageHeatmap.css'

const MONTH_LABELS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
] as const

const CELL = 24
const GAP = 2
const ROW_LABEL_W = 140
const HEADER_H = 20

const COLOR_MISSING = 'rgba(107, 114, 128, 0.15)'
const COLOR_HIGH = 'rgba(34, 197, 94, 0.90)'
const COLOR_MID = 'rgba(245, 158, 11, 0.85)'
const COLOR_LOW = 'rgba(239, 68, 68, 0.60)'

interface YearAggregate {
  bars: number
  expected: number
  coverage: number
  cells: CoverageCell[]
}

type HoverState = {
  symbol: string
  timeframe: string
  year: number
  bars: number
  expected: number
  cells: CoverageCell[]
  x: number
  y: number
}

function aggregateByYear(cells: CoverageCell[]): Map<number, YearAggregate> {
  const partial = new Map<number, { bars: number; expected: number; cells: CoverageCell[] }>()
  for (const cell of cells) {
    let agg = partial.get(cell.year)
    if (!agg) {
      agg = { bars: 0, expected: 0, cells: [] }
      partial.set(cell.year, agg)
    }
    agg.bars += cell.bars
    agg.expected += cell.expected
    agg.cells.push(cell)
  }
  const result = new Map<number, YearAggregate>()
  for (const [year, agg] of partial) {
    const coverage =
      agg.expected > 0 ? Math.min(1.0, agg.bars / agg.expected) : 0
    agg.cells.sort((a, b) => a.month - b.month)
    result.set(year, { ...agg, coverage })
  }
  return result
}

function colorForCoverage(missing: boolean, coverage: number): string {
  if (missing) return COLOR_MISSING
  if (coverage >= 0.99) return COLOR_HIGH
  if (coverage >= 0.75) return COLOR_MID
  return COLOR_LOW
}

function rowLabel(row: CoverageRow): string {
  return `${row.symbol}  ${row.timeframe}`
}

function pctBars(bars: number, expected: number): string {
  if (expected <= 0) return '0.0%'
  return `${((bars / expected) * 100).toFixed(1)}%`
}

function monthBreakdown(cells: CoverageCell[]): string {
  return cells
    .map((c) => `${MONTH_LABELS[c.month - 1]} ${c.bars}/${c.expected}`)
    .join('  ')
}

const LEGEND_ITEMS = [
  { label: '>99%', color: COLOR_HIGH },
  { label: '75–99%', color: COLOR_MID },
  { label: '<75%', color: COLOR_LOW },
  { label: 'missing', color: COLOR_MISSING },
] as const

export function CoverageHeatmap() {
  const [hover, setHover] = useState<HoverState | null>(null)

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['coverage'],
    queryFn: getCoverage,
  })

  const rows = data?.rows ?? []

  const years = useMemo(() => {
    const set = new Set<number>()
    for (const row of rows) {
      for (const cell of row.cells) {
        set.add(cell.year)
      }
    }
    return [...set].sort((a, b) => a - b)
  }, [rows])

  const yearMaps = useMemo(
    () => rows.map((row) => aggregateByYear(row.cells)),
    [rows],
  )

  if (isLoading) {
    return <div className="coverage-heatmap__state">Loading coverage…</div>
  }

  if (isError) {
    return (
      <ErrorDisplay
        message={`Failed to load coverage: ${String(error)}`}
        onRetry={() => refetch()}
      />
    )
  }

  if (rows.length === 0) {
    return (
      <div className="coverage-heatmap__empty">
        No coverage data. Ingest bars to populate this view.
      </div>
    )
  }

  const width = ROW_LABEL_W + years.length * (CELL + GAP)
  const height = HEADER_H + rows.length * (CELL + GAP)

  return (
    <div className="coverage-heatmap">
      <div className="coverage-heatmap__svg-wrap">
        <svg
          width={width}
          height={height}
          role="img"
          aria-label="Data coverage heatmap"
        >
          {years.map((year, i) => (
            <text
              key={year}
              x={ROW_LABEL_W + i * (CELL + GAP) + CELL / 2}
              y={HEADER_H - 6}
              textAnchor="middle"
              className="coverage-heatmap__header-label"
            >
              {year}
            </text>
          ))}

          {rows.map((row, rowIdx) => {
            const y = HEADER_H + rowIdx * (CELL + GAP)
            const byYear = yearMaps[rowIdx]
            return (
              <g key={`${row.venue}-${row.symbol}-${row.timeframe}`}>
                <text
                  x={ROW_LABEL_W - 8}
                  y={y + CELL / 2 + 4}
                  textAnchor="end"
                  className="coverage-heatmap__row-label"
                >
                  {rowLabel(row)}
                </text>
                {years.map((year, colIdx) => {
                  const agg = byYear.get(year)
                  const missing = agg === undefined
                  const x = ROW_LABEL_W + colIdx * (CELL + GAP)
                  const fill = colorForCoverage(missing, agg?.coverage ?? 0)
                  return (
                    <rect
                      key={year}
                      x={x}
                      y={y}
                      width={CELL}
                      height={CELL}
                      fill={fill}
                      rx={2}
                      className="coverage-heatmap__cell"
                      data-testid={`cell-${rowIdx}-${year}`}
                      onMouseEnter={() => {
                        if (missing || !agg) {
                          setHover(null)
                          return
                        }
                        setHover({
                          symbol: row.symbol,
                          timeframe: row.timeframe,
                          year,
                          bars: agg.bars,
                          expected: agg.expected,
                          cells: agg.cells,
                          x: x + CELL / 2,
                          y,
                        })
                      }}
                      onMouseLeave={() => setHover(null)}
                    />
                  )
                })}
              </g>
            )
          })}
        </svg>

        {hover ? (
          <div
            className="coverage-heatmap__tooltip"
            style={{ left: hover.x, top: hover.y + CELL + 8 }}
            role="tooltip"
          >
            <span className="coverage-heatmap__tooltip-label">
              {hover.symbol} · {hover.timeframe} · {hover.year}
            </span>
            <span className="coverage-heatmap__tooltip-value">
              Bars: {hover.bars} / {hover.expected} ({pctBars(hover.bars, hover.expected)})
            </span>
            <span className="coverage-heatmap__tooltip-months">
              {monthBreakdown(hover.cells)}
            </span>
          </div>
        ) : null}
      </div>

      <div className="coverage-heatmap__legend" aria-hidden="true">
        {LEGEND_ITEMS.map((item) => (
          <span key={item.label} className="coverage-heatmap__legend-item">
            <span
              className="coverage-heatmap__legend-swatch"
              style={{ background: item.color }}
            />
            {item.label}
          </span>
        ))}
      </div>
    </div>
  )
}
