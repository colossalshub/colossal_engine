import { useOutletContext } from 'react-router-dom'

import { DrawdownChart } from '../DrawdownChart'
import { EquityCurve } from '../EquityCurve'
import { MonthlyHeatmap } from '../MonthlyHeatmap'
import { OverviewSummary } from '../OverviewSummary'
import type { TearSheetContext } from '../index'

export default function OverviewTab() {
  const { data } = useOutletContext<TearSheetContext>()
  return (
    <div className="tear-sheet-tab">
      <OverviewSummary kpis={data.kpis} />
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">Equity</h2>
        <EquityCurve data={data.equity} />
      </section>
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">Underwater</h2>
        <DrawdownChart data={data.drawdown} />
      </section>
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">Monthly Returns</h2>
        <MonthlyHeatmap data={data.monthly_returns} />
      </section>
    </div>
  )
}
