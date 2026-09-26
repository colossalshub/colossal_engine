import { screen, waitFor } from '@testing-library/react'
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

describe('StrategyForm', () => {
  afterEach(() => {
    vi.restoreAllMocks()
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
        params: { trade_size: '1', timeframe: '1d', venue: 'binance' },
        universe: ['BTC/USDT'],
        start_ts: expect.any(Number),
        end_ts: expect.any(Number),
      })
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
        params: { trade_size: '1', timeframe: '4h', venue: 'binance' },
        universe: ['BTC/USDT'],
        start_ts: expect.any(Number),
        end_ts: expect.any(Number),
      })
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
