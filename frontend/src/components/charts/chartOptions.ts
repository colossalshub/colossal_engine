import { CrosshairMode, LineStyle, type ChartOptions, type DeepPartial } from 'lightweight-charts'

import type { Theme } from '../../lib/theme'

export type { Theme }

export function readTheme(): Theme {
  const attr = document.documentElement.getAttribute('data-theme')
  return attr === 'dark' ? 'dark' : 'light'
}

export function chartOptionsFor(theme: Theme): DeepPartial<ChartOptions> {
  const dark = theme === 'dark'
  return {
    layout: {
      background: { color: dark ? '#131722' : '#ffffff' },
      textColor: dark ? '#9ca3af' : '#4b5563',
      fontSize: 11,
      fontFamily: 'Inter, sans-serif',
    },
    grid: {
      vertLines: { color: dark ? '#1f2937' : '#e5e7eb' },
      horzLines: { color: dark ? '#1f2937' : '#e5e7eb' },
    },
    rightPriceScale: { borderColor: dark ? '#1f2937' : '#e5e7eb' },
    timeScale: {
      borderColor: dark ? '#1f2937' : '#e5e7eb',
      timeVisible: true,
      secondsVisible: false,
    },
    crosshair: {
      mode: CrosshairMode.Magnet,
      vertLine: { color: dark ? '#6b7280' : '#9ca3af', style: LineStyle.LargeDashed },
      horzLine: { color: dark ? '#6b7280' : '#9ca3af', style: LineStyle.LargeDashed },
    },
  }
}
