import { createContext, useContext } from 'react'

export interface User {
  id: number
  first_name: string
  last_name: string
  email: string
}

export interface RegisterForm {
  first_name: string
  last_name: string
  email: string
  password: string
  confirm_password: string
}

interface AuthState {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<User>
  register: (form: RegisterForm) => Promise<User>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthState | null>(null)

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
