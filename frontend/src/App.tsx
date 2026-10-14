import { useEffect, useState } from 'react'

type Health = { name: string; version: string }

// Starter page: checks the frontend can reach the API through the Vite proxy
function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/v1/')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(setHealth)
      .catch((err: Error) => setError(err.message))
  }, [])

  return (
    <main className="mx-auto max-w-md p-6">
      <h1 className="mb-4 text-2xl font-bold">Frontend is running</h1>
      <div className="rounded border border-gray-300 p-4">
        <h2 className="mb-2 font-semibold">API status</h2>
        {health && (
          <p className="text-green-700">
            Connected: {health.name} v{health.version}
          </p>
        )}
        {error && (
          <p className="text-red-700">
            Cannot reach API ({error}). Is the backend running on port 3000?
          </p>
        )}
        {!health && !error && <p className="text-gray-500">Checking...</p>}
      </div>
    </main>
  )
}

export default App
