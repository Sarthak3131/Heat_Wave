import {
  Activity,
  Bell,
  Clock3,
  CloudSun,
  Map,
  Menu,
  ThermometerSun,
} from 'lucide-react'
import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'

const navigation = [
  { to: '/', label: 'Dashboard', icon: Activity, end: true },
  { to: '/forecast', label: 'Forecast', icon: CloudSun },
  { to: '/map', label: 'City map', icon: Map },
  { to: '/history', label: 'History', icon: Clock3 },
  { to: '/alerts', label: 'Alerts', icon: Bell },
]

function AppLayout() {
  const [menuOpen, setMenuOpen] = useState(false)

  function closeMenu() {
    setMenuOpen(false)
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <header className="site-header">
        <div className="header-inner">
          <NavLink
            className="brand"
            to="/"
            aria-label="HeatWatch home"
            onClick={closeMenu}
          >
            <span className="brand-mark" aria-hidden="true">
              <ThermometerSun size={21} strokeWidth={2.2} />
            </span>
            <span className="brand-name">Heat<span>Watch</span></span>
          </NavLink>

          <button
            aria-expanded={menuOpen}
            aria-controls="primary-navigation"
            aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
            className="menu-toggle"
            onClick={() => setMenuOpen((open) => !open)}
            type="button"
          >
            <Menu size={21} />
          </button>

          <nav
            aria-label="Main navigation"
            className={`main-navigation${menuOpen ? ' is-open' : ''}`}
            id="primary-navigation"
          >
            {navigation.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                className={({ isActive }) =>
                  `navigation-link${isActive ? ' is-active' : ''}`
                }
                end={end}
                key={to}
                onClick={closeMenu}
                to={to}
              >
                <Icon aria-hidden="true" size={17} />
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>

          <div className="header-status">
            <span className="status-dot" aria-hidden="true" />
            <span>Educational prototype</span>
          </div>
        </div>
      </header>

      <main className="main-content" id="main-content">
        <Outlet />
      </main>

      <footer className="site-footer">
        <div className="footer-inner">
          <span>HeatWatch <span aria-hidden="true">·</span> Learning through local weather</span>
          <NavLink to="/about">About this project</NavLink>
        </div>
        <p className="disclaimer">
          Informational only — not an official emergency warning service.
        </p>
      </footer>
    </div>
  )
}

export default AppLayout
