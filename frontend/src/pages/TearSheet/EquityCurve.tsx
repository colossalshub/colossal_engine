import {
  LineSeries,
  type IChartApi,
  type ISeriesApi,
  type LineData,
  type MouseEventParams,
  type SeriesType,
  type Time,
  type UTCTimestamp,
} from 'lightweight-charts'
import { useCallback } from 'react'

import type { EquityPoint } from '../../api/types'
import { BaseChart, type TooltipPayload } from '../../components/charts/BaseChart'

interface EquityCurveProps {
  data: EquityPoint[]
  height?: number
}

function toTime(tsMs: number): UTCTimestamp {
  return (tsMs / 1000) as UTCTimestamp
}

function fmt(value: number): string {
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

export function EquityCurve({ data, height = 280 }: EquityCurveProps) {
  const hasBenchmark = data.some((p) => p.benchmark !== null)

  const createSeries = useCallback(
    (chart: IChartApi): ISeriesApi<SeriesType>[] => {
      const equitySeries = chart.addSeries(LineSeries, {
        color: '#3b82f6',
        lineWidth: 2,
        priceLineVisible: false,
        lastValueVisible: true,
      })
      equitySeries.setData(
        data.map(
          (p): LineData<Time> => ({
            time: toTime(p.ts),
            value: p.equity,
          }),
        ),
      )

      const series: ISeriesApi<SeriesType>[] = [equitySeries]

      if (hasBenchmark) {
        const benchmarkSeries = chart.addSeries(LineSeries, {
          color: '#6b7280',
          lineWidth: 1,
          priceLineVisible: false,
          lastValueVisible: false,
        })
        benchmarkSeries.setData(
          data
            .filter((p): p is EquityPoint & { benchmark: number } => p.benchmark !== null)
            .map(
              (p): LineData<Time> => ({
                time: toTime(p.ts),
                value: p.benchmark,
              }),
            ),
        )
        series.push(benchmarkSeries)
      }

      return series
    },
    [data, hasBenchmark],
  )

  const buildTooltip = useCallback(
    (
      params: MouseEventParams,
      series: ISeriesApi<SeriesType>[],
    ): TooltipPayload | null => {
      if (!params.time || params.seriesData.size === 0) return null
      const eqData = params.seriesData.get(series[0])
      if (!eqData || !('value' in eqData)) return null
      const eqValue = (eqData as LineData<Time>).value

      const rows = [{ label: 'Equity', value: fmt(eqValue) }]

      if (series.length > 1) {
        const benchData = params.seriesData.get(series[1])
        if (benchData && 'value' in benchData) {
          rows.push({
            label: 'Benchmark',
            value: fmt((benchData as LineData<Time>).value),
          })
        }
      }

      return { time: params.time, rows }
    },
    [],
  )

  if (data.length === 0) {
    return <div className="equity-curve__empty">No equity data for this run.</div>
  }

  return (
    <BaseChart
      height={height}
      createSeries={createSeries}
      buildTooltip={buildTooltip}
    />
  )
}
