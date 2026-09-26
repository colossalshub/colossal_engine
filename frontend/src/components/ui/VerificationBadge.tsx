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
  const { verified, discrepancy_pct } = verification

  if (verified) {
    return (
      <span className="verification-badge verification-badge--ok" title={`Source: ${verification.source}`}>
        <span className="verification-badge__icon" aria-hidden="true">✓</span>
        <span className="verification-badge__label">
          Equity verified · discrepancy {fmtPct(discrepancy_pct)}
        </span>
      </span>
    )
  }

  return (
    <span className="verification-badge verification-badge--warn" title={`Source: ${verification.source}`}>
      <span className="verification-badge__icon" aria-hidden="true">!</span>
      <span className="verification-badge__label">
        Equity discrepancy {fmtPct(discrepancy_pct)}
      </span>
    </span>
  )
}
