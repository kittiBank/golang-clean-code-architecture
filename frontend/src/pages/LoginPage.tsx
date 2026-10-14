import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router'

import { useAuth } from '../auth/useAuth'
import { Alert } from '../components/Alert'
import { AuthCard, SubmitButton } from '../components/AuthCard'
import { TextField } from '../components/TextField'

// Set by RegisterPage (after sign-up) or RequireAuth (page that needed login)
type LocationState = { email?: string; registered?: boolean; from?: string } | null

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const state = useLocation().state as LocationState

  const [email, setEmail] = useState(state?.email ?? '')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await login({ email, password })
      navigate(state?.from ?? '/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
      setLoading(false)
    }
  }

  return (
    <AuthCard title="Log in">
      {state?.registered && !error && (
        <Alert type="success">Account created. Please log in.</Alert>
      )}
      {error && <Alert type="error">{error}</Alert>}

      <form onSubmit={handleSubmit}>
        <TextField
          label="Email"
          name="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={loading}
        />
        <TextField
          label="Password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={loading}
        />
        <SubmitButton loading={loading}>{loading ? 'Logging in...' : 'Log in'}</SubmitButton>
      </form>

      <p className="mt-4 text-center text-sm text-gray-600">
        No account?{' '}
        <Link to="/register" className="text-blue-600 hover:underline">
          Register
        </Link>
      </p>
    </AuthCard>
  )
}
