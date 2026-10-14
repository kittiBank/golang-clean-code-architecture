import { useEffect, useEffectEvent, useState } from 'react'

import { ApiError } from '../api/client'

type Result<T> = {
  key: string // which request this result belongs to
  data: T | null
  error: string | null
}

/**
 * Load data from the API whenever `key` changes (`key` must describe everything
 * the fetcher depends on, e.g. the URL query). While reloading, the previous
 * data is kept so pages don't flash empty.
 */
export function useApi<T>(fetcher: () => Promise<T>, key: string) {
  const [result, setResult] = useState<Result<T> | null>(null)
  const fetchData = useEffectEvent(fetcher) // always the latest fetcher, without re-running the effect

  useEffect(() => {
    let cancelled = false
    fetchData()
      .then((data) => {
        if (!cancelled) setResult({ key, data, error: null })
      })
      .catch((err: unknown) => {
        // 401 = session ended: the auth guard is already redirecting to /login
        if (cancelled || (err instanceof ApiError && err.status === 401)) return
        const message = err instanceof Error ? err.message : 'Something went wrong'
        setResult({ key, data: null, error: message })
      })
    return () => {
      cancelled = true
    }
  }, [key])

  const loading = result?.key !== key
  return {
    data: result?.data ?? null,
    error: loading ? null : (result?.error ?? null),
    loading,
  }
}
