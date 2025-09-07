"use client"

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Bot, 
  Play, 
  Pause, 
  Square, 
  TrendingUp, 
  TrendingDown,
  Clock,
  DollarSign,
  Target,
  Settings
} from 'lucide-react'
import { Agent } from '@/lib/api'
import { formatCurrency, formatPercentage, getStatusColor, getRiskColor } from '@/lib/utils'

interface AgentCardProps {
  agent: Agent
  onStart?: (id: string) => void
  onStop?: (id: string) => void
  onPause?: (id: string) => void
  onSettings?: (id: string) => void
}

export function AgentCard({ agent, onStart, onStop, onPause, onSettings }: AgentCardProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <Play className="h-3 w-3" />
      case 'paused':
        return <Pause className="h-3 w-3" />
      case 'stopped':
        return <Square className="h-3 w-3" />
      default:
        return <Clock className="h-3 w-3" />
    }
  }

  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'active':
        return 'success'
      case 'paused':
        return 'warning'
      case 'stopped':
        return 'secondary'
      case 'error':
        return 'destructive'
      default:
        return 'defi'
    }
  }

  const getRiskVariant = (risk: string) => {
    switch (risk) {
      case 'low':
        return 'success'
      case 'medium':
        return 'warning'
      case 'high':
        return 'destructive'
      default:
        return 'secondary'
    }
  }

  const isProfit = agent.total_profit > 0

  return (
    <Card className="card-hover glow-effect">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-defi-primary/10">
              <Bot className="h-5 w-5 text-defi-primary" />
            </div>
            <div>
              <CardTitle className="text-lg">{agent.name}</CardTitle>
              <div className="flex items-center space-x-2 mt-1">
                <Badge variant={getStatusVariant(agent.status) as any}>
                  {getStatusIcon(agent.status)}
                  {agent.status}
                </Badge>
                <Badge variant={getRiskVariant(agent.risk_level) as any}>
                  {agent.risk_level} risk
                </Badge>
              </div>
            </div>
          </div>
          <Button 
            variant="ghost" 
            size="icon"
            onClick={() => onSettings?.(agent.id)}
          >
            <Settings className="h-4 w-4" />
          </Button>
        </div>
        
        {agent.description && (
          <p className="text-sm text-muted-foreground mt-2">
            {agent.description}
          </p>
        )}
      </CardHeader>
      
      <CardContent>
        {/* Strategy info */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-muted-foreground">Strategy:</span>
            <span className="font-medium capitalize">{agent.strategy_type}</span>
          </div>
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-muted-foreground">Max Investment:</span>
            <span className="font-medium">{formatCurrency(agent.max_investment)}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Stop Loss:</span>
            <span className="font-medium">{formatPercentage(agent.stop_loss_percent)}</span>
          </div>
        </div>

        {/* Performance metrics */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="text-center p-3 rounded-lg bg-muted/50">
            <div className={`flex items-center justify-center mb-1 ${isProfit ? 'text-success' : 'text-destructive'}`}>
              {isProfit ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
            </div>
            <div className={`text-sm font-bold ${isProfit ? 'text-success' : 'text-destructive'}`}>
              {formatCurrency(agent.total_profit)}
            </div>
            <div className="text-xs text-muted-foreground">Profit</div>
          </div>
          
          <div className="text-center p-3 rounded-lg bg-muted/50">
            <div className="flex items-center justify-center mb-1 text-defi-secondary">
              <Target className="h-4 w-4" />
            </div>
            <div className="text-sm font-bold">{agent.total_trades}</div>
            <div className="text-xs text-muted-foreground">Trades</div>
          </div>
          
          <div className="text-center p-3 rounded-lg bg-muted/50">
            <div className="flex items-center justify-center mb-1 text-defi-primary">
              <DollarSign className="h-4 w-4" />
            </div>
            <div className="text-sm font-bold">{formatPercentage(agent.success_rate / 100)}</div>
            <div className="text-xs text-muted-foreground">Success</div>
          </div>
        </div>

        {/* Protocols */}
        {agent.protocols.length > 0 && (
          <div className="mb-4">
            <div className="text-sm text-muted-foreground mb-2">Protocols:</div>
            <div className="flex flex-wrap gap-1">
              {agent.protocols.map((protocol) => (
                <Badge key={protocol} variant="outline" className="text-xs">
                  {protocol}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex gap-2">
          {agent.status === 'created' || agent.status === 'stopped' || agent.status === 'paused' ? (
            <Button 
              variant="defi" 
              size="sm" 
              className="flex-1"
              onClick={() => onStart?.(agent.id)}
            >
              <Play className="h-3 w-3 mr-1" />
              Start
            </Button>
          ) : (
            <>
              <Button 
                variant="warning" 
                size="sm" 
                className="flex-1"
                onClick={() => onPause?.(agent.id)}
              >
                <Pause className="h-3 w-3 mr-1" />
                Pause
              </Button>
              <Button 
                variant="destructive" 
                size="sm" 
                className="flex-1"
                onClick={() => onStop?.(agent.id)}
              >
                <Square className="h-3 w-3 mr-1" />
                Stop
              </Button>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
