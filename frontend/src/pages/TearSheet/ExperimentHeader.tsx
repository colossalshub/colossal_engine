import { Link } from 'react-router-dom'

import type { RunSummary, Verification } from '../../api/types'
import { Badge } from '../../components/ui/Badge'
import { VerificationBadge } from '../../components/ui/VerificationBadge'

interface ExperimentHeaderProps {
  run: RunSummary
  params: Record<string, unknown>
  verification: Verification
}

function formatDate(tsMs: number): string {
  return new Date(tsMs).toISOString().slice(0, 10)
}

function nonEmptyString(value: unknown): string | null {
  if (typeof value !== 'string') return null
  const trimmed = value.trim()
  return trimmed.length > 0 ? trimmed : null
}

function feeLabel(value: unknown): string | null {
  if (typeof value !== 'string') return null
  const pct = ((parseFloat(value) || 0) * 100).toFixed(2)
  return `fees ${pct}%`
}

function gitLabel(sha: string | null, dirty: boolean): string | null {
  if (sha == null || sha.length === 0) return null
  const short = sha.slice(0, 7)
  return dirty ? `git ${short} (dirty)` : `git ${short}`
}

export function ExperimentHeader({ run, params, verification }: ExperimentHeaderProps) {
  const timeframe = nonEmptyString(params.timeframe)
  const benchmark =
    typeof params.benchmark_symbol === 'string' && params.benchmark_symbol
      ? params.benchmark_symbol
      : null
  const fees = feeLabel(params.maker_fee)
  const git = gitLabel(run.git_sha, run.git_dirty)

  return (
    <header className="tear-sheet__header">
      <div className="tear-sheet__header-row">
        <Link to="/" className="tear-sheet__back">← Back</Link>
        <h1 className="tear-sheet__name">{run.name}</h1>
        <Badge status={run.status} />
        <VerificationBadge verification={verification} />
      </div>
      <div className="tear-sheet__meta">
        <span className="tear-sheet__meta-mono">strategy {run.strategy}</span>
        <span className="tear-sheet__meta-sep">·</span>
        <span>{run.universe[0]}</span>
        {run.universe.length > 1 ? (
          <>
            <span className="tear-sheet__meta-sep">·</span>
            <span className="tear-sheet__meta-mono">only first symbol executed</span>
          </>
        ) : null}
        <span className="tear-sheet__meta-sep">·</span>
        <span>
          {formatDate(run.start_ts)} → {formatDate(run.end_ts)}
        </span>
        {timeframe ? (
          <>
            <span className="tear-sheet__meta-sep">·</span>
            <span className="tear-sheet__meta-mono">timeframe {timeframe}</span>
          </>
        ) : null}
        {fees ? (
          <>
            <span className="tear-sheet__meta-sep">·</span>
            <span className="tear-sheet__meta-mono">{fees}</span>
          </>
        ) : null}
        {benchmark ? (
          <>
            <span className="tear-sheet__meta-sep">·</span>
            <span className="tear-sheet__meta-mono">benchmark {benchmark}</span>
          </>
        ) : null}
        {git ? (
          <>
            <span className="tear-sheet__meta-sep">·</span>
            <span className="tear-sheet__meta-mono">{git}</span>
          </>
        ) : null}
      </div>
    </header>
  )
}
