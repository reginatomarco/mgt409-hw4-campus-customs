import { useEffect, useState, type ReactNode } from 'react'
import { getJson, postJson } from './api'
import { AuthContext, type RegisterForm, type User } from './authContext'

// The session lives in an HttpOnly cookie set by the backend; this only mirrors who is logged in.
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getJson<User>('/api/auth/me')
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [])

  async function login(email: string, password: string) {
    const u = await postJson<User>('/api/auth/login', { email, password })
    setUser(u)
    return u
  }

  async function register(form: RegisterForm) {
    const u = await postJson<User>('/api/auth/register', form)
    setUser(u)
    return u
  }

  async function logout() {
    await fetch('/api/auth/logout', { method: 'POST' })
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, loading, login, register, logout }}>{children}</AuthContext.Provider>
}
