"use client"

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  TrendingUp, 
  Bot, 
  DollarSign, 
  Target,
  Activity,
  Zap
} from 'lucide-react'
import { formatCurrency, formatPercentage } from '@/lib/utils'

interface DashboardStatsProps {
  stats?: {
    total_agents: number
    active_agents: number
    total_profit: number
    successful_trades: number
    success_rate: number
  }
  loading?: boolean
}

export function DashboardStats({ stats, loading = false }: DashboardStatsProps) {
  const mockStats = {
    total_agents: 12,
    active_agents: 8,
    total_profit: 15420.50,
    successful_trades: 247,
    success_rate: 0.89
  }

  const data = stats || mockStats

  if (loading) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        {Array.from({ length: 5 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="pb-3">
              <div className="h-4 bg-muted rounded w-16" />
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-muted rounded w-20 mb-2" />
              <div className="h-3 bg-muted rounded w-12" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  const statCards = [
    {
      title: 'Total Agents',
      value: data.total_agents,
      icon: Bot,
      color: 'text-defi-primary',
      bgColor: 'bg-defi-primary/10'
    },
    {
      title: 'Active Agents',
      value: data.active_agents,
      icon: Activity,
      color: 'text-success',
      bgColor: 'bg-success/10',
      badge: 'Live'
    },
    {
      title: 'Total Profit',
      value: formatCurrency(data.total_profit),
      icon: DollarSign,
      color: 'text-success',
      bgColor: 'bg-success/10',
      change: '+12.5%'
    },
    {
      title: 'Successful Trades',
      value: data.successful_trades,
      icon: Target,
      color: 'text-defi-secondary',
      bgColor: 'bg-defi-secondary/10'
    },
    {
      title: 'Success Rate',
      value: formatPercentage(data.success_rate),
      icon: TrendingUp,
      color: 'text-success',
      bgColor: 'bg-success/10',
      change: '+2.1%'
    }
  ]

  return (
    <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8 animate-slide-in">
      {statCards.map((stat, index) => {
        const Icon = stat.icon
        return (
          <Card key={stat.title} className="card-hover glow-effect" style={{ animationDelay: `${index * 0.1}s` }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold">{stat.value}</div>
                  {stat.change && (
                    <div className="flex items-center text-xs text-success">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      {stat.change}
                    </div>
                  )}
                </div>
                {stat.badge && (
                  <Badge variant="success" className="ml-2">
                    <Zap className="h-3 w-3 mr-1" />
                    {stat.badge}
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
