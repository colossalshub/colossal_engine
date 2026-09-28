export const LAYOUT_STORAGE_KEY = 'colossal_quant.tearsheet.layout.v1'

export const LAYOUT_SAVE_MS = 300

export const WIDGET_IDS = ['kpis', 'price', 'equity', 'drawdown', 'monthly', 'ledger'] as const

export type WidgetId = (typeof WIDGET_IDS)[number]

export interface WidgetGeom {
  visible: boolean
  x: number
  y: number
  w: number
  h: number
}

export interface TearSheetLayoutConfig {
  widgets: Record<WidgetId, WidgetGeom>
}

export interface LayoutPatch {
  i: string
  x: number
  y: number
  w: number
  h: number
}

/** §9.5 default: 12 columns, row height 40px. Heights cover chart defaults in §9.7. */
export function defaultLayout(): TearSheetLayoutConfig {
  return {
    widgets: {
      kpis: { visible: true, x: 0, y: 0, w: 12, h: 7 },
      price: { visible: true, x: 0, y: 7, w: 12, h: 11 },
      equity: { visible: true, x: 0, y: 18, w: 6, h: 8 },
      drawdown: { visible: true, x: 6, y: 18, w: 6, h: 8 },
      monthly: { visible: true, x: 0, y: 26, w: 12, h: 6 },
      ledger: { visible: true, x: 0, y: 32, w: 12, h: 14 },
    },
  }
}

export function isWidgetId(id: string): id is WidgetId {
  return (WIDGET_IDS as readonly string[]).includes(id)
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function isWidgetGeom(value: unknown): value is WidgetGeom {
  if (!isRecord(value)) return false
  const { visible, x, y, w, h } = value
  return (
    typeof visible === 'boolean' &&
    isGridInt(x) &&
    isGridInt(y) &&
    isGridInt(w) &&
    isGridInt(h) &&
    x >= 0 &&
    x <= 11 &&
    y >= 0 &&
    w >= 1 &&
    w <= 12 &&
    h >= 1 &&
    x + w <= 12
  )
}

function isGridInt(value: unknown): value is number {
  return typeof value === 'number' && Number.isInteger(value)
}

/** Missing or invalid JSON falls back to the §9.5 default grid. */
export function readLayout(raw: string | null): TearSheetLayoutConfig {
  if (raw == null || raw.trim() === '') return defaultLayout()
  try {
    const parsed: unknown = JSON.parse(raw)
    if (!isRecord(parsed) || !isRecord(parsed.widgets)) return defaultLayout()
    const widgets = {} as TearSheetLayoutConfig['widgets']
    for (const id of WIDGET_IDS) {
      const geom = parsed.widgets[id]
      if (!isWidgetGeom(geom)) return defaultLayout()
      widgets[id] = {
        visible: geom.visible,
        x: geom.x,
        y: geom.y,
        w: geom.w,
        h: geom.h,
      }
    }
    return { widgets }
  } catch {
    return defaultLayout()
  }
}

export function toggleWidget(config: TearSheetLayoutConfig, id: WidgetId): TearSheetLayoutConfig {
  const current = config.widgets[id]
  return {
    widgets: {
      ...config.widgets,
      [id]: { ...current, visible: !current.visible },
    },
  }
}

export function applyLayoutChange(
  config: TearSheetLayoutConfig,
  layout: readonly LayoutPatch[],
): TearSheetLayoutConfig {
  let changed = false
  const widgets = { ...config.widgets }
  for (const item of layout) {
    if (!isWidgetId(item.i)) continue
    const current = widgets[item.i]
    if (
      current.x === item.x &&
      current.y === item.y &&
      current.w === item.w &&
      current.h === item.h
    ) {
      continue
    }
    widgets[item.i] = {
      ...current,
      x: item.x,
      y: item.y,
      w: item.w,
      h: item.h,
    }
    changed = true
  }
  return changed ? { widgets } : config
}
