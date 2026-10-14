import { useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'

import { register } from '../api/auth'
import { Alert } from '../components/Alert'
import { AuthCard, SubmitButton } from '../components/AuthCard'
import { TextField } from '../components/TextField'

const MAX_PASSWORD_BYTES = 72 // bcrypt limit, enforced by the API too

const EMPTY_FORM = {
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  confirm_password: '',
}

function validate(form: typeof EMPTY_FORM): string | null {
  if (new TextEncoder().encode(form.password).length > MAX_PASSWORD_BYTES) {
    return `Password must be at most ${MAX_PASSWORD_BYTES} bytes`
  }
  if (form.password !== form.confirm_password) return 'Passwords do not match'
  return null
}

export function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState(EMPTY_FORM)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    setForm({ ...form, [event.target.name]: event.target.value })
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const validationError = validate(form)
    if (validationError) {
      setError(validationError)
      return
    }

    setError(null)
    setLoading(true)
    try {
      const { confirm_password: _, ...data } = form
      await register(data)
      // Register doesn't log in (same as the API): go to login with the email filled in
      navigate('/login', { state: { email: form.email, registered: true } })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
      setLoading(false)
    }
  }

  return (
    <AuthCard title="Create account">
      {error && <Alert type="error">{error}</Alert>}

      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-2 gap-3">
          <TextField label="First name" name="first_name" autoComplete="given-name" value={form.first_name} onChange={handleChange} disabled={loading} />
          <TextField label="Last name" name="last_name" autoComplete="family-name" value={form.last_name} onChange={handleChange} disabled={loading} />
        </div>
        <TextField label="Email" name="email" type="email" autoComplete="email" required value={form.email} onChange={handleChange} disabled={loading} />
        <TextField label="Password" name="password" type="password" autoComplete="new-password" required value={form.password} onChange={handleChange} disabled={loading} />
        <TextField label="Confirm password" name="confirm_password" type="password" autoComplete="new-password" required value={form.confirm_password} onChange={handleChange} disabled={loading} />
        <SubmitButton loading={loading}>{loading ? 'Creating account...' : 'Register'}</SubmitButton>
      </form>

      <p className="mt-4 text-center text-sm text-gray-600">
        Already have an account?{' '}
        <Link to="/login" className="text-blue-600 hover:underline">
          Log in
        </Link>
      </p>
    </AuthCard>
  )
}
