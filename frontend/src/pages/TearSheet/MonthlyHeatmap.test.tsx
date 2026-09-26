import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { MonthlyReturns } from '../../api/types'
import { MonthlyHeatmap } from './MonthlyHeatmap'

const sample: MonthlyReturns[] = [
  {
    year: 2024,
    months: [0.03, -0.01, 0.08, 0.04, null, null, null, null, null, null, null, null],
  },
  {
    year: 2025,
    months: [-0.02, 0.06, null, null, null, null, null, null, null, null, null, null],
  },
]

describe('MonthlyHeatmap', () => {
  it('renders the empty state when data is empty', () => {
    render(<MonthlyHeatmap data={[]} />)
    expect(screen.getByText('No monthly data for this run.')).toBeInTheDocument()
  })

  it('renders one cell per (year, month)', () => {
    render(<MonthlyHeatmap data={sample} />)
    // 2 years * 12 months = 24 cells
    const cells = screen.getAllByTestId(/^cell-/)
    expect(cells).toHaveLength(24)
  })

  it('renders the year labels', () => {
    render(<MonthlyHeatmap data={sample} />)
    expect(screen.getByText('2024')).toBeInTheDocument()
    expect(screen.getByText('2025')).toBeInTheDocument()
  })

  it('renders all 12 month headers', () => {
    render(<MonthlyHeatmap data={sample} />)
    for (const label of ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']) {
      expect(screen.getByText(label)).toBeInTheDocument()
    }
  })

  it('colors a strong positive month with the strong green shade', () => {
    render(<MonthlyHeatmap data={sample} />)
    const cell = screen.getByTestId('cell-2024-2') // 0.08 = 8% > 5%
    expect(cell.getAttribute('fill')).toBe('rgba(34, 197, 94, 0.90)')
  })

  it('colors a light positive month with the light green shade', () => {
    render(<MonthlyHeatmap data={sample} />)
    const cell = screen.getByTestId('cell-2024-0') // 0.03 = 3% in [2%, 5%)
    expect(cell.getAttribute('fill')).toBe('rgba(34, 197, 94, 0.60)')
  })

  it('colors a small negative month with the light red shade', () => {
    render(<MonthlyHeatmap data={sample} />)
    const cell = screen.getByTestId('cell-2024-1') // -0.01 = -1% < 2%
    expect(cell.getAttribute('fill')).toBe('rgba(239, 68, 68, 0.30)')
  })

  it('colors a null month with the neutral grey', () => {
    render(<MonthlyHeatmap data={sample} />)
    const cell = screen.getByTestId('cell-2024-5') // null
    expect(cell.getAttribute('fill')).toBe('rgba(107, 114, 128, 0.15)')
  })

  it('shows a tooltip on hover with month, year, and formatted return', () => {
    render(<MonthlyHeatmap data={sample} />)
    const cell = screen.getByTestId('cell-2024-2')
    fireEvent.mouseEnter(cell)
    expect(screen.getByRole('tooltip')).toBeInTheDocument()
    expect(screen.getByText('Mar 2024')).toBeInTheDocument()
    expect(screen.getByText('+8.00%')).toBeInTheDocument()
  })

  it('formats a negative return without a plus sign', () => {
    render(<MonthlyHeatmap data={sample} />)
    fireEvent.mouseEnter(screen.getByTestId('cell-2024-1'))
    expect(screen.getByText('-1.00%')).toBeInTheDocument()
  })

  it('formats a null month tooltip value as an em dash', () => {
    render(<MonthlyHeatmap data={sample} />)
    fireEvent.mouseEnter(screen.getByTestId('cell-2024-5'))
    expect(screen.getByText('—')).toBeInTheDocument()
  })

  it('hides the tooltip on mouse leave', () => {
    render(<MonthlyHeatmap data={sample} />)
    const cell = screen.getByTestId('cell-2024-2')
    fireEvent.mouseEnter(cell)
    expect(screen.getByRole('tooltip')).toBeInTheDocument()
    fireEvent.mouseLeave(cell)
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument()
  })

  it('sorts years ascending even when given out of order', () => {
    const reversed: MonthlyReturns[] = [sample[1], sample[0]]
    render(<MonthlyHeatmap data={reversed} />)
    const cells = screen.getAllByTestId(/^cell-/)
    // First cell rendered should be 2024-0, last should be 2025-11
    expect(cells[0].getAttribute('data-testid')).toBe('cell-2024-0')
    expect(cells[cells.length - 1].getAttribute('data-testid')).toBe('cell-2025-11')
  })
})
