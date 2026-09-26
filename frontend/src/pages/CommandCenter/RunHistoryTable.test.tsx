import { screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { RunList, RunSummary } from '../../api/types'
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
  status: 'done',
  sharpe: 1.23,
  cagr: 0.15,
  max_drawdown: -0.08,
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
})
