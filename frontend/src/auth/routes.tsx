import { Navigate, Outlet, useLocation } from 'react-router'

import { useAuth } from './useAuth'

/** Pages that need login: send anonymous users to /login, then back here afterwards. */
export function RequireAuth() {
  const { user } = useAuth()
  const location = useLocation()

  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  return <Outlet />
}

/** Login/register pages: already logged-in users go straight to the home page. */
export function GuestOnly() {
  const { user } = useAuth()

  if (user) return <Navigate to="/" replace />
  return <Outlet />
}
