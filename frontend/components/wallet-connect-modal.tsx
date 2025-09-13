'use client'

import React, { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Wallet,
  ChevronRight,
  Check,
  X,
  Shield,
  AlertCircle,
  Loader2,
  ExternalLink,
  Copy,
  LogOut,
  Sparkles,
  Zap
} from 'lucide-react'

interface WalletOption {
  id: string
  name: string
  icon: string
  chains: ('solana' | 'ethereum')[]
  installed?: boolean
  downloadUrl?: string
}

const walletOptions: WalletOption[] = [
  {
    id: 'phantom',
    name: 'Phantom',
    icon: '/wallets/phantom.svg',
    chains: ['solana'],
    installed: typeof window !== 'undefined' && !!(window as any).phantom?.solana,
    downloadUrl: 'https://phantom.app/download'
  },
  {
    id: 'metamask',
    name: 'MetaMask',
    icon: '/wallets/metamask.svg',
    chains: ['ethereum'],
    installed: typeof window !== 'undefined' && !!(window as any).ethereum?.isMetaMask,
    downloadUrl: 'https://metamask.io/download/'
  },
  {
    id: 'coinbase',
    name: 'Coinbase Wallet',
    icon: '/wallets/coinbase.svg',
    chains: ['ethereum', 'solana'],
    installed: typeof window !== 'undefined' && !!(window as any).coinbaseWalletExtension,
    downloadUrl: 'https://www.coinbase.com/wallet'
  },
  {
    id: 'walletconnect',
    name: 'WalletConnect',
    icon: '/wallets/walletconnect.svg',
    chains: ['ethereum'],
    installed: true, // Always available via QR
    downloadUrl: 'https://walletconnect.com/'
  },
  {
    id: 'solflare',
    name: 'Solflare',
    icon: '/wallets/solflare.svg',
    chains: ['solana'],
    installed: typeof window !== 'undefined' && !!(window as any).solflare,
    downloadUrl: 'https://solflare.com/'
  },
  {
    id: 'trust',
    name: 'Trust Wallet',
    icon: '/wallets/trust.svg',
    chains: ['ethereum', 'solana'],
    installed: typeof window !== 'undefined' && !!(window as any).trustwallet,
    downloadUrl: 'https://trustwallet.com/'
  }
]

interface WalletConnectModalProps {
  open: boolean
  onClose: () => void
  onConnect: (wallet: WalletOption, address: string, signature: string) => void
}

// Wallet icons as inline SVG components
const WalletIcons: Record<string, React.FC<{ className?: string }>> = {
  phantom: ({ className }) => (
    <svg className={className} viewBox="0 0 40 40" fill="none">
      <rect width="40" height="40" rx="8" fill="#4E3FCE"/>
      <path d="M30.5 20C30.5 25.799 25.799 30.5 20 30.5C14.201 30.5 9.5 25.799 9.5 20C9.5 14.201 14.201 9.5 20 9.5C25.799 9.5 30.5 14.201 30.5 20Z" fill="white"/>
      <circle cx="16" cy="17" r="2" fill="#4E3FCE"/>
      <circle cx="24" cy="17" r="2" fill="#4E3FCE"/>
    </svg>
  ),
  metamask: ({ className }) => (
    <svg className={className} viewBox="0 0 40 40" fill="none">
      <rect width="40" height="40" rx="8" fill="#F6851B"/>
      <path d="M32 11L20 20L8 11L20 29L32 11Z" fill="white"/>
    </svg>
  ),
  coinbase: ({ className }) => (
    <svg className={className} viewBox="0 0 40 40" fill="none">
      <rect width="40" height="40" rx="8" fill="#0052FF"/>
      <rect x="12" y="12" width="16" height="16" rx="2" fill="white"/>
    </svg>
  ),
  walletconnect: ({ className }) => (
    <svg className={className} viewBox="0 0 40 40" fill="none">
      <rect width="40" height="40" rx="8" fill="#3B99FC"/>
      <path d="M13.5 15.5C17.5 11.5 22.5 11.5 26.5 15.5L27.5 16.5L28.5 15.5C29.5 14.5 31 14.5 32 15.5C33 16.5 33 18 32 19L20 31L8 19C7 18 7 16.5 8 15.5C9 14.5 10.5 14.5 11.5 15.5L12.5 16.5L13.5 15.5Z" fill="white"/>
    </svg>
  ),
  solflare: ({ className }) => (
    <svg className={className} viewBox="0 0 40 40" fill="none">
      <rect width="40" height="40" rx="8" fill="#FC5C31"/>
      <circle cx="20" cy="20" r="8" fill="white"/>
      <circle cx="20" cy="20" r="4" fill="#FC5C31"/>
    </svg>
  ),
  trust: ({ className }) => (
    <svg className={className} viewBox="0 0 40 40" fill="none">
      <rect width="40" height="40" rx="8" fill="#3375BB"/>
      <path d="M20 8L30 13V20C30 26 26 30 20 32C14 30 10 26 10 20V13L20 8Z" fill="white"/>
    </svg>
  )
}

export function WalletConnectModal({ open, onClose, onConnect }: WalletConnectModalProps) {
  const [selectedChain, setSelectedChain] = useState<'solana' | 'ethereum'>('solana')
  const [connecting, setConnecting] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [step, setStep] = useState<'select' | 'connecting' | 'signing' | 'success'>('select')
  const [connectedAddress, setConnectedAddress] = useState<string | null>(null)
  const [walletInstallStates, setWalletInstallStates] = useState<Record<string, boolean>>({})

  // Check wallet installation states on mount and when modal opens
  useEffect(() => {
    if (open) {
      const states: Record<string, boolean> = {}
      walletOptions.forEach(wallet => {
        if (wallet.id === 'phantom') {
          states[wallet.id] = !!(window as any).phantom?.solana
        } else if (wallet.id === 'metamask') {
          states[wallet.id] = !!(window as any).ethereum?.isMetaMask
        } else if (wallet.id === 'coinbase') {
          states[wallet.id] = !!(window as any).coinbaseWalletExtension
        } else if (wallet.id === 'solflare') {
          states[wallet.id] = !!(window as any).solflare
        } else if (wallet.id === 'trust') {
          states[wallet.id] = !!(window as any).trustwallet
        } else if (wallet.id === 'walletconnect') {
          states[wallet.id] = true // Always available
        }
      })
      setWalletInstallStates(states)
    }
  }, [open])

  const filteredWallets = walletOptions.filter(w => w.chains.includes(selectedChain))

  const handleWalletSelect = async (wallet: WalletOption) => {
    // Check if wallet is installed
    if (!walletInstallStates[wallet.id] && wallet.id !== 'walletconnect') {
      if (wallet.downloadUrl) {
        window.open(wallet.downloadUrl, '_blank')
      }
      return
    }

    setConnecting(wallet.id)
    setError(null)
    setStep('connecting')

    try {
      let address: string | null = null
      let signature: string | null = null

      if (wallet.id === 'phantom' && selectedChain === 'solana') {
        const phantom = (window as any).phantom?.solana
        if (!phantom) {
          setError('Phantom wallet not found. Please install it.')
          setStep('select')
          setConnecting(null)
          return
        }

        // Connect to Phantom
        const response = await phantom.connect()
        address = response.publicKey.toString()
        
        // Sign message for authentication
        setStep('signing')
        const message = `Sign this message to authenticate with DeFAI\nTimestamp: ${Date.now()}\nAddress: ${address}`
        const encodedMessage = new TextEncoder().encode(message)
        const signedMessage = await phantom.signMessage(encodedMessage, 'utf8')
        
        // Convert signature to base58
        const bs58 = await import('bs58')
        signature = bs58.default.encode(signedMessage.signature)
        
      } else if (wallet.id === 'metamask' && selectedChain === 'ethereum') {
        const ethereum = (window as any).ethereum
        if (!ethereum || !ethereum.isMetaMask) {
          setError('MetaMask not found. Please install it.')
          setStep('select')
          setConnecting(null)
          return
        }

        // Request accounts
        const accounts = await ethereum.request({ method: 'eth_requestAccounts' })
        address = accounts[0]
        
        // Sign message for authentication
        setStep('signing')
        const message = `Sign this message to authenticate with DeFAI\nTimestamp: ${Date.now()}\nAddress: ${address}`
        signature = await ethereum.request({
          method: 'personal_sign',
          params: [message, address]
        })
      } else if (wallet.id === 'walletconnect') {
        // WalletConnect implementation placeholder
        setError('WalletConnect integration coming soon')
        setStep('select')
        setConnecting(null)
        return
      } else {
        // Other wallet implementations
        setError('This wallet integration is coming soon')
        setStep('select')
        setConnecting(null)
        return
      }

      if (address && signature) {
        setConnectedAddress(address)
        setStep('success')
        
        // Call onConnect callback
        setTimeout(() => {
          onConnect(wallet, address, signature)
          onClose()
        }, 1500)
      }
    } catch (err: any) {
      console.error('Wallet connection error:', err)
      setError(err.message || 'Failed to connect wallet')
      setStep('select')
    } finally {
      if (step !== 'success') {
        setConnecting(null)
      }
    }
  }

  const copyAddress = () => {
    if (connectedAddress) {
      navigator.clipboard.writeText(connectedAddress)
    }
  }

  const formatAddress = (address: string) => {
    if (address.length > 10) {
      return `${address.slice(0, 6)}...${address.slice(-4)}`
    }
    return address
  }

  // Reset state when modal closes
  useEffect(() => {
    if (!open) {
      setStep('select')
      setError(null)
      setConnecting(null)
      setConnectedAddress(null)
    }
  }, [open])

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-lg bg-gray-950 border-gray-800">
        <DialogHeader>
          <DialogTitle className="flex items-center text-xl text-white">
            <div className="relative mr-3">
              <div className="absolute inset-0 bg-gradient-to-r from-defi-primary to-defi-secondary rounded-full blur-lg opacity-50" />
              <div className="relative p-2 rounded-full bg-gradient-to-r from-defi-primary to-defi-secondary">
                <Wallet className="h-5 w-5 text-white" />
              </div>
            </div>
            Connect Wallet
          </DialogTitle>
          <DialogDescription className="text-gray-300">
            {step === 'select' && 'Choose your wallet to connect and authenticate'}
            {step === 'connecting' && 'Connecting to your wallet...'}
            {step === 'signing' && 'Please sign the message in your wallet'}
            {step === 'success' && 'Successfully connected!'}
          </DialogDescription>
        </DialogHeader>

        <AnimatePresence mode="wait">
          {step === 'select' && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              {/* Chain selector */}
              <div className="flex gap-2 p-1 bg-gray-900 rounded-xl">
                <button
                  onClick={() => setSelectedChain('solana')}
                  className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    selectedChain === 'solana'
                      ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg shadow-purple-500/20'
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  <div className="flex items-center justify-center gap-2">
                    <Zap className="w-4 h-4" />
                    Solana
                  </div>
                </button>
                <button
                  onClick={() => setSelectedChain('ethereum')}
                  className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    selectedChain === 'ethereum'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/20'
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  <div className="flex items-center justify-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    Ethereum
                  </div>
                </button>
              </div>

              {/* Wallet options */}
              <div className="space-y-3">
                {filteredWallets.map((wallet) => {
                  const Icon = WalletIcons[wallet.id]
                  const isInstalled = walletInstallStates[wallet.id] || false
                  const isConnecting = connecting === wallet.id
                  
                  return (
                    <motion.button
                      key={wallet.id}
                      whileHover={{ scale: isInstalled ? 1.02 : 1 }}
                      whileTap={{ scale: isInstalled ? 0.98 : 1 }}
                      onClick={() => handleWalletSelect(wallet)}
                      disabled={connecting !== null && !isConnecting}
                      className={`
                        w-full p-4 rounded-xl border transition-all relative overflow-hidden
                        ${isConnecting
                          ? 'border-defi-primary bg-gradient-to-r from-defi-primary/10 to-defi-secondary/10'
                          : isInstalled
                          ? 'border-gray-800 hover:border-defi-primary/50 bg-gray-900/50 hover:bg-gray-900'
                          : 'border-gray-800/50 bg-gray-900/30 hover:border-gray-700'
                        }
                        ${connecting !== null && !isConnecting ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                      `}
                    >
                      {/* Gradient overlay for connecting state */}
                      {isConnecting && (
                        <div className="absolute inset-0 bg-gradient-to-r from-defi-primary/5 to-defi-secondary/5 animate-pulse" />
                      )}
                      
                      <div className="flex items-center justify-between relative">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 rounded-xl overflow-hidden bg-gray-800 p-0.5">
                            {Icon ? (
                              <Icon className="w-full h-full" />
                            ) : (
                              <div className="w-full h-full rounded-lg bg-gradient-to-r from-defi-primary to-defi-secondary" />
                            )}
                          </div>
                          <div className="text-left">
                            <div className="font-semibold text-white">{wallet.name}</div>
                            <div className="text-xs text-gray-300">
                              {isInstalled ? (
                                'Ready to connect'
                              ) : (
                                <span className="text-yellow-400 font-medium">Click to install</span>
                              )}
                            </div>
                          </div>
                        </div>
                        {isConnecting ? (
                          <Loader2 className="h-5 w-5 animate-spin text-defi-primary" />
                        ) : isInstalled ? (
                          <ChevronRight className="h-5 w-5 text-gray-300" />
                        ) : (
                          <ExternalLink className="h-5 w-5 text-gray-300" />
                        )}
                      </div>
                    </motion.button>
                  )
                })}
              </div>

              {/* Error message */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-3 rounded-lg bg-red-500/10 border border-red-500/20"
                >
                  <div className="flex items-start gap-2">
                    <AlertCircle className="h-4 w-4 text-red-400 mt-0.5" />
                    <div className="text-sm text-red-400">{error}</div>
                  </div>
                </motion.div>
              )}

              {/* Security note */}
              <div className="p-3 rounded-lg bg-defi-primary/10 border border-defi-primary/30">
                <div className="flex items-start gap-2">
                  <Shield className="h-4 w-4 text-defi-primary mt-0.5" />
                  <div className="text-xs text-gray-300">
                    We'll ask you to sign a message to verify ownership. This is free and doesn't involve any transaction.
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {step === 'connecting' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="py-12 text-center"
            >
              <div className="relative inline-flex mb-6">
                <div className="absolute inset-0 bg-defi-primary/20 rounded-full blur-2xl animate-pulse" />
                <div className="relative">
                  <Loader2 className="h-16 w-16 text-defi-primary animate-spin" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Wallet className="h-6 w-6 text-defi-primary" />
                  </div>
                </div>
              </div>
              <h3 className="text-lg font-semibold mb-2 text-white">Connecting...</h3>
              <p className="text-sm text-gray-200">
                Please approve the connection in your wallet
              </p>
            </motion.div>
          )}

          {step === 'signing' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="py-12 text-center"
            >
              <div className="relative inline-flex mb-6">
                <div className="absolute inset-0 bg-defi-secondary/20 rounded-full blur-2xl animate-pulse" />
                <motion.div
                  animate={{ rotate: [0, 10, -10, 0] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="relative"
                >
                  <Shield className="h-16 w-16 text-defi-secondary" />
                </motion.div>
              </div>
              <h3 className="text-lg font-semibold mb-2 text-white">Sign Message</h3>
              <p className="text-sm text-gray-200">
                Please sign the authentication message in your wallet
              </p>
              <div className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-defi-secondary/10 border border-defi-secondary/20">
                <div className="w-2 h-2 rounded-full bg-defi-secondary animate-pulse" />
                <span className="text-xs text-defi-secondary">Waiting for signature...</span>
              </div>
            </motion.div>
          )}

          {step === 'success' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="py-12 text-center"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', duration: 0.5, delay: 0.1 }}
                className="relative inline-flex mb-6"
              >
                <div className="absolute inset-0 bg-green-500/20 rounded-full blur-2xl" />
                <div className="relative p-4 rounded-full bg-gradient-to-r from-green-500 to-emerald-500">
                  <Check className="h-8 w-8 text-white" />
                </div>
              </motion.div>
              <h3 className="text-lg font-semibold mb-2 text-white">Connected Successfully!</h3>
              {connectedAddress && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="space-y-3"
                >
                  <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gray-800 border border-gray-700">
                    <span className="text-sm font-mono text-white">{formatAddress(connectedAddress)}</span>
                    <button
                      onClick={copyAddress}
                      className="p-1.5 hover:bg-gray-700 rounded-md transition-colors"
                    >
                      <Copy className="h-3 w-3 text-gray-300" />
                    </button>
                  </div>
                  <p className="text-xs text-gray-300">Redirecting to dashboard...</p>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </DialogContent>
    </Dialog>
  )
}
