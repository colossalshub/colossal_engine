import { useOutletContext } from 'react-router-dom'

import type { TearSheetContext } from '../index'

export default function DataTab() {
  const { data } = useOutletContext<TearSheetContext>()
  const assumptions = data.execution_assumptions

  return (
    <div className="tear-sheet-tab">
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">Data & Methodology</h2>
        <div className="tear-sheet-tab__placeholder">
          Full methodology header arrives in Phase U.3.2
        </div>
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
