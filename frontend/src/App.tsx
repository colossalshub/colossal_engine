import { Navigate, Route, Routes } from 'react-router-dom'

import { Shell } from './components/layout/Shell'
import CommandCenter from './pages/CommandCenter'
import Compare from './pages/Compare'
import DataManager from './pages/DataManager'
import TearSheetLayout from './pages/TearSheet'
import DataTab from './pages/TearSheet/tabs/DataTab'
import ExecutionTab from './pages/TearSheet/tabs/ExecutionTab'
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
          <Route
            path="regimes"
            element={
              <PlaceholderTab
                title="Regimes"
                message="Not available for this run. No regime classification is attached to this result."
              />
            }
          />
          <Route
            path="robustness"
            element={
              <PlaceholderTab
                title="Robustness"
                message="No robustness analysis is attached to this run."
              />
            }
          />
          <Route path="execution" element={<ExecutionTab />} />
        </Route>
        <Route path="/data" element={<DataManager />} />
      </Route>
    </Routes>
  )
}
