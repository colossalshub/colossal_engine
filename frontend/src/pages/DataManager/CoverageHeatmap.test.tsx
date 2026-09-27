import { fireEvent, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { CoverageResponse } from '../../api/types'
import { renderWithProviders } from '../../test-utils'
import * as dataApi from '../../api/data'
import { CoverageHeatmap } from './CoverageHeatmap'

function fullYear2024(barsPerMonth: number, expectedPerMonth: number): CoverageResponse {
  const cells = Array.from({ length: 12 }, (_, i) => ({
    year: 2024,
    month: i + 1,
    bars: barsPerMonth,
    expected: expectedPerMonth,
    coverage: expectedPerMonth > 0 ? barsPerMonth / expectedPerMonth : 0,
  }))
  return {
    rows: [
      {
        venue: 'binance',
        symbol: 'BTC/USDT',
        timeframe: '1d',
        cells,
      },
    ],
  }
}

describe('CoverageHeatmap', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('shows empty state when rows are empty', async () => {
    vi.spyOn(dataApi, 'getCoverage').mockResolvedValue({ rows: [] })

    renderWithProviders(<CoverageHeatmap />)

    await waitFor(() => {
      expect(
        screen.getByText('No coverage data. Ingest bars to populate this view.'),
      ).toBeInTheDocument()
    })
  })

  it('shows loading state initially', () => {
    vi.spyOn(dataApi, 'getCoverage').mockReturnValue(new Promise(() => {}))

    renderWithProviders(<CoverageHeatmap />)

    expect(screen.getByText('Loading coverage…')).toBeInTheDocument()
  })

  it('shows error state on failure', async () => {
    vi.spyOn(dataApi, 'getCoverage').mockRejectedValue(new Error('boom'))

    renderWithProviders(<CoverageHeatmap />)

    await waitFor(() => {
      expect(screen.getByText(/Failed to load coverage/)).toBeInTheDocument()
    })
  })

  it('renders year headers across rows', async () => {
    vi.spyOn(dataApi, 'getCoverage').mockResolvedValue({
      rows: [
        {
          venue: 'binance',
          symbol: 'BTC/USDT',
          timeframe: '1d',
          cells: [{ year: 2024, month: 1, bars: 31, expected: 31, coverage: 1 }],
        },
        {
          venue: 'binance',
          symbol: 'ETH/USDT',
          timeframe: '1d',
          cells: [{ year: 2025, month: 1, bars: 31, expected: 31, coverage: 1 }],
        },
      ],
    })

    renderWithProviders(<CoverageHeatmap />)

    await waitFor(() => {
      expect(screen.getByText('2024')).toBeInTheDocument()
      expect(screen.getByText('2025')).toBeInTheDocument()
    })
  })

  it('renders row labels for symbol and timeframe', async () => {
    vi.spyOn(dataApi, 'getCoverage').mockResolvedValue({
      rows: [
        {
          venue: 'binance',
          symbol: 'BTC/USDT',
          timeframe: '1d',
          cells: [{ year: 2024, month: 1, bars: 31, expected: 31, coverage: 1 }],
        },
      ],
    })

    renderWithProviders(<CoverageHeatmap />)

    await waitFor(() => {
      expect(screen.getByText(/BTC\/USDT\s+1d/)).toBeInTheDocument()
    })
  })

  it('opens the hover tooltip below the cell', async () => {
    vi.spyOn(dataApi, 'getCoverage').mockResolvedValue(fullYear2024(31, 31))

    renderWithProviders(<CoverageHeatmap />)

    const cell = await screen.findByTestId('cell-0-2024')
    fireEvent.mouseEnter(cell)

    const tooltip = screen.getByRole('tooltip')
    expect(tooltip).toHaveTextContent('BTC/USDT · 1d · 2024')
    expect(tooltip).toHaveTextContent('Bars: 372 / 372')
    const top = Number.parseFloat(tooltip.style.top)
    const cellTop = Number.parseFloat(cell.getAttribute('y') ?? '0')
    expect(top).toBeGreaterThan(cellTop)
  })

  it('colors cells by aggregated year coverage', async () => {
    const full = fullYear2024(31, 31)
    const partial = fullYear2024(15, 31)
    vi.spyOn(dataApi, 'getCoverage')
      .mockResolvedValueOnce(full)
      .mockResolvedValueOnce(partial)

    const { unmount } = renderWithProviders(<CoverageHeatmap />)
    await waitFor(() => {
      const cell = screen.getByTestId('cell-0-2024')
      expect(cell.getAttribute('fill')).toBe('rgba(34, 197, 94, 0.90)')
    })
    unmount()

    renderWithProviders(<CoverageHeatmap />)
    await waitFor(() => {
      const cell = screen.getByTestId('cell-0-2024')
      expect(cell.getAttribute('fill')).toBe('rgba(239, 68, 68, 0.60)')
    })
  })
})
