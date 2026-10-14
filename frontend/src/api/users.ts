import { apiRequest } from './client'
import type { User } from './types'

export function getProfile(): Promise<User> {
  return apiRequest<User>('/users/profile', { auth: true })
}
