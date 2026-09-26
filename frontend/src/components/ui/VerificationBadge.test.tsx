import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { Verification } from '../../api/types'
import { VerificationBadge } from './VerificationBadge'

describe('VerificationBadge', () => {
  it('renders "Equity reconciled" when verified with source account_report', () => {
    const verification: Verification = {
      verified: true,
      discrepancy_pct: 0.001,
      source: 'account_report',
    }
    render(<VerificationBadge verification={verification} />)
    expect(screen.getByText(/Equity reconciled/)).toBeInTheDocument()
  })

  it('renders "Equity verified (self-consistent)" when verified with source self_consistent', () => {
    const verification: Verification = {
      verified: true,
      discrepancy_pct: 0.001,
      source: 'self_consistent',
    }
    render(<VerificationBadge verification={verification} />)
    expect(screen.getByText(/Equity verified \(self-consistent\)/)).toBeInTheDocument()
  })

  it('renders the discrepancy percentage', () => {
    const verification: Verification = {
      verified: true,
      discrepancy_pct: 0.42,
      source: 'account_report',
    }
    render(<VerificationBadge verification={verification} />)
    expect(screen.getByText(/0\.42%/)).toBeInTheDocument()
  })

  it('renders an unverified discrepancy for account_report source', () => {
    const verification: Verification = {
      verified: false,
      discrepancy_pct: 1.5,
      source: 'account_report',
    }
    render(<VerificationBadge verification={verification} />)
    expect(screen.getByText(/Equity discrepancy/)).toBeInTheDocument()
    expect(screen.queryByText(/self-consistent/)).not.toBeInTheDocument()
  })

  it('renders an unverified discrepancy reflecting self-consistent mode', () => {
    const verification: Verification = {
      verified: false,
      discrepancy_pct: 1.5,
      source: 'self_consistent',
    }
    render(<VerificationBadge verification={verification} />)
    expect(screen.getByText(/Equity discrepancy \(self-consistent\)/)).toBeInTheDocument()
  })

  it('sets the title attribute to the verification source', () => {
    const verification: Verification = {
      verified: true,
      discrepancy_pct: 0.0,
      source: 'account_report',
    }
    const { container } = render(<VerificationBadge verification={verification} />)
    const badge = container.querySelector('.verification-badge')
    expect(badge).toHaveAttribute('title', 'Source: account_report')
  })
})
