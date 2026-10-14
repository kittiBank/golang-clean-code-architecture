import { Link, useLocation, useParams } from 'react-router'

import { ApiError } from '../api/client'
import { getRecord } from '../api/data'
import type { User } from '../api/types'
import { Alert } from '../components/Alert'
import { DetailList } from '../components/DetailList'
import { useApi } from '../hooks/useApi'
import { formatDate, fullName } from '../utils/format'

async function fetchUser(id: string) {
  if (!/^[1-9]\d*$/.test(id)) throw new Error('User not found')
  try {
    return await getRecord<User>('users', id)
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) throw new Error('User not found')
    throw err
  }
}

export function UserDetailPage() {
  const { id = '' } = useParams()
  // Set by the users list, so "Back" returns to the same page and filters
  const listSearch = (useLocation().state as { listSearch?: string } | null)?.listSearch
  const { data, error, loading } = useApi(() => fetchUser(id), id)
  const user = data?.data

  return (
    <>
      <Link
        to={listSearch ? `/users?${listSearch}` : '/users'}
        className="mb-4 inline-block text-sm text-blue-600 hover:underline"
      >
        ← Back to users
      </Link>
      <h1 className="mb-4 text-2xl font-bold text-gray-900">
        {user ? fullName(user) || user.email : 'User'}
      </h1>

      {error && <Alert type="error">{error}</Alert>}
      {loading && !user && <p className="text-gray-500">Loading...</p>}
      {user && (
        <DetailList
          rows={[
            ['User ID', user.id],
            ['Email', user.email],
            ['First name', user.first_name || '-'],
            ['Last name', user.last_name || '-'],
            ['Created', formatDate(user.created_at)],
            ['Last updated', formatDate(user.updated_at)],
          ]}
        />
      )}
    </>
  )
}
