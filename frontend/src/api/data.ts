import { apiRequest } from './client'
import type { DataListResponse, DataResponse } from './types'

export type ListParams = {
  page?: number
  pageSize?: number
  filters?: Record<string, string> // exact-match filters on whitelisted fields
}

/** GET /data/{slug}/ — one page of records. */
export function listRecords<T>(
  slug: string,
  { page = 1, pageSize = 10, filters = {} }: ListParams = {},
): Promise<DataListResponse<T>> {
  const query = new URLSearchParams({
    _page: String(page),
    _pageSize: String(pageSize),
    ...filters,
  })
  return apiRequest(`/data/${encodeURIComponent(slug)}/?${query}`, { auth: true })
}

/** GET /data/{slug}/{id} — one record. */
export function getRecord<T>(slug: string, id: string | number): Promise<DataResponse<T>> {
  return apiRequest(`/data/${encodeURIComponent(slug)}/${encodeURIComponent(id)}`, { auth: true })
}
