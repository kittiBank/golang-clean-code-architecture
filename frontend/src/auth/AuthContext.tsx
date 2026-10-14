import { useCallback, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

import * as authApi from '../api/auth'
import type { LoginRequest, User } from '../api/types'
import { clearSession, getRefreshToken, loadSession, onSessionChange, saveSession } from './storage'
import { AuthContext } from './useAuth'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => loadSession()?.user ?? null)
  const [sessionExpired, setSessionExpired] = useState(false)

  // Storage is the source of truth: login, logout, token refresh and expiry
  // (from the API client) all go through it, and this keeps React in sync.
  useEffect(
    () =>
      onSessionChange((session, reason) => {
        setUser(session?.user ?? null)
        setSessionExpired(reason === 'expired')
      }),
    [],
  )

  const login = useCallback(async (credentials: LoginRequest) => {
    saveSession(await authApi.login(credentials))
  }, [])

  const logout = useCallback(async () => {
    const refresh = getRefreshToken()
    try {
      if (refresh) await authApi.logout(refresh)
    } catch {
      // Session may already be invalid on the server; log out locally anyway
    } finally {
      clearSession('logout')
    }
  }, [])

  const value = useMemo(
    () => ({ user, sessionExpired, login, logout }),
    [user, sessionExpired, login, logout],
  )
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
