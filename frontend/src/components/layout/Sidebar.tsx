import { NavLink } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/', label: 'Command Center', end: true },
  { to: '/data', label: 'Data Manager', end: false },
] as const

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar__logo">colossal</div>
      <nav className="sidebar__nav" aria-label="Primary">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              isActive ? 'sidebar__item sidebar__item--active' : 'sidebar__item'
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
