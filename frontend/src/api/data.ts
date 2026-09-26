import { apiGet } from './client'
import type { CoverageResponse } from './types'

export async function getCoverage(): Promise<CoverageResponse> {
  return apiGet<CoverageResponse>('/data/coverage')
}
