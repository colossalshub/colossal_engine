import { apiGet, apiPost } from './client'
import type { RunCreate, RunList, RunSummary, TearSheet, TradePage } from './types'

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

export async function getTrades(
  runId: string,
  params: { page?: number; page_size?: number } = {},
): Promise<TradePage> {
  const search = new URLSearchParams()
  if (params.page !== undefined) search.set('page', String(params.page))
  if (params.page_size !== undefined) search.set('page_size', String(params.page_size))
  const qs = search.toString()
  return apiGet<TradePage>(
    `/runs/${encodeURIComponent(runId)}/trades${qs ? `?${qs}` : ''}`,
  )
}

export async function createRun(payload: RunCreate): Promise<RunSummary> {
  return apiPost<RunSummary>('/runs', payload)
}
