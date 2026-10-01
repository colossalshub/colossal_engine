import { useOutletContext } from 'react-router-dom'

import { VerificationBadge } from '../../../components/ui/VerificationBadge'
import type { TearSheetContext } from '../index'

function stringParam(params: Record<string, unknown>, key: string): string | null {
  const value = params[key]
  if (typeof value !== 'string') return null
  const trimmed = value.trim()
  return trimmed.length > 0 ? trimmed : null
}

function gitLabel(sha: string | null, dirty: boolean): string {
  if (sha == null || sha.length === 0) return '—'
  return dirty ? `${sha} (dirty)` : sha
}

export default function DataTab() {
  const { data } = useOutletContext<TearSheetContext>()
  const { run, params, verification } = data
  const assumptions = data.execution_assumptions
  const timeframe = stringParam(params, 'timeframe')
  const benchmark = stringParam(params, 'benchmark_symbol')

  return (
    <div className="tear-sheet-tab">
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">Data & Methodology</h2>
        <dl className="tear-sheet-tab__facts">
          <dt>Strategy</dt>
          <dd>{run.strategy}</dd>
          <dt>Git SHA</dt>
          <dd>{gitLabel(run.git_sha, run.git_dirty)}</dd>
          <dt>Timeframe</dt>
          <dd>{timeframe ?? '—'}</dd>
          <dt>Fees</dt>
          <dd>{`maker ${assumptions.maker_fee} · taker ${assumptions.taker_fee}`}</dd>
          <dt>Benchmark</dt>
          <dd>{benchmark ?? 'none'}</dd>
          <dt>Verification</dt>
          <dd>
            <VerificationBadge verification={verification} />
          </dd>
        </dl>
      </section>
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">Execution assumptions</h2>
        <dl>
          <dt>Maker fee</dt>
          <dd>{assumptions.maker_fee}</dd>
          <dt>Taker fee</dt>
          <dd>{assumptions.taker_fee}</dd>
          <dt>Bar time</dt>
          <dd>{assumptions.bar_ts}</dd>
          <dt>Order type</dt>
          <dd>{assumptions.order_type}</dd>
          <dt>Fill model</dt>
          <dd>{assumptions.fill_model}</dd>
          <dt>Equity time</dt>
          <dd>{assumptions.equity_ts}</dd>
          <dt>Fill time</dt>
          <dd>{assumptions.fill_ts}</dd>
          <dt>Marker time</dt>
          <dd>{assumptions.marker_ts}</dd>
          <dt>Fill included in equity</dt>
          <dd>{assumptions.fill_included_in_equity}</dd>
        </dl>
      </section>
    </div>
  )
}
