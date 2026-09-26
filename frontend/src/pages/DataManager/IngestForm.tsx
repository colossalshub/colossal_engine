import { useMutation } from '@tanstack/react-query'
import type { FormEvent } from 'react'
import { useState } from 'react'

import { ApiClientError } from '../../api/client'
import { postIngest } from '../../api/data'
import type { IngestRequest } from '../../api/types'
import './ingestForm.css'

const TIMEFRAMES = [
  { value: '15m', label: '15m' },
  { value: '1h', label: '1h' },
  { value: '4h', label: '4h' },
  { value: '1d', label: '1d' },
  { value: '1w', label: '1w' },
] as const

function todayISO(): string {
  return new Date().toISOString().slice(0, 10)
}

export function IngestForm() {
  const [venue, setVenue] = useState<string>('binance')
  const [symbol, setSymbol] = useState<string>('BTC/USDT')
  const [timeframe, setTimeframe] = useState<string>('1d')
  const [startDate, setStartDate] = useState<string>('2024-01-01')
  const [endDate, setEndDate] = useState<string>(todayISO())
  const [successCommand, setSuccessCommand] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: (payload: IngestRequest) => postIngest(payload),
    onSuccess: (data) => {
      setSuccessCommand(data.command)
    },
  })

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    mutation.mutate({
      venue,
      symbol,
      timeframe,
      start: startDate,
      end: endDate,
    })
  }

  const serverError =
    mutation.error instanceof ApiClientError
      ? mutation.error.message
      : mutation.isError
        ? String(mutation.error)
        : null

  if (successCommand !== null) {
    return (
      <div className="ingest-form__success">
        Ingestion started. Command: <code>{successCommand}</code>. Re-check
        coverage in a minute.
      </div>
    )
  }

  return (
    <form className="ingest-form" onSubmit={handleSubmit}>
      <div className="ingest-form__grid">
        <label className="ingest-form__field">
          <span className="ingest-form__label">Venue</span>
          <input
            className="ingest-form__input"
            type="text"
            value={venue}
            onChange={(e) => setVenue(e.target.value)}
          />
        </label>

        <label className="ingest-form__field">
          <span className="ingest-form__label">Symbol</span>
          <input
            className="ingest-form__input"
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
          />
        </label>

        <label className="ingest-form__field">
          <span className="ingest-form__label">Timeframe</span>
          <select
            className="ingest-form__input"
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
          >
            {TIMEFRAMES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </label>

        <label className="ingest-form__field">
          <span className="ingest-form__label">Start</span>
          <input
            className="ingest-form__input"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </label>

        <label className="ingest-form__field">
          <span className="ingest-form__label">End</span>
          <input
            className="ingest-form__input"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </label>
      </div>

      {serverError ? (
        <div className="ingest-form__error">{serverError}</div>
      ) : null}

      <div className="ingest-form__actions">
        <button
          type="submit"
          className="ingest-form__submit"
          disabled={mutation.isPending}
        >
          {mutation.isPending ? 'Starting…' : 'Ingest'}
        </button>
      </div>
    </form>
  )
}
