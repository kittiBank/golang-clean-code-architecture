import type { LoginResponse, TokenPair, User } from '../api/types'

// Session kept in localStorage so a page reload stays logged in
const STORAGE_KEY = 'auth'

type StoredSession = {
  user: User
  token: TokenPair
}

/** 'expired' = the API rejected the session and it could not be refreshed. */
export type SessionEndReason = 'logout' | 'expired'

type SessionListener = (session: StoredSession | null, reason?: SessionEndReason) => void

const listeners = new Set<SessionListener>()

/** Get notified whenever the session is saved or cleared (e.g. by the API client). */
export function onSessionChange(listener: SessionListener): () => void {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

export function loadSession(): StoredSession | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as StoredSession) : null
  } catch {
    return null
  }
}

export function saveSession(session: LoginResponse): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session))
  } catch {
    // Storage unavailable (e.g. private mode): stay logged in for this tab only
  }
  listeners.forEach((listener) => listener(session))
}

export function clearSession(reason: SessionEndReason = 'logout'): void {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch {
    // ignore
  }
  listeners.forEach((listener) => listener(null, reason))
}

export function getAccessToken(): string | null {
  return loadSession()?.token.access ?? null
}

export function getRefreshToken(): string | null {
  return loadSession()?.token.refresh ?? null
}
