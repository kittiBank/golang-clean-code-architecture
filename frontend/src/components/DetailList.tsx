import type { ReactNode } from 'react'

/** Label / value rows, used by the profile and user detail pages. */
export function DetailList({ rows }: { rows: [label: string, value: ReactNode][] }) {
  return (
    <dl className="divide-y divide-gray-200 rounded border border-gray-200 bg-white">
      {rows.map(([label, value]) => (
        <div key={label} className="grid grid-cols-3 gap-4 px-4 py-3">
          <dt className="text-sm font-medium text-gray-500">{label}</dt>
          <dd className="col-span-2 text-sm break-all text-gray-900">{value}</dd>
        </div>
      ))}
    </dl>
  )
}
