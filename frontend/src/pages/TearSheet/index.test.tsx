import { screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import * as runsApi from '../../api/runs'
import type { TearSheet } from '../../api/types'
import { renderWithProviders } from '../../test-utils'
import TearSheetPage from './index'

const sampleTearsheet: TearSheet = {
  run: {
    run_id: 'r-1',
    name: 'buy_hold BTC/USDT 1d',
    strategy: 'buy_hold',
    universe: ['BTC/USDT', 'ETH/USDT'],
    start_ts: 1704067200000,
    end_ts: 1706659200000,
    created_at: 1704067200000,
    git_sha: 'abcdef1234567890',
    git_dirty: false,
    status: 'done',
    sharpe: 1.23,
    cagr: 0.15,
    max_drawdown: -0.08,
  },
  params: {},
  kpis: {
    sharpe: 1.23, sortino: 1.8, cagr: 0.15, volatility: 0.2,
    max_drawdown: -0.08, calmar: 1.9, win_rate: 0.6,
    profit_factor: 1.7, turnover: 0.5, total_trades: 10,
    avg_duration_days: 3.2,
  },
  equity: [],
  drawdown: [],
  price: [],
  markers: [],
  monthly_returns: [],
  verification: { verified: true, discrepancy_pct: 0.0, source: 'reconstructed' },
  artifacts: {},
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('TearSheet page', () => {
  it('renders the run name and status badge on success', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })
    await waitFor(() => {
      expect(screen.getByText('buy_hold BTC/USDT 1d')).toBeInTheDocument()
    })
    expect(screen.getByText('done')).toBeInTheDocument()
  })

  it('renders the universe and formatted date range', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })
    await waitFor(() => {
      expect(screen.getByText('BTC/USDT · ETH/USDT')).toBeInTheDocument()
    })
    expect(screen.getByText('2024-01-01 → 2024-01-31')).toBeInTheDocument()
  })

  it('renders the short git sha', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })
    await waitFor(() => {
      expect(screen.getByText(/git abcdef1/)).toBeInTheDocument()
    })
  })

  it('renders all six placeholder sections', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })
    await waitFor(() => {
      expect(screen.getByText('KPI Strip')).toBeInTheDocument()
    })
    expect(screen.getByText('Price + Fills')).toBeInTheDocument()
    expect(screen.getByText('Equity')).toBeInTheDocument()
    expect(screen.getByText('Underwater')).toBeInTheDocument()
    expect(screen.getByText('Monthly Returns')).toBeInTheDocument()
    expect(screen.getByText('Trade Ledger')).toBeInTheDocument()
  })

  it('shows a loading state before data resolves', () => {
    vi.spyOn(runsApi, 'getTearsheet').mockImplementation(
      () => new Promise(() => {}),
    )
    renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })
    expect(screen.getByText('Loading tear sheet…')).toBeInTheDocument()
  })

  it('shows an error state when the fetch fails', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockRejectedValue(new Error('boom'))
    renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })
    await waitFor(() => {
      expect(screen.getByText(/Failed to load tear sheet/)).toBeInTheDocument()
    })
  })
})
