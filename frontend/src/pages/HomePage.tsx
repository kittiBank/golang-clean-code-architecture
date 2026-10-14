import { useAuth } from '../auth/useAuth'

// Placeholder landing page after login; profile / users pages come next
export function HomePage() {
  const { user, logout } = useAuth()
  const name = [user?.first_name, user?.last_name].filter(Boolean).join(' ') || user?.email

  return (
    <main className="mx-auto max-w-2xl p-6">
      <div className="flex items-center justify-between border-b border-gray-200 pb-4">
        <h1 className="text-2xl font-bold text-gray-900">Home</h1>
        <button
          onClick={logout}
          className="rounded border border-gray-300 px-3 py-1.5 text-sm hover:bg-gray-100"
        >
          Log out
        </button>
      </div>
      <p className="mt-4 text-gray-700">
        Logged in as <strong>{name}</strong> ({user?.email})
      </p>
    </main>
  )
}
