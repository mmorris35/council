/**
 * API client for Council backend.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3001'

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('council_token')
  }

  setToken(token) {
    this.token = token
    localStorage.setItem('council_token', token)
  }

  clearToken() {
    this.token = null
    localStorage.removeItem('council_token')
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      if (response.status === 401) {
        this.clearToken()
        window.location.href = '/login'
      }
      throw new Error(`API error: ${response.status}`)
    }

    return response.json()
  }

  async getDashboard() {
    return this.request('/dashboard')
  }

  async getAgent(agentId) {
    return this.request(`/agents/${agentId}`)
  }

  async getPortfolios() {
    return this.request('/portfolios')
  }

  async getPortfolio(portfolioId) {
    return this.request(`/portfolios/${portfolioId}`)
  }
}

export const apiClient = new ApiClient()
export default apiClient
