import { Routes, Route } from 'react-router-dom'
import './App.css'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import AnalysisResults from './pages/AnalysisResults'
import Portfolio from './pages/Portfolio'
import PublicPortfolio from './pages/PublicPortfolio'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/analysis/:analysisId"
        element={<ProtectedRoute><AnalysisResults /></ProtectedRoute>}
      />
      <Route path="/portfolio" element={<ProtectedRoute><Portfolio /></ProtectedRoute>} />
      <Route path="/portfolio/public/:slug" element={<PublicPortfolio />} />
    </Routes>
  )
}

export default App
