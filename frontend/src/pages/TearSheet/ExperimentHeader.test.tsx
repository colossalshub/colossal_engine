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
  research_stage: null,
  hypothesis_id: null,
  strategy_version: null,
  in_sample_start_ts: null,
  in_sample_end_ts: null,
  validation_start_ts: null,
  validation_end_ts: null,
  oos_start_ts: null,
  oos_end_ts: null,
  trial_index: null,
  trial_count: null,
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

  it('shows persisted research metadata, including explicit nulls', () => {
    renderHeader()
    const region = screen.getByRole('region', { name: 'Research identity' })
    const labels = [...region.querySelectorAll('dt')].map((term) => term.textContent)
    expect(labels).toEqual([
      'Experiment',
      'Research Stage',
      'Hypothesis',
      'Strategy Version',
      'In-sample UTC',
      'Validation UTC',
      'OOS UTC',
      'Trial Index',
      'Trial Count',
    ])
    for (const term of region.querySelectorAll('dt')) {
      expect(term.nextElementSibling?.textContent).toBe('—')
    }
    expect(screen.queryByText(/venue/i)).not.toBeInTheDocument()
    expect(screen.queryByText('Dataset identity')).not.toBeInTheDocument()
  })

  it('renders populated research identity with exact strings, stages, and UTC ranges', () => {
    const stages = ['exploration', 'validation', 'oos'] as const
    const labels = ['Exploration', 'Validation', 'OOS']
    for (const [index, research_stage] of stages.entries()) {
      const view = renderHeader({
        run: {
          experiment_id: '  exp-A  ',
          research_stage,
          hypothesis_id: ' H/alpha ',
          strategy_version: ' v1+dirty ',
          in_sample_start_ts: 1704067200123,
          in_sample_end_ts: 1704153600456,
          validation_start_ts: 1704153600456,
          validation_end_ts: 1704240000789,
          oos_start_ts: 1704240000789,
          oos_end_ts: 1704326400000,
          trial_index: 7,
          trial_count: 3,
        },
      })
      const region = screen.getByRole('region', { name: 'Research identity' })
      const value = (label: string) =>
        [...region.querySelectorAll('dt')].find((term) => term.textContent === label)
          ?.nextElementSibling?.textContent
      expect(value('Experiment')).toBe('  exp-A  ')
      expect(value('Research Stage')).toBe(labels[index])
      expect(value('Hypothesis')).toBe(' H/alpha ')
      expect(value('Strategy Version')).toBe(' v1+dirty ')
      expect(value('In-sample UTC')).toBe('2024-01-01T00:00:00.123Z → 2024-01-02T00:00:00.456Z')
      expect(value('Validation UTC')).toBe('2024-01-02T00:00:00.456Z → 2024-01-03T00:00:00.789Z')
      expect(value('OOS UTC')).toBe('2024-01-03T00:00:00.789Z → 2024-01-04T00:00:00.000Z')
      expect(value('Trial Index')).toBe('7')
      expect(value('Trial Count')).toBe('3')
      view.unmount()
    }
  })

  it('keeps partial, reversed, and overlapping ranges and exact trial numbers', () => {
    renderHeader({
      run: {
        in_sample_start_ts: 0,
        in_sample_end_ts: null,
        validation_start_ts: null,
        validation_end_ts: 0,
        oos_start_ts: 1000,
        oos_end_ts: 0,
        trial_index: 0,
        trial_count: -2,
      },
    })
    const region = screen.getByRole('region', { name: 'Research identity' })
    const value = (label: string) =>
      [...region.querySelectorAll('dt')].find((term) => term.textContent === label)
        ?.nextElementSibling?.textContent
    expect(value('In-sample UTC')).toBe('1970-01-01T00:00:00.000Z → —')
    expect(value('Validation UTC')).toBe('— → 1970-01-01T00:00:00.000Z')
    expect(value('OOS UTC')).toBe('1970-01-01T00:00:01.000Z → 1970-01-01T00:00:00.000Z')
    expect(value('Trial Index')).toBe('0')
    expect(value('Trial Count')).toBe('-2')
  })
})
