import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

export function formatPercentage(value: number): string {
  return `${(value * 100).toFixed(2)}%`
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value)
}

export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'active':
      return 'text-success bg-success/10'
    case 'paused':
      return 'text-warning bg-warning/10'
    case 'stopped':
      return 'text-muted-foreground bg-muted'
    case 'error':
      return 'text-destructive bg-destructive/10'
    case 'created':
      return 'text-defi-primary bg-defi-primary/10'
    default:
      return 'text-muted-foreground bg-muted'
  }
}

export function getRiskColor(risk: string): string {
  switch (risk.toLowerCase()) {
    case 'low':
      return 'text-success bg-success/10'
    case 'medium':
      return 'text-warning bg-warning/10'
    case 'high':
      return 'text-destructive bg-destructive/10'
    default:
      return 'text-muted-foreground bg-muted'
  }
}
