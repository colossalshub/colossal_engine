import { screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import * as runsApi from '../../api/runs'
import type { TearSheet } from '../../api/types'
import { renderWithProviders } from '../../test-utils'
import App from '../../App'

vi.mock('../../components/charts/BaseChart', () => ({
  BaseChart: ({ height }: { height: number }) => (
    <div className="base-chart" style={{ height }} />
  ),
}))

class ResizeObserverStub implements ResizeObserver {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

globalThis.ResizeObserver = ResizeObserverStub

const defaultExecutionAssumptions = {
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
}

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
    experiment_id: null,
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
  execution_assumptions: defaultExecutionAssumptions,
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
    renderWithProviders(<App />, { route: '/runs/r-1/overview' })
    await waitFor(() => {
      expect(screen.getByText('buy_hold BTC/USDT 1d')).toBeInTheDocument()
    })
    expect(screen.getByText('done')).toBeInTheDocument()
  })

  it('renders the universe and formatted date range', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    renderWithProviders(<App />, { route: '/runs/r-1/overview' })
    await waitFor(() => {
      expect(screen.getByText('BTC/USDT')).toBeInTheDocument()
    })
    expect(screen.getByText('only first symbol executed')).toBeInTheDocument()
    expect(screen.queryByText('ETH/USDT')).not.toBeInTheDocument()
    expect(screen.getByText('2024-01-01 → 2024-01-31')).toBeInTheDocument()
  })

  it('multi-symbol universe renders the note', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue({
      ...sampleTearsheet,
      run: {
        ...sampleTearsheet.run,
        universe: ['BTC/USDT', 'ETH/USDT'],
      },
    })
    renderWithProviders(<App />, { route: '/runs/r-1/overview' })
    await waitFor(() => {
      expect(screen.getByText('BTC/USDT')).toBeInTheDocument()
    })
    expect(screen.getByText('only first symbol executed')).toBeInTheDocument()
    expect(screen.queryByText('ETH/USDT')).not.toBeInTheDocument()
  })

  it('displays fees when params contain maker_fee', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue({
      ...sampleTearsheet,
      params: { maker_fee: '0.001' },
    })
    renderWithProviders(<App />, { route: '/runs/r-1/overview' })
    await waitFor(() => {
      expect(screen.getByText('fees 0.10%')).toBeInTheDocument()
    })
  })

  it('displays benchmark when params contain it', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue({
      ...sampleTearsheet,
      params: { benchmark_symbol: 'BTC/USDT' },
    })
    renderWithProviders(<App />, { route: '/runs/r-1/overview' })
    await waitFor(() => {
      expect(screen.getByText('benchmark BTC/USDT')).toBeInTheDocument()
    })
  })

  it('renders the short git sha', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    renderWithProviders(<App />, { route: '/runs/r-1/overview' })
    await waitFor(() => {
      expect(screen.getByText(/git abcdef1/)).toBeInTheDocument()
    })
  })

  it('overview tab renders the executive summary', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    renderWithProviders(<App />, { route: '/runs/r-1/overview' })
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Headline' })).toBeInTheDocument()
    })
    expect(screen.getByRole('heading', { name: 'Secondary' })).toBeInTheDocument()
    const headline = screen.getByRole('heading', { name: 'Headline' }).closest('section')
    const secondary = screen.getByRole('heading', { name: 'Secondary' }).closest('section')
    expect(headline).not.toBeNull()
    expect(secondary).not.toBeNull()
    for (const label of ['CAGR', 'Sharpe', 'Max DD']) {
      expect(within(headline as HTMLElement).getByText(label)).toBeInTheDocument()
    }
    for (const label of [
      'Sortino',
      'Volatility',
      'Calmar',
      'Profit Factor',
      'Turnover',
    ]) {
      expect(within(secondary as HTMLElement).getByText(label)).toBeInTheDocument()
    }
    expect(screen.queryByRole('tab', { name: 'Returns' })).not.toBeInTheDocument()
    expect(within(secondary as HTMLElement).queryByText('Win Rate')).not.toBeInTheDocument()
    expect(within(secondary as HTMLElement).queryByText('Trades')).not.toBeInTheDocument()
    expect(within(secondary as HTMLElement).queryByText('Avg Duration')).not.toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Equity' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Underwater' })).not.toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Monthly Returns' })).toBeInTheDocument()
    expect(screen.getByText('No equity data for this run.')).toBeInTheDocument()
    expect(screen.queryByText('No drawdown data for this run.')).not.toBeInTheDocument()
  })

  it('performance tab renders price then a dominant equity chart without underwater', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue({
      ...sampleTearsheet,
      price: [{ ts: 1704067200000, open: 1, high: 2, low: 1, close: 1.5, volume: 1 }],
      equity: [{ ts: 1704067200000, equity: 100, benchmark: null }],
      drawdown: [{ ts: 1704067200000, dd: -0.1 }],
    })
    renderWithProviders(<App />, { route: '/runs/r-1/performance' })
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Price + Fills' })).toBeInTheDocument()
    })
    const price = screen.getByRole('heading', { name: 'Price + Fills' })
    const equity = screen.getByRole('heading', { name: 'Equity' })
    expect(price.compareDocumentPosition(equity) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(equity.closest('section')?.parentElement).not.toHaveClass('tear-sheet-tab__grid-2')
    const charts = document.querySelectorAll('.base-chart')
    expect(charts).toHaveLength(2)
    expect(charts[0]).toHaveStyle({ height: '420px' })
    expect(charts[1]).toHaveStyle({ height: '420px' })
    expect(screen.queryByRole('heading', { name: 'Underwater' })).not.toBeInTheDocument()
    expect(screen.queryByText(/rolling/i)).not.toBeInTheDocument()
  })

  it('trades tab renders the trade ledger', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    vi.spyOn(runsApi, 'getTrades').mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 50,
    })
    renderWithProviders(<App />, { route: '/runs/r-1/trades' })
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Closed trades' })).toBeInTheDocument()
    })
    const summary = screen.getByRole('heading', { name: 'Closed trades' })
    const ledger = screen.getByRole('heading', { name: 'Trade Ledger' })
    expect(summary.compareDocumentPosition(ledger) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(within(summary.closest('section') as HTMLElement).getByText('Win Rate')).toBeInTheDocument()
    expect(within(summary.closest('section') as HTMLElement).getByText('60.0%')).toBeInTheDocument()
    expect(screen.queryByText(/MAE/)).not.toBeInTheDocument()
    expect(screen.queryByText(/MFE/)).not.toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText('No trades generated for this period.')).toBeInTheDocument()
    })
  })

  it('data tab shows execution assumptions from tear sheet', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue({
      ...sampleTearsheet,
      params: { maker_fee: '0.002' },
      execution_assumptions: {
        ...defaultExecutionAssumptions,
        maker_fee: '0.009',
        taker_fee: '0.008',
      },
    })
    renderWithProviders(<App />, { route: '/runs/r-1/data' })
    await waitFor(() => {
      expect(screen.getByText('buy_hold')).toBeInTheDocument()
    })
    expect(
      screen.queryByText('Full methodology header arrives in Phase U.3.2'),
    ).not.toBeInTheDocument()
    expect(screen.queryByText('Strategy version')).not.toBeInTheDocument()
    expect(screen.queryByText('Dataset identity')).not.toBeInTheDocument()
    const methodology = screen.getByRole('heading', { name: 'Data & Methodology' }).closest('section')
    expect(methodology).not.toBeNull()
    expect(within(methodology as HTMLElement).queryByText('Experiment ID')).not.toBeInTheDocument()
    expect(within(methodology as HTMLElement).getByText('Date range').nextElementSibling).toHaveTextContent(
      '2024-01-01 → 2024-01-31',
    )
    expect(screen.getByText('abcdef1234567890')).toBeInTheDocument()
    expect(screen.getByText('—')).toBeInTheDocument()
    expect(screen.getByText('maker 0.009 · taker 0.008')).toBeInTheDocument()
    expect(screen.getByText('none')).toBeInTheDocument()
    expect(screen.getAllByText(/Equity verified \(self-consistent\)/)).toHaveLength(2)
    expect(screen.getByText('0.009')).toBeInTheDocument()
    expect(screen.getByText('0.008')).toBeInTheDocument()
    expect(screen.getByText('open')).toBeInTheDocument()
    expect(screen.getByText('market')).toBeInTheDocument()
    expect(screen.getByText('not_passed')).toBeInTheDocument()
    expect(screen.queryByText('on_bar')).not.toBeInTheDocument()
    expect(screen.getByText('fees 0.20%')).toBeInTheDocument()
    const clock = screen.getByRole('heading', { name: 'Clock' }).closest('section')
    expect(clock).not.toBeNull()
    expect(within(clock as HTMLElement).getByText('open_then_each_close')).toBeInTheDocument()
    expect(within(clock as HTMLElement).getByText('bar_close')).toBeInTheDocument()
    expect(within(clock as HTMLElement).getByText('fill')).toBeInTheDocument()
    expect(within(clock as HTMLElement).getByText('same_timestamp')).toBeInTheDocument()
    const execution = screen.getByRole('heading', { name: 'Execution assumptions' }).closest('section')
    expect(execution).not.toBeNull()
    expect(within(execution as HTMLElement).getByText('Maker fee')).toBeInTheDocument()
    expect(within(execution as HTMLElement).queryByText('Equity time')).not.toBeInTheDocument()
  })

  it('data tab methodology header shows timeframe, benchmark, and dirty git', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue({
      ...sampleTearsheet,
      run: {
        ...sampleTearsheet.run,
        git_sha: null,
        git_dirty: true,
      },
      params: { timeframe: '1d', benchmark_symbol: '  ETH/USDT  ' },
    })
    renderWithProviders(<App />, { route: '/runs/r-1/data' })
    await waitFor(() => {
      expect(screen.getByText('1d')).toBeInTheDocument()
    })
    expect(screen.getByText('ETH/USDT')).toBeInTheDocument()
    expect(screen.getByText('Git SHA').nextElementSibling).toHaveTextContent('—')
    expect(screen.queryByText(/\(dirty\)/)).not.toBeInTheDocument()
  })

  it('data tab renders a non-null experiment id', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue({
      ...sampleTearsheet,
      run: {
        ...sampleTearsheet.run,
        experiment_id: 'experiment-42',
      },
    })
    renderWithProviders(<App />, { route: '/runs/r-1/data' })
    await waitFor(() => {
      expect(screen.getByText('Experiment ID').nextElementSibling).toHaveTextContent(
        'experiment-42',
      )
    })
  })

  it('data tab stays up when the tear sheet omits execution assumptions', async () => {
    const sheet: TearSheet = { ...sampleTearsheet }
    delete (sheet as { execution_assumptions?: TearSheet['execution_assumptions'] })
      .execution_assumptions
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sheet)
    renderWithProviders(<App />, { route: '/runs/r-1/data' })
    await waitFor(() => {
      expect(screen.getByText('buy_hold')).toBeInTheDocument()
    })
    expect(screen.getByText('Fees').nextElementSibling).toHaveTextContent('—')
    expect(
      screen.getByText('Execution assumptions are not on this response.'),
    ).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Clock' })).not.toBeInTheDocument()
    expect(
      screen.queryByText('Something went wrong rendering this page.'),
    ).not.toBeInTheDocument()
  })

  it('data tab methodology header appends dirty when a git sha is present', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue({
      ...sampleTearsheet,
      run: {
        ...sampleTearsheet.run,
        git_sha: 'deadbeef',
        git_dirty: true,
      },
    })
    renderWithProviders(<App />, { route: '/runs/r-1/data' })
    await waitFor(() => {
      expect(screen.getByText('deadbeef (dirty)')).toBeInTheDocument()
    })
  })

  it('regimes tab says classification is not attached', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    renderWithProviders(<App />, { route: '/runs/r-1/regimes' })
    await waitFor(() => {
      expect(
        screen.getByText(
          'Not available for this run. No regime classification is attached to this result.',
        ),
      ).toBeInTheDocument()
    })
    expect(screen.queryByText(/Monte Carlo/i)).not.toBeInTheDocument()
  })

  it('robustness tab says no analysis is attached', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    renderWithProviders(<App />, { route: '/runs/r-1/robustness' })
    await waitFor(() => {
      expect(
        screen.getByText('No robustness analysis is attached to this run.'),
      ).toBeInTheDocument()
    })
    expect(screen.queryByText(/walk-forward/i)).not.toBeInTheDocument()
  })

  it('execution tab shows assumption strings from the tear sheet', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    renderWithProviders(<App />, { route: '/runs/r-1/execution' })
    await waitFor(() => {
      expect(screen.getByText('Signal and order').nextElementSibling).toHaveTextContent('on_bar')
    })
    expect(screen.getByText('Latency').nextElementSibling).toHaveTextContent('not_passed')
    expect(screen.queryByText(/gross P&L/i)).not.toBeInTheDocument()
  })

  it('nav rail renders all eight items in research-review order', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    renderWithProviders(<App />, { route: '/runs/r-1/overview' })
    const nav = await screen.findByRole('navigation', { name: 'Tear sheet sections' })
    const links = within(nav).getAllByRole('link')
    expect(links).toHaveLength(8)
    const labels = [
      'Overview',
      'Performance',
      'Trades',
      'Risk',
      'Regimes',
      'Execution',
      'Robustness',
      'Data',
    ]
    expect(links.map((link) => link.textContent?.split('Phase')[0])).toEqual(labels)
    expect(within(nav).getByRole('link', { name: 'Execution' })).toBeInTheDocument()
    expect(within(nav).getByRole('link', { name: /^Regimes.*Phase 21/ })).toBeInTheDocument()
    expect(within(nav).getByRole('link', { name: /^Robustness.*Phase 18–20/ })).toBeInTheDocument()
  })

  it('routes to Risk and marks it as the active nav item', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    renderWithProviders(<App />, { route: '/runs/r-1/risk' })
    const nav = await screen.findByRole('navigation', { name: 'Tear sheet sections' })
    expect(screen.getByRole('heading', { name: 'Risk metrics' })).toBeInTheDocument()
    expect(within(nav).getByRole('link', { name: 'Risk' })).toHaveClass(
      'tear-sheet-nav__item--active',
    )
    expect(within(nav).getByRole('link', { name: /^Overview/ })).not.toHaveClass(
      'tear-sheet-nav__item--active',
    )
  })

  it('index route redirects to overview', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockResolvedValue(sampleTearsheet)
    renderWithProviders(<App />, { route: '/runs/r-1' })
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Monthly Returns' })).toBeInTheDocument()
    })
    const nav = screen.getByRole('navigation', { name: 'Tear sheet sections' })
    expect(within(nav).getByRole('link', { name: /^Overview/ })).toHaveClass(
      'tear-sheet-nav__item--active',
    )
  })
  it('shows a loading state before data resolves', () => {
    vi.spyOn(runsApi, 'getTearsheet').mockImplementation(
      () => new Promise(() => {}),
    )
    renderWithProviders(<App />, { route: '/runs/r-1/overview' })
    expect(screen.getByText('Loading tear sheet…')).toBeInTheDocument()
  })

  it('shows an error state when the fetch fails', async () => {
    vi.spyOn(runsApi, 'getTearsheet').mockRejectedValue(new Error('boom'))
    renderWithProviders(<App />, { route: '/runs/r-1/overview' })
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

      renderWithProviders(<App />, { route: '/runs/r-1/overview' })

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

      renderWithProviders(<App />, { route: '/runs/r-1/overview' })

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
    renderWithProviders(<App />, { route: '/runs/r-1/overview' })
    await waitFor(() => {
      expect(screen.getByText('Backtest in progress…')).toBeInTheDocument()
    })
    expect(screen.queryByText('KPIs')).not.toBeInTheDocument()
    expect(screen.queryByText('Price + Fills')).not.toBeInTheDocument()
  })
})


