"use client"

import React, { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Bot, 
  Zap, 
  Target, 
  Shield,
  TrendingUp,
  Coins,
  Plus,
  X
} from 'lucide-react'

interface CreateAgentModalProps {
  open: boolean
  onClose: () => void
  onSubmit: (data: any) => void
}

const strategyTypes = [
  {
    id: 'yield_farming',
    name: 'Yield Farming',
    description: 'Automatically stake tokens in high-yield pools',
    icon: TrendingUp,
    risk: 'medium',
    apy: '8-15%'
  },
  {
    id: 'arbitrage',
    name: 'Arbitrage',
    description: 'Exploit price differences across DEXs',
    icon: Zap,
    risk: 'high',
    apy: '12-25%'
  },
  {
    id: 'lending',
    name: 'Lending',
    description: 'Lend tokens to earn interest',
    icon: Coins,
    risk: 'low',
    apy: '4-8%'
  }
]

const riskLevels = [
  { value: 'low', label: 'Conservative', color: 'text-success bg-success/10' },
  { value: 'medium', label: 'Balanced', color: 'text-warning bg-warning/10' },
  { value: 'high', label: 'Aggressive', color: 'text-destructive bg-destructive/10' },
]

const protocols = [
  'jupiter', 'raydium', 'orca', 'marginfi', 'solend', 'kamino'
]

const tokens = [
  'SOL', 'USDC', 'USDT', 'RAY', 'ORCA', 'MNGO', 'SRM', 'FTT'
]

export function CreateAgentModal({ open, onClose, onSubmit }: CreateAgentModalProps) {
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    strategy_type: '',
    risk_level: 'medium',
    protocols: [] as string[],
    watched_tokens: [] as string[],
    max_investment: 1000,
    min_profit_threshold: 0.01,
    stop_loss_percent: 0.1,
    is_public: false
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
    onClose()
    // Reset form
    setFormData({
      name: '',
      description: '',
      strategy_type: '',
      risk_level: 'medium',
      protocols: [],
      watched_tokens: [],
      max_investment: 1000,
      min_profit_threshold: 0.01,
      stop_loss_percent: 0.1,
      is_public: false
    })
    setStep(1)
  }

  const toggleProtocol = (protocol: string) => {
    setFormData(prev => ({
      ...prev,
      protocols: prev.protocols.includes(protocol)
        ? prev.protocols.filter(p => p !== protocol)
        : [...prev.protocols, protocol]
    }))
  }

  const toggleToken = (token: string) => {
    setFormData(prev => ({
      ...prev,
      watched_tokens: prev.watched_tokens.includes(token)
        ? prev.watched_tokens.filter(t => t !== token)
        : [...prev.watched_tokens, token]
    }))
  }

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center text-2xl">
            <Bot className="h-6 w-6 mr-2 text-defi-primary" />
            Create AI Agent
          </DialogTitle>
          <DialogDescription>
            Configure your autonomous DeFi trading agent
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {step === 1 && (
            <div className="space-y-6 animate-fade-in">
              <div>
                <label className="text-sm font-medium mb-2 block text-gray-200">Agent Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-4 py-2.5 border border-defi-primary/30 bg-gray-800/50 text-white rounded-lg focus:ring-2 focus:ring-defi-primary focus:border-defi-primary focus:bg-gray-800/70 transition-all placeholder:text-gray-500"
                  placeholder="My DeFi Agent"
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block text-gray-200">Description (Optional)</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full px-4 py-2.5 border border-defi-primary/30 bg-gray-800/50 text-white rounded-lg focus:ring-2 focus:ring-defi-primary focus:border-defi-primary focus:bg-gray-800/70 transition-all placeholder:text-gray-500 resize-none"
                  placeholder="Describe your agent's purpose..."
                  rows={3}
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-3 block text-gray-200">Strategy Type</label>
                <div className="grid md:grid-cols-3 gap-3">
                  {strategyTypes.map((strategy) => {
                    const Icon = strategy.icon
                    const isSelected = formData.strategy_type === strategy.id
                    return (
                      <Card
                        key={strategy.id}
                        className={`cursor-pointer transition-all ${
                          isSelected 
                            ? 'ring-2 ring-defi-primary bg-defi-primary/5' 
                            : 'hover:bg-muted/50'
                        }`}
                        onClick={() => setFormData(prev => ({ ...prev, strategy_type: strategy.id }))}
                      >
                        <CardHeader className="pb-2">
                          <div className="flex items-center space-x-2">
                            <Icon className="h-5 w-5 text-defi-primary" />
                            <CardTitle className="text-base">{strategy.name}</CardTitle>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <p className="text-sm text-muted-foreground mb-2">
                            {strategy.description}
                          </p>
                          <div className="flex justify-between items-center">
                            <Badge variant={strategy.risk === 'low' ? 'success' : strategy.risk === 'medium' ? 'warning' : 'destructive'}>
                              {strategy.risk} risk
                            </Badge>
                            <span className="text-sm font-semibold text-success">
                              {strategy.apy}
                            </span>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6 animate-fade-in">
              <div>
                <label className="text-sm font-medium mb-3 block">Risk Level</label>
                <div className="grid grid-cols-3 gap-3">
                  {riskLevels.map((risk) => (
                    <Card
                      key={risk.value}
                      className={`cursor-pointer transition-all ${
                        formData.risk_level === risk.value 
                          ? 'ring-2 ring-defi-primary bg-defi-primary/5' 
                          : 'hover:bg-muted/50'
                      }`}
                      onClick={() => setFormData(prev => ({ ...prev, risk_level: risk.value as any }))}
                    >
                      <CardContent className="p-4 text-center">
                        <Shield className={`h-6 w-6 mx-auto mb-2 ${risk.color.split(' ')[0]}`} />
                        <div className="font-medium">{risk.label}</div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-3 block">Maximum Investment</label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                  <input
                    type="number"
                    value={formData.max_investment}
                    onChange={(e) => setFormData(prev => ({ ...prev, max_investment: parseFloat(e.target.value) || 0 }))}
                    className="w-full pl-8 pr-3 py-2 border border-input bg-background rounded-md focus:ring-2 focus:ring-defi-primary focus:border-transparent"
                    min="100"
                    max="100000"
                    step="100"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Min Profit Threshold</label>
                  <div className="relative">
                    <input
                      type="number"
                      value={formData.min_profit_threshold * 100}
                      onChange={(e) => setFormData(prev => ({ ...prev, min_profit_threshold: parseFloat(e.target.value) / 100 || 0.01 }))}
                      className="w-full pr-8 pl-3 py-2 border border-input bg-background rounded-md focus:ring-2 focus:ring-defi-primary focus:border-transparent"
                      min="0.1"
                      max="10"
                      step="0.1"
                      required
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">%</span>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Stop Loss</label>
                  <div className="relative">
                    <input
                      type="number"
                      value={formData.stop_loss_percent * 100}
                      onChange={(e) => setFormData(prev => ({ ...prev, stop_loss_percent: parseFloat(e.target.value) / 100 || 0.1 }))}
                      className="w-full pr-8 pl-3 py-2 border border-input bg-background rounded-md focus:ring-2 focus:ring-defi-primary focus:border-transparent"
                      min="5"
                      max="50"
                      step="5"
                      required
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">%</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6 animate-fade-in">
              <div>
                <label className="text-sm font-medium mb-3 block">DeFi Protocols</label>
                <div className="grid grid-cols-3 gap-2">
                  {protocols.map((protocol) => (
                    <Button
                      key={protocol}
                      type="button"
                      variant={formData.protocols.includes(protocol) ? 'defi' : 'outline'}
                      size="sm"
                      onClick={() => toggleProtocol(protocol)}
                      className="justify-start"
                    >
                      {formData.protocols.includes(protocol) ? (
                        <X className="h-3 w-3 mr-1" />
                      ) : (
                        <Plus className="h-3 w-3 mr-1" />
                      )}
                      {protocol}
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-3 block">Watched Tokens</label>
                <div className="grid grid-cols-4 gap-2">
                  {tokens.map((token) => (
                    <Button
                      key={token}
                      type="button"
                      variant={formData.watched_tokens.includes(token) ? 'defi' : 'outline'}
                      size="sm"
                      onClick={() => toggleToken(token)}
                      className="justify-start"
                    >
                      {formData.watched_tokens.includes(token) ? (
                        <X className="h-3 w-3 mr-1" />
                      ) : (
                        <Plus className="h-3 w-3 mr-1" />
                      )}
                      {token}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-between pt-6 border-t border-border">
            <div className="flex space-x-2">
              {step > 1 && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setStep(step - 1)}
                >
                  Previous
                </Button>
              )}
            </div>
            
            <div className="flex space-x-2">
              <Button
                type="button"
                variant="ghost"
                onClick={onClose}
              >
                Cancel
              </Button>
              
              {step < 3 ? (
                <Button
                  type="button"
                  variant="defi"
                  onClick={() => setStep(step + 1)}
                  disabled={step === 1 && (!formData.name || !formData.strategy_type)}
                >
                  Next
                </Button>
              ) : (
                <Button
                  type="submit"
                  variant="defi"
                  disabled={!formData.name || !formData.strategy_type}
                >
                  <Bot className="h-4 w-4 mr-2" />
                  Create Agent
                </Button>
              )}
            </div>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
