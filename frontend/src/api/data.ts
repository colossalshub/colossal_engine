import { apiGet, apiPost } from './client'
import type { CoverageResponse, IngestRequest, IngestResponse } from './types'

export async function getCoverage(): Promise<CoverageResponse> {
  return apiGet<CoverageResponse>('/data/coverage')
}

export async function postIngest(payload: IngestRequest): Promise<IngestResponse> {
  return apiPost<IngestResponse>('/data/ingest', payload)
}
