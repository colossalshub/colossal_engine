import { useState } from 'react'

import type { MonthlyReturns } from '../../api/types'
import './monthlyHeatmap.css'

interface MonthlyHeatmapProps {
  data: MonthlyReturns[]
}

const MONTH_LABELS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
] as const

const CELL = 28
const GAP = 2
const ROW_LABEL_W = 44
const HEADER_H = 20

type HoverState = {
  year: number
  monthIdx: number
  value: number | null
  x: number
  y: number
}

function colorFor(value: number | null): string {
  if (value == null) return 'rgba(107, 114, 128, 0.15)'
  const abs = Math.abs(value)
  if (value > 0) {
    if (abs < 0.02) return 'rgba(34, 197, 94, 0.30)'
    if (abs < 0.05) return 'rgba(34, 197, 94, 0.60)'
    return 'rgba(34, 197, 94, 0.90)'
  }
  if (abs < 0.02) return 'rgba(239, 68, 68, 0.30)'
  if (abs < 0.05) return 'rgba(239, 68, 68, 0.60)'
  return 'rgba(239, 68, 68, 0.90)'
}

function fmt(value: number | null): string {
  if (value == null) return '—'
  const pct = (value * 100).toFixed(2)
  return value >= 0 ? `+${pct}%` : `${pct}%`
}

export function MonthlyHeatmap({ data }: MonthlyHeatmapProps) {
  const [hover, setHover] = useState<HoverState | null>(null)

  if (data.length === 0) {
    return (
      <div className="monthly-heatmap__empty">No monthly data for this run.</div>
    )
  }

  const years = [...data].sort((a, b) => a.year - b.year)
  const width = ROW_LABEL_W + 12 * (CELL + GAP)
  const height = HEADER_H + years.length * (CELL + GAP)

  return (
    <div className="monthly-heatmap">
      <div className="monthly-heatmap__svg-wrap">
        <svg
          width={width}
          height={height}
          role="img"
          aria-label="Monthly returns heatmap"
        >
          {/* Column headers */}
          {MONTH_LABELS.map((label, i) => (
            <text
              key={label}
              x={ROW_LABEL_W + i * (CELL + GAP) + CELL / 2}
              y={HEADER_H - 6}
              textAnchor="middle"
              className="monthly-heatmap__header-label"
            >
              {label}
            </text>
          ))}

          {/* Year rows */}
          {years.map((row, rowIdx) => {
            const y = HEADER_H + rowIdx * (CELL + GAP)
            return (
              <g key={row.year}>
                <text
                  x={ROW_LABEL_W - 8}
                  y={y + CELL / 2 + 4}
                  textAnchor="end"
                  className="monthly-heatmap__year-label"
                >
                  {row.year}
                </text>
                {row.months.map((value, mIdx) => {
                  const x = ROW_LABEL_W + mIdx * (CELL + GAP)
                  return (
                    <rect
                      key={mIdx}
                      x={x}
                      y={y}
                      width={CELL}
                      height={CELL}
                      fill={colorFor(value)}
                      rx={2}
                      className="monthly-heatmap__cell"
                      data-testid={`cell-${row.year}-${mIdx}`}
                      onMouseEnter={() =>
                        setHover({
                          year: row.year,
                          monthIdx: mIdx,
                          value,
                          x: x + CELL / 2,
                          y,
                        })
                      }
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
            className="monthly-heatmap__tooltip"
            style={{ left: hover.x, top: hover.y - 8 }}
            role="tooltip"
          >
            <span className="monthly-heatmap__tooltip-label">
              {MONTH_LABELS[hover.monthIdx]} {hover.year}
            </span>
            <span className="monthly-heatmap__tooltip-value">
              {fmt(hover.value)}
            </span>
          </div>
        ) : null}
      </div>
    </div>
  )
}
