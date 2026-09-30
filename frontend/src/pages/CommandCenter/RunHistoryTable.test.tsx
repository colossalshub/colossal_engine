import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from '../../App'
import type { RunList, RunSummary, TearSheet } from '../../api/types'
import { RunHistoryTable } from './RunHistoryTable'
import * as runsApi from '../../api/runs'
import { renderWithProviders } from '../../test-utils'

// AG Grid needs ResizeObserver + matchMedia in jsdom

const sampleRun: RunSummary = {
  run_id: 'r-1',
  name: 'buy_hold BTC/USDT 1d',
  strategy: 'buy_hold',
  universe: ['BTC/USDT'],
  start_ts: 1704067200000,
  end_ts: 1706659200000,
  created_at: 1704067200000,
  git_sha: 'abc',
  git_dirty: false,
  experiment_id: null,
  status: 'done',
  sharpe: 1.23,
  cagr: 0.15,
  max_drawdown: -0.08,
}

const sampleTearsheet: TearSheet = {
  run: sampleRun,
  params: {},
  kpis: {
    sharpe: null, sortino: null, cagr: null, volatility: null,
    max_drawdown: null, calmar: null, win_rate: null,
    profit_factor: null, turnover: null, total_trades: null,
    avg_duration_days: null,
  },
  equity: [],
  drawdown: [],
  price: [],
  markers: [],
  monthly_returns: [],
  verification: { verified: true, discrepancy_pct: 0, source: 'reconstructed' },
  execution_assumptions: {
    bar_ts: 'open',
    nautilus_bar_ts_event: 'close',
    signal_and_order: 'on_bar',
    order_type: 'market',
    sizing_price_when_deploy_pct_positive: 'bar.close',
    maker_fee_default: '0.001',
    taker_fee_default: '0.001',
    maker_fee: '0.001',
    taker_fee: '0.001',
    fill_model: 'not_passed',
    latency: 'not_passed',
    spread: 'not_passed',
    queue_model: 'not_passed',
    partial_fills: 'not_passed',
  },
  artifacts: {},
}

describe('RunHistoryTable', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders rows when data loads', async () => {
    const list: RunList = { items: [sampleRun], total: 1, page: 1, page_size: 50 }
    vi.spyOn(runsApi, 'listRuns').mockResolvedValue(list)

    renderWithProviders(<RunHistoryTable />)

    await waitFor(() => {
      expect(screen.getByText('buy_hold BTC/USDT 1d')).toBeInTheDocument()
    })
  })

  it('shows loading state initially', () => {
    vi.spyOn(runsApi, 'listRuns').mockReturnValue(new Promise(() => {}))

    renderWithProviders(<RunHistoryTable />)

    expect(screen.getByText('Loading runs…')).toBeInTheDocument()
  })

  it('shows empty state', async () => {
    const list: RunList = { items: [], total: 0, page: 1, page_size: 50 }
    vi.spyOn(runsApi, 'listRuns').mockResolvedValue(list)

    renderWithProviders(<RunHistoryTable />)

    await waitFor(() => {
      expect(screen.getByText('No backtest runs yet.')).toBeInTheDocument()
    })
  })

  it('shows error state', async () => {
    vi.spyOn(runsApi, 'listRuns').mockRejectedValue(new Error('boom'))

    renderWithProviders(<RunHistoryTable />)

    await waitFor(() => {
      expect(screen.getByText(/Failed to load runs/)).toBeInTheDocument()
    })
  })

  it('polls when a queued run is present', async () => {
    vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval'] })
    try {
      const queuedRun: RunSummary = { ...sampleRun, status: 'queued' }
      const list: RunList = { items: [queuedRun], total: 1, page: 1, page_size: 50 }
      const listRunsSpy = vi.spyOn(runsApi, 'listRuns').mockResolvedValue(list)

      renderWithProviders(<RunHistoryTable />)

      await waitFor(() => {
        expect(listRunsSpy).toHaveBeenCalledTimes(1)
      })

      await vi.advanceTimersByTimeAsync(2000)

      await waitFor(() => {
        expect(listRunsSpy.mock.calls.length).toBeGreaterThanOrEqual(2)
      })
    } finally {
      vi.useRealTimers()
    }
  }, 15_000)

  it('does not poll when all runs are done', async () => {
    vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval'] })
    try {
      const list: RunList = { items: [sampleRun], total: 1, page: 1, page_size: 50 }
      const listRunsSpy = vi.spyOn(runsApi, 'listRuns').mockResolvedValue(list)

      renderWithProviders(<RunHistoryTable />)

      await waitFor(() => {
        expect(listRunsSpy).toHaveBeenCalledTimes(1)
      })

      await vi.advanceTimersByTimeAsync(5000)

      expect(listRunsSpy).toHaveBeenCalledTimes(1)
    } finally {
      vi.useRealTimers()
    }
  }, 15_000)

  it('navigates to the tear sheet when a row is double-clicked', async () => {
    const user = userEvent.setup()
    vi.spyOn(runsApi, 'listRuns').mockResolvedValue({
      items: [sampleRun],
      total: 1,
      page: 1,
      page_size: 50,
    })
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)

    renderWithProviders(<App />, { route: '/' })

    const cell = await screen.findByText('buy_hold BTC/USDT 1d')
    await user.dblClick(cell)

    await waitFor(() => {
      expect(screen.getByText('← Back')).toBeInTheDocument()
    })
  })
})
