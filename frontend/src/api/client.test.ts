import { afterEach, describe, expect, it, vi } from 'vitest'
import { apiGet, ApiClientError } from './client'
import type { RunList } from './types'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('apiGet', () => {
  it('returns parsed JSON on 200', async () => {
    const body: RunList = { total: 0, items: [], page: 1, page_size: 50 }
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(body), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    const result = await apiGet<RunList>('/runs')

    expect(result).toEqual(body)
    expect(fetchMock).toHaveBeenCalledWith('/api/runs', {
      method: 'GET',
      headers: { Accept: 'application/json' },
    })
  })

  it('throws ApiClientError with ApiError envelope on 404', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          error: {
            code: 'NOT_FOUND',
            message: 'run x not found',
            details: null,
          },
        }),
        { status: 404, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    vi.stubGlobal('fetch', fetchMock)

    try {
      await apiGet('/runs/x')
      expect.unreachable('expected ApiClientError')
    } catch (err) {
      expect(err).toBeInstanceOf(ApiClientError)
      expect(err).toMatchObject({
        status: 404,
        code: 'NOT_FOUND',
        message: 'run x not found',
      })
    }
  })

  it('throws ApiClientError with INTERNAL on 500 and non-JSON body', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response('oops', { status: 500 }))
    vi.stubGlobal('fetch', fetchMock)

    try {
      await apiGet('/runs')
      expect.unreachable('expected ApiClientError')
    } catch (err) {
      expect(err).toBeInstanceOf(ApiClientError)
      expect(err).toMatchObject({ status: 500, code: 'INTERNAL' })
    }
  })

  it('throws ApiClientError with INTERNAL when response.json() fails on 500', async () => {
    const response = new Response('', { status: 500 })
    vi.spyOn(response, 'json').mockRejectedValue(new SyntaxError('Unexpected end of JSON input'))
    const fetchMock = vi.fn().mockResolvedValue(response)
    vi.stubGlobal('fetch', fetchMock)

    await expect(apiGet('/runs')).rejects.toMatchObject({
      status: 500,
      code: 'INTERNAL',
      message: 'HTTP 500',
    })
  })
})
