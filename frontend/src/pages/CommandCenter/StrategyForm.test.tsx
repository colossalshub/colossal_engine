import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useLocation } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiClientError } from '../../api/client'
import * as runsApi from '../../api/runs'
import type { RunSummary } from '../../api/types'
import { renderWithProviders } from '../../test-utils'
import { StrategyForm } from './StrategyForm'

const sampleRun: RunSummary = {
  run_id: 'abc',
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
  status: 'queued',
  sharpe: null,
  cagr: null,
  max_drawdown: null,
}

// `renderWithProviders` already wraps a non-<App/> element in an outer
// <Routes> with `/runs/:id` and `*` branches (see test-utils.tsx), both of
// which render this same element. Nesting another <Routes>/<Route> pair
// inside it (matching the same `/runs/:id` path with no trailing `*`)
// triggers a react-router-dom warning and the descendant route never
// re-matches after `navigate()`. Instead, read the current location
// directly so the same harness renders the tear-sheet placeholder once
// navigation lands on `/runs/:id`.
function Harness() {
  const location = useLocation()
  if (location.pathname.startsWith('/runs/')) {
    return <div>Tear sheet {location.pathname}</div>
  }
  return <StrategyForm />
}

function renderForm() {
  return renderWithProviders(<Harness />, { route: '/' })
}

const researchFields = [
  ['experiment_id', 'Experiment ID'],
  ['hypothesis_id', 'Hypothesis ID'],
  ['strategy_version', 'Strategy version'],
  ['in_sample_start_ts', 'In-sample start (UTC)'],
  ['in_sample_end_ts', 'In-sample end (UTC)'],
  ['validation_start_ts', 'Validation start (UTC)'],
  ['validation_end_ts', 'Validation end (UTC)'],
  ['oos_start_ts', 'OOS start (UTC)'],
  ['oos_end_ts', 'OOS end (UTC)'],
  ['trial_index', 'Trial index'],
  ['trial_count', 'Trial count'],
] as const

function fillResearch(label: string, value: string) {
  fireEvent.change(screen.getByLabelText(label), { target: { value } })
}

describe('StrategyForm', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders accessible optional research controls blank with all stage options', () => {
    renderForm()
    const section = screen.getByRole('region', { name: 'Research metadata (optional)' })
    for (const [, label] of researchFields) {
      expect(within(section).getByLabelText(label)).toHaveValue('')
    }
    const stage = within(section).getByLabelText('Research stage')
    expect(stage).toHaveValue('')
    expect(within(stage).getAllByRole('option').map((option) => [option.textContent, (option as HTMLOptionElement).value])).toEqual([
      ['Unset', ''], ['Exploration', 'exploration'], ['Validation', 'validation'], ['OOS', 'oos'],
    ])
  })

  it('submits every research field at top level with trimmed strings and UTC midnight dates', async () => {
    const spy = vi.spyOn(runsApi, 'createRun').mockResolvedValue(sampleRun)
    renderForm()
    fillResearch('Experiment ID', ' experiment-1 ')
    fillResearch('Hypothesis ID', ' hypothesis-1 ')
    fillResearch('Strategy version', ' v2 ')
    fillResearch('Research stage', 'validation')
    const dates = ['2023-01-01', '2023-06-30', '2023-07-01', '2023-12-31', '2024-01-01', '2024-02-29']
    researchFields.slice(3, 9).forEach(([, label], index) => fillResearch(label, dates[index]))
    fillResearch('Trial index', ' 2 ')
    fillResearch('Trial count', ' 10 ')
    fireEvent.click(screen.getByRole('button', { name: /Run/ }))
    await waitFor(() => expect(spy).toHaveBeenCalledOnce())
    const payload = spy.mock.calls[0][0]
    expect(payload).toMatchObject({
      experiment_id: 'experiment-1', hypothesis_id: 'hypothesis-1', strategy_version: 'v2', research_stage: 'validation',
      in_sample_start_ts: 1672531200000, in_sample_end_ts: 1688083200000,
      validation_start_ts: 1688169600000, validation_end_ts: 1703980800000,
      oos_start_ts: 1704067200000, oos_end_ts: 1709164800000,
      trial_index: 2, trial_count: 10,
    })
    for (const [key] of researchFields) expect(payload.params).not.toHaveProperty(key)
    expect(payload.params).not.toHaveProperty('research_stage')
  })

  it.each(['exploration', 'validation', 'oos'])('submits stage %s', async (stage) => {
    const spy = vi.spyOn(runsApi, 'createRun').mockResolvedValue(sampleRun)
    renderForm()
    fillResearch('Research stage', stage)
    fireEvent.click(screen.getByRole('button', { name: /Run/ }))
    await waitFor(() => expect(spy).toHaveBeenCalledWith(expect.objectContaining({ research_stage: stage })))
  })

  it.each(['whitespace', 'cleared'])('omits %s research fields and unset stage', async (mode) => {
    const spy = vi.spyOn(runsApi, 'createRun').mockResolvedValue(sampleRun)
    renderForm()
    for (const [, label] of researchFields) {
      if (mode === 'cleared') fillResearch(label, '2024-01-01')
      fillResearch(label, mode === 'whitespace' ? '   ' : '')
    }
    fillResearch('Research stage', 'oos')
    fillResearch('Research stage', '')
    fireEvent.click(screen.getByRole('button', { name: /Run/ }))
    await waitFor(() => expect(spy).toHaveBeenCalledOnce())
    for (const [key] of researchFields) expect(spy.mock.calls[0][0]).not.toHaveProperty(key)
    expect(spy.mock.calls[0][0]).not.toHaveProperty('research_stage')
  })

  it.each(researchFields.slice(3, 9))('allows the single date endpoint %s', async (key, label) => {
    const spy = vi.spyOn(runsApi, 'createRun').mockResolvedValue(sampleRun)
    renderForm()
    fillResearch(label, '2024-02-29')
    fireEvent.click(screen.getByRole('button', { name: /Run/ }))
    await waitFor(() => expect(spy).toHaveBeenCalledOnce())
    const payload = spy.mock.calls[0][0]
    expect(payload).toHaveProperty(key, 1709164800000)
    for (const [otherKey] of researchFields.slice(3, 9)) {
      if (otherKey !== key) expect(payload).not.toHaveProperty(otherKey)
    }
  })

  it('allows reversed and overlapping research ranges and index greater than count', async () => {
    const spy = vi.spyOn(runsApi, 'createRun').mockResolvedValue(sampleRun)
    renderForm()
    for (const [, label] of researchFields.slice(3, 9)) {
      fillResearch(label, label.includes('start') ? '2025-12-31' : '2023-01-01')
    }
    fillResearch('Trial index', '8')
    fillResearch('Trial count', '2')
    fireEvent.click(screen.getByRole('button', { name: /Run/ }))
    await waitFor(() => expect(spy).toHaveBeenCalledOnce())
    expect(spy.mock.calls[0][0]).toMatchObject({
      in_sample_start_ts: 1767139200000, in_sample_end_ts: 1672531200000,
      validation_start_ts: 1767139200000, validation_end_ts: 1672531200000,
      oos_start_ts: 1767139200000, oos_end_ts: 1672531200000, trial_index: 8, trial_count: 2,
    })
  })

  it.each(['0', '-2', '+3', '9007199254740991', '-9007199254740991'])('accepts safe integer trials %s', async (value) => {
    const spy = vi.spyOn(runsApi, 'createRun').mockResolvedValue(sampleRun)
    renderForm()
    fillResearch('Trial index', value)
    fillResearch('Trial count', value)
    fireEvent.click(screen.getByRole('button', { name: /Run/ }))
    await waitFor(() => expect(spy).toHaveBeenCalledWith(expect.objectContaining({ trial_index: Number(value), trial_count: Number(value) })))
  })

  it.each(['Trial index', 'Trial count'])('rejects invalid nonblank values for %s', async (label) => {
    const spy = vi.spyOn(runsApi, 'createRun')
    renderForm()
    for (const value of ['1.5', 'NaN', 'Infinity', '-Infinity', '9007199254740992', '-9007199254740992', '2junk', '1e2', '0x10', '+']) {
      fillResearch(label, value)
      fireEvent.click(screen.getByRole('button', { name: /Run/ }))
      expect(screen.getByText(`${label} must be a complete safe integer.`)).toBeInTheDocument()
      expect(spy).not.toHaveBeenCalled()
    }
  })

  it.each(researchFields.slice(3, 9))('rejects invalid nonblank dates for %s', async (_key, label) => {
    const spy = vi.spyOn(runsApi, 'createRun')
    renderForm()
    for (const value of ['2024-02-30', '2023-02-29', '2024-13-01', '2024-01-32', 'not-a-date', '2024-1-01']) {
      fillResearch(label, value)
      fireEvent.click(screen.getByRole('button', { name: /Run/ }))
      expect(screen.getByText(`${label}: invalid date. Use YYYY-MM-DD.`)).toBeInTheDocument()
      expect(spy).not.toHaveBeenCalled()
    }
  })

  it('renders with default universe chip "BTC/USDT"', () => {
    renderForm()

    expect(screen.getByText('BTC/USDT')).toBeInTheDocument()
  })

  it('adding a symbol via input + Enter adds a chip', async () => {
    const user = userEvent.setup()
    renderForm()

    const input = screen.getByPlaceholderText('BTC/USDT then Enter')
    await user.type(input, 'ETH/USDT{enter}')

    expect(screen.getByText('ETH/USDT')).toBeInTheDocument()
  })

  it('removing a chip via the × button', async () => {
    const user = userEvent.setup()
    renderForm()

    const removeButton = screen.getByLabelText('Remove BTC/USDT')
    await user.click(removeButton)

    expect(screen.queryByText('BTC/USDT')).not.toBeInTheDocument()
  })

  it('submitting with empty universe shows a client error', async () => {
    const user = userEvent.setup()
    const createRunSpy = vi.spyOn(runsApi, 'createRun')
    renderForm()

    await user.click(screen.getByLabelText('Remove BTC/USDT'))
    await user.click(screen.getByRole('button', { name: /Run/ }))

    expect(screen.getByText('Add at least one symbol.')).toBeInTheDocument()
    expect(createRunSpy).not.toHaveBeenCalled()
  })

  it('start >= end shows a client error', async () => {
    const user = userEvent.setup()
    const createRunSpy = vi.spyOn(runsApi, 'createRun')
    renderForm()

    const dateInputs = screen.getAllByDisplayValue(/\d{4}-\d{2}-\d{2}/)

    await user.clear(dateInputs[0])
    await user.type(dateInputs[0], '2024-12-01')
    await user.clear(dateInputs[1])
    await user.type(dateInputs[1], '2024-01-01')

    await user.click(screen.getByRole('button', { name: /Run/ }))

    expect(
      screen.getByText('Start date must be before end date.'),
    ).toBeInTheDocument()
    expect(createRunSpy).not.toHaveBeenCalled()
  })

  it('valid submit calls createRun with the expected payload', async () => {
    const user = userEvent.setup()
    const createRunSpy = vi
      .spyOn(runsApi, 'createRun')
      .mockResolvedValue(sampleRun)
    renderForm()

    await user.click(screen.getByRole('button', { name: /Run/ }))

    await waitFor(() => {
      expect(createRunSpy).toHaveBeenCalledWith({
        strategy: 'buy_hold',
        params: {
          trade_size: '1',
          deploy_pct: '1',
          timeframe: '1d',
          venue: 'binance',
          maker_fee: '0.001',
          taker_fee: '0.001',
          benchmark_symbol: '',
        },
        universe: ['BTC/USDT'],
        start_ts: expect.any(Number),
        end_ts: expect.any(Number),
      })
    })
  })

  it('changing the fee input updates the payload', async () => {
    const user = userEvent.setup()
    const createRunSpy = vi
      .spyOn(runsApi, 'createRun')
      .mockResolvedValue(sampleRun)
    renderForm()

    const feeInput = screen.getByLabelText('Fee % (each side)')
    await user.clear(feeInput)
    await user.type(feeInput, '0.05')
    await user.click(screen.getByRole('button', { name: /Run/ }))

    await waitFor(() => {
      expect(createRunSpy).toHaveBeenCalledWith({
        strategy: 'buy_hold',
        params: {
          trade_size: '1',
          deploy_pct: '1',
          timeframe: '1d',
          venue: 'binance',
          maker_fee: '0.0005',
          taker_fee: '0.0005',
          benchmark_symbol: '',
        },
        universe: ['BTC/USDT'],
        start_ts: expect.any(Number),
        end_ts: expect.any(Number),
      })
    })
  })

  it('entering a benchmark sends it in params', async () => {
    const user = userEvent.setup()
    const createRunSpy = vi
      .spyOn(runsApi, 'createRun')
      .mockResolvedValue(sampleRun)
    renderForm()

    const benchmarkInput = screen.getByPlaceholderText('e.g. BTC/USDT')
    await user.type(benchmarkInput, 'BTC/USDT')
    await user.click(screen.getByRole('button', { name: /Run/ }))

    await waitFor(() => {
      expect(createRunSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          params: expect.objectContaining({
            benchmark_symbol: 'BTC/USDT',
          }),
        }),
      )
    })
  })

  it('choosing "EMA 9/21" and submitting sends strategy "ema_cross"', async () => {
    const user = userEvent.setup()
    const createRunSpy = vi
      .spyOn(runsApi, 'createRun')
      .mockResolvedValue(sampleRun)
    renderForm()

    await user.selectOptions(screen.getByLabelText('Strategy'), 'ema_cross')
    await user.click(screen.getByRole('button', { name: /Run/ }))

    await waitFor(() => {
      expect(createRunSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          strategy: 'ema_cross',
        }),
      )
    })
  })

  it('changing the timeframe dropdown sends the new value in params', async () => {
    const user = userEvent.setup()
    const createRunSpy = vi
      .spyOn(runsApi, 'createRun')
      .mockResolvedValue(sampleRun)
    renderForm()

    await user.selectOptions(screen.getByLabelText('Timeframe'), '4h')
    await user.click(screen.getByRole('button', { name: /Run/ }))

    await waitFor(() => {
      expect(createRunSpy).toHaveBeenCalledWith({
        strategy: 'buy_hold',
        params: {
          trade_size: '1',
          deploy_pct: '1',
          timeframe: '4h',
          venue: 'binance',
          maker_fee: '0.001',
          taker_fee: '0.001',
          benchmark_symbol: '',
        },
        universe: ['BTC/USDT'],
        start_ts: expect.any(Number),
        end_ts: expect.any(Number),
      })
    })
  })

  it('changing deploy % updates the payload', async () => {
    const user = userEvent.setup()
    const createRunSpy = vi
      .spyOn(runsApi, 'createRun')
      .mockResolvedValue(sampleRun)
    renderForm()

    const deployInput = screen.getByLabelText('% Deployed')
    await user.clear(deployInput)
    await user.type(deployInput, '50')
    await user.click(screen.getByRole('button', { name: /Run/ }))

    await waitFor(() => {
      expect(createRunSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          params: expect.objectContaining({
            deploy_pct: '0.5',
          }),
        }),
      )
    })
  })

  it('on success navigates to /runs/:id', async () => {
    const user = userEvent.setup()
    vi.spyOn(runsApi, 'createRun').mockResolvedValue(sampleRun)
    renderForm()

    await user.click(screen.getByRole('button', { name: /Run/ }))

    await waitFor(() => {
      expect(screen.getByText('Tear sheet /runs/abc')).toBeInTheDocument()
    })
  })

  it('server error renders the message', async () => {
    const user = userEvent.setup()
    vi.spyOn(runsApi, 'createRun').mockRejectedValue(
      new ApiClientError(422, 'VALIDATION', 'universe must contain at least one symbol'),
    )
    renderForm()

    await user.click(screen.getByRole('button', { name: /Run/ }))

    await waitFor(() => {
      expect(
        document.querySelector('.strategy-form__error')?.textContent,
      ).toBe('universe must contain at least one symbol')
    })
  })

  it('submit button is disabled while pending', async () => {
    const user = userEvent.setup()
    vi.spyOn(runsApi, 'createRun').mockReturnValue(new Promise(() => {}))
    renderForm()

    const button = screen.getByRole('button', { name: /Run/ })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Running…' })).toBeDisabled()
    })
  })
})
