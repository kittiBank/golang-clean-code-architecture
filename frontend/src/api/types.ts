// Shapes returned by the FastAPI backend (see python-api/app/domain/schemas)

export type User = {
  id: number
  email: string
  first_name: string | null
  last_name: string | null
  created_at: string | null
  updated_at: string | null
}

export type TokenPair = {
  access: string
  refresh: string
}

export type LoginResponse = {
  user: User
  token: TokenPair
}

export type RegisterRequest = {
  email: string
  password: string
  first_name: string
  last_name: string
}

export type LoginRequest = {
  email: string
  password: string
}

// Every API error has this body: {"trace_id": "users-002", "message": "..."}
export type ApiErrorBody = {
  trace_id: string
  message: string
}
