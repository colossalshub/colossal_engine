import { render, screen } from '@testing-library/react'
import { CandlestickSeries, createSeriesMarkers } from 'lightweight-charts'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { OHLCV, TradeMarker } from '../../api/types'
import { PriceChart } from './PriceChart'

const setDataSpy = vi.fn()
const addSeriesSpy = vi.fn(() => ({ setData: setDataSpy }))

vi.mock('../../components/charts/BaseChart', () => ({
  BaseChart: ({ createSeries }: { createSeries: (c: unknown) => unknown }) => {
    const fakeChart = { addSeries: addSeriesSpy }
    createSeries(fakeChart)
    return <div data-testid="base-chart-mock" />
  },
}))

// LWC v5 moved series markers to a plugin (`createSeriesMarkers`), not a
// method on the series returned by `addSeries`. Mock only that export;
// keep everything else (CandlestickSeries, types) from the real module.
vi.mock('lightweight-charts', async (importOriginal) => {
  const actual = await importOriginal<typeof import('lightweight-charts')>()
  return {
    ...actual,
    createSeriesMarkers: vi.fn(() => ({
      setMarkers: vi.fn(),
      markers: vi.fn(() => []),
      detach: vi.fn(),
    })),
  }
})

const createSeriesMarkersSpy = vi.mocked(createSeriesMarkers)

const sampleBars: OHLCV[] = [
  { ts: 1704067200000, open: 100, high: 110, low: 95, close: 105, volume: 10 },
  { ts: 1704153600000, open: 105, high: 115, low: 100, close: 112, volume: 12 },
]

beforeEach(() => {
  addSeriesSpy.mockClear()
  setDataSpy.mockClear()
  createSeriesMarkersSpy.mockClear()
})

describe('PriceChart', () => {
  it('renders a BaseChart when data is non-empty', () => {
    render(<PriceChart data={sampleBars} />)
    expect(screen.getByTestId('base-chart-mock')).toBeInTheDocument()
  })

  it('renders the empty state when data is empty', () => {
    render(<PriceChart data={[]} />)
    expect(screen.getByText('No price data for this run.')).toBeInTheDocument()
    expect(screen.queryByTestId('base-chart-mock')).not.toBeInTheDocument()
  })

  it('calls addSeries with CandlestickSeries', () => {
    render(<PriceChart data={sampleBars} />)
    expect(addSeriesSpy).toHaveBeenCalledTimes(1)
    expect(addSeriesSpy).toHaveBeenCalledWith(CandlestickSeries, expect.any(Object))
  })

  it('maps bars to seconds-based OHLC data', () => {
    render(<PriceChart data={sampleBars} />)
    expect(setDataSpy).toHaveBeenCalledTimes(1)
    const payload = setDataSpy.mock.calls[0][0]
    expect(payload).toHaveLength(2)
    expect(payload[0]).toEqual({
      time: 1704067200,
      open: 100,
      high: 110,
      low: 95,
      close: 105,
    })
  })

  it('does not create series markers when markers is omitted', () => {
    render(<PriceChart data={sampleBars} />)
    expect(createSeriesMarkersSpy).not.toHaveBeenCalled()
  })

  it('maps a buy marker to a belowBar green arrowUp', () => {
    const markers: TradeMarker[] = [
      { ts: 1704067200000, side: 'buy', price: 100, qty: 1 },
    ]
    render(<PriceChart data={sampleBars} markers={markers} />)
    expect(createSeriesMarkersSpy).toHaveBeenCalledTimes(1)
    const passedMarkers = createSeriesMarkersSpy.mock.calls[0][1]
    expect(passedMarkers).toHaveLength(1)
    expect(passedMarkers?.[0]).toMatchObject({
      time: 1704067200,
      position: 'belowBar',
      color: '#22c55e',
      shape: 'arrowUp',
      text: 'B',
    })
  })

  it('maps a sell marker to an aboveBar red arrowDown', () => {
    const markers: TradeMarker[] = [
      { ts: 1704067200000, side: 'sell', price: 100, qty: 1 },
    ]
    render(<PriceChart data={sampleBars} markers={markers} />)
    expect(createSeriesMarkersSpy).toHaveBeenCalledTimes(1)
    const passedMarkers = createSeriesMarkersSpy.mock.calls[0][1]
    expect(passedMarkers).toHaveLength(1)
    expect(passedMarkers?.[0]).toMatchObject({
      time: 1704067200,
      position: 'aboveBar',
      color: '#ef4444',
      shape: 'arrowDown',
      text: 'S',
    })
  })

  it('preserves marker order for mixed buy/sell markers', () => {
    const markers: TradeMarker[] = [
      { ts: 1704067200000, side: 'buy', price: 100, qty: 1 },
      { ts: 1704153600000, side: 'sell', price: 112, qty: 1 },
    ]
    render(<PriceChart data={sampleBars} markers={markers} />)
    expect(createSeriesMarkersSpy).toHaveBeenCalledTimes(1)
    const passedMarkers = createSeriesMarkersSpy.mock.calls[0][1]
    expect(passedMarkers).toHaveLength(2)
    expect(passedMarkers?.[0]).toMatchObject({ position: 'belowBar' })
    expect(passedMarkers?.[1]).toMatchObject({ position: 'aboveBar' })
  })
})
