import { useEffect, useState } from 'react'

import { ApiError } from '../api/client'
import type { User } from '../api/types'
import { getProfile } from '../api/users'
import { Alert } from '../components/Alert'

function formatDate(value: string | null): string {
  return value ? new Date(value).toLocaleString() : '-'
}

export function ProfilePage() {
  const [profile, setProfile] = useState<User | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    getProfile()
      .then((user) => !cancelled && setProfile(user))
      .catch((err: unknown) => {
        // 401 = session ended: the auth guard is already redirecting to /login
        if (cancelled || (err instanceof ApiError && err.status === 401)) return
        setError(err instanceof Error ? err.message : 'Could not load profile')
      })
    return () => {
      cancelled = true
    }
  }, [])

  const rows: [string, string | number][] = profile
    ? [
        ['User ID', profile.id],
        ['Email', profile.email],
        ['First name', profile.first_name || '-'],
        ['Last name', profile.last_name || '-'],
        ['Member since', formatDate(profile.created_at)],
        ['Last updated', formatDate(profile.updated_at)],
      ]
    : []

  return (
    <>
      <h1 className="mb-4 text-2xl font-bold text-gray-900">Profile</h1>
      {error && <Alert type="error">{error}</Alert>}
      {!profile && !error && <p className="text-gray-500">Loading...</p>}
      {profile && (
        <dl className="divide-y divide-gray-200 rounded border border-gray-200 bg-white">
          {rows.map(([label, value]) => (
            <div key={label} className="grid grid-cols-3 gap-4 px-4 py-3">
              <dt className="text-sm font-medium text-gray-500">{label}</dt>
              <dd className="col-span-2 text-sm text-gray-900">{value}</dd>
            </div>
          ))}
        </dl>
      )}
    </>
  )
}
