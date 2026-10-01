import { afterEach, describe, expect, it, vi } from 'vitest'
import { createRun, getTearsheet, listRuns } from './runs'
import type { ResearchStage, RunCreate, RunList, RunSummary, TearSheet } from './types'

afterEach(() => {
  vi.unstubAllGlobals()
})

const runListBody: RunList = {
  total: 0,
  items: [],
  page: 1,
  page_size: 50,
}

function mockFetchOk(body: unknown = runListBody) {
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(JSON.stringify(body), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }),
  )
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

describe('listRuns', () => {
  it('calls /api/runs with no query string when params omitted', async () => {
    const fetchMock = mockFetchOk()

    const result = await listRuns()

    expect(fetchMock).toHaveBeenCalledWith('/api/runs', {
      method: 'GET',
      headers: { Accept: 'application/json' },
    })
    expect(result).toEqual(runListBody)
  })

  it('calls /api/runs?strategy=buy_hold when strategy is set', async () => {
    const fetchMock = mockFetchOk()

    await listRuns({ strategy: 'buy_hold' })

    expect(fetchMock).toHaveBeenCalledWith('/api/runs?strategy=buy_hold', {
      method: 'GET',
      headers: { Accept: 'application/json' },
    })
  })

  it('calls /api/runs with page and page_size query params', async () => {
    const fetchMock = mockFetchOk()

    await listRuns({ page: 2, page_size: 10 })

    expect(fetchMock).toHaveBeenCalledWith('/api/runs?page=2&page_size=10', {
      method: 'GET',
      headers: { Accept: 'application/json' },
    })
  })

  it('parses response as RunList', async () => {
    mockFetchOk()

    const result = await listRuns()

    expect(result).toEqual(runListBody)
  })
})

const baseCreate: RunCreate = {
  strategy: 'buy_hold', params: { deploy_pct: 50 }, universe: ['BTCUSDT'],
  start_ts: 1704067200000, end_ts: 1735689600000,
}

const baseSummary: RunSummary = {
  run_id: 'research-run', name: 'Research run', strategy: baseCreate.strategy,
  universe: baseCreate.universe, start_ts: baseCreate.start_ts, end_ts: baseCreate.end_ts,
  created_at: 1735689600000, git_sha: null, git_dirty: false, experiment_id: null,
  research_stage: null, hypothesis_id: null, strategy_version: null,
  in_sample_start_ts: null, in_sample_end_ts: null, validation_start_ts: null,
  validation_end_ts: null, oos_start_ts: null, oos_end_ts: null, trial_index: null, trial_count: null,
  status: 'queued', sharpe: null, cagr: null, max_drawdown: null,
}

const researchMetadata = {
  experiment_id: 'experiment-1', research_stage: 'validation', hypothesis_id: 'hypothesis-1',
  strategy_version: 'v1', in_sample_start_ts: 1704067200000, in_sample_end_ts: 1711929600000,
  validation_start_ts: 1711929600000, validation_end_ts: 1719792000000,
  oos_start_ts: 1719792000000, oos_end_ts: 1735689600000, trial_index: 2, trial_count: 5,
} satisfies RunCreateMetadata

interface RunCreateMetadata extends Pick<RunCreate,
  'experiment_id' | 'research_stage' | 'hypothesis_id' | 'strategy_version' |
  'in_sample_start_ts' | 'in_sample_end_ts' | 'validation_start_ts' | 'validation_end_ts' |
  'oos_start_ts' | 'oos_end_ts' | 'trial_index' | 'trial_count'> {}

const nullMetadata = {
  experiment_id: null, research_stage: null, hypothesis_id: null, strategy_version: null,
  in_sample_start_ts: null, in_sample_end_ts: null, validation_start_ts: null,
  validation_end_ts: null, oos_start_ts: null, oos_end_ts: null, trial_index: null, trial_count: null,
} satisfies RunCreateMetadata

describe('research metadata wire contracts', () => {
  it.each([researchMetadata, nullMetadata])('preserves top-level create metadata %j', async (metadata) => {
    const payload: RunCreate = { ...baseCreate, ...metadata }
    const response: RunSummary = { ...baseSummary, ...metadata }
    const fetchMock = mockFetchOk(response)

    const result = await createRun(payload)

    expect(fetchMock).toHaveBeenCalledWith('/api/runs', {
      method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...baseCreate, ...metadata }),
    })
    expect(payload.params).toEqual({ deploy_pct: 50 })
    expect(result).toEqual(response)
  })

  it('supports omitted request metadata and explicit null response metadata', async () => {
    const fetchMock = mockFetchOk(baseSummary)
    const result = await createRun(baseCreate)

    expect(fetchMock).toHaveBeenCalledWith('/api/runs', {
      method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify(baseCreate),
    })
    expect(result).toEqual(baseSummary)
    for (const key of Object.keys(researchMetadata)) {
      expect(baseCreate).not.toHaveProperty(key)
      expect(result).toHaveProperty(key, null)
    }
  })

  it.each([researchMetadata, nullMetadata])('preserves metadata in run lists %j', async (metadata) => {
    const body: RunList = { ...runListBody, total: 1, items: [{ ...baseSummary, ...metadata }] }
    mockFetchOk(body)

    expect(await listRuns()).toEqual(body)
  })

  it.each([researchMetadata, nullMetadata])('preserves tear-sheet run metadata %j', async (metadata) => {
    const body: TearSheet = {
      run: { ...baseSummary, ...metadata }, params: baseCreate.params,
      kpis: { sharpe: null, sortino: null, cagr: null, volatility: null, max_drawdown: null,
        calmar: null, win_rate: null, profit_factor: null, turnover: null,
        total_trades: null, avg_duration_days: null },
      equity: [], drawdown: [], price: [], markers: [], monthly_returns: [], artifacts: {},
      verification: { verified: false, discrepancy_pct: 0, source: 'self_consistent' },
      execution_assumptions: {
        bar_ts: '', nautilus_bar_ts_event: '', signal_and_order: '', order_type: '',
        sizing_price_when_deploy_pct_positive: '', maker_fee_default: '', taker_fee_default: '',
        maker_fee: '', taker_fee: '', fill_model: '', latency: '', spread: '', queue_model: '',
        partial_fills: '', equity_ts: '', fill_ts: '', marker_ts: '', fill_included_in_equity: '',
      },
    }
    const fetchMock = mockFetchOk(body)

    expect(await getTearsheet(baseSummary.run_id)).toEqual(body)
    expect(fetchMock).toHaveBeenCalledWith('/api/runs/research-run/tearsheet', {
      method: 'GET', headers: { Accept: 'application/json' },
    })
  })

  it('rejects incomplete response metadata at compile time', () => {
    const { research_stage, ...incompleteSummary } = baseSummary
    // @ts-expect-error RunSummary requires research_stage even when its value is null.
    const missingStage: RunSummary = incompleteSummary
    const incompleteMetadata: Omit<RunSummary, keyof RunCreateMetadata> = {
      run_id: baseSummary.run_id, name: baseSummary.name, strategy: baseSummary.strategy,
      universe: baseSummary.universe, start_ts: baseSummary.start_ts, end_ts: baseSummary.end_ts,
      created_at: baseSummary.created_at, git_sha: null, git_dirty: false,
      status: 'queued', sharpe: null, cagr: null, max_drawdown: null,
    }
    // @ts-expect-error RunSummary requires all research metadata keys.
    const missingMetadata: RunSummary = incompleteMetadata

    expect(research_stage).toBeNull()
    expect(missingStage).not.toHaveProperty('research_stage')
    expect(missingMetadata).not.toHaveProperty('trial_count')
  })

  it('typechecks all supported stages and rejects unsupported literals at compile time', () => {
    const stages: ResearchStage[] = ['exploration', 'validation', 'oos']
    const requests: RunCreate[] = stages.map((research_stage) => ({ ...baseCreate, research_stage }))
    const summaries: RunSummary[] = stages.map((research_stage) => ({ ...baseSummary, research_stage }))
    // @ts-expect-error ResearchStage excludes unsupported stage literals.
    const unsupportedStage: ResearchStage = 'holdout'
    // @ts-expect-error RunCreate also excludes unsupported stage literals.
    const unsupportedRequest: RunCreate = { ...baseCreate, research_stage: 'holdout' }
    // @ts-expect-error RunSummary also excludes unsupported stage literals.
    const unsupportedSummary: RunSummary = { ...baseSummary, research_stage: 'holdout' }

    expect(requests.map((request) => request.research_stage)).toEqual(stages)
    expect(summaries.map((summary) => summary.research_stage)).toEqual(stages)
    // These values exist at runtime: the wire types do not perform runtime validation.
    expect(unsupportedStage).toBe('holdout')
    expect(unsupportedRequest.research_stage).toBe('holdout')
    expect(unsupportedSummary.research_stage).toBe('holdout')
  })
})
