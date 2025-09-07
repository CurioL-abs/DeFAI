import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'

export interface Agent {
  id: string
  name: string
  description?: string
  strategy_type: string
  strategy_config: Record<string, any>
  risk_level: 'low' | 'medium' | 'high'
  wallet_address?: string
  chain: string
  protocols: string[]
  watched_tokens: string[]
  max_investment: number
  min_profit_threshold: number
  stop_loss_percent: number
  status: 'created' | 'active' | 'paused' | 'stopped' | 'error'
  created_at: string
  updated_at: string
  last_active_at?: string
  owner_id: string
  is_public: boolean
  total_profit: number
  total_trades: number
  success_rate: number
}

export interface CreateAgentRequest {
  name: string
  description?: string
  strategy_type: string
  strategy_config?: Record<string, any>
  risk_level?: 'low' | 'medium' | 'high'
  protocols?: string[]
  watched_tokens?: string[]
  max_investment?: number
  min_profit_threshold?: number
  stop_loss_percent?: number
  is_public?: boolean
}

export interface UpdateAgentRequest {
  name?: string
  description?: string
  strategy_config?: Record<string, any>
  risk_level?: 'low' | 'medium' | 'high'
  protocols?: string[]
  watched_tokens?: string[]
  max_investment?: number
  min_profit_threshold?: number
  stop_loss_percent?: number
  is_public?: boolean
}

export interface AgentExecution {
  id: string
  agent_id: string
  strategy_type: string
  protocol?: string
  status: 'pending' | 'executing' | 'completed' | 'failed' | 'cancelled'
  start_time: string
  end_time?: string
  duration_seconds?: number
  transaction_ids: string[]
  profit: number
  profit_percent: number
  success: boolean
  error_message?: string
}

export interface AgentPerformance {
  id: string
  agent_id: string
  date: string
  period_type: string
  trades_count: number
  successful_trades: number
  total_profit: number
  net_profit: number
  success_rate: number
  roi_percent: number
  portfolio_value: number
}

class ApiClient {
  private client = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  constructor() {
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message)
        return Promise.reject(error)
      }
    )
  }

  // Agent endpoints
  async getAgents(): Promise<Agent[]> {
    const response = await this.client.get<Agent[]>('/agents/')
    return response.data
  }

  async getAgent(id: string): Promise<Agent> {
    const response = await this.client.get<Agent>(`/agents/${id}`)
    return response.data
  }

  async createAgent(data: CreateAgentRequest): Promise<Agent> {
    const response = await this.client.post<Agent>('/agents/', data)
    return response.data
  }

  async updateAgent(id: string, data: UpdateAgentRequest): Promise<Agent> {
    const response = await this.client.put<Agent>(`/agents/${id}`, data)
    return response.data
  }

  async deleteAgent(id: string): Promise<void> {
    await this.client.delete(`/agents/${id}`)
  }

  async startAgent(id: string): Promise<Agent> {
    const response = await this.client.post<Agent>(`/agents/${id}/start`)
    return response.data
  }

  async stopAgent(id: string): Promise<Agent> {
    const response = await this.client.post<Agent>(`/agents/${id}/stop`)
    return response.data
  }

  async pauseAgent(id: string): Promise<Agent> {
    const response = await this.client.post<Agent>(`/agents/${id}/pause`)
    return response.data
  }

  // Performance endpoints
  async getAgentExecutions(agentId: string): Promise<AgentExecution[]> {
    const response = await this.client.get<AgentExecution[]>(`/agents/${agentId}/executions`)
    return response.data
  }

  async getAgentPerformance(agentId: string): Promise<AgentPerformance[]> {
    const response = await this.client.get<AgentPerformance[]>(`/agents/${agentId}/performance`)
    return response.data
  }

  // Dashboard endpoints
  async getDashboardStats(): Promise<{
    total_agents: number
    active_agents: number
    total_profit: number
    successful_trades: number
    success_rate: number
  }> {
    const response = await this.client.get('/dashboard/stats')
    return response.data
  }

  async getHealthCheck(): Promise<{ status: string; service: string; solana_connected: boolean }> {
    const response = await this.client.get('/health')
    return response.data
  }
}

export const apiClient = new ApiClient()
