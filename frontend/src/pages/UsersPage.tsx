import type { FormEvent } from 'react'
import { Link, useSearchParams } from 'react-router'

import { listRecords } from '../api/data'
import type { User } from '../api/types'
import { Alert } from '../components/Alert'
import { Pagination } from '../components/Pagination'
import { useApi } from '../hooks/useApi'
import { formatDate } from '../utils/format'

const PAGE_SIZES = [10, 20, 50]
const DEFAULT_PAGE_SIZE = 10

// Must match the filterable fields in python-api/app/crud_registry.py
const FILTERS = [
  { name: 'email', label: 'Email' },
  { name: 'first_name', label: 'First name' },
  { name: 'last_name', label: 'Last name' },
]

function toPositiveInt(value: string | null, fallback: number): number {
  const number = Number(value)
  return Number.isInteger(number) && number > 0 ? number : fallback
}

export function UsersPage() {
  // Page, page size and filters live in the URL: shareable, survive reload, back button works
  const [params, setParams] = useSearchParams()
  const page = toPositiveInt(params.get('page'), 1)
  const sizeParam = toPositiveInt(params.get('size'), DEFAULT_PAGE_SIZE)
  const pageSize = PAGE_SIZES.includes(sizeParam) ? sizeParam : DEFAULT_PAGE_SIZE
  const filters: Record<string, string> = {}
  for (const { name } of FILTERS) {
    const value = params.get(name)
    if (value) filters[name] = value
  }

  const { data, error, loading } = useApi(
    () => listRecords<User>('users', { page, pageSize, filters }),
    params.toString(),
  )

  function updateParams(changes: Record<string, string | number | null>) {
    const next = new URLSearchParams(params)
    for (const [key, value] of Object.entries(changes)) {
      if (value === null || value === '') next.delete(key)
      else next.set(key, String(value))
    }
    setParams(next)
  }

  function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const changes: Record<string, string | null> = { page: null }
    for (const { name } of FILTERS) changes[name] = String(form.get(name) ?? '').trim()
    updateParams(changes)
  }

  function clearFilters() {
    updateParams({ page: null, ...Object.fromEntries(FILTERS.map(({ name }) => [name, null])) })
  }

  const hasFilters = Object.keys(filters).length > 0

  return (
    <>
      <h1 className="mb-4 text-2xl font-bold text-gray-900">Users</h1>

      {/* key: reset the inputs when the URL changes (e.g. Clear, back button) */}
      <form
        key={params.toString()}
        onSubmit={handleSearch}
        className="mb-4 flex flex-wrap items-end gap-3 rounded border border-gray-200 bg-white p-4"
      >
        {FILTERS.map(({ name, label }) => (
          <div key={name} className="min-w-40 flex-1">
            <label htmlFor={`filter-${name}`} className="mb-1 block text-sm font-medium text-gray-700">
              {label}
            </label>
            <input
              id={`filter-${name}`}
              name={name}
              defaultValue={filters[name] ?? ''}
              placeholder="Exact match"
              className="w-full rounded border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        ))}
        <div className="flex gap-2">
          <button
            type="submit"
            className="rounded bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
          >
            Search
          </button>
          {hasFilters && (
            <button
              type="button"
              onClick={clearFilters}
              className="rounded border border-gray-300 bg-white px-4 py-1.5 text-sm hover:bg-gray-100"
            >
              Clear
            </button>
          )}
        </div>
      </form>

      {error && <Alert type="error">{error}</Alert>}

      {data && (
        <div className={loading ? 'opacity-60' : ''}>
          <div className="mb-3 overflow-x-auto rounded border border-gray-200 bg-white">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-gray-200 bg-gray-50 whitespace-nowrap text-gray-600">
                <tr>
                  <th className="px-4 py-2 font-medium">ID</th>
                  <th className="px-4 py-2 font-medium">Email</th>
                  <th className="px-4 py-2 font-medium">First name</th>
                  <th className="px-4 py-2 font-medium">Last name</th>
                  <th className="px-4 py-2 font-medium">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {data.data.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-gray-500">{user.id}</td>
                    <td className="px-4 py-2">
                      <Link
                        to={`/users/${user.id}`}
                        state={{ listSearch: params.toString() }}
                        className="text-blue-600 hover:underline"
                      >
                        {user.email}
                      </Link>
                    </td>
                    <td className="px-4 py-2">{user.first_name || '-'}</td>
                    <td className="px-4 py-2">{user.last_name || '-'}</td>
                    <td className="px-4 py-2 whitespace-nowrap text-gray-500">{formatDate(user.created_at)}</td>
                  </tr>
                ))}
                {data.data.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                      No users found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3">
            <Pagination
              page={data.page}
              pageSize={data.page_size}
              totalPage={data.total_page}
              totalData={data.total_data}
              onPageChange={(next) => updateParams({ page: next === 1 ? null : next })}
            />
            <label className="flex items-center gap-2 text-sm text-gray-600">
              Rows per page
              <select
                value={pageSize}
                onChange={(e) => updateParams({ size: e.target.value, page: null })}
                className="rounded border border-gray-300 bg-white px-2 py-1"
              >
                {PAGE_SIZES.map((size) => (
                  <option key={size} value={size}>
                    {size}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>
      )}

      {!data && loading && <p className="text-gray-500">Loading...</p>}
    </>
  )
}
