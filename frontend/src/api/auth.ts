import { apiRequest } from './client'
import type { LoginRequest, LoginResponse, RegisterRequest, User } from './types'

export function register(data: RegisterRequest): Promise<User> {
  return apiRequest<User>('/users/register', { method: 'POST', body: data })
}

export function login(data: LoginRequest): Promise<LoginResponse> {
  return apiRequest<LoginResponse>('/users/login', { method: 'POST', body: data })
}

export function logout(refreshToken: string): Promise<null> {
  return apiRequest<null>('/users/logout', {
    method: 'POST',
    body: { refresh_token: refreshToken },
  })
}
