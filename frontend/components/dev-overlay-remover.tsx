'use client'

import { useEffect } from 'react'

export function DevOverlayRemover() {
  useEffect(() => {
    // Function to remove Next.js dev overlay
    const removeDevOverlay = () => {
      // Remove by common selectors
      const selectors = [
        '[data-nextjs-dialog-overlay]',
        '[data-nextjs-dialog]',
        '[data-react-dev-tools]',
        '[data-react-devtools]',
        '.__react-devtools-overlay__',
        '#react-devtools-overlay',
        '[style*="z-index: 9999"]',
        '[style*="z-index:9999"]',
        '[style*="z-index: 99999"]',
        '[style*="z-index:99999"]',
        '[style*="z-index: 2147483647"]',
      ]

      selectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(el => {
          el.remove()
        })
      })

      // Remove fixed positioned elements in corners
      const fixedElements = document.querySelectorAll('body > div[style*="position: fixed"]')
      fixedElements.forEach(el => {
        const style = el.getAttribute('style') || ''
        // Check if it's likely a dev tool (in corner, high z-index)
        if (
          style.includes('bottom') && 
          (style.includes('right') || style.includes('left')) &&
          (style.includes('z-index') || style.includes('border-radius'))
        ) {
          el.remove()
        }
      })

      // Specifically target Next.js 15 dev indicator
      const allDivs = document.querySelectorAll('body > div')
      allDivs.forEach(div => {
        // Check if it's the Next.js floating button
        const hasButton = div.querySelector('button')
        const style = div.getAttribute('style') || ''
        
        if (hasButton && style.includes('position') && style.includes('fixed')) {
          // Check button content for typical Next.js dev indicators
          const buttonText = hasButton.textContent || ''
          const buttonStyle = hasButton.getAttribute('style') || ''
          
          if (
            buttonText.includes('Static') ||
            buttonText.includes('Route') ||
            buttonText.includes('Turbopack') ||
            buttonText.includes('Preferences') ||
            buttonStyle.includes('border-radius') ||
            div.querySelector('[style*="border-radius"]')
          ) {
            div.remove()
          }
        }
      })
    }

    // Remove on mount
    removeDevOverlay()

    // Remove any that appear later
    const interval = setInterval(removeDevOverlay, 500)

    // Use MutationObserver for immediate removal
    const observer = new MutationObserver(() => {
      removeDevOverlay()
    })

    observer.observe(document.body, {
      childList: true,
      subtree: false,
    })

    // Cleanup
    return () => {
      clearInterval(interval)
      observer.disconnect()
    }
  }, [])

  return null
}
