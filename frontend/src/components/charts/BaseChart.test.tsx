import { act, render, screen } from '@testing-library/react'
import type {
  Coordinate,
  IChartApi,
  ISeriesApi,
  MouseEventParams,
  SeriesType,
  UTCTimestamp,
} from 'lightweight-charts'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { BaseChart, type TooltipPayload } from './BaseChart'

const lwc = vi.hoisted(() => {
  const state: { handler: ((params: MouseEventParams) => void) | null } = { handler: null }
  const chart = {
    addSeries: vi.fn(),
    subscribeCrosshairMove: vi.fn((handler: (params: MouseEventParams) => void) => {
      state.handler = handler
    }),
    unsubscribeCrosshairMove: vi.fn(),
    remove: vi.fn(),
    applyOptions: vi.fn(),
    resize: vi.fn(),
  }
  return { state, chart, createChart: vi.fn(() => chart) }
})

vi.mock('lightweight-charts', () => ({
  createChart: lwc.createChart,
  CrosshairMode: { Normal: 0, Magnet: 1, Hidden: 2, MagnetOHLC: 3 },
  LineStyle: { Solid: 0, Dotted: 1, Dashed: 2, LargeDashed: 3, SparseDotted: 4 },
}))

// The stub is only passed through BaseChart as an opaque handle, never called.
const fakeSeries = {} as ISeriesApi<SeriesType>
const TIME = 1_700_000_000 as UTCTimestamp

function buildTooltip(): TooltipPayload {
  return { time: TIME, rows: [{ label: 'Close', value: '101.50' }] }
}

function moveCrosshair(params: Partial<MouseEventParams>) {
  act(() => {
    lwc.state.handler?.({ seriesData: new Map(), ...params })
  })
}

function point(x: number, y: number) {
  return { x: x as Coordinate, y: y as Coordinate }
}

function renderChart(props: Partial<Parameters<typeof BaseChart>[0]> = {}) {
  const createSeries = vi.fn((_chart: IChartApi) => fakeSeries)
  const utils = render(
    <BaseChart height={300} createSeries={createSeries} buildTooltip={buildTooltip} {...props} />,
  )
  return { ...utils, createSeries }
}

function tooltipEl(container: HTMLElement) {
  return container.querySelector<HTMLElement>('.base-chart__tooltip')
}

describe('BaseChart', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    lwc.state.handler = null
  })

  it('renders the container without crashing', () => {
    const { container } = renderChart()
    const root = container.querySelector<HTMLElement>('.base-chart')
    expect(root).toBeInTheDocument()
    expect(root?.style.height).toBe('300px')
    expect(container.querySelector('.base-chart__container')).toBeInTheDocument()
  })

  it('creates the chart with the magnet crosshair on the container element', () => {
    const { container } = renderChart()
    expect(lwc.createChart).toHaveBeenCalledTimes(1)
    const [target, options] = lwc.createChart.mock.calls[0] as unknown as [
      HTMLElement,
      { crosshair: { mode: number } },
    ]
    expect(target).toBe(container.querySelector('.base-chart__container'))
    expect(options.crosshair.mode).toBe(1)
  })

  it('calls createSeries once after mount with the chart instance', () => {
    const { createSeries } = renderChart()
    expect(createSeries).toHaveBeenCalledTimes(1)
    expect(createSeries).toHaveBeenCalledWith(lwc.chart)
  })

  it('passes the chart and series array to onReady', () => {
    const onReady = vi.fn()
    renderChart({ onReady })
    expect(onReady).toHaveBeenCalledTimes(1)
    expect(onReady).toHaveBeenCalledWith(lwc.chart, [fakeSeries])
  })

  it('unsubscribes the crosshair handler and then removes the chart on unmount', () => {
    const { unmount } = renderChart()
    const handler = lwc.state.handler
    unmount()
    expect(lwc.chart.unsubscribeCrosshairMove).toHaveBeenCalledWith(handler)
    expect(lwc.chart.remove).toHaveBeenCalledTimes(1)
    const unsubscribeOrder = lwc.chart.unsubscribeCrosshairMove.mock.invocationCallOrder[0]
    const removeOrder = lwc.chart.remove.mock.invocationCallOrder[0]
    expect(unsubscribeOrder).toBeLessThan(removeOrder)
  })

  it('renders the tooltip when a crosshair event fires', () => {
    const { container } = renderChart()
    expect(tooltipEl(container)).toBeNull()
    moveCrosshair({ time: TIME, point: point(100, 50) })
    expect(screen.getByText('Close')).toBeInTheDocument()
    expect(screen.getByText('101.50')).toBeInTheDocument()
  })

  it('passes the created series to buildTooltip', () => {
    const spy = vi.fn(buildTooltip)
    renderChart({ buildTooltip: spy })
    moveCrosshair({ time: TIME, point: point(100, 50) })
    expect(spy).toHaveBeenCalledWith(expect.objectContaining({ time: TIME }), [fakeSeries])
  })

  it('hides the tooltip when the crosshair leaves the chart', () => {
    const { container } = renderChart()
    moveCrosshair({ time: TIME, point: point(100, 50) })
    expect(tooltipEl(container)).not.toBeNull()
    moveCrosshair({ time: TIME, point: undefined })
    expect(tooltipEl(container)).toBeNull()
  })

  it('hides the tooltip when the crosshair is outside the data range', () => {
    const { container } = renderChart()
    moveCrosshair({ time: TIME, point: point(100, 50) })
    moveCrosshair({ time: undefined, point: point(100, 50) })
    expect(tooltipEl(container)).toBeNull()
  })

  it('renders no tooltip when buildTooltip returns null', () => {
    const { container } = renderChart({ buildTooltip: () => null })
    moveCrosshair({ time: TIME, point: point(100, 50) })
    expect(tooltipEl(container)).toBeNull()
  })

  it('positions the tooltip right of the cursor and flips left near the right edge', () => {
    const { container } = renderChart()
    const chartContainer = container.querySelector('.base-chart__container')
    Object.defineProperty(chartContainer, 'clientWidth', { value: 800 })

    moveCrosshair({ time: TIME, point: point(100, 50) })
    expect(tooltipEl(container)?.style.left).toBe('112px')
    expect(tooltipEl(container)?.style.top).toBe('62px')

    moveCrosshair({ time: TIME, point: point(750, 50) })
    expect(tooltipEl(container)?.style.left).toBe('618px')
  })
})
