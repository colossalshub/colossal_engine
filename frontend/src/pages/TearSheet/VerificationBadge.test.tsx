import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { Verification } from '../../api/types'
import { VerificationBadge } from '../../components/ui/VerificationBadge'

function renderBadge(verification: Verification) {
  const { container } = render(<VerificationBadge verification={verification} />)
  const root = container.querySelector('.verification-badge')
  if (!root) throw new Error('verification-badge root not found')
  return root as HTMLSpanElement
}

describe('VerificationBadge', () => {
  it('verified state renders "Equity verified"', () => {
    render(
      <VerificationBadge
        verification={{ verified: true, discrepancy_pct: 0.0, source: 'reconstructed' }}
      />,
    )
    expect(screen.getByText(/Equity verified/)).toBeInTheDocument()
  })

  it('verified with sub-0.01% discrepancy renders "<0.01%"', () => {
    render(
      <VerificationBadge
        verification={{ verified: true, discrepancy_pct: 0.001, source: 'reconstructed' }}
      />,
    )
    expect(screen.getByText(/<0\.01%/)).toBeInTheDocument()
  })

  it('verified with 0.5% discrepancy renders "0.50%"', () => {
    render(
      <VerificationBadge
        verification={{ verified: true, discrepancy_pct: 0.5, source: 'reconstructed' }}
      />,
    )
    expect(screen.getByText(/0\.50%/)).toBeInTheDocument()
  })

  it('unverified state renders "Equity discrepancy"', () => {
    render(
      <VerificationBadge
        verification={{ verified: false, discrepancy_pct: 1.23, source: 'reconstructed' }}
      />,
    )
    expect(screen.getByText(/Equity discrepancy/)).toBeInTheDocument()
    expect(screen.getByText(/1\.23%/)).toBeInTheDocument()
  })

  it('unverified applies the warn tone class', () => {
    const root = renderBadge({
      verified: false,
      discrepancy_pct: 1.23,
      source: 'reconstructed',
    })
    expect(root).toHaveClass('verification-badge--warn')
  })

  it('verified applies the ok tone class', () => {
    const root = renderBadge({
      verified: true,
      discrepancy_pct: 0.0,
      source: 'reconstructed',
    })
    expect(root).toHaveClass('verification-badge--ok')
  })

  it('source appears in title attribute', () => {
    const root = renderBadge({
      verified: true,
      discrepancy_pct: 0.0,
      source: 'reconstructed_from_portfolio_returns',
    })
    expect(root.getAttribute('title')).toContain('reconstructed_from_portfolio_returns')
  })
})
