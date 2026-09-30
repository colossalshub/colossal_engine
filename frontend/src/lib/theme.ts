import { useEffect, useState } from 'react'

export type Theme = 'light' | 'dark'

function readAttr(): Theme {
  return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'
}

export function useTheme(): Theme {
  const [theme, setTheme] = useState<Theme>(readAttr)

  useEffect(() => {
    const observer = new MutationObserver(() => setTheme(readAttr()))
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme'],
    })
    return () => observer.disconnect()
  }, [])

  return theme
}

const STORAGE_KEY = 'quant-theme'

export function getStoredTheme(): Theme {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw === 'light' || raw === 'dark') return raw
  } catch {
    // localStorage unavailable (private mode, etc.)
  }
  return 'light'
}

export function applyTheme(theme: Theme): void {
  document.documentElement.setAttribute('data-theme', theme)
  try {
    localStorage.setItem(STORAGE_KEY, theme)
  } catch {
    // best-effort persistence
  }
}
