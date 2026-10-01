import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { FormEvent, KeyboardEvent } from 'react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { ApiClientError } from '../../api/client'
import { createRun } from '../../api/runs'
import type { ResearchStage, RunCreate } from '../../api/types'
import './strategyForm.css'

const STRATEGIES = [
  { value: 'buy_hold', label: 'Buy & Hold' },
  { value: 'ema_cross', label: 'EMA 9/21' },
] as const

const TIMEFRAMES = [
  { value: '15m', label: '15m' },
  { value: '1h', label: '1h' },
  { value: '4h', label: '4h' },
  { value: '1d', label: '1d' },
  { value: '1w', label: '1w' },
] as const

const RESEARCH_STRINGS = [
  ['experiment_id', 'Experiment ID'],
  ['hypothesis_id', 'Hypothesis ID'],
  ['strategy_version', 'Strategy version'],
] as const

const RESEARCH_DATES = [
  ['in_sample_start_ts', 'In-sample start (UTC)'],
  ['in_sample_end_ts', 'In-sample end (UTC)'],
  ['validation_start_ts', 'Validation start (UTC)'],
  ['validation_end_ts', 'Validation end (UTC)'],
  ['oos_start_ts', 'OOS start (UTC)'],
  ['oos_end_ts', 'OOS end (UTC)'],
] as const

const RESEARCH_TRIALS = [
  ['trial_index', 'Trial index'],
  ['trial_count', 'Trial count'],
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
  const [feePercent, setFeePercent] = useState<string>('0.1')
  const [deployPercent, setDeployPercent] = useState<string>('100')
  const [benchmark, setBenchmark] = useState<string>('')
  const [name, setName] = useState<string>('')
  const [research, setResearch] = useState<Record<string, string>>({})
  const [researchStage, setResearchStage] = useState<ResearchStage | ''>('')
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

    const parsedFee = parseFloat(feePercent)
    const feeDecimal = Number.isFinite(parsedFee)
      ? (parsedFee / 100).toString()
      : '0.001'
    const parsedDeploy = parseFloat(deployPercent)
    const deployPct = Number.isFinite(parsedDeploy)
      ? (parsedDeploy / 100).toString()
      : '1.0'
    const payload: RunCreate = {
      strategy,
      params: {
        trade_size: '1', // kept for backwards compat
        deploy_pct: deployPct,
        timeframe,
        venue: 'binance',
        maker_fee: feeDecimal,
        taker_fee: feeDecimal,
        benchmark_symbol: benchmark.trim(),
      },
      universe,
      start_ts,
      end_ts,
    }
    if (name.trim()) {
      payload.name = name.trim()
    }
    for (const [key] of RESEARCH_STRINGS) {
      const value = research[key]?.trim()
      if (value) payload[key] = value
    }
    if (researchStage) payload.research_stage = researchStage
    for (const [key, label] of RESEARCH_DATES) {
      const value = research[key]?.trim()
      if (!value) continue
      const timestamp = Date.parse(`${value}T00:00:00.000Z`)
      if (
        !/^\d{4}-\d{2}-\d{2}$/.test(value) ||
        !Number.isFinite(timestamp) ||
        new Date(timestamp).toISOString().slice(0, 10) !== value
      ) {
        setFormError(`${label}: invalid date. Use YYYY-MM-DD.`)
        return
      }
      payload[key] = timestamp
    }
    for (const [key, label] of RESEARCH_TRIALS) {
      const value = research[key]?.trim()
      if (!value) continue
      const trial = Number(value)
      if (!/^[+-]?\d+$/.test(value) || !Number.isSafeInteger(trial)) {
        setFormError(`${label} must be a complete safe integer.`)
        return
      }
      payload[key] = trial
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
          <span className="strategy-form__label">% Deployed</span>
          <input
            className="strategy-form__input"
            type="number"
            step="1"
            min="0"
            max="100"
            value={deployPercent}
            onChange={(e) => setDeployPercent(e.target.value)}
          />
        </label>
      </div>

      <div className="strategy-form__row strategy-form__row--4col">
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

        <label className="strategy-form__field">
          <span className="strategy-form__label">Fee % (each side)</span>
          <input
            className="strategy-form__input"
            type="number"
            step="0.01"
            min="0"
            value={feePercent}
            onChange={(e) => setFeePercent(e.target.value)}
          />
        </label>

        <label className="strategy-form__field">
          <span className="strategy-form__label">Benchmark (optional)</span>
          <input
            className="strategy-form__input"
            type="text"
            value={benchmark}
            onChange={(e) => setBenchmark(e.target.value)}
            placeholder="e.g. BTC/USDT"
          />
        </label>
      </div>

      <section aria-label="Research metadata (optional)">
        <h3>Research metadata (optional)</h3>
        <div className="strategy-form__row strategy-form__row--4col">
          {RESEARCH_STRINGS.map(([key, label]) => (
            <label key={key} className="strategy-form__field">
              <span className="strategy-form__label">{label}</span>
              <input
                className="strategy-form__input"
                type="text"
                value={research[key] ?? ''}
                onChange={(e) => setResearch({ ...research, [key]: e.target.value })}
              />
            </label>
          ))}
          <label className="strategy-form__field">
            <span className="strategy-form__label">Research stage</span>
            <select
              className="strategy-form__input"
              value={researchStage}
              onChange={(e) => setResearchStage(e.target.value as ResearchStage | '')}
            >
              <option value="">Unset</option>
              <option value="exploration">Exploration</option>
              <option value="validation">Validation</option>
              <option value="oos">OOS</option>
            </select>
          </label>
        </div>
        <div className="strategy-form__row strategy-form__row--3col">
          {RESEARCH_DATES.map(([key, label]) => (
            <label key={key} className="strategy-form__field">
              <span className="strategy-form__label">{label}</span>
              <input
                className="strategy-form__input"
                type="text"
                placeholder="YYYY-MM-DD"
                value={research[key] ?? ''}
                onChange={(e) => setResearch({ ...research, [key]: e.target.value })}
              />
            </label>
          ))}
        </div>
        <div className="strategy-form__row">
          {RESEARCH_TRIALS.map(([key, label]) => (
            <label key={key} className="strategy-form__field">
              <span className="strategy-form__label">{label}</span>
              <input
                className="strategy-form__input"
                type="text"
                inputMode="numeric"
                value={research[key] ?? ''}
                onChange={(e) => setResearch({ ...research, [key]: e.target.value })}
              />
            </label>
          ))}
        </div>
      </section>

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
