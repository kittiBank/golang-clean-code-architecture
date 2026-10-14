import { useCallback, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

import * as authApi from '../api/auth'
import type { LoginRequest, User } from '../api/types'
import { clearSession, loadSession, saveSession } from './storage'
import { AuthContext } from './useAuth'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => loadSession()?.user ?? null)

  const login = useCallback(async (credentials: LoginRequest) => {
    const session = await authApi.login(credentials)
    saveSession(session)
    setUser(session.user)
  }, [])

  const logout = useCallback(async () => {
    const refresh = loadSession()?.token.refresh
    try {
      if (refresh) await authApi.logout(refresh)
    } catch {
      // Session may already be invalid on the server; log out locally anyway
    } finally {
      clearSession()
      setUser(null)
    }
  }, [])

  const value = useMemo(() => ({ user, login, logout }), [user, login, logout])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
