import { NavLink } from 'react-router-dom'
import './tearSheetNav.css'

interface NavItem {
  to: string
  label: string
  planned?: string
}

const ITEMS: NavItem[] = [
  { to: 'overview', label: 'Overview' },
  { to: 'performance', label: 'Performance' },
  { to: 'trades', label: 'Trades' },
  { to: 'risk', label: 'Risk' },
  { to: 'regimes', label: 'Regimes', planned: 'Phase 21' },
  { to: 'execution', label: 'Execution' },
  { to: 'robustness', label: 'Robustness', planned: 'Phase 18–20' },
  { to: 'data', label: 'Data' },
]

export function TearSheetNav() {
  return (
    <nav className="tear-sheet-nav" aria-label="Tear sheet sections">
      {ITEMS.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            isActive ? 'tear-sheet-nav__item tear-sheet-nav__item--active' : 'tear-sheet-nav__item'
          }
        >
          <span className="tear-sheet-nav__label">{item.label}</span>
          {item.planned ? (
            <span className="tear-sheet-nav__planned">{item.planned}</span>
          ) : null}
        </NavLink>
      ))}
    </nav>
  )
}
