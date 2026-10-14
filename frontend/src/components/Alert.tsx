import type { ReactNode } from 'react'

const STYLES = {
  error: 'border-red-300 bg-red-50 text-red-800',
  success: 'border-green-300 bg-green-50 text-green-800',
}

export function Alert({ type, children }: { type: keyof typeof STYLES; children: ReactNode }) {
  return (
    <div role={type === 'error' ? 'alert' : 'status'} className={`mb-4 rounded border px-3 py-2 text-sm ${STYLES[type]}`}>
      {children}
    </div>
  )
}
