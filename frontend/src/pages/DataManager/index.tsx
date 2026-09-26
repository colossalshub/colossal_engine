import { CoverageHeatmap } from './CoverageHeatmap'
import './dataManager.css'

export default function DataManager() {
  return (
    <div className="data-manager">
      <section className="data-manager__section">
        <h2 className="data-manager__heading">Coverage</h2>
        <CoverageHeatmap />
      </section>
    </div>
  )
}
