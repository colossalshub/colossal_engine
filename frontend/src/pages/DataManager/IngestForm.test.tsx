import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiClientError } from '../../api/client'
import * as dataApi from '../../api/data'
import { renderWithProviders } from '../../test-utils'
import { IngestForm } from './IngestForm'

describe('IngestForm', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders the form with default values', () => {
    renderWithProviders(<IngestForm />)

    expect(screen.getByDisplayValue('binance')).toBeInTheDocument()
    expect(screen.getByDisplayValue('BTC/USDT')).toBeInTheDocument()
    expect(screen.getByDisplayValue('1d')).toBeInTheDocument()
    expect(screen.getByDisplayValue('2024-01-01')).toBeInTheDocument()
  })

  it('clicking submit calls postIngest with the form values', async () => {
    const user = userEvent.setup()
    const postIngestSpy = vi.spyOn(dataApi, 'postIngest').mockResolvedValue({
      status: 'started',
      command: 'python scripts/ingest_bars.py',
    })
    renderWithProviders(<IngestForm />)

    await user.click(screen.getByRole('button', { name: 'Ingest' }))

    await waitFor(() => {
      expect(postIngestSpy).toHaveBeenCalledWith({
        venue: 'binance',
        symbol: 'BTC/USDT',
        timeframe: '1d',
        start: '2024-01-01',
        end: expect.any(String),
      })
    })
  })

  it('success path shows the ingestion started message and the command', async () => {
    const user = userEvent.setup()
    vi.spyOn(dataApi, 'postIngest').mockResolvedValue({
      status: 'started',
      command: 'python scripts/ingest_bars.py --venue binance',
    })
    renderWithProviders(<IngestForm />)

    await user.click(screen.getByRole('button', { name: 'Ingest' }))

    await waitFor(() => {
      expect(screen.getByText(/Ingestion started/)).toBeInTheDocument()
      expect(
        screen.getByText('python scripts/ingest_bars.py --venue binance'),
      ).toBeInTheDocument()
    })
  })

  it('error path shows the error message', async () => {
    const user = userEvent.setup()
    vi.spyOn(dataApi, 'postIngest').mockRejectedValue(
      new ApiClientError(422, 'VALIDATION', 'invalid timeframe: banana'),
    )
    renderWithProviders(<IngestForm />)

    await user.click(screen.getByRole('button', { name: 'Ingest' }))

    await waitFor(() => {
      expect(
        document.querySelector('.ingest-form__error')?.textContent,
      ).toBe('invalid timeframe: banana')
    })
  })
})
