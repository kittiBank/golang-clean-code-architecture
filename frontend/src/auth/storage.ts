import type { LoginResponse, TokenPair, User } from '../api/types'

// Session kept in localStorage so a page reload stays logged in
const STORAGE_KEY = 'auth'

type StoredSession = {
  user: User
  token: TokenPair
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
}

export function clearSession(): void {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch {
    // ignore
  }
}

export function getAccessToken(): string | null {
  return loadSession()?.token.access ?? null
}
