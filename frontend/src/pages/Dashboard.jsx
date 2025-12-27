import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import apiClient from '../api/client'

const AGENT_COLORS = {
  buffett: 'bg-blue-500',
  graham: 'bg-green-500',
  lynch: 'bg-purple-500',
  dalio: 'bg-orange-500',
  bogle: 'bg-gray-500',
  wood: 'bg-pink-500',
}

function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchData() {
      try {
        const result = await apiClient.getDashboard()
        setData(result)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-500">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-primary">Council</h1>
        <p className="text-gray-600">Legendary Investor AI Agents</p>
      </header>

      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-2">Total Portfolio Value</h2>
        <p className="text-4xl font-bold text-primary">
          ${data?.total_value?.toLocaleString() || '0'}
        </p>
      </div>

      <h2 className="text-2xl font-semibold mb-4">Your Agents</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data?.agents?.map((agent) => (
          <Link
            key={agent.agent_type}
            to={`/agents/${agent.agent_type}`}
            className="block"
          >
            <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6">
              <div className="flex items-center mb-4">
                <div className={`w-12 h-12 rounded-full ${AGENT_COLORS[agent.agent_type]} flex items-center justify-center text-white font-bold text-lg`}>
                  {agent.agent_name?.charAt(0) || '?'}
                </div>
                <div className="ml-4">
                  <h3 className="font-semibold text-lg">{agent.agent_name}</h3>
                  <p className="text-gray-500 text-sm capitalize">{agent.agent_type}</p>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Portfolio Value</span>
                  <span className="font-semibold">${agent.portfolio_value?.toLocaleString() || '0'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Positions</span>
                  <span className="font-semibold">{agent.num_positions || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Last Run</span>
                  <span className="text-sm text-gray-500">
                    {agent.last_run ? new Date(agent.last_run).toLocaleDateString() : 'Never'}
                  </span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default Dashboard
