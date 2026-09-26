import { render, screen } from '@testing-library/react'
import { AreaSeries } from 'lightweight-charts'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { DrawdownPoint } from '../../api/types'
import { DrawdownChart } from './DrawdownChart'

const setDataSpy = vi.fn()
const addSeriesSpy = vi.fn(() => ({ setData: setDataSpy }))

vi.mock('../../components/charts/BaseChart', () => ({
  BaseChart: ({ createSeries }: { createSeries: (c: unknown) => unknown }) => {
    const fakeChart = { addSeries: addSeriesSpy }
    createSeries(fakeChart)
    return <div data-testid="base-chart-mock" />
  },
}))

const sampleData: DrawdownPoint[] = [
  { ts: 1704067200000, dd: 0 },
  { ts: 1704153600000, dd: -0.01 },
  { ts: 1704240000000, dd: -0.05 },
  { ts: 1704326400000, dd: -0.02 },
]

beforeEach(() => {
  addSeriesSpy.mockClear()
  setDataSpy.mockClear()
})

describe('DrawdownChart', () => {
  it('renders a BaseChart when data is non-empty', () => {
    render(<DrawdownChart data={sampleData} />)
    expect(screen.getByTestId('base-chart-mock')).toBeInTheDocument()
  })

  it('renders the empty state when data is empty', () => {
    render(<DrawdownChart data={[]} />)
    expect(screen.getByText('No drawdown data for this run.')).toBeInTheDocument()
    expect(screen.queryByTestId('base-chart-mock')).not.toBeInTheDocument()
  })

  it('calls addSeries with AreaSeries', () => {
    render(<DrawdownChart data={sampleData} />)
    expect(addSeriesSpy).toHaveBeenCalledTimes(1)
    expect(addSeriesSpy).toHaveBeenCalledWith(AreaSeries, expect.any(Object))
  })

  it('maps drawdown points to seconds-based AreaData', () => {
    render(<DrawdownChart data={sampleData} />)
    const payload = setDataSpy.mock.calls[0][0]
    expect(payload).toHaveLength(4)
    expect(payload[0]).toEqual({ time: 1704067200, value: 0 })
    expect(payload[2]).toEqual({ time: 1704240000, value: -0.05 })
  })
})
