import { afterEach, describe, expect, it, vi } from 'vitest'
import { listRuns } from './runs'
import type { RunList } from './types'

afterEach(() => {
  vi.unstubAllGlobals()
})

const runListBody: RunList = {
  total: 0,
  items: [],
  page: 1,
  page_size: 50,
}

function mockFetchOk() {
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(JSON.stringify(runListBody), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }),
  )
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

describe('listRuns', () => {
  it('calls /api/runs with no query string when params omitted', async () => {
    const fetchMock = mockFetchOk()

    const result = await listRuns()

    expect(fetchMock).toHaveBeenCalledWith('/api/runs', {
      method: 'GET',
      headers: { Accept: 'application/json' },
    })
    expect(result).toEqual(runListBody)
  })

  it('calls /api/runs?strategy=buy_hold when strategy is set', async () => {
    const fetchMock = mockFetchOk()

    await listRuns({ strategy: 'buy_hold' })

    expect(fetchMock).toHaveBeenCalledWith('/api/runs?strategy=buy_hold', {
      method: 'GET',
      headers: { Accept: 'application/json' },
    })
  })

  it('calls /api/runs with page and page_size query params', async () => {
    const fetchMock = mockFetchOk()

    await listRuns({ page: 2, page_size: 10 })

    expect(fetchMock).toHaveBeenCalledWith('/api/runs?page=2&page_size=10', {
      method: 'GET',
      headers: { Accept: 'application/json' },
    })
  })

  it('parses response as RunList', async () => {
    mockFetchOk()

    const result = await listRuns()

    expect(result).toEqual(runListBody)
  })
})
