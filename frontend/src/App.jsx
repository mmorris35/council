import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import AgentDetail from './pages/AgentDetail'
import Login from './pages/Login'

function App() {
  return (
    <div className="min-h-screen">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/agents/:agentId" element={<AgentDetail />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </div>
  )
}

export default App
