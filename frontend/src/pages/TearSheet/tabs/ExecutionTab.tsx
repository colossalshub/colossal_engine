import { Fragment } from 'react'
import { useOutletContext } from 'react-router-dom'

import type { ExecutionAssumptions } from '../../../api/types'
import type { TearSheetContext } from '../index'

const ROWS: { label: string; key: keyof ExecutionAssumptions }[] = [
  { label: 'Bar time', key: 'bar_ts' },
  { label: 'Nautilus bar event', key: 'nautilus_bar_ts_event' },
  { label: 'Signal and order', key: 'signal_and_order' },
  { label: 'Order type', key: 'order_type' },
  { label: 'Sizing price', key: 'sizing_price_when_deploy_pct_positive' },
  { label: 'Maker fee', key: 'maker_fee' },
  { label: 'Taker fee', key: 'taker_fee' },
  { label: 'Default maker fee', key: 'maker_fee_default' },
  { label: 'Default taker fee', key: 'taker_fee_default' },
  { label: 'Fill model', key: 'fill_model' },
  { label: 'Latency', key: 'latency' },
  { label: 'Spread', key: 'spread' },
  { label: 'Queue', key: 'queue_model' },
  { label: 'Partial fills', key: 'partial_fills' },
  { label: 'Equity time', key: 'equity_ts' },
  { label: 'Fill time', key: 'fill_ts' },
  { label: 'Marker time', key: 'marker_ts' },
  { label: 'Fill included in equity', key: 'fill_included_in_equity' },
]

function readAssumptions(value: unknown): ExecutionAssumptions | null {
  if (value == null || typeof value !== 'object') return null
  const record = value as Record<string, unknown>
  if (typeof record.maker_fee !== 'string') return null
  return value as ExecutionAssumptions
}

export default function ExecutionTab() {
  const { data } = useOutletContext<TearSheetContext>()
  const assumptions = readAssumptions(data.execution_assumptions)

  return (
    <div className="tear-sheet-tab">
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">Execution</h2>
        {assumptions == null ? (
          <p className="tear-sheet-tab__note">
            Execution assumptions are not on this response.
          </p>
        ) : (
          <dl className="tear-sheet-tab__facts">
            {ROWS.map((row) => (
              <Fragment key={row.key}>
                <dt>{row.label}</dt>
                <dd>{assumptions[row.key]}</dd>
              </Fragment>
            ))}
          </dl>
        )}
      </section>
    </div>
  )
}
