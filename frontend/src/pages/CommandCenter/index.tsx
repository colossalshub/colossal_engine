import { RunHistoryTable } from './RunHistoryTable'
import './commandCenter.css'

export default function CommandCenter() {
  return (
    <div className="command-center">
      <section className="command-center__section">
        <h2 className="command-center__heading">Run History</h2>
        <RunHistoryTable />
      </section>
    </div>
  )
}
