"use client"

import React from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Bot, 
  Zap, 
  Wallet, 
  Settings, 
  Bell,
  Plus
} from 'lucide-react'

interface NavbarProps {
  onCreateAgent?: () => void
}

export function Navbar({ onCreateAgent }: NavbarProps) {
  return (
    <nav className="border-b border-border/40 bg-card/50 backdrop-blur-sm">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo and title */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="relative">
                <Bot className="h-8 w-8 text-defi-primary animate-pulse-glow" />
              </div>
              <div className="flex flex-col">
                <h1 className="text-xl font-bold gradient-text">DeFAI</h1>
                <p className="text-xs text-muted-foreground">AI Agents</p>
              </div>
            </div>
            
            {/* Status badge */}
            <Badge variant="success" className="hidden md:flex">
              <Zap className="h-3 w-3 mr-1" />
              Live
            </Badge>
          </div>

          {/* Navigation items */}
          <div className="flex items-center space-x-4">
            {/* Wallet connection */}
            <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-muted/50">
              <Wallet className="h-4 w-4 text-defi-secondary" />
              <span className="text-sm font-mono">
                {/* Mock wallet address */}
                9x8...7y6z
              </span>
            </div>

            {/* Notifications */}
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-4 w-4" />
              <span className="absolute -top-1 -right-1 h-3 w-3 bg-defi-accent rounded-full text-[10px] flex items-center justify-center text-white">
                3
              </span>
            </Button>

            {/* Settings */}
            <Button variant="ghost" size="icon">
              <Settings className="h-4 w-4" />
            </Button>

            {/* Create Agent Button */}
            <Button 
              variant="defi" 
              onClick={onCreateAgent}
              className="hidden md:flex"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Agent
            </Button>
          </div>
        </div>
      </div>
    </nav>
  )
}
