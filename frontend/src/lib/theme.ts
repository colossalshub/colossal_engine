export type Theme = 'light' | 'dark'

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
