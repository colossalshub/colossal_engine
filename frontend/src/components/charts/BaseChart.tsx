import {
  createChart,
  CrosshairMode,
  LineStyle,
  type ChartOptions,
  type DeepPartial,
  type IChartApi,
  type ISeriesApi,
  type MouseEventParams,
  type SeriesType,
  type Time,
} from 'lightweight-charts'
import { useEffect, useRef, useState } from 'react'
import './baseChart.css'

export interface TooltipRow {
  label: string
  value: string
}

export interface TooltipPayload {
  time: Time
  rows: TooltipRow[]
}

interface BaseChartProps {
  height: number
  createSeries: (chart: IChartApi) => ISeriesApi<SeriesType> | ISeriesApi<SeriesType>[]
  buildTooltip?: (
    params: MouseEventParams,
    series: ISeriesApi<SeriesType>[],
  ) => TooltipPayload | null
  onReady?: (chart: IChartApi, series: ISeriesApi<SeriesType>[]) => void
}

interface TooltipState {
  payload: TooltipPayload
  left: number
  top: number
}

const TOOLTIP_OFFSET_PX = 12
const TOOLTIP_FALLBACK_WIDTH_PX = 120

const CHART_OPTIONS: DeepPartial<ChartOptions> = {
  layout: {
    background: { color: '#000000' },
    textColor: '#9ca3af',
    fontSize: 11,
    fontFamily: 'Inter, sans-serif',
  },
  grid: {
    vertLines: { color: '#262626' },
    horzLines: { color: '#262626' },
  },
  rightPriceScale: { borderColor: '#262626' },
  timeScale: {
    borderColor: '#262626',
    timeVisible: true,
    secondsVisible: false,
  },
  crosshair: {
    mode: CrosshairMode.Magnet,
    vertLine: { color: '#6b7280', style: LineStyle.LargeDashed },
    horzLine: { color: '#6b7280', style: LineStyle.LargeDashed },
  },
  handleScroll: {
    mouseWheel: false,
    pressedMouseMove: true,
    horzTouchDrag: false,
    vertTouchDrag: false,
  },
  handleScale: {
    mouseWheel: false,
    pinch: true,
    axisPressedMouseMove: true,
    axisDoubleClickReset: true,
  },
}

/**
 * lightweight-charts lifecycle wrapper with an HTML crosshair tooltip.
 *
 * `createSeries` and `onReady` run once, on mount. Series data must use
 * `Time` in seconds: convert epoch-ms `ts` with `(ts / 1000) as UTCTimestamp`.
 *
 * `params.seriesData` values are typed as the union
 * `BarData | LineData | HistogramData | CustomData`; LWC does not narrow it by
 * series type, so `buildTooltip` callers must cast the value they read to the
 * concrete data type of their series, e.g.
 * `params.seriesData.get(candles) as CandlestickData<Time> | undefined`.
 */
export function BaseChart({ height, createSeries, buildTooltip, onReady }: BaseChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const buildTooltipRef = useRef(buildTooltip)
  const [tooltip, setTooltip] = useState<TooltipState | null>(null)

  useEffect(() => {
    buildTooltipRef.current = buildTooltip
  }, [buildTooltip])

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const chart = createChart(container, {
      ...CHART_OPTIONS,
      width: container.clientWidth,
      height: container.clientHeight,
    })
    chartRef.current = chart

    const created = createSeries(chart)
    const series = Array.isArray(created) ? created : [created]

    const handleCrosshairMove = (params: MouseEventParams) => {
      const build = buildTooltipRef.current
      if (!build || params.point === undefined || params.time === undefined) {
        setTooltip(null)
        return
      }
      const payload = build(params, series)
      if (!payload) {
        setTooltip(null)
        return
      }
      const tooltipWidth = tooltipRef.current?.offsetWidth || TOOLTIP_FALLBACK_WIDTH_PX
      const { x, y } = params.point
      let left = x + TOOLTIP_OFFSET_PX
      if (left + tooltipWidth > container.clientWidth) {
        left = x - TOOLTIP_OFFSET_PX - tooltipWidth
      }
      setTooltip({ payload, left, top: y + TOOLTIP_OFFSET_PX })
    }
    chart.subscribeCrosshairMove(handleCrosshairMove)

    const resizeObserver = new ResizeObserver(() => {
      chart.applyOptions({ width: container.clientWidth, height: container.clientHeight })
    })
    resizeObserver.observe(container)

    onReady?.(chart, series)

    return () => {
      resizeObserver.disconnect()
      chart.unsubscribeCrosshairMove(handleCrosshairMove)
      chart.remove()
      chartRef.current = null
    }
    // oxlint-disable-next-line react-hooks/exhaustive-deps -- chart is created once per mount; factories are read at mount only
  }, [])

  return (
    <div className="base-chart" style={{ height }}>
      <div ref={containerRef} className="base-chart__container" />
      {tooltip ? (
        <div
          ref={tooltipRef}
          className="base-chart__tooltip"
          style={{ left: tooltip.left, top: tooltip.top }}
        >
          {tooltip.payload.rows.map((row) => (
            <div key={row.label} className="base-chart__tooltip-row">
              <span className="base-chart__tooltip-label">{row.label}</span>
              <span className="base-chart__tooltip-value">{row.value}</span>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  )
}
