import { Route, Routes } from 'react-router-dom'

import { Shell } from './components/layout/Shell'
import CommandCenter from './pages/CommandCenter'
import Compare from './pages/Compare'
import DataManager from './pages/DataManager'
import TearSheet from './pages/TearSheet'

export default function App() {
  return (
    <Routes>
      <Route element={<Shell />}>
        <Route path="/" element={<CommandCenter />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/runs/:id" element={<TearSheet />} />
        <Route path="/data" element={<DataManager />} />
      </Route>
    </Routes>
  )
}
