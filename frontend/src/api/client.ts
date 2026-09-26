/**
 * Minimal fetch wrapper for `/api/*` routes (Vite dev proxy → backend; see PROJECT.md §5).
 *
 * - `apiGet` is the only function for now. `apiPost` etc. come when needed (§5: no premature abstraction).
 * - Non-2xx responses throw `ApiClientError` with `code`, `message`, `status`, `details` extracted from the §4.4 `ApiError` envelope.
 * - Malformed error bodies fall back to `code="INTERNAL"` and a plain `HTTP <status>` message — never throws a parsing error on top of the HTTP error.
 * - The path argument is appended to `/api` — callers pass `/runs`, not `/api/runs`.
 */

import type { ApiError } from './types'

const API_BASE = '/api'

export class ApiClientError extends Error {
  readonly status: number
  readonly code: string
  readonly details: unknown

  constructor(status: number, code: string, message: string, details: unknown = null) {
    super(message)
    this.name = 'ApiClientError'
    this.status = status
    this.code = code
    this.details = details
  }
}

async function parseError(response: Response): Promise<ApiClientError> {
  let body: unknown = null
  try {
    body = await response.json()
  } catch {
    return new ApiClientError(
      response.status,
      'INTERNAL',
      `HTTP ${response.status}`,
    )
  }
  if (
    typeof body === 'object' &&
    body !== null &&
    'error' in body &&
    typeof (body as { error: unknown }).error === 'object' &&
    (body as { error: unknown }).error !== null
  ) {
    const err = (body as { error: ApiError['error'] }).error
    return new ApiClientError(
      response.status,
      err.code,
      err.message,
      err.details ?? null,
    )
  }
  return new ApiClientError(
    response.status,
    'INTERNAL',
    `HTTP ${response.status}`,
  )
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
  })
  if (!response.ok) {
    throw await parseError(response)
  }
  return (await response.json()) as T
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    throw await parseError(response)
  }
  return (await response.json()) as T
}
