import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import * as runsApi from '../../api/runs'
import type { TearSheet } from '../../api/types'
import { renderWithProviders } from '../../test-utils'
import TearSheetPage from './index'
import { LAYOUT_STORAGE_KEY, defaultLayout } from './tearsheetLayout'

class ResizeObserverStub implements ResizeObserver {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

globalThis.ResizeObserver = ResizeObserverStub

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

beforeEach(() => {
  localStorage.clear()
})

afterEach(() => {
  vi.restoreAllMocks()
  localStorage.clear()
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

  it('displays fees when params contain maker_fee', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue({
      ...sampleTearsheet,
      params: { maker_fee: '0.001' },
    })
    renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })
    await waitFor(() => {
      expect(screen.getByText('fees 0.10%')).toBeInTheDocument()
    })
  })

  it('displays benchmark when params contain it', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue({
      ...sampleTearsheet,
      params: { benchmark_symbol: 'BTC/USDT' },
    })
    renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })
    await waitFor(() => {
      expect(screen.getByText('benchmark BTC/USDT')).toBeInTheDocument()
    })
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
      expect(screen.getByText('KPIs')).toBeInTheDocument()
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

  it('polls when the run is queued', async () => {
    vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval'] })
    try {
      const getTearsheetSpy = vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue({
        ...sampleTearsheet,
        run: { ...sampleTearsheet.run, status: 'queued' },
      })

      renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })

      await waitFor(() => {
        expect(getTearsheetSpy).toHaveBeenCalledTimes(1)
      })

      await vi.advanceTimersByTimeAsync(2000)

      await waitFor(() => {
        expect(getTearsheetSpy.mock.calls.length).toBeGreaterThanOrEqual(2)
      })
    } finally {
      vi.useRealTimers()
    }
  })

  it('does not poll when the run is done', async () => {
    vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval'] })
    try {
      const getTearsheetSpy = vi
        .spyOn(runsApi, 'getTearsheet')
        .mockResolvedValue(sampleTearsheet)

      renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })

      await waitFor(() => {
        expect(getTearsheetSpy).toHaveBeenCalledTimes(1)
      })

      await vi.advanceTimersByTimeAsync(5000)

      expect(getTearsheetSpy).toHaveBeenCalledTimes(1)
    } finally {
      vi.useRealTimers()
    }
  })

  it('shows the empty state for a queued run instead of charts', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue({
      ...sampleTearsheet,
      run: { ...sampleTearsheet.run, status: 'queued' },
    })
    renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })
    await waitFor(() => {
      expect(screen.getByText('Backtest in progress…')).toBeInTheDocument()
    })
    expect(screen.queryByText('KPIs')).not.toBeInTheDocument()
    expect(screen.queryByText('Price + Fills')).not.toBeInTheDocument()
  })

  it('renders a drag handle on each visible widget', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'KPIs' })).toBeInTheDocument()
    })
    expect(document.querySelectorAll('.drag-handle')).toHaveLength(6)
  })

  it('hides a widget from the picker and keeps it available to restore', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    const user = userEvent.setup()
    renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Price + Fills' })).toBeInTheDocument()
    })

    await user.click(screen.getByRole('button', { name: /widgets/i }))
    await user.click(screen.getByRole('checkbox', { name: 'Price + Fills' }))

    expect(screen.queryByRole('heading', { name: 'Price + Fills' })).not.toBeInTheDocument()
    expect(screen.getByRole('checkbox', { name: 'Price + Fills' })).not.toBeChecked()
    expect(screen.getByRole('heading', { name: 'KPIs' })).toBeInTheDocument()
  })

  it('debounces layout toggles into localStorage', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    const user = userEvent.setup()
    renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /widgets/i })).toBeInTheDocument()
    })

    await user.click(screen.getByRole('button', { name: /widgets/i }))
    await user.click(screen.getByRole('checkbox', { name: 'KPIs' }))

    await waitFor(() => {
      const raw = localStorage.getItem(LAYOUT_STORAGE_KEY)
      expect(raw).toBeTruthy()
      const parsed = JSON.parse(raw ?? '') as {
        widgets: { kpis: { visible: boolean } }
      }
      expect(parsed.widgets.kpis.visible).toBe(false)
    })
  })

  it('restores a saved layout and ignores invalid JSON', async () => {
    const stored = defaultLayout()
    stored.widgets.ledger.visible = false
    localStorage.setItem(LAYOUT_STORAGE_KEY, JSON.stringify(stored))
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    const { unmount } = renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'KPIs' })).toBeInTheDocument()
    })
    expect(screen.queryByRole('heading', { name: 'Trade Ledger' })).not.toBeInTheDocument()
    unmount()

    localStorage.setItem(LAYOUT_STORAGE_KEY, '{not-json')
    renderWithProviders(<TearSheetPage />, { route: '/runs/r-1' })
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Trade Ledger' })).toBeInTheDocument()
    })
    expect(screen.getByRole('heading', { name: 'KPIs' })).toBeInTheDocument()
  })
})
