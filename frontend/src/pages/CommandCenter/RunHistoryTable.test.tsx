import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

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
    equity_ts: 'open_then_each_close',
    fill_ts: 'bar_close',
    marker_ts: 'fill',
    fill_included_in_equity: 'same_timestamp',
  },
  artifacts: {},
}

describe('RunHistoryTable', () => {
  beforeEach(() => {
    // jsdom has no layout: give the real grid enough viewport width to render
    // all columns without substituting a grid mock or captured definitions.
    vi.spyOn(HTMLElement.prototype, 'clientWidth', 'get').mockReturnValue(5000)
  })

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

  it('renders metadata verbatim, nulls, mixed stages and experiments in API order', async () => {
    const runs: RunSummary[] = [
      {
        ...sampleRun, run_id: 'explore', name: 'Exploratory trial',
        experiment_id: '  exp-A  ', research_stage: 'exploration',
        hypothesis_id: ' H/alpha ', strategy_version: ' v1+dirty ',
        in_sample_start_ts: 1704067200123, in_sample_end_ts: 1704153600456,
        validation_start_ts: 1704153600456, validation_end_ts: 1704240000789,
        oos_start_ts: 1704240000789, oos_end_ts: 1704326400000,
        trial_index: 7, trial_count: 3,
      },
      { ...sampleRun, run_id: 'validate', name: 'Validation trial', experiment_id: 'exp-B', research_stage: 'validation' },
      { ...sampleRun, run_id: 'holdout', name: 'Holdout trial', experiment_id: '  exp-A  ', research_stage: 'oos' },
      { ...sampleRun, run_id: 'legacy', name: 'Legacy run' },
    ]
    vi.spyOn(runsApi, 'listRuns').mockResolvedValue({ items: runs, total: 4, page: 1, page_size: 50 })
    const { container } = renderWithProviders(<RunHistoryTable />)
    await screen.findByText('Exploratory trial')
    const rows = () => within(container).getAllByRole('row').filter((row) => row.hasAttribute('row-index'))
    const cell = (row: Element, id: string) => row.querySelector(`[col-id="${id}"]`)
    await waitFor(() => expect(rows()).toHaveLength(4))
    expect(rows().map((row) => cell(row, 'name')?.textContent)).toEqual(runs.map((run) => run.name))
    expect(Array.from(container.querySelectorAll('.ag-header-cell-text')).map((el) => el.textContent)).toEqual([
      '', // Existing checkbox-selection column has no header text.
      'Name', 'Experiment', 'Research Stage', 'Hypothesis', 'Strategy Version',
      'In-sample UTC', 'Validation UTC', 'OOS UTC', 'Trial Index', 'Trial Count',
      'Strategy', 'Created', 'Sharpe', 'CAGR', 'Max DD', 'Status',
    ])
    const populated = rows()[0]
    for (const [id, value] of Object.entries({
      experiment_id: '  exp-A  ', research_stage: 'Exploration', hypothesis_id: ' H/alpha ', strategy_version: ' v1+dirty ',
      in_sample: '2024-01-01T00:00:00.123Z → 2024-01-02T00:00:00.456Z',
      validation: '2024-01-02T00:00:00.456Z → 2024-01-03T00:00:00.789Z',
      oos: '2024-01-03T00:00:00.789Z → 2024-01-04T00:00:00.000Z', trial_index: '7', trial_count: '3',
      sharpe: '1.23', cagr: '15.0%', max_drawdown: '-8.0%', status: 'done', strategy: 'buy_hold', created_at: '2024-01-01',
    })) expect(cell(populated, id)?.textContent).toBe(value)
    expect(rows().map((row) => cell(row, 'research_stage')?.textContent)).toEqual(['Exploration', 'Validation', 'OOS', '—'])
    expect(cell(rows()[1], 'experiment_id')?.textContent).toBe('exp-B')
    expect(cell(rows()[2], 'experiment_id')?.textContent).toBe('  exp-A  ')
    for (const id of ['experiment_id', 'research_stage', 'hypothesis_id', 'strategy_version', 'in_sample', 'validation', 'oos', 'trial_index', 'trial_count']) {
      expect(cell(rows()[3], id)?.textContent).toBe('—')
    }
  })

  it('preserves partial epoch endpoints, reversed and overlapping ranges and signed trial numbers', async () => {
    const runs: RunSummary[] = [
      { ...sampleRun, name: 'Partial ranges', in_sample_start_ts: 0, validation_end_ts: 0, oos_start_ts: -1, trial_index: 0, trial_count: -2 },
      { ...sampleRun, run_id: 'reversed', name: 'Reversed ranges', research_stage: 'oos', in_sample_start_ts: 1000, in_sample_end_ts: 0, validation_start_ts: 0, validation_end_ts: 1000, oos_start_ts: 0, oos_end_ts: 1000, trial_index: -5, trial_count: 0 },
    ]
    vi.spyOn(runsApi, 'listRuns').mockResolvedValue({ items: runs, total: 2, page: 1, page_size: 50 })
    const { container } = renderWithProviders(<RunHistoryTable />)
    await screen.findByText('Partial ranges')
    const rows = within(container).getAllByRole('row').filter((row) => row.hasAttribute('row-index'))
    for (const [index, expected] of [
      { in_sample: '1970-01-01T00:00:00.000Z → —', validation: '— → 1970-01-01T00:00:00.000Z', oos: '1969-12-31T23:59:59.999Z → —', trial_index: '0', trial_count: '-2' },
      { in_sample: '1970-01-01T00:00:01.000Z → 1970-01-01T00:00:00.000Z', validation: '1970-01-01T00:00:00.000Z → 1970-01-01T00:00:01.000Z', oos: '1970-01-01T00:00:00.000Z → 1970-01-01T00:00:01.000Z', trial_index: '-5', trial_count: '0' },
    ].entries()) {
      for (const [id, value] of Object.entries(expected)) expect(rows[index].querySelector(`[col-id="${id}"]`)?.textContent).toBe(value)
    }
  })

  it.each(['experiment_id', 'research_stage', 'hypothesis_id', 'strategy_version', 'in_sample', 'validation', 'oos', 'trial_index', 'trial_count'])('sorts the real grid by %s', async (id) => {
    const user = userEvent.setup()
    const runs: RunSummary[] = [
      { ...sampleRun, name: 'Last', experiment_id: 'z', research_stage: 'validation', hypothesis_id: 'z', strategy_version: 'z', in_sample_start_ts: 1000, validation_start_ts: 1000, oos_start_ts: 1000, trial_index: 2, trial_count: 2 },
      { ...sampleRun, run_id: 'first', name: 'First', experiment_id: 'a', research_stage: 'exploration', hypothesis_id: 'a', strategy_version: 'a', in_sample_start_ts: 0, validation_start_ts: 0, oos_start_ts: 0, trial_index: -1, trial_count: -1 },
    ]
    vi.spyOn(runsApi, 'listRuns').mockResolvedValue({ items: runs, total: 2, page: 1, page_size: 50 })
    const { container } = renderWithProviders(<RunHistoryTable />)
    await screen.findByText('Last')
    const header = container.querySelector(`.ag-header-cell[col-id="${id}"]`)!
    await user.click(within(header as HTMLElement).getByText(/.+/))
    await waitFor(() => expect(container.querySelector('[role="row"][row-index="0"] [col-id="name"]')?.textContent).toBe('First'))
    expect(header).toHaveAttribute('aria-sort', 'ascending')
  })

  it('selects distinct run IDs even for a shared experiment and stage', async () => {
    const user = userEvent.setup()
    const onSelectionChange = vi.fn()
    const runs = [sampleRun, { ...sampleRun, run_id: 'r-2', name: 'Second run' }].map((run) => ({ ...run, experiment_id: 'same', research_stage: 'exploration' as const }))
    vi.spyOn(runsApi, 'listRuns').mockResolvedValue({ items: runs, total: 2, page: 1, page_size: 50 })
    const { container } = renderWithProviders(<RunHistoryTable onSelectionChange={onSelectionChange} />)
    await screen.findByText('Second run')
    for (const index of [0, 1]) {
      const row = container.querySelector(`[role="row"][row-index="${index}"]`)!
      await user.click(within(row as HTMLElement).getByRole('checkbox'))
    }
    await waitFor(() => expect(onSelectionChange).toHaveBeenLastCalledWith(['r-1', 'r-2']))
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
