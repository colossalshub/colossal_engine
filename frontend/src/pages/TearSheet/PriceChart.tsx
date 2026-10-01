import {
  CandlestickSeries,
  createSeriesMarkers,
  type CandlestickData,
  type IChartApi,
  type ISeriesApi,
  type MouseEventParams,
  type SeriesMarker,
  type SeriesType,
  type Time,
  type UTCTimestamp,
} from 'lightweight-charts'
import { useCallback } from 'react'

import type { OHLCV, TradeMarker } from '../../api/types'
import { BaseChart, type TooltipPayload } from '../../components/charts/BaseChart'

interface PriceChartProps {
  data: OHLCV[]
  markers?: TradeMarker[]
  height?: number
}

function toTime(tsMs: number): UTCTimestamp {
  return (tsMs / 1000) as UTCTimestamp
}

function toSeriesMarkers(markers: TradeMarker[]): SeriesMarker<Time>[] {
  return markers.map((m) => ({
    time: toTime(m.ts),
    position: m.side === 'buy' ? 'belowBar' : 'aboveBar',
    color: m.side === 'buy' ? '#22c55e' : '#ef4444',
    shape: m.side === 'buy' ? 'arrowUp' : 'arrowDown',
    text: m.side === 'buy' ? 'B' : 'S',
  }))
}

export function PriceChart({ data, markers = [], height = 420 }: PriceChartProps) {
  const createSeries = useCallback(
    (chart: IChartApi) => {
      const series = chart.addSeries(CandlestickSeries, {
        upColor: '#22c55e',
        downColor: '#ef4444',
        wickUpColor: '#22c55e',
        wickDownColor: '#ef4444',
        borderVisible: false,
      })
      series.setData(
        data.map(
          (bar): CandlestickData<Time> => ({
            time: toTime(bar.ts),
            open: bar.open,
            high: bar.high,
            low: bar.low,
            close: bar.close,
          }),
        ),
      )
      // NOTE: LWC v5 moved series markers to a plugin API. `ISeriesApi` no
      // longer has `setMarkers` — see docs/ai/guides/frontend-tooling.md.
      if (markers.length > 0) {
        void createSeriesMarkers(series, toSeriesMarkers(markers))
      }
      return series
    },
    [data, markers],
  )

  const buildTooltip = useCallback(
    (
      params: MouseEventParams,
      series: ISeriesApi<SeriesType>[],
    ): TooltipPayload | null => {
      if (!params.time || params.seriesData.size === 0) return null
      const seriesData = params.seriesData.get(series[0])
      if (!seriesData || !('open' in seriesData)) return null
      const bar = seriesData as CandlestickData<Time>
      return {
        time: params.time,
        rows: [
          { label: 'O', value: bar.open.toFixed(2) },
          { label: 'H', value: bar.high.toFixed(2) },
          { label: 'L', value: bar.low.toFixed(2) },
          { label: 'C', value: bar.close.toFixed(2) },
        ],
      }
    },
    [],
  )

  if (data.length === 0) {
    return <div className="price-chart__empty">No price data for this run.</div>
  }

  return (
    <BaseChart
      height={height}
      createSeries={createSeries}
      buildTooltip={buildTooltip}
    />
  )
}
