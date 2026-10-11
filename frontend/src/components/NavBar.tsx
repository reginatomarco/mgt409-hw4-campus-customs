import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../authContext'

const pages = [
  { to: '/', label: 'Home' },
  { to: '/products', label: 'Products' },
  { to: '/about', label: 'About Us' },
]

export default function NavBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)

  async function handleLogout() {
    await logout()
    navigate('/')
  }

  const close = () => setMenuOpen(false)

  return (
    <header className="navbar">
      <div className="announcement">
        Officially licensed Yale gear · 57 Broadway, New Haven · Bulldog-approved since forever
      </div>
      <div className="navbar-inner">
        <NavLink to="/" className="brand" onClick={close}>
          <span className="brand-mark">CC</span>
          <span className="brand-text">
            Campus Customs
            <small>Yale Bulldog Blue</small>
          </span>
        </NavLink>
        <button
          type="button"
          className="menu-toggle"
          aria-label="Toggle menu"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? '✕' : '☰'}
        </button>
        <nav className={menuOpen ? 'open' : undefined}>
          {pages.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.to === '/'} className="nav-link" onClick={close}>
              {link.label}
            </NavLink>
          ))}
          <span className="nav-divider" />
          {user ? (
            <>
              <span className="nav-user">
                <span className="avatar">{user.first_name.charAt(0).toUpperCase()}</span>
                {user.first_name}
              </span>
              <button
                type="button"
                className="nav-link nav-button"
                onClick={() => {
                  close()
                  handleLogout()
                }}
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className="nav-link" onClick={close}>
                Log in
              </NavLink>
              <NavLink to="/create-account" className="nav-cta" onClick={close}>
                Create Account
              </NavLink>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}
