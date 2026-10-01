import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { KpiBlock } from '../../api/types'
import { TradesSummary } from './TradesSummary'

function kpis(overrides: Partial<KpiBlock> = {}): KpiBlock {
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

describe('TradesSummary', () => {
  it('shows the closed-trade KPIs with the existing formatters', () => {
    render(<TradesSummary kpis={kpis()} />)

    expect(within(card('Trades')).getByText('10')).toBeInTheDocument()
    expect(within(card('Win Rate')).getByText('60.0%')).toBeInTheDocument()
    expect(within(card('Profit Factor')).getByText('1.70')).toBeInTheDocument()
    expect(within(card('Avg Duration')).getByText('3.2d')).toBeInTheDocument()
    expect(within(card('Win Rate')).getByText('60.0%').className).toContain(
      'kpi-card__value--neutral',
    )
  })

  it('renders nulls as em dashes and omits a null average duration', () => {
    render(
      <TradesSummary
        kpis={kpis({
          total_trades: null,
          win_rate: null,
          profit_factor: null,
          avg_duration_days: null,
        })}
      />,
    )

    expect(within(card('Trades')).getByText('—')).toBeInTheDocument()
    expect(within(card('Win Rate')).getByText('—')).toBeInTheDocument()
    expect(within(card('Profit Factor')).getByText('—')).toBeInTheDocument()
    expect(screen.queryByText('Avg Duration')).not.toBeInTheDocument()
  })

  it('keeps a zero average duration', () => {
    render(<TradesSummary kpis={kpis({ avg_duration_days: 0 })} />)
    expect(within(card('Avg Duration')).getByText('0.0d')).toBeInTheDocument()
  })

  it('does not invent trade-path statistics', () => {
    render(<TradesSummary kpis={kpis()} />)
    expect(screen.queryByText(/MAE/)).not.toBeInTheDocument()
    expect(screen.queryByText(/MFE/)).not.toBeInTheDocument()
    expect(screen.queryByText(/R-multiple/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/expectancy/i)).not.toBeInTheDocument()
    expect(screen.queryByText('Sharpe')).not.toBeInTheDocument()
  })
})
