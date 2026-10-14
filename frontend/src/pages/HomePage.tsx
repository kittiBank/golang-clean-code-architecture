import { Link } from 'react-router'

import { useAuth } from '../auth/useAuth'

export function HomePage() {
  const { user } = useAuth()
  const name = [user?.first_name, user?.last_name].filter(Boolean).join(' ') || user?.email

  return (
    <>
      <h1 className="mb-4 text-2xl font-bold text-gray-900">Welcome, {name}</h1>
      <ul className="list-inside list-disc space-y-1 text-gray-700">
        <li>
          <Link to="/users" className="text-blue-600 hover:underline">
            Users
          </Link>{' '}
          — browse and search all users
        </li>
        <li>
          <Link to="/profile" className="text-blue-600 hover:underline">
            Profile
          </Link>{' '}
          — your account details
        </li>
      </ul>
    </>
  )
}
