import { Navigate, Route, Routes } from 'react-router-dom'

import { Shell } from './components/layout/Shell'
import CommandCenter from './pages/CommandCenter'
import Compare from './pages/Compare'
import DataManager from './pages/DataManager'
import TearSheetLayout from './pages/TearSheet'
import DataTab from './pages/TearSheet/tabs/DataTab'
import OverviewTab from './pages/TearSheet/tabs/OverviewTab'
import PerformanceTab from './pages/TearSheet/tabs/PerformanceTab'
import PlaceholderTab from './pages/TearSheet/tabs/PlaceholderTab'
import TradesTab from './pages/TearSheet/tabs/TradesTab'

export default function App() {
  return (
    <Routes>
      <Route element={<Shell />}>
        <Route path="/" element={<CommandCenter />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/runs/:id" element={<TearSheetLayout />}>
          <Route index element={<Navigate to="overview" replace />} />
          <Route path="overview" element={<OverviewTab />} />
          <Route path="performance" element={<PerformanceTab />} />
          <Route path="trades" element={<TradesTab />} />
          <Route path="data" element={<DataTab />} />
          <Route path="regimes" element={<PlaceholderTab title="Regimes" phase="Phase 21" />} />
          <Route
            path="robustness"
            element={<PlaceholderTab title="Robustness" phase="Phase 18–20" />}
          />
          <Route
            path="execution"
            element={<PlaceholderTab title="Execution" phase="Phase 15, 24" />}
          />
        </Route>
        <Route path="/data" element={<DataManager />} />
      </Route>
    </Routes>
  )
}
