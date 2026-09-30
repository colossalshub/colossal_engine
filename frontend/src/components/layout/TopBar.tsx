import { useLocation } from 'react-router-dom'
import { ThemeToggle } from './ThemeToggle'

function breadcrumbFor(pathname: string): string {
  if (pathname === '/') return 'Command Center'
  if (pathname.startsWith('/runs/')) return 'Tear Sheet'
  if (pathname.startsWith('/data')) return 'Data Manager'
  return ''
}

export function TopBar() {
  const { pathname } = useLocation()
  return (
    <header className="topbar">
      <span className="topbar__breadcrumb">{breadcrumbFor(pathname)}</span>
      <div className="topbar__actions">
        <ThemeToggle />
      </div>
    </header>
  )
}
