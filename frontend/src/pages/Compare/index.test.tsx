import { screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import * as runsApi from '../../api/runs'
import type { RunSummary, TearSheet } from '../../api/types'
import { renderWithProviders } from '../../test-utils'
import Compare from './index'

function makeRun(id: string, name: string): RunSummary {
  return {
    run_id: id,
    name,
    strategy: 'buy_hold',
    universe: ['BTC/USDT'],
    start_ts: 1704067200000,
    end_ts: 1706659200000,
    created_at: 1704067200000,
    git_sha: 'abc',
    git_dirty: false,
    experiment_id: null,
    status: 'done',
    sharpe: 1.0,
    cagr: 0.1,
    max_drawdown: -0.05,
  }
}

function makeTearsheet(id: string, name: string): TearSheet {
  return {
    run: makeRun(id, name),
    params: {},
    kpis: {
      sharpe: 1.0,
      sortino: null,
      cagr: 0.1,
      volatility: null,
      max_drawdown: -0.05,
      calmar: null,
      win_rate: null,
      profit_factor: null,
      turnover: null,
      total_trades: null,
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
}

describe('Compare page', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('shows select at least 2 when only one id', () => {
    renderWithProviders(<Compare />, { route: '/compare?ids=a' })
    expect(screen.getByText(/Select at least 2 runs to compare/)).toBeInTheDocument()
  })

  it('shows select at least 2 when no ids', () => {
    renderWithProviders(<Compare />, { route: '/compare' })
    expect(screen.getByText(/Select at least 2 runs to compare/)).toBeInTheDocument()
  })

  it('shows loading state', () => {
    vi.spyOn(runsApi, 'getTearsheet').mockReturnValue(new Promise(() => {}))
    renderWithProviders(<Compare />, { route: '/compare?ids=a,b' })
    expect(screen.getByText('Loading comparison…')).toBeInTheDocument()
  })

  it('shows error state', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockRejectedValue(new Error('boom'))
    renderWithProviders(<Compare />, { route: '/compare?ids=a,b' })
    await waitFor(() => {
      expect(screen.getByText(/Failed to load comparison/)).toBeInTheDocument()
    })
  })

  it('renders one column per run', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockImplementation(async (id: string) => {
      if (id === 'a') return makeTearsheet('a', 'Run Alpha')
      if (id === 'b') return makeTearsheet('b', 'Run Beta')
      throw new Error(`unexpected id ${id}`)
    })
    renderWithProviders(<Compare />, { route: '/compare?ids=a,b' })
    await waitFor(() => {
      expect(screen.getByText('Run Alpha')).toBeInTheDocument()
    })
    expect(screen.getByText('Run Beta')).toBeInTheDocument()
  })

  it('calls getTearsheet with each id', async () => {
    const spy = vi.spyOn(runsApi, 'getTearsheet').mockImplementation(async (id: string) =>
      makeTearsheet(id, `Run ${id}`),
    )
    renderWithProviders(<Compare />, { route: '/compare?ids=a,b' })
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(2)
    })
    expect(spy).toHaveBeenCalledWith('a')
    expect(spy).toHaveBeenCalledWith('b')
  })
})
