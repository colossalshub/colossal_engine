import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { KpiBlock } from '../../api/types'
import { OverviewSummary } from './OverviewSummary'

function fullKpis(overrides: Partial<KpiBlock> = {}): KpiBlock {
  return {
    sharpe: 1.234,
    sortino: 1.8,
    cagr: 0.152,
    volatility: 0.2,
    max_drawdown: -0.083,
    calmar: 1.9,
    win_rate: 0.6,
    profit_factor: 1.7,
    turnover: 0.5,
    total_trades: 10,
    avg_duration_days: 3.2,
    ...overrides,
  }
}

function card(label: string): HTMLElement {
  const node = screen.getByText(label).closest('.kpi-card')
  expect(node).not.toBeNull()
  return node as HTMLElement
}

describe('OverviewSummary', () => {
  it('shows headline and secondary KPIs together', () => {
    render(<OverviewSummary kpis={fullKpis()} />)

    expect(screen.getByRole('heading', { name: 'Headline' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Secondary' })).toBeInTheDocument()
    expect(screen.queryByRole('tab', { name: 'Returns' })).not.toBeInTheDocument()

    expect(within(card('CAGR')).getByText('15.2%')).toBeInTheDocument()
    expect(within(card('Sharpe')).getByText('1.23')).toBeInTheDocument()
    expect(within(card('Max DD')).getByText('-8.3%')).toBeInTheDocument()
    expect(within(card('Sortino')).getByText('1.80')).toBeInTheDocument()
    expect(within(card('Volatility')).getByText('20.0%')).toBeInTheDocument()
    expect(within(card('Calmar')).getByText('1.90')).toBeInTheDocument()
    expect(within(card('Win Rate')).getByText('60.0%')).toBeInTheDocument()
    expect(within(card('Profit Factor')).getByText('1.70')).toBeInTheDocument()
    expect(within(card('Trades')).getByText('10')).toBeInTheDocument()
    expect(within(card('Avg Duration')).getByText('3.2d')).toBeInTheDocument()
    expect(within(card('Turnover')).getByText('0.50')).toBeInTheDocument()

    expect(within(card('Sharpe')).getByText('1.23').className).toContain('kpi-card__value--pos')
    expect(within(card('Max DD')).getByText('-8.3%').className).toContain('kpi-card__value--neg')
    expect(within(card('Volatility')).getByText('20.0%').className).toContain('kpi-card__value--neutral')
  })

  it('renders nulls as em dashes and omits a null average duration', () => {
    render(
      <OverviewSummary
        kpis={fullKpis({
          sharpe: null,
          cagr: null,
          max_drawdown: null,
          avg_duration_days: null,
        })}
      />,
    )

    expect(within(card('Sharpe')).getByText('—')).toBeInTheDocument()
    expect(within(card('CAGR')).getByText('—')).toBeInTheDocument()
    expect(within(card('Max DD')).getByText('—')).toBeInTheDocument()
    expect(screen.queryByText('Avg Duration')).not.toBeInTheDocument()
    expect(screen.getByText('Turnover')).toBeInTheDocument()
  })

  it('does not add metrics the tear sheet does not supply', () => {
    render(<OverviewSummary kpis={fullKpis()} />)
    expect(screen.queryByText(/cumulative/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/rolling/i)).not.toBeInTheDocument()
  })
})
