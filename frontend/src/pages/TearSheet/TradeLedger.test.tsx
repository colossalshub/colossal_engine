import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { Trade, TradePage } from '../../api/types'
import * as runsApi from '../../api/runs'
import { renderWithProviders } from '../../test-utils'
import { formatTradeQty, TradeLedger } from './TradeLedger'

const sampleTrade: Trade = {
  trade_id: 't-1',
  symbol: 'BTC/USDT',
  side: 'long',
  entry_ts: 1704067200000,
  exit_ts: null,
  entry_px: 42000,
  exit_px: null,
  qty: 0.5,
  pnl: -12.34,
  pnl_pct: -0.01,
  fees: 12.34,
  duration_s: 0,
}

const sampleTrade2: Trade = {
  trade_id: 't-2',
  symbol: 'ETH/USDT',
  side: 'short',
  entry_ts: 1704153600000,
  exit_ts: 1704240000000,
  entry_px: 2200,
  exit_px: 2100,
  qty: 1.5,
  pnl: 150,
  pnl_pct: 0.045,
  fees: 5,
  duration_s: 86400,
}

describe('formatTradeQty', () => {
  it('renders zero as 0', () => {
    expect(formatTradeQty(0)).toBe('0')
    expect(formatTradeQty(0.5)).toBe('0.5000')
    expect(formatTradeQty(null)).toBe('—')
  })
})

describe('TradeLedger', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('shows empty state when total is 0', async () => {
    const page: TradePage = { items: [], total: 0, page: 1, page_size: 50 }
    vi.spyOn(runsApi, 'getTrades').mockResolvedValue(page)

    renderWithProviders(<TradeLedger runId="r-1" />)

    await waitFor(() => {
      expect(
        screen.getByText('No trades generated for this period.'),
      ).toBeInTheDocument()
    })
  })

  it('renders rows when data loads', async () => {
    const page: TradePage = {
      items: [sampleTrade, sampleTrade2],
      total: 2,
      page: 1,
      page_size: 50,
    }
    vi.spyOn(runsApi, 'getTrades').mockResolvedValue(page)

    renderWithProviders(<TradeLedger runId="r-1" />)

    await waitFor(() => {
      expect(screen.getByText('t-1')).toBeInTheDocument()
    })
  })

  it('renders the range line', async () => {
    const page: TradePage = {
      items: [sampleTrade],
      total: 142,
      page: 1,
      page_size: 50,
    }
    vi.spyOn(runsApi, 'getTrades').mockResolvedValue(page)

    renderWithProviders(<TradeLedger runId="r-1" />)

    await waitFor(() => {
      expect(screen.getByText('Showing 1–50 of 142')).toBeInTheDocument()
    })
  })

  it('renders the page label', async () => {
    const page: TradePage = {
      items: [sampleTrade],
      total: 142,
      page: 1,
      page_size: 50,
    }
    vi.spyOn(runsApi, 'getTrades').mockResolvedValue(page)

    renderWithProviders(<TradeLedger runId="r-1" />)

    await waitFor(() => {
      expect(screen.getByText('Page 1 of 3')).toBeInTheDocument()
    })
  })

  it('disables the Prev button on page 1', async () => {
    const page: TradePage = {
      items: [sampleTrade],
      total: 142,
      page: 1,
      page_size: 50,
    }
    vi.spyOn(runsApi, 'getTrades').mockResolvedValue(page)

    renderWithProviders(<TradeLedger runId="r-1" />)

    await waitFor(() => {
      expect(screen.getByText('← Prev')).toBeInTheDocument()
    })
    expect(screen.getByText('← Prev')).toBeDisabled()
  })

  it('enables the Next button on page 1', async () => {
    const page: TradePage = {
      items: [sampleTrade],
      total: 142,
      page: 1,
      page_size: 50,
    }
    vi.spyOn(runsApi, 'getTrades').mockResolvedValue(page)

    renderWithProviders(<TradeLedger runId="r-1" />)

    await waitFor(() => {
      expect(screen.getByText('Next →')).toBeInTheDocument()
    })
    expect(screen.getByText('Next →')).not.toBeDisabled()
  })

  it('clicking Next moves to page 2', async () => {
    const user = userEvent.setup()
    const getTrades = vi.spyOn(runsApi, 'getTrades').mockImplementation(
      (_runId: string, params?: { page?: number; page_size?: number }) => {
        const page = params?.page ?? 1
        return Promise.resolve({
          items: [sampleTrade],
          total: 142,
          page,
          page_size: 50,
        })
      },
    )

    renderWithProviders(<TradeLedger runId="r-1" />)

    await waitFor(() => {
      expect(screen.getByText('Page 1 of 3')).toBeInTheDocument()
    })

    await user.click(screen.getByText('Next →'))

    await waitFor(() => {
      expect(screen.getByText('Page 2 of 3')).toBeInTheDocument()
    })

    expect(getTrades).toHaveBeenCalledWith('r-1', { page: 2, page_size: 50 })
  })

  it('clicking Next twice disables Next on the last page', async () => {
    const user = userEvent.setup()
    vi.spyOn(runsApi, 'getTrades').mockImplementation(
      (_runId: string, params?: { page?: number; page_size?: number }) => {
        const page = params?.page ?? 1
        return Promise.resolve({
          items: [sampleTrade],
          total: 142,
          page,
          page_size: 50,
        })
      },
    )

    renderWithProviders(<TradeLedger runId="r-1" />)

    await waitFor(() => {
      expect(screen.getByText('Page 1 of 3')).toBeInTheDocument()
    })

    await user.click(screen.getByText('Next →'))
    await waitFor(() => {
      expect(screen.getByText('Page 2 of 3')).toBeInTheDocument()
    })

    await user.click(screen.getByText('Next →'))
    await waitFor(() => {
      expect(screen.getByText('Page 3 of 3')).toBeInTheDocument()
    })

    expect(screen.getByText('Next →')).toBeDisabled()
  })

  it('shows the loading state', () => {
    vi.spyOn(runsApi, 'getTrades').mockReturnValue(new Promise(() => {}))

    renderWithProviders(<TradeLedger runId="r-1" />)

    expect(screen.getByText('Loading trades…')).toBeInTheDocument()
  })

  it('shows the error state', async () => {
    vi.spyOn(runsApi, 'getTrades').mockRejectedValue(new Error('boom'))

    renderWithProviders(<TradeLedger runId="r-1" />)

    await waitFor(() => {
      expect(screen.getByText(/Failed to load trades/)).toBeInTheDocument()
    })
  })
})
