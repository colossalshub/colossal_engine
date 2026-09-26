import { Route, Routes } from 'react-router-dom'

import CommandCenter from './pages/CommandCenter'
import DataManager from './pages/DataManager'
import TearSheet from './pages/TearSheet'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<CommandCenter />} />
      <Route path="/runs/:id" element={<TearSheet />} />
      <Route path="/data" element={<DataManager />} />
    </Routes>
  )
}
