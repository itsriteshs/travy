import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Nav } from './components/Nav'
import { Home } from './pages/Home'
import { Planner } from './pages/Planner'
import { Groupy } from './pages/Groupy'
import { Travison } from './pages/Travison'
import { Results } from './pages/Results'
import { RouterPage, SecurityPage, DemoPage } from './pages/Stubs'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[var(--background)]">
        <Nav />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/groupy" element={<Groupy />} />
          <Route path="/travison" element={<Travison />} />
          <Route path="/planner" element={<Planner />} />
          <Route path="/results" element={<Results />} />
          <Route path="/router" element={<RouterPage />} />
          <Route path="/security" element={<SecurityPage />} />
          <Route path="/demo" element={<DemoPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
