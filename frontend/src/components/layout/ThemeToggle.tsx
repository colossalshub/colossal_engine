import { useEffect, useState } from 'react'
import { applyTheme, getStoredTheme, type Theme } from '../../lib/theme'
import './themeToggle.css'

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(() => getStoredTheme())

  useEffect(() => {
    applyTheme(theme)
  }, [theme])

  const next = theme === 'light' ? 'dark' : 'light'

  return (
    <button
      type="button"
      className="theme-toggle"
      aria-label={`Switch to ${next} theme`}
      title={`Switch to ${next} theme`}
      onClick={() => setTheme(next)}
    >
      {theme === 'light' ? '☾' : '☀'}
    </button>
  )
}
