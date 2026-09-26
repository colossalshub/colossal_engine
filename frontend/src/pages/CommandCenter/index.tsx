import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { StrategyForm } from './StrategyForm'
import { RunHistoryTable } from './RunHistoryTable'
import './commandCenter.css'

export default function CommandCenter() {
  const [selected, setSelected] = useState<string[]>([])
  const navigate = useNavigate()

  return (
    <div className="command-center">
      <section className="command-center__section">
        <h2 className="command-center__heading">New Run</h2>
        <StrategyForm />
      </section>
      <section className="command-center__section">
        <div className="command-center__section-header">
          <h2 className="command-center__heading">Run History</h2>
          {selected.length >= 2 ? (
            <button
              type="button"
              className="command-center__compare-btn"
              onClick={() => navigate(`/compare?ids=${selected.join(',')}`)}
            >
              Compare {selected.length}
            </button>
          ) : null}
        </div>
        <RunHistoryTable onSelectionChange={setSelected} />
      </section>
    </div>
  )
}
