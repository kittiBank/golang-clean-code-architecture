import { getProfile } from '../api/users'
import { Alert } from '../components/Alert'
import { DetailList } from '../components/DetailList'
import { useApi } from '../hooks/useApi'
import { formatDate } from '../utils/format'

export function ProfilePage() {
  const { data: profile, error, loading } = useApi(getProfile, 'profile')

  return (
    <>
      <h1 className="mb-4 text-2xl font-bold text-gray-900">Profile</h1>
      {error && <Alert type="error">{error}</Alert>}
      {loading && !profile && <p className="text-gray-500">Loading...</p>}
      {profile && (
        <DetailList
          rows={[
            ['User ID', profile.id],
            ['Email', profile.email],
            ['First name', profile.first_name || '-'],
            ['Last name', profile.last_name || '-'],
            ['Member since', formatDate(profile.created_at)],
            ['Last updated', formatDate(profile.updated_at)],
          ]}
        />
      )}
    </>
  )
}
