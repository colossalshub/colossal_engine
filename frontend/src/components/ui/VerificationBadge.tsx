import type { Verification } from '../../api/types'
import './verificationBadge.css'

interface VerificationBadgeProps {
  verification: Verification
}

function fmtPct(v: number): string {
  // Discrepancy is already a percentage (§4.4): 0.5 means 0.5%.
  // Show more precision for very small values so "0.00%" doesn't look broken.
  if (v < 0.01 && v > 0) return '<0.01%'
  return `${v.toFixed(2)}%`
}

export function VerificationBadge({ verification }: VerificationBadgeProps) {
  const { verified, discrepancy_pct, source } = verification

  // "account_report" means the reconstructed equity curve was checked
  // against Nautilus's authoritative per-currency account balances — a
  // genuinely independent check. Anything else (including the
  // "self_consistent" fallback used when the account report is missing or
  // predates this check) only proves the reconstruction agrees with itself.
  const isAccountReport = source === 'account_report'

  if (verified) {
    const label = isAccountReport ? 'Equity reconciled' : 'Equity verified (self-consistent)'
    return (
      <span className="verification-badge verification-badge--ok" title={`Source: ${source}`}>
        <span className="verification-badge__icon" aria-hidden="true">✓</span>
        <span className="verification-badge__label">
          {label} · discrepancy {fmtPct(discrepancy_pct)}
        </span>
      </span>
    )
  }

  const label = isAccountReport ? 'Equity discrepancy' : 'Equity discrepancy (self-consistent)'
  return (
    <span className="verification-badge verification-badge--warn" title={`Source: ${source}`}>
      <span className="verification-badge__icon" aria-hidden="true">!</span>
      <span className="verification-badge__label">
        {label} · discrepancy {fmtPct(discrepancy_pct)}
      </span>
    </span>
  )
}
