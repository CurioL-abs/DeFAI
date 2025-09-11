"use client"

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { WalletConnectModal } from '@/components/wallet-connect-modal'
import { motion } from 'framer-motion'
import { 
  Bot, 
  Zap, 
  Wallet, 
  Settings, 
  Bell,
  Plus,
  ChevronDown,
  Copy,
  LogOut,
  User,
  ExternalLink
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

interface NavbarProps {
  onCreateAgent?: () => void
}

export function Navbar({ onCreateAgent }: NavbarProps) {
  const [showWalletModal, setShowWalletModal] = useState(false)
  const [walletConnected, setWalletConnected] = useState(false)
  const [walletAddress, setWalletAddress] = useState<string | null>(null)
  const [walletChain, setWalletChain] = useState<'solana' | 'ethereum' | null>(null)
  const [balance, setBalance] = useState<number>(0)

  const handleWalletConnect = (wallet: any, address: string, signature: string) => {
    // This would normally call the authentication API
    setWalletAddress(address)
    setWalletConnected(true)
    setWalletChain(wallet.chains[0])
    setShowWalletModal(false)
    
    // Mock balance
    setBalance(Math.random() * 100)
  }

  const handleDisconnect = () => {
    setWalletConnected(false)
    setWalletAddress(null)
    setWalletChain(null)
    setBalance(0)
  }

  const copyAddress = () => {
    if (walletAddress) {
      navigator.clipboard.writeText(walletAddress)
    }
  }

  const formatAddress = (address: string) => {
    if (address.length > 10) {
      return `${address.slice(0, 6)}...${address.slice(-4)}`
    }
    return address
  }

  const openExplorer = () => {
    if (walletAddress && walletChain) {
      const explorerUrl = walletChain === 'solana' 
        ? `https://solscan.io/account/${walletAddress}`
        : `https://etherscan.io/address/${walletAddress}`
      window.open(explorerUrl, '_blank')
    }
  }

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
          <div className="flex items-center space-x-3">
            {/* Wallet connection */}
            {!walletConnected ? (
              <Button
                onClick={() => setShowWalletModal(true)}
                variant="default"
                size="sm"
                className="bg-gradient-to-r from-defi-primary to-defi-secondary hover:opacity-90 text-white shadow-lg shadow-defi-primary/25 group"
              >
                <Wallet className="h-4 w-4 mr-2 group-hover:rotate-12 transition-transform" />
                Connect Wallet
              </Button>
            ) : (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button 
                    variant="outline" 
                    size="sm"
                    className="border-defi-primary/30 hover:border-defi-primary/50 bg-gray-900/50 hover:bg-gray-900/70 transition-all"
                  >
                    <div className="flex items-center gap-2">
                      {/* Chain indicator */}
                      <div className={`w-2 h-2 rounded-full animate-pulse ${
                        walletChain === 'solana' 
                          ? 'bg-gradient-to-r from-purple-500 to-blue-500' 
                          : 'bg-gradient-to-r from-blue-500 to-purple-500'
                      }`} />
                      
                      {/* Balance */}
                      <div className="hidden sm:flex flex-col items-start">
                        <span className="text-xs text-muted-foreground">Balance</span>
                        <span className="text-sm font-medium">
                          {balance.toFixed(2)} {walletChain === 'solana' ? 'SOL' : 'ETH'}
                        </span>
                      </div>
                      
                      {/* Address */}
                      <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-defi-primary/10">
                        <Wallet className="h-3 w-3 text-defi-primary" />
                        <span className="text-sm font-mono text-defi-primary">
                          {walletAddress && formatAddress(walletAddress)}
                        </span>
                      </div>
                      
                      <ChevronDown className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56 bg-gray-900/95 backdrop-blur-xl border-defi-primary/20">
                  <DropdownMenuLabel className="text-xs text-muted-foreground">
                    Connected to {walletChain === 'solana' ? 'Solana' : 'Ethereum'}
                  </DropdownMenuLabel>
                  
                  <DropdownMenuSeparator className="bg-border/50" />
                  
                  <DropdownMenuItem 
                    onClick={copyAddress}
                    className="cursor-pointer hover:bg-defi-primary/10"
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy Address
                  </DropdownMenuItem>
                  
                  <DropdownMenuItem 
                    onClick={openExplorer}
                    className="cursor-pointer hover:bg-defi-primary/10"
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    View on Explorer
                  </DropdownMenuItem>
                  
                  <DropdownMenuItem className="cursor-pointer hover:bg-defi-primary/10">
                    <User className="h-4 w-4 mr-2" />
                    Profile
                  </DropdownMenuItem>
                  
                  <DropdownMenuSeparator className="bg-border/50" />
                  
                  <DropdownMenuItem 
                    onClick={handleDisconnect}
                    className="cursor-pointer hover:bg-destructive/10 text-destructive"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Disconnect
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}

            {/* Notifications */}
            <Button 
              variant="ghost" 
              size="icon" 
              className="relative hover:bg-defi-primary/10 transition-colors"
            >
              <Bell className="h-5 w-5 text-gray-300 hover:text-white transition-colors" />
              <span className="absolute -top-1 -right-1 h-3 w-3 bg-defi-accent rounded-full text-[10px] flex items-center justify-center text-white font-bold">
                3
              </span>
            </Button>

            {/* Settings */}
            <Button 
              variant="ghost" 
              size="icon"
              className="hover:bg-defi-primary/10 transition-colors"
            >
              <Settings className="h-5 w-5 text-gray-300 hover:text-white transition-colors" />
            </Button>

            {/* Removed duplicate Create Agent Button from navbar */}
          </div>
        </div>
      </div>
      
      {/* Wallet Connect Modal */}
      <WalletConnectModal
        open={showWalletModal}
        onClose={() => setShowWalletModal(false)}
        onConnect={handleWalletConnect}
      />
    </nav>
  )
}
