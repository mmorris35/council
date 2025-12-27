import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import apiClient from '../api/client'

function AgentDetail() {
  const { agentId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const result = await apiClient.getAgent(agentId)
        setData(result)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [agentId])

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  const chartData = data?.recent_runs?.map(run => ({
    date: new Date(run.date).toLocaleDateString(),
    value: run.value_after,
  })).reverse() || []

  return (
    <div className="container mx-auto px-4 py-8">
      <Link to="/" className="text-primary hover:underline mb-4 inline-block">
        Back to Dashboard
      </Link>

      <header className="mb-8">
        <h1 className="text-3xl font-bold text-primary">{data?.agent_name}</h1>
        <p className="text-gray-600 capitalize">{data?.agent_type} Strategy</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm">Total Value</h3>
          <p className="text-2xl font-bold">${data?.portfolio?.total_value?.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm">Cash</h3>
          <p className="text-2xl font-bold">${data?.portfolio?.cash?.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm">Positions</h3>
          <p className="text-2xl font-bold">{data?.portfolio?.positions?.length || 0}</p>
        </div>
      </div>

      {chartData.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Portfolio History</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#1a365d" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Current Positions</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">Symbol</th>
                <th className="text-right py-2">Shares</th>
                <th className="text-right py-2">Avg Cost</th>
                <th className="text-right py-2">Current</th>
                <th className="text-right py-2">Value</th>
                <th className="text-right py-2">Gain/Loss</th>
              </tr>
            </thead>
            <tbody>
              {data?.portfolio?.positions?.map((pos) => (
                <tr key={pos.symbol} className="border-b">
                  <td className="py-2 font-semibold">{pos.symbol}</td>
                  <td className="text-right py-2">{pos.shares}</td>
                  <td className="text-right py-2">${pos.avg_cost?.toFixed(2)}</td>
                  <td className="text-right py-2">${pos.current_price?.toFixed(2)}</td>
                  <td className="text-right py-2">${pos.market_value?.toLocaleString()}</td>
                  <td className={`text-right py-2 ${pos.gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {pos.gain_loss_pct?.toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Transactions</h2>
        <div className="space-y-3">
          {data?.recent_transactions?.map((txn) => (
            <div key={txn.transaction_id} className="flex items-center justify-between border-b pb-3">
              <div>
                <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                  txn.type === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {txn.type.toUpperCase()}
                </span>
                <span className="ml-2 font-semibold">{txn.symbol}</span>
                <span className="ml-2 text-gray-600">{txn.shares} shares @ ${txn.price}</span>
              </div>
              <div className="text-gray-500 text-sm">
                {new Date(txn.date).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default AgentDetail
