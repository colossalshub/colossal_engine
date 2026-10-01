import { render, screen, within } from '@testing-library/react'
import { MemoryRouter, Outlet, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import type { KpiBlock, TearSheet } from '../../../api/types'
import RiskTab from './RiskTab'

vi.mock('../DrawdownChart', () => ({
  DrawdownChart: ({ data }: { data: TearSheet['drawdown'] }) => (
    <div data-testid="drawdown-chart">{JSON.stringify(data)}</div>
  ),
}))

function fullKpis(overrides: Partial<KpiBlock> = {}): KpiBlock {
  return {
    sharpe: 1.23,
    sortino: 1.8,
    cagr: 0.15,
    volatility: 0.2,
    max_drawdown: -0.08,
    calmar: 1.9,
    win_rate: 0.6,
    profit_factor: 1.7,
    turnover: 0.5,
    total_trades: 10,
    avg_duration_days: 3.2,
    ...overrides,
  }
}

function renderTab(kpis: KpiBlock) {
  const data = {
    kpis,
    drawdown: [{ ts: 1704067200000, dd: -0.08 }],
  } as TearSheet
  render(
    <MemoryRouter>
      <Routes>
        <Route element={<Outlet context={{ data, runId: 'r-1' }} />}>
          <Route index element={<RiskTab />} />
        </Route>
      </Routes>
    </MemoryRouter>,
  )
}

function card(label: string): HTMLElement {
  const node = screen.getByText(label).closest('.kpi-card')
  expect(node).not.toBeNull()
  return node as HTMLElement
}

describe('RiskTab', () => {
  it('shows supplied risk KPIs and the existing drawdown series', () => {
    renderTab(fullKpis())

    expect(within(card('Sharpe')).getByText('1.23')).toBeInTheDocument()
    expect(within(card('Sortino')).getByText('1.80')).toBeInTheDocument()
    expect(within(card('Volatility')).getByText('20.0%')).toBeInTheDocument()
    expect(within(card('Max DD')).getByText('-8.0%')).toBeInTheDocument()
    expect(within(card('Calmar')).getByText('1.90')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Underwater' })).toBeInTheDocument()
    expect(screen.getByTestId('drawdown-chart')).toHaveTextContent(
      '[{"ts":1704067200000,"dd":-0.08}]',
    )
    expect(screen.queryByText(/Ulcer/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/recovery factor/i)).not.toBeInTheDocument()
  })

  it('renders all null risk KPIs as em dashes', () => {
    renderTab(
      fullKpis({
        sharpe: null,
        sortino: null,
        volatility: null,
        max_drawdown: null,
        calmar: null,
      }),
    )

    expect(screen.getAllByText('—')).toHaveLength(5)
  })
})
