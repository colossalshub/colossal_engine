import { useOutletContext } from 'react-router-dom'

import { DrawdownChart } from '../DrawdownChart'
import { EquityCurve } from '../EquityCurve'
import { PriceChart } from '../PriceChart'
import type { TearSheetContext } from '../index'

export default function PerformanceTab() {
  const { data } = useOutletContext<TearSheetContext>()
  return (
    <div className="tear-sheet-tab">
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">Price + Fills</h2>
        <PriceChart data={data.price} markers={data.markers} />
      </section>
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">Equity</h2>
        <EquityCurve data={data.equity} height={420} />
      </section>
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">Underwater</h2>
        <DrawdownChart data={data.drawdown} height={280} />
      </section>
    </div>
  )
}
