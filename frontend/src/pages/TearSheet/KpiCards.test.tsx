import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { KpiBlock } from '../../api/types'
import { KpiCards } from './KpiCards'

function fullKpis(overrides: Partial<KpiBlock> = {}): KpiBlock {
  return {
    sharpe: 0,
    sortino: 0,
    cagr: 0,
    volatility: 0,
    max_drawdown: 0,
    calmar: 0,
    win_rate: 0,
    profit_factor: 0,
    turnover: 0,
    total_trades: 0,
    avg_duration_days: 0,
    ...overrides,
  }
}

describe('KpiCards', () => {
  it('renders all 11 labels', () => {
    render(<KpiCards kpis={fullKpis()} />)
    const labels = [
      'Sharpe',
      'Sortino',
      'CAGR',
      'Volatility',
      'Max DD',
      'Calmar',
      'Win Rate',
      'Profit Factor',
      'Turnover',
      'Trades',
      'Avg Duration',
    ]
    for (const label of labels) {
      expect(screen.getByText(label)).toBeInTheDocument()
    }
  })

  it('formats a positive Sharpe', () => {
    render(<KpiCards kpis={fullKpis({ sharpe: 1.234 })} />)
    const card = screen.getByText('Sharpe').closest('.kpi-card')
    expect(card).not.toBeNull()
    expect(within(card as HTMLElement).getByText('1.23')).toBeInTheDocument()
  })

  it('formats CAGR as a percentage', () => {
    render(<KpiCards kpis={fullKpis({ cagr: 0.152 })} />)
    const card = screen.getByText('CAGR').closest('.kpi-card')
    expect(card).not.toBeNull()
    expect(within(card as HTMLElement).getByText('15.2%')).toBeInTheDocument()
  })

  it('formats max drawdown as a negative percentage', () => {
    render(<KpiCards kpis={fullKpis({ max_drawdown: -0.083 })} />)
    const card = screen.getByText('Max DD').closest('.kpi-card')
    expect(card).not.toBeNull()
    expect(within(card as HTMLElement).getByText('-8.3%')).toBeInTheDocument()
  })

  it('nulls render as em dash', () => {
    render(<KpiCards kpis={fullKpis({ sharpe: null })} />)
    const card = screen.getByText('Sharpe').closest('.kpi-card')
    expect(card).not.toBeNull()
    expect(within(card as HTMLElement).getByText('—')).toBeInTheDocument()
  })

  it('positive Sharpe gets the pos tone class', () => {
    render(<KpiCards kpis={fullKpis({ sharpe: 1.23 })} />)
    const card = screen.getByText('Sharpe').closest('.kpi-card')
    expect(card).not.toBeNull()
    const value = within(card as HTMLElement).getByText('1.23')
    expect(value.className).toContain('kpi-card__value--pos')
  })

  it('negative max drawdown gets the neg tone class', () => {
    render(<KpiCards kpis={fullKpis({ max_drawdown: -0.083 })} />)
    const card = screen.getByText('Max DD').closest('.kpi-card')
    expect(card).not.toBeNull()
    const value = within(card as HTMLElement).getByText('-8.3%')
    expect(value.className).toContain('kpi-card__value--neg')
  })

  it('total trades renders as integer', () => {
    render(<KpiCards kpis={fullKpis({ total_trades: 10.0 })} />)
    const card = screen.getByText('Trades').closest('.kpi-card')
    expect(card).not.toBeNull()
    expect(within(card as HTMLElement).getByText('10')).toBeInTheDocument()
  })

  it('avg duration renders with d suffix', () => {
    render(<KpiCards kpis={fullKpis({ avg_duration_days: 3.2 })} />)
    const card = screen.getByText('Avg Duration').closest('.kpi-card')
    expect(card).not.toBeNull()
    expect(within(card as HTMLElement).getByText('3.2d')).toBeInTheDocument()
  })
})
