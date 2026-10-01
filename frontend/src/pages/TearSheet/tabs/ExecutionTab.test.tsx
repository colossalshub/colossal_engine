import { render, screen } from '@testing-library/react'
import { MemoryRouter, Outlet, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import type { ExecutionAssumptions, TearSheet } from '../../../api/types'
import ExecutionTab from './ExecutionTab'

const assumptions: ExecutionAssumptions = {
  bar_ts: 'open',
  nautilus_bar_ts_event: 'close',
  signal_and_order: 'on_bar',
  order_type: 'market',
  sizing_price_when_deploy_pct_positive: 'bar.close',
  maker_fee_default: '0.001',
  taker_fee_default: '0.002',
  maker_fee: '0.001',
  taker_fee: '0.002',
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

function renderTab(value: unknown) {
  const data = { execution_assumptions: value } as TearSheet
  render(
    <MemoryRouter>
      <Routes>
        <Route element={<Outlet context={{ data, runId: 'r-1' }} />}>
          <Route index element={<ExecutionTab />} />
        </Route>
      </Routes>
    </MemoryRouter>,
  )
}

describe('ExecutionTab', () => {
  it('shows each assumption string verbatim', () => {
    renderTab(assumptions)

    const expected: [string, string][] = [
      ['Bar time', 'open'],
      ['Nautilus bar event', 'close'],
      ['Signal and order', 'on_bar'],
      ['Order type', 'market'],
      ['Sizing price', 'bar.close'],
      ['Maker fee', '0.001'],
      ['Taker fee', '0.002'],
      ['Default maker fee', '0.001'],
      ['Default taker fee', '0.002'],
      ['Fill model', 'not_passed'],
      ['Latency', 'not_passed'],
      ['Spread', 'not_passed'],
      ['Queue', 'not_passed'],
      ['Partial fills', 'not_passed'],
      ['Equity time', 'open_then_each_close'],
      ['Fill time', 'bar_close'],
      ['Marker time', 'fill'],
      ['Fill included in equity', 'same_timestamp'],
    ]
    for (const [label, value] of expected) {
      expect(screen.getByText(label).nextElementSibling).toHaveTextContent(value)
    }
    expect(screen.queryByText('0.003')).not.toBeInTheDocument()
    expect(screen.queryByText(/gross/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/funding/i)).not.toBeInTheDocument()
  })

  it('says the assumptions are missing once', () => {
    renderTab(undefined)
    expect(
      screen.getByText('Execution assumptions are not on this response.'),
    ).toBeInTheDocument()
    expect(screen.queryByText('Maker fee')).not.toBeInTheDocument()
  })
})
