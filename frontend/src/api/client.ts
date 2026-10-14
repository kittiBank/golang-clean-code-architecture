import { clearSession, getAccessToken, getRefreshToken, saveSession } from '../auth/storage'
import type { ApiErrorBody, LoginResponse } from './types'

const BASE_URL = '/api/v1' // proxied to FastAPI by Vite (see vite.config.ts)

export class ApiError extends Error {
  status: number
  traceId: string

  constructor(status: number, traceId: string, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.traceId = traceId
  }
}

type RequestOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  body?: unknown
  auth?: boolean // attach "Authorization: Bearer <access token>", refreshing it if needed
}

/** Call the API and return the parsed JSON. Throws ApiError on any failure. */
export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const tokenUsed = options.auth ? getAccessToken() : null
  let response = await send(path, options, tokenUsed)

  if (response.status === 401 && options.auth) {
    // Access token expired or revoked: get a new one, then retry once
    if (await ensureFreshToken(tokenUsed)) {
      response = await send(path, options, getAccessToken())
    } else {
      clearSession('expired') // RequireAuth sends the user to /login
    }
  }
  return parseResponse<T>(response)
}

async function send(path: string, options: RequestOptions, token: string | null): Promise<Response> {
  const { method = 'GET', body } = options
  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers['Authorization'] = `Bearer ${token}`

  try {
    return await fetch(BASE_URL + path, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiError(0, 'network-error', 'Cannot reach the server. Is the backend running?')
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    const error = data as ApiErrorBody | null
    throw new ApiError(
      response.status,
      error?.trace_id ?? 'unknown-error',
      error?.message ?? `Request failed (HTTP ${response.status})`,
    )
  }
  return data as T
}

// --- Token refresh ---

// The API rotates refresh tokens (each one works once), so concurrent 401s
// must share a single refresh call instead of each starting their own.
let refreshInFlight: Promise<boolean> | null = null

async function ensureFreshToken(tokenUsed: string | null): Promise<boolean> {
  // Another request already refreshed while this one was in flight: just retry
  const current = getAccessToken()
  if (current && current !== tokenUsed) return true

  refreshInFlight ??= refreshSession().finally(() => {
    refreshInFlight = null
  })
  return refreshInFlight
}

async function refreshSession(): Promise<boolean> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return false

  try {
    const response = await send(
      '/users/refresh-token',
      { method: 'POST', body: { refresh_token: refreshToken } },
      null,
    )
    if (!response.ok) return false
    saveSession((await response.json()) as LoginResponse)
    return true
  } catch {
    return false
  }
}
