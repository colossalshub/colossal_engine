import { render, screen } from '@testing-library/react'
import { CandlestickSeries } from 'lightweight-charts'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { OHLCV } from '../../api/types'
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

const sampleBars: OHLCV[] = [
  { ts: 1704067200000, open: 100, high: 110, low: 95, close: 105, volume: 10 },
  { ts: 1704153600000, open: 105, high: 115, low: 100, close: 112, volume: 12 },
]

beforeEach(() => {
  addSeriesSpy.mockClear()
  setDataSpy.mockClear()
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
})
