"use client"

import React, { useState, useEffect } from 'react'
import { Navbar } from '@/components/navbar'
import { DashboardStats } from '@/components/dashboard-stats'
import { AgentCard } from '@/components/agent-card'
import { CreateAgentModal } from '@/components/create-agent-modal'
import { FloatingActionButton } from '@/components/floating-action-button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts'
import {
  TrendingUp,
  Activity,
  ArrowRight,
  Filter,
  Search,
  Plus
} from 'lucide-react'
import { Agent, apiClient } from '@/lib/api'

// Mock data for charts
const performanceData = [
  { name: 'Jan', profit: 4000, trades: 24 },
  { name: 'Feb', profit: 3000, trades: 13 },
  { name: 'Mar', profit: 2000, trades: 18 },
  { name: 'Apr', profit: 2780, trades: 39 },
  { name: 'May', profit: 1890, trades: 28 },
  { name: 'Jun', profit: 2390, trades: 34 },
  { name: 'Jul', profit: 3490, trades: 45 },
]

const portfolioData = [
  { name: '00:00', value: 10000 },
  { name: '04:00', value: 10200 },
  { name: '08:00', value: 9800 },
  { name: '12:00', value: 10500 },
  { name: '16:00', value: 11200 },
  { name: '20:00', value: 10800 },
  { name: '24:00', value: 11500 },
]

export default function DashboardPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)

  // Fetch agents on component mount
  useEffect(() => {
    fetchAgents()
  }, [])

  const fetchAgents = async () => {
    try {
      setLoading(true)
      const agentsData = await apiClient.getAgents()
      setAgents(agentsData)
    } catch (err) {
      console.error('Failed to fetch agents:', err)
      setError('Failed to load agents')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateAgent = () => {
    setShowCreateModal(true)
  }

  const handleCreateAgentSubmit = async (data: any) => {
    try {
      console.log('Creating agent with data:', data)
      const newAgent = await apiClient.createAgent(data)
      setAgents(prev => [newAgent, ...prev])
      console.log('Agent created successfully:', newAgent)
    } catch (err) {
      console.error('Failed to create agent:', err)
    }
  }

  const handleAgentStart = async (id: string) => {
    try {
      console.log('Starting agent:', id)
      // await apiClient.startAgent(id)
      // fetchAgents() // Refresh agents
    } catch (err) {
      console.error('Failed to start agent:', err)
    }
  }

  const handleAgentStop = async (id: string) => {
    try {
      console.log('Stopping agent:', id)
      // await apiClient.stopAgent(id)
      // fetchAgents() // Refresh agents
    } catch (err) {
      console.error('Failed to stop agent:', err)
    }
  }

  const handleAgentPause = async (id: string) => {
    try {
      console.log('Pausing agent:', id)
      // await apiClient.pauseAgent(id)
      // fetchAgents() // Refresh agents
    } catch (err) {
      console.error('Failed to pause agent:', err)
    }
  }

  return (
    <div className="min-h-screen">
      <Navbar onCreateAgent={handleCreateAgent} />
      
      {/* Main content */}
      <div className="container mx-auto px-4 py-8">
        {/* Welcome section */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-4xl font-bold mb-2">
            Welcome to <span className="gradient-text">DeFAI</span>
          </h1>
          <p className="text-xl text-muted-foreground">
            Your autonomous DeFi AI agents are working 24/7 to maximize your yields
          </p>
        </div>

        {/* Dashboard stats */}
        <DashboardStats loading={false} />

        {/* Charts section */}
        <div className="grid lg:grid-cols-2 gap-6 mb-8 animate-slide-in">
          <Card className="card-hover">
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="h-5 w-5 mr-2 text-success" />
                Performance Overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis 
                    dataKey="name" 
                    stroke="hsl(var(--muted-foreground))" 
                    fontSize={12}
                  />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="profit" 
                    stroke="hsl(var(--defi-primary))" 
                    strokeWidth={3}
                    dot={{ fill: 'hsl(var(--defi-primary))', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Activity className="h-5 w-5 mr-2 text-defi-secondary" />
                Portfolio Value (24h)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={portfolioData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis 
                    dataKey="name" 
                    stroke="hsl(var(--muted-foreground))" 
                    fontSize={12}
                  />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                  />
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(var(--defi-secondary))" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="hsl(var(--defi-secondary))" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="hsl(var(--defi-secondary))"
                    fill="url(#colorValue)"
                    strokeWidth={3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Agents section */}
        <div className="animate-slide-in" style={{ animationDelay: '0.2s' }}>
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-4">
            <div>
              <h2 className="text-2xl font-bold mb-1">Your AI Agents</h2>
              <p className="text-sm text-muted-foreground">
                {agents.length > 0 
                  ? `${agents.length} active agent${agents.length > 1 ? 's' : ''} managing your portfolio`
                  : 'Deploy your first AI agent to start automated trading'
                }
              </p>
            </div>
            {agents.length > 0 && (
              <div className="flex items-center gap-2">
                <Button 
                  variant="ghost" 
                  size="sm"
                  className="text-muted-foreground hover:text-foreground"
                >
                  <Filter className="h-4 w-4" />
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm"
                  className="text-muted-foreground hover:text-foreground"
                >
                  <Search className="h-4 w-4" />
                </Button>
                <div className="h-4 w-px bg-border mx-2" />
                <Button 
                  variant="default" 
                  size="sm"
                  onClick={handleCreateAgent}
                  className="bg-defi-primary hover:bg-defi-primary/90 text-white shadow-lg shadow-defi-primary/25"
                >
                  <Plus className="h-4 w-4 mr-1.5" />
                  Create Agent
                </Button>
              </div>
            )}
          </div>

          {/* Agents grid */}
          {loading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Array.from({ length: 6 }).map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardHeader>
                    <div className="h-6 bg-muted rounded w-32 mb-2" />
                    <div className="h-4 bg-muted rounded w-24" />
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="h-4 bg-muted rounded" />
                      <div className="h-4 bg-muted rounded w-3/4" />
                      <div className="h-20 bg-muted rounded" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : error ? (
            <Card className="text-center py-12">
              <CardContent>
                <p className="text-muted-foreground mb-4">{error}</p>
                <Button onClick={fetchAgents}>Try Again</Button>
              </CardContent>
            </Card>
          ) : agents.length === 0 ? (
            <Card className="relative overflow-hidden border-dashed border-2 border-defi-primary/30 bg-gradient-to-br from-defi-primary/5 via-transparent to-defi-secondary/5">
              <div className="absolute inset-0 bg-grid-white/[0.02] pointer-events-none" />
              <CardContent className="py-16">
                <div className="flex flex-col items-center text-center max-w-md mx-auto">
                  {/* Animated icon */}
                  <div className="relative mb-6">
                    <div className="absolute inset-0 bg-defi-primary/20 rounded-full blur-2xl animate-pulse" />
                    <div className="relative p-5 rounded-full bg-gradient-to-br from-defi-primary/10 to-defi-secondary/10 border border-defi-primary/20">
                      <Plus className="h-10 w-10 text-defi-primary" />
                    </div>
                  </div>
                  
                  <h3 className="text-2xl font-bold mb-3 bg-gradient-to-r from-defi-primary to-defi-secondary bg-clip-text text-transparent">
                    Deploy Your First AI Agent
                  </h3>
                  <p className="text-muted-foreground mb-8 leading-relaxed">
                    Start your DeFi journey with an autonomous AI agent that works 24/7 to optimize your yields across multiple protocols.
                  </p>
                  
                  {/* Primary CTA with animation */}
                  <Button 
                    variant="default" 
                    size="lg"
                    onClick={handleCreateAgent}
                    className="bg-gradient-to-r from-defi-primary to-defi-secondary hover:opacity-90 text-white shadow-xl shadow-defi-primary/25 transform hover:scale-105 transition-all duration-200"
                  >
                    <Plus className="h-5 w-5 mr-2" />
                    Create AI Agent
                  </Button>
                  
                  {/* Additional info */}
                  <div className="flex items-center gap-6 mt-8 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
                      <span>No coding required</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
                      <span>Start with $100</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
                      <span>Cancel anytime</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {agents.map((agent, index) => (
                <div 
                  key={agent.id} 
                  className="animate-slide-in"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <AgentCard
                    agent={agent}
                    onStart={handleAgentStart}
                    onStop={handleAgentStop}
                    onPause={handleAgentPause}
                    onSettings={(id) => console.log('Settings for agent:', id)}
                  />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-16 pt-8 border-t border-border/40">
          <p className="text-sm text-muted-foreground">
            Powered by AI • Built on Solana • Trade with confidence
          </p>
        </div>
      </div>
      
      {/* Create Agent Modal */}
      <CreateAgentModal
        open={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSubmit={handleCreateAgentSubmit}
      />
      
      {/* Floating Action Button - Shows when user has agents */}
      {agents.length > 0 && (
        <FloatingActionButton 
          onClick={handleCreateAgent}
          showAfterScroll={100}
        />
      )}
    </div>
  )
}
