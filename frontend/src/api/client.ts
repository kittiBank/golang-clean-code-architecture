import { getAccessToken } from '../auth/storage'
import type { ApiErrorBody } from './types'

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
  auth?: boolean // attach "Authorization: Bearer <access token>"
}

/** Call the API and return the parsed JSON. Throws ApiError on any failure. */
export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, auth = false } = options

  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (auth) {
    const token = getAccessToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  let response: Response
  try {
    response = await fetch(BASE_URL + path, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiError(0, 'network-error', 'Cannot reach the server. Is the backend running?')
  }

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
