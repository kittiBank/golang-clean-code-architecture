type PaginationProps = {
  page: number
  pageSize: number
  totalPage: number
  totalData: number
  onPageChange: (page: number) => void
}

const buttonClass =
  'rounded border border-gray-300 bg-white px-3 py-1.5 text-sm hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50'

export function Pagination({ page, pageSize, totalPage, totalData, onPageChange }: PaginationProps) {
  const first = totalData === 0 ? 0 : Math.min((page - 1) * pageSize + 1, totalData)
  const last = Math.min(page * pageSize, totalData)

  return (
    <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-gray-600">
      <span>
        Showing {first}–{last} of {totalData}
      </span>
      <div className="flex items-center gap-2">
        <button className={buttonClass} disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
          Previous
        </button>
        <span>
          Page {page} of {Math.max(totalPage, 1)}
        </span>
        <button
          className={buttonClass}
          disabled={page >= totalPage}
          onClick={() => onPageChange(page + 1)}
        >
          Next
        </button>
      </div>
    </div>
  )
}
