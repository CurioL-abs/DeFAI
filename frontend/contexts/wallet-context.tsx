'use client'

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import Cookies from 'js-cookie'
import { apiClient } from '@/lib/api'

interface WalletState {
  isConnected: boolean
  address: string | null
  chain: 'solana' | 'ethereum' | null
  walletType: string | null
  balance: number
  isAuthenticated: boolean
  authToken: string | null
  user: any | null
}

interface WalletContextType extends WalletState {
  connect: () => void
  disconnect: () => void
  authenticate: (address: string, signature: string, chain: string) => Promise<boolean>
  refreshBalance: () => Promise<void>
}

const WalletContext = createContext<WalletContextType | undefined>(undefined)

export function WalletProvider({ children }: { children: React.ReactNode }) {
  const [walletState, setWalletState] = useState<WalletState>({
    isConnected: false,
    address: null,
    chain: null,
    walletType: null,
    balance: 0,
    isAuthenticated: false,
    authToken: null,
    user: null
  })

  const [showConnectModal, setShowConnectModal] = useState(false)

  // Load saved session on mount
  useEffect(() => {
    const savedToken = Cookies.get('auth_token')
    const savedAddress = Cookies.get('wallet_address')
    const savedChain = Cookies.get('wallet_chain') as 'solana' | 'ethereum' | null
    const savedWalletType = Cookies.get('wallet_type')

    if (savedToken && savedAddress && savedChain) {
      setWalletState(prev => ({
        ...prev,
        isConnected: true,
        address: savedAddress,
        chain: savedChain,
        walletType: savedWalletType,
        isAuthenticated: true,
        authToken: savedToken
      }))
      
      // Verify token is still valid
      verifyAuth(savedToken)
    }
  }, [])

  const verifyAuth = async (token: string) => {
    try {
      // Call backend to verify token
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/verify`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        // Token is invalid, clear session
        disconnect()
      } else {
        const data = await response.json()
        setWalletState(prev => ({
          ...prev,
          user: data.user
        }))
      }
    } catch (error) {
      console.error('Auth verification failed:', error)
      disconnect()
    }
  }

  const authenticate = async (address: string, signature: string, chain: string): Promise<boolean> => {
    try {
      // Call backend authentication endpoint
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/wallet`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          address,
          signature,
          chain,
          message: `Sign this message to authenticate with DeFAI\nTimestamp: ${Date.now()}\nAddress: ${address}`
        })
      })

      if (!response.ok) {
        throw new Error('Authentication failed')
      }

      const data = await response.json()
      
      // Save auth token and wallet info
      Cookies.set('auth_token', data.token, { expires: 7 })
      Cookies.set('wallet_address', address, { expires: 7 })
      Cookies.set('wallet_chain', chain, { expires: 7 })
      
      // Update state
      setWalletState(prev => ({
        ...prev,
        isConnected: true,
        address,
        chain: chain as 'solana' | 'ethereum',
        isAuthenticated: true,
        authToken: data.token,
        user: data.user
      }))

      // Set default authorization header for API client
      if (apiClient) {
        (apiClient as any).client.defaults.headers.common['Authorization'] = `Bearer ${data.token}`
      }

      return true
    } catch (error) {
      console.error('Authentication error:', error)
      return false
    }
  }

  const refreshBalance = async () => {
    if (!walletState.address || !walletState.chain) return

    try {
      if (walletState.chain === 'solana') {
        // Get SOL balance
        const response = await fetch(`https://api.mainnet-beta.solana.com`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            jsonrpc: '2.0',
            id: 1,
            method: 'getBalance',
            params: [walletState.address]
          })
        })
        
        const data = await response.json()
        const balance = data.result?.value ? data.result.value / 1e9 : 0
        
        setWalletState(prev => ({ ...prev, balance }))
      } else if (walletState.chain === 'ethereum') {
        // Get ETH balance
        const ethereum = (window as any).ethereum
        if (ethereum) {
          const balance = await ethereum.request({
            method: 'eth_getBalance',
            params: [walletState.address, 'latest']
          })
          
          // Convert from wei to ETH
          const ethBalance = parseInt(balance, 16) / 1e18
          setWalletState(prev => ({ ...prev, balance: ethBalance }))
        }
      }
    } catch (error) {
      console.error('Failed to refresh balance:', error)
    }
  }

  const connect = useCallback(() => {
    setShowConnectModal(true)
  }, [])

  const disconnect = useCallback(() => {
    // Clear cookies
    Cookies.remove('auth_token')
    Cookies.remove('wallet_address')
    Cookies.remove('wallet_chain')
    Cookies.remove('wallet_type')
    
    // Clear API client auth header
    if (apiClient) {
      delete (apiClient as any).client.defaults.headers.common['Authorization']
    }
    
    // Reset state
    setWalletState({
      isConnected: false,
      address: null,
      chain: null,
      walletType: null,
      balance: 0,
      isAuthenticated: false,
      authToken: null,
      user: null
    })

    // Disconnect from wallet
    if (walletState.chain === 'solana') {
      const phantom = (window as any).phantom?.solana
      if (phantom) {
        phantom.disconnect()
      }
    }
  }, [walletState.chain])

  // Auto-refresh balance when connected
  useEffect(() => {
    if (walletState.isConnected && walletState.address) {
      refreshBalance()
      
      // Refresh every 30 seconds
      const interval = setInterval(refreshBalance, 30000)
      return () => clearInterval(interval)
    }
  }, [walletState.isConnected, walletState.address, walletState.chain])

  return (
    <WalletContext.Provider
      value={{
        ...walletState,
        connect,
        disconnect,
        authenticate,
        refreshBalance
      }}
    >
      {children}
    </WalletContext.Provider>
  )
}

export function useWallet() {
  const context = useContext(WalletContext)
  if (context === undefined) {
    throw new Error('useWallet must be used within a WalletProvider')
  }
  return context
}
