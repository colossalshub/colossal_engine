import { fireEvent, render, screen, within } from '@testing-library/react'
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

function openGroup(name: string): void {
  fireEvent.click(screen.getByRole('tab', { name }))
}

describe('KpiCards', () => {
  it('opens Returns and shows one group at a time', () => {
    render(<KpiCards kpis={fullKpis()} />)
    expect(screen.getByRole('tab', { name: 'Returns', selected: true })).toBeInTheDocument()
    expect(screen.getByText('CAGR')).toBeInTheDocument()
    expect(screen.queryByText('Sharpe')).not.toBeInTheDocument()
    expect(screen.queryByText('Win Rate')).not.toBeInTheDocument()
    expect(screen.queryByText('Turnover')).not.toBeInTheDocument()

    openGroup('Risk')
    expect(screen.getByRole('tab', { name: 'Risk', selected: true })).toBeInTheDocument()
    expect(screen.queryByText('CAGR')).not.toBeInTheDocument()
    for (const label of ['Sharpe', 'Sortino', 'Volatility', 'Max DD', 'Calmar']) {
      expect(screen.getByText(label)).toBeInTheDocument()
    }

    openGroup('Trading')
    expect(screen.queryByText('Sharpe')).not.toBeInTheDocument()
    for (const label of ['Win Rate', 'Profit Factor', 'Trades', 'Avg Duration']) {
      expect(screen.getByText(label)).toBeInTheDocument()
    }

    openGroup('Portfolio')
    expect(screen.getByText('Turnover')).toBeInTheDocument()
    expect(screen.queryByText('Win Rate')).not.toBeInTheDocument()
    expect(screen.getAllByRole('tab', { selected: true })).toHaveLength(1)
  })

  it('formats a positive Sharpe', () => {
    render(<KpiCards kpis={fullKpis({ sharpe: 1.234 })} />)
    openGroup('Risk')
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
    openGroup('Risk')
    const card = screen.getByText('Max DD').closest('.kpi-card')
    expect(card).not.toBeNull()
    expect(within(card as HTMLElement).getByText('-8.3%')).toBeInTheDocument()
  })

  it('nulls render as em dash', () => {
    render(<KpiCards kpis={fullKpis({ sharpe: null })} />)
    openGroup('Risk')
    const card = screen.getByText('Sharpe').closest('.kpi-card')
    expect(card).not.toBeNull()
    expect(within(card as HTMLElement).getByText('—')).toBeInTheDocument()
  })

  it('positive Sharpe gets the pos tone class', () => {
    render(<KpiCards kpis={fullKpis({ sharpe: 1.23 })} />)
    openGroup('Risk')
    const card = screen.getByText('Sharpe').closest('.kpi-card')
    expect(card).not.toBeNull()
    const value = within(card as HTMLElement).getByText('1.23')
    expect(value.className).toContain('kpi-card__value--pos')
  })

  it('negative max drawdown gets the neg tone class', () => {
    render(<KpiCards kpis={fullKpis({ max_drawdown: -0.083 })} />)
    openGroup('Risk')
    const card = screen.getByText('Max DD').closest('.kpi-card')
    expect(card).not.toBeNull()
    const value = within(card as HTMLElement).getByText('-8.3%')
    expect(value.className).toContain('kpi-card__value--neg')
  })

  it('total trades renders as integer', () => {
    render(<KpiCards kpis={fullKpis({ total_trades: 10.0 })} />)
    openGroup('Trading')
    const card = screen.getByText('Trades').closest('.kpi-card')
    expect(card).not.toBeNull()
    expect(within(card as HTMLElement).getByText('10')).toBeInTheDocument()
  })

  it('avg duration renders with d suffix', () => {
    render(<KpiCards kpis={fullKpis({ avg_duration_days: 3.2 })} />)
    openGroup('Trading')
    const card = screen.getByText('Avg Duration').closest('.kpi-card')
    expect(card).not.toBeNull()
    expect(within(card as HTMLElement).getByText('3.2d')).toBeInTheDocument()
  })

  it('omits avg duration when the metric is null', () => {
    render(<KpiCards kpis={fullKpis({ avg_duration_days: null })} />)
    openGroup('Trading')
    expect(screen.queryByText('Avg Duration')).not.toBeInTheDocument()
    expect(screen.getByText('Trades')).toBeInTheDocument()
  })
})
