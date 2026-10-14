import { NavLink, Outlet } from 'react-router'

import { useAuth } from '../auth/useAuth'

function navClass({ isActive }: { isActive: boolean }) {
  return `rounded px-3 py-1.5 text-sm ${
    isActive ? 'bg-gray-200 font-medium text-gray-900' : 'text-gray-600 hover:bg-gray-100'
  }`
}

/** Header + navigation shared by all logged-in pages. */
export function AppLayout() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-between gap-2 px-4 py-3">
          <nav className="flex items-center gap-1">
            <span className="mr-3 font-bold text-gray-900">User Management</span>
            <NavLink to="/" end className={navClass}>
              Home
            </NavLink>
            <NavLink to="/users" className={navClass}>
              Users
            </NavLink>
            <NavLink to="/profile" className={navClass}>
              Profile
            </NavLink>
          </nav>
          <div className="flex items-center gap-3">
            <span className="hidden text-sm text-gray-600 sm:inline">{user?.email}</span>
            <button
              onClick={logout}
              className="rounded border border-gray-300 px-3 py-1.5 text-sm hover:bg-gray-100"
            >
              Log out
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-4xl p-4">
        <Outlet />
      </main>
    </div>
  )
}
