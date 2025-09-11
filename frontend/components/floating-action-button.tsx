'use client'

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Plus, Bot, Zap, ChevronUp } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface FloatingActionButtonProps {
  onClick: () => void
  showAfterScroll?: number
}

export function FloatingActionButton({ onClick, showAfterScroll = 200 }: FloatingActionButtonProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      const scrolled = window.scrollY > showAfterScroll
      setIsVisible(scrolled)
      
      // Collapse when scrolling
      if (scrolled && isExpanded) {
        setIsExpanded(false)
      }
    }

    window.addEventListener('scroll', handleScroll)
    handleScroll() // Check initial scroll position

    return () => window.removeEventListener('scroll', handleScroll)
  }, [showAfterScroll, isExpanded])

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="fixed bottom-6 right-6 z-50"
        >
          {/* Main FAB */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onClick}
            onMouseEnter={() => setIsExpanded(true)}
            onMouseLeave={() => setIsExpanded(false)}
            className="relative group"
          >
            {/* Glow effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-defi-primary to-defi-secondary rounded-full blur-lg opacity-75 group-hover:opacity-100 transition-opacity" />
            
            {/* Button */}
            <div className="relative flex items-center justify-center h-14 px-4 bg-gradient-to-r from-defi-primary to-defi-secondary rounded-full shadow-2xl">
              <Plus className="h-6 w-6 text-white" />
              
              {/* Expanded text */}
              <AnimatePresence>
                {isExpanded && (
                  <motion.span
                    initial={{ width: 0, opacity: 0 }}
                    animate={{ width: 'auto', opacity: 1 }}
                    exit={{ width: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="ml-2 text-white font-medium whitespace-nowrap overflow-hidden"
                  >
                    Create Agent
                  </motion.span>
                )}
              </AnimatePresence>
            </div>

            {/* Pulse animation */}
            <div className="absolute inset-0 bg-gradient-to-r from-defi-primary to-defi-secondary rounded-full animate-ping opacity-25" />
          </motion.button>

          {/* Tooltip on hover */}
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="absolute bottom-full right-0 mb-2 px-3 py-2 bg-gray-900/95 text-white text-sm rounded-lg whitespace-nowrap backdrop-blur-sm border border-defi-primary/20"
              >
                <div className="flex items-center gap-2">
                  <Bot className="h-4 w-4 text-defi-primary" />
                  <span>Deploy AI Agent</span>
                </div>
                <div className="text-xs text-gray-400 mt-1">Click or press A</div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
