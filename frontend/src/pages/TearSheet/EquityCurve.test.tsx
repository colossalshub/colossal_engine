import { render, screen } from '@testing-library/react'
import { LineSeries } from 'lightweight-charts'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { EquityPoint } from '../../api/types'
import { EquityCurve } from './EquityCurve'

const setDataSpy = vi.fn()
const addSeriesSpy = vi.fn(() => ({ setData: setDataSpy }))

vi.mock('../../components/charts/BaseChart', () => ({
  BaseChart: ({ createSeries }: { createSeries: (c: unknown) => unknown }) => {
    const fakeChart = { addSeries: addSeriesSpy }
    createSeries(fakeChart)
    return <div data-testid="base-chart-mock" />
  },
}))

const sampleData: EquityPoint[] = [
  { ts: 1704067200000, equity: 100000, benchmark: 100000 },
  { ts: 1704153600000, equity: 101000, benchmark: 99500 },
  { ts: 1704240000000, equity: 99000, benchmark: 99800 },
]

beforeEach(() => {
  addSeriesSpy.mockClear()
  setDataSpy.mockClear()
})

describe('EquityCurve', () => {
  it('renders a BaseChart when data is non-empty', () => {
    render(<EquityCurve data={sampleData} />)
    expect(screen.getByTestId('base-chart-mock')).toBeInTheDocument()
  })

  it('renders the empty state when data is empty', () => {
    render(<EquityCurve data={[]} />)
    expect(screen.getByText('No equity data for this run.')).toBeInTheDocument()
    expect(screen.queryByTestId('base-chart-mock')).not.toBeInTheDocument()
  })

  it('creates two series when benchmark is present', () => {
    render(<EquityCurve data={sampleData} />)
    expect(addSeriesSpy).toHaveBeenCalledTimes(2)
    expect(addSeriesSpy).toHaveBeenNthCalledWith(1, LineSeries, expect.any(Object))
    expect(addSeriesSpy).toHaveBeenNthCalledWith(2, LineSeries, expect.any(Object))
  })

  it('creates only one series when all benchmarks are null', () => {
    const noBench: EquityPoint[] = sampleData.map((p) => ({ ...p, benchmark: null }))
    render(<EquityCurve data={noBench} />)
    expect(addSeriesSpy).toHaveBeenCalledTimes(1)
  })

  it('maps equity data to seconds-based LineData', () => {
    render(<EquityCurve data={sampleData} />)
    // setData is called for each series; the first call is the equity series
    const equityPayload = setDataSpy.mock.calls[0][0]
    expect(equityPayload).toHaveLength(3)
    expect(equityPayload[0]).toEqual({ time: 1704067200, value: 100000 })
  })

  it('excludes null benchmark points from the benchmark series', () => {
    const mixed: EquityPoint[] = [
      { ts: 1704067200000, equity: 100000, benchmark: null },
      { ts: 1704153600000, equity: 101000, benchmark: 99500 },
      { ts: 1704240000000, equity: 99000, benchmark: null },
    ]
    render(<EquityCurve data={mixed} />)
    // Second setData call is the benchmark series
    const benchPayload = setDataSpy.mock.calls[1][0]
    expect(benchPayload).toHaveLength(1)
    expect(benchPayload[0]).toEqual({ time: 1704153600, value: 99500 })
  })
})
