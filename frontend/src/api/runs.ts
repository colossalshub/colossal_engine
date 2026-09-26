import { apiGet } from './client'
import type { RunList, TearSheet } from './types'

export async function listRuns(params?: {
  strategy?: string
  status?: string
  page?: number
  page_size?: number
}): Promise<RunList> {
  const search = new URLSearchParams()
  if (params?.strategy) search.set('strategy', params.strategy)
  if (params?.status) search.set('status', params.status)
  if (params?.page !== undefined) search.set('page', String(params.page))
  if (params?.page_size !== undefined) search.set('page_size', String(params.page_size))
  const qs = search.toString()
  return apiGet<RunList>(`/runs${qs ? `?${qs}` : ''}`)
}

export async function getTearsheet(runId: string): Promise<TearSheet> {
  return apiGet<TearSheet>(`/runs/${encodeURIComponent(runId)}/tearsheet`)
}
