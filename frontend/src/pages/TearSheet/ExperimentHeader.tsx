import { Link } from 'react-router-dom'

import type { ResearchStage, RunSummary, Verification } from '../../api/types'
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

function textOrDash(value: string | null): string {
  return value ?? '—'
}

function trialOrDash(value: number | null): string {
  return value === null ? '—' : String(value)
}

function stageOrDash(value: ResearchStage | null): string {
  if (value === null) return '—'
  return { exploration: 'Exploration', validation: 'Validation', oos: 'OOS' }[value]
}

function formatResearchRange(start: number | null, end: number | null): string {
  if (start === null && end === null) return '—'
  const utc = (ts: number | null) => (ts === null ? '—' : new Date(ts).toISOString())
  return `${utc(start)} → ${utc(end)}`
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
      <section className="tear-sheet__research" aria-label="Research identity">
        <dl className="tear-sheet__research-facts">
          <dt>Experiment</dt>
          <dd>{textOrDash(run.experiment_id)}</dd>
          <dt>Research Stage</dt>
          <dd>{stageOrDash(run.research_stage)}</dd>
          <dt>Hypothesis</dt>
          <dd>{textOrDash(run.hypothesis_id)}</dd>
          <dt>Strategy Version</dt>
          <dd>{textOrDash(run.strategy_version)}</dd>
          <dt>In-sample UTC</dt>
          <dd>{formatResearchRange(run.in_sample_start_ts, run.in_sample_end_ts)}</dd>
          <dt>Validation UTC</dt>
          <dd>{formatResearchRange(run.validation_start_ts, run.validation_end_ts)}</dd>
          <dt>OOS UTC</dt>
          <dd>{formatResearchRange(run.oos_start_ts, run.oos_end_ts)}</dd>
          <dt>Trial Index</dt>
          <dd>{trialOrDash(run.trial_index)}</dd>
          <dt>Trial Count</dt>
          <dd>{trialOrDash(run.trial_count)}</dd>
        </dl>
      </section>
    </header>
  )
}
