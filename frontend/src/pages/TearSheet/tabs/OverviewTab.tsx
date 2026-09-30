import { useOutletContext } from 'react-router-dom'

import { KpiCards } from '../KpiCards'
import { MonthlyHeatmap } from '../MonthlyHeatmap'
import type { TearSheetContext } from '../index'

export default function OverviewTab() {
  const { data } = useOutletContext<TearSheetContext>()
  return (
    <div className="tear-sheet-tab">
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">KPIs</h2>
        <KpiCards kpis={data.kpis} />
      </section>
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">Monthly Returns</h2>
        <MonthlyHeatmap data={data.monthly_returns} />
      </section>
    </div>
  )
}
