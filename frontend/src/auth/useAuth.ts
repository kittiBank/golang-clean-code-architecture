import { createContext, useContext } from 'react'

import type { LoginRequest, User } from '../api/types'

export type AuthContextValue = {
  user: User | null
  sessionExpired: boolean // true after the API ended the session (shown on the login page)
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside <AuthProvider>')
  return context
}
