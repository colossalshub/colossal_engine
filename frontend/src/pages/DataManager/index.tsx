import { CoverageHeatmap } from './CoverageHeatmap'
import { IngestForm } from './IngestForm'
import './dataManager.css'

export default function DataManager() {
  return (
    <div className="data-manager">
      <section className="data-manager__section">
        <h2 className="data-manager__heading">Coverage</h2>
        <CoverageHeatmap />
      </section>
      <section className="data-manager__section">
        <h2 className="data-manager__heading">Ingestion</h2>
        <IngestForm />
      </section>
    </div>
  )
}
