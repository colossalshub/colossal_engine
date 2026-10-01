import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import type { RunSummary, Verification } from '../../api/types'
import { ExperimentHeader } from './ExperimentHeader'

const run: RunSummary = {
  run_id: 'r-1',
  name: 'EMA Cross',
  strategy: 'ema_cross',
  universe: ['BTC/USDT'],
  start_ts: 1704067200000,
  end_ts: 1706659200000,
  created_at: 1704067200000,
  git_sha: 'abcdef1234567890',
  git_dirty: false,
  experiment_id: null,
  status: 'done',
  sharpe: 1.23,
  cagr: 0.15,
  max_drawdown: -0.08,
}

const verification: Verification = {
  verified: true,
  discrepancy_pct: 0,
  source: 'account_report',
}

function renderHeader(
  overrides: {
    run?: Partial<RunSummary>
    params?: Record<string, unknown>
    verification?: Verification
  } = {},
) {
  return render(
    <MemoryRouter>
      <ExperimentHeader
        run={{ ...run, ...overrides.run }}
        params={overrides.params ?? {}}
        verification={overrides.verification ?? verification}
      />
    </MemoryRouter>,
  )
}

describe('ExperimentHeader', () => {
  it('shows the run identity that the tear sheet already has', () => {
    renderHeader({
      params: { timeframe: '1d', maker_fee: '0.001', benchmark_symbol: 'ETH/USDT' },
    })

    expect(screen.getByRole('link', { name: '← Back' })).toHaveAttribute('href', '/')
    expect(screen.getByRole('heading', { name: 'EMA Cross' })).toBeInTheDocument()
    expect(screen.getByText('strategy ema_cross')).toBeInTheDocument()
    expect(screen.getByText('BTC/USDT')).toBeInTheDocument()
    expect(screen.getByText('2024-01-01 → 2024-01-31')).toBeInTheDocument()
    expect(screen.getByText('timeframe 1d')).toBeInTheDocument()
    expect(screen.getByText('fees 0.10%')).toBeInTheDocument()
    expect(screen.getByText('benchmark ETH/USDT')).toBeInTheDocument()
    expect(screen.getByText('git abcdef1')).toBeInTheDocument()
    expect(screen.getByText('done')).toBeInTheDocument()
    expect(screen.getByText(/Equity reconciled/)).toBeInTheDocument()
    expect(screen.queryByText('only first symbol executed')).not.toBeInTheDocument()
  })

  it('notes that only the first symbol was executed', () => {
    renderHeader({ run: { universe: ['BTC/USDT', 'ETH/USDT'] } })
    expect(screen.getByText('BTC/USDT')).toBeInTheDocument()
    expect(screen.getByText('only first symbol executed')).toBeInTheDocument()
    expect(screen.queryByText('ETH/USDT')).not.toBeInTheDocument()
  })

  it('omits timeframe, fees, benchmark, and git when they are absent', () => {
    renderHeader({
      run: { git_sha: null, git_dirty: true },
      params: { timeframe: '   ', maker_fee: 0.001, benchmark_symbol: '' },
    })
    expect(screen.queryByText(/timeframe/)).not.toBeInTheDocument()
    expect(screen.queryByText(/fees/)).not.toBeInTheDocument()
    expect(screen.queryByText(/benchmark/)).not.toBeInTheDocument()
    expect(screen.queryByText(/git /)).not.toBeInTheDocument()
    expect(screen.queryByText(/\(dirty\)/)).not.toBeInTheDocument()
  })

  it('appends dirty only when a git sha is present', () => {
    renderHeader({ run: { git_sha: 'deadbeef', git_dirty: true } })
    expect(screen.getByText('git deadbee (dirty)')).toBeInTheDocument()
  })

  it('does not invent venue, strategy version, or dataset identity', () => {
    renderHeader()
    expect(screen.queryByText(/venue/i)).not.toBeInTheDocument()
    expect(screen.queryByText('Strategy version')).not.toBeInTheDocument()
    expect(screen.queryByText('Dataset identity')).not.toBeInTheDocument()
  })
})
