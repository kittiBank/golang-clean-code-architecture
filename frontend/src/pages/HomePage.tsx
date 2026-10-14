import { Link } from 'react-router'

import { useAuth } from '../auth/useAuth'

// Placeholder landing page after login; the users list comes next
export function HomePage() {
  const { user } = useAuth()
  const name = [user?.first_name, user?.last_name].filter(Boolean).join(' ') || user?.email

  return (
    <>
      <h1 className="mb-4 text-2xl font-bold text-gray-900">Welcome, {name}</h1>
      <p className="text-gray-700">
        See your account details on the{' '}
        <Link to="/profile" className="text-blue-600 hover:underline">
          Profile
        </Link>{' '}
        page.
      </p>
    </>
  )
}
