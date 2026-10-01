import { useOutletContext } from 'react-router-dom'

import { TradeLedger } from '../TradeLedger'
import { TradesSummary } from '../TradesSummary'
import type { TearSheetContext } from '../index'

export default function TradesTab() {
  const { data } = useOutletContext<TearSheetContext>()
  return (
    <div className="tear-sheet-tab">
      <TradesSummary kpis={data.kpis} />
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">Trade Ledger</h2>
        <TradeLedger runId={data.run.run_id} />
      </section>
    </div>
  )
}
