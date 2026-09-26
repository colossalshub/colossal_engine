import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { FormEvent, KeyboardEvent } from 'react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { ApiClientError } from '../../api/client'
import { createRun } from '../../api/runs'
import type { RunCreate } from '../../api/types'
import './strategyForm.css'

const STRATEGIES = [{ value: 'buy_hold', label: 'Buy & Hold' }] as const

const TIMEFRAMES = [
  { value: '15m', label: '15m' },
  { value: '1h', label: '1h' },
  { value: '4h', label: '4h' },
  { value: '1d', label: '1d' },
  { value: '1w', label: '1w' },
] as const

function dateStrToEpochMs(dateStr: string): number {
  // dateStr is "YYYY-MM-DD" from <input type="date">. Interpret as UTC midnight.
  const [y, m, d] = dateStr.split('-').map((s) => Number(s))
  return Date.UTC(y, m - 1, d)
}

function todayISO(): string {
  return new Date().toISOString().slice(0, 10)
}

export function StrategyForm() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [strategy, setStrategy] = useState<string>('buy_hold')
  const [timeframe, setTimeframe] = useState<string>('1d')
  const [universe, setUniverse] = useState<string[]>(['BTC/USDT'])
  const [symbolInput, setSymbolInput] = useState<string>('')
  const [startDate, setStartDate] = useState<string>('2024-01-01')
  const [endDate, setEndDate] = useState<string>(todayISO())
  const [name, setName] = useState<string>('')
  const [formError, setFormError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: (payload: RunCreate) => createRun(payload),
    onSuccess: (run) => {
      void queryClient.invalidateQueries({ queryKey: ['runs'] })
      navigate(`/runs/${run.run_id}`)
    },
  })

  function addSymbol() {
    const s = symbolInput.trim().toUpperCase()
    if (!s) return
    if (universe.includes(s)) {
      setSymbolInput('')
      return
    }
    setUniverse([...universe, s])
    setSymbolInput('')
  }

  function removeSymbol(s: string) {
    setUniverse(universe.filter((x) => x !== s))
  }

  function handleSymbolKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') {
      e.preventDefault()
      addSymbol()
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setFormError(null)

    if (universe.length === 0) {
      setFormError('Add at least one symbol.')
      return
    }
    const start_ts = dateStrToEpochMs(startDate)
    const end_ts = dateStrToEpochMs(endDate)
    if (!Number.isFinite(start_ts) || !Number.isFinite(end_ts)) {
      setFormError('Invalid date.')
      return
    }
    if (start_ts >= end_ts) {
      setFormError('Start date must be before end date.')
      return
    }

    const payload: RunCreate = {
      strategy,
      params: { trade_size: '1', timeframe },
      universe,
      start_ts,
      end_ts,
    }
    if (name.trim()) {
      payload.name = name.trim()
    }
    mutation.mutate(payload)
  }

  const serverError =
    mutation.error instanceof ApiClientError
      ? mutation.error.message
      : mutation.isError
        ? String(mutation.error)
        : null

  return (
    <form className="strategy-form" onSubmit={handleSubmit}>
      <div className="strategy-form__row strategy-form__row--3col">
        <label className="strategy-form__field">
          <span className="strategy-form__label">Strategy</span>
          <select
            className="strategy-form__input"
            value={strategy}
            onChange={(e) => setStrategy(e.target.value)}
          >
            {STRATEGIES.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </label>

        <label className="strategy-form__field">
          <span className="strategy-form__label">Timeframe</span>
          <select
            className="strategy-form__input"
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

        <label className="strategy-form__field">
          <span className="strategy-form__label">Name (optional)</span>
          <input
            className="strategy-form__input"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="auto-generated if blank"
          />
        </label>
      </div>

      <div className="strategy-form__field">
        <span className="strategy-form__label">Universe</span>
        <div className="strategy-form__chips">
          {universe.map((s) => (
            <span key={s} className="strategy-form__chip">
              {s}
              <button
                type="button"
                className="strategy-form__chip-remove"
                onClick={() => removeSymbol(s)}
                aria-label={`Remove ${s}`}
              >
                ×
              </button>
            </span>
          ))}
          <input
            className="strategy-form__chip-input"
            type="text"
            value={symbolInput}
            onChange={(e) => setSymbolInput(e.target.value)}
            onKeyDown={handleSymbolKeyDown}
            placeholder="BTC/USDT then Enter"
          />
        </div>
      </div>

      <div className="strategy-form__row">
        <label className="strategy-form__field">
          <span className="strategy-form__label">Start</span>
          <input
            className="strategy-form__input"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </label>

        <label className="strategy-form__field">
          <span className="strategy-form__label">End</span>
          <input
            className="strategy-form__input"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </label>
      </div>

      {formError || serverError ? (
        <div className="strategy-form__error">{formError ?? serverError}</div>
      ) : null}

      <div className="strategy-form__actions">
        <button
          type="submit"
          className="strategy-form__submit"
          disabled={mutation.isPending}
        >
          {mutation.isPending ? 'Running…' : '▶ Run'}
        </button>
      </div>
    </form>
  )
}
