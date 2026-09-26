import {
  AreaSeries,
  type AreaData,
  type IChartApi,
  type ISeriesApi,
  type MouseEventParams,
  type SeriesType,
  type Time,
  type UTCTimestamp,
} from 'lightweight-charts'
import { useCallback } from 'react'

import type { DrawdownPoint } from '../../api/types'
import { BaseChart, type TooltipPayload } from '../../components/charts/BaseChart'

interface DrawdownChartProps {
  data: DrawdownPoint[]
  height?: number
}

function toTime(tsMs: number): UTCTimestamp {
  return (tsMs / 1000) as UTCTimestamp
}

function fmtPct(v: number): string {
  return `${(v * 100).toFixed(2)}%`
}

export function DrawdownChart({ data, height = 280 }: DrawdownChartProps) {
  const createSeries = useCallback(
    (chart: IChartApi) => {
      const series = chart.addSeries(AreaSeries, {
        lineColor: '#ef4444',
        lineWidth: 1,
        topColor: 'rgba(239, 68, 68, 0.20)',
        bottomColor: 'rgba(239, 68, 68, 0.02)',
        priceLineVisible: false,
        lastValueVisible: false,
        invertFilledArea: false,
      })
      series.setData(
        data.map(
          (p): AreaData<Time> => ({
            time: toTime(p.ts),
            value: p.dd,
          }),
        ),
      )
      return series
    },
    [data],
  )

  const buildTooltip = useCallback(
    (
      params: MouseEventParams,
      series: ISeriesApi<SeriesType>[],
    ): TooltipPayload | null => {
      if (!params.time || params.seriesData.size === 0) return null
      const ddData = params.seriesData.get(series[0])
      if (!ddData || !('value' in ddData)) return null
      const dd = (ddData as AreaData<Time>).value
      return {
        time: params.time,
        rows: [{ label: 'Drawdown', value: fmtPct(dd) }],
      }
    },
    [],
  )

  if (data.length === 0) {
    return <div className="drawdown-chart__empty">No drawdown data for this run.</div>
  }

  return (
    <BaseChart
      height={height}
      createSeries={createSeries}
      buildTooltip={buildTooltip}
    />
  )
}
