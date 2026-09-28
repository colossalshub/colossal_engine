import { describe, expect, it } from 'vitest'

import {
  LAYOUT_STORAGE_KEY,
  WIDGET_IDS,
  applyLayoutChange,
  defaultLayout,
  readLayout,
  toggleWidget,
} from './tearsheetLayout'

describe('tearsheet layout persistence', () => {
  it('uses the storage key from §9.5', () => {
    expect(LAYOUT_STORAGE_KEY).toBe('colossal_quant.tearsheet.layout.v1')
  })

  it('ships every core widget visible in the default grid', () => {
    const layout = defaultLayout()
    for (const id of WIDGET_IDS) {
      expect(layout.widgets[id].visible).toBe(true)
    }
    expect(layout.widgets.price).toMatchObject({ x: 0, w: 12, h: 11 })
    expect(layout.widgets.equity.w).toBe(6)
    expect(layout.widgets.drawdown).toMatchObject({ x: 6, w: 6 })
    expect(layout.widgets.kpis.w).toBe(12)
    expect(layout.widgets.monthly.w).toBe(12)
    expect(layout.widgets.ledger.w).toBe(12)
  })

  it('falls back to the default layout when storage is empty or invalid', () => {
    expect(readLayout(null)).toEqual(defaultLayout())
    expect(readLayout('')).toEqual(defaultLayout())
    expect(readLayout('{')).toEqual(defaultLayout())
    expect(readLayout('[]')).toEqual(defaultLayout())
    expect(readLayout(JSON.stringify({ widgets: { kpis: { visible: true } } }))).toEqual(
      defaultLayout(),
    )
  })

  it('loads a valid config and ignores nothing required', () => {
    const stored = defaultLayout()
    stored.widgets.price.visible = false
    stored.widgets.equity.x = 6
    stored.widgets.equity.w = 6
    const loaded = readLayout(JSON.stringify(stored))
    expect(loaded.widgets.price.visible).toBe(false)
    expect(loaded.widgets.equity).toMatchObject({ x: 6, w: 6, visible: true })
    expect(loaded.widgets.kpis.visible).toBe(true)
  })

  it('toggles visibility without dropping geometry', () => {
    const next = toggleWidget(defaultLayout(), 'ledger')
    expect(next.widgets.ledger.visible).toBe(false)
    expect(next.widgets.ledger).toMatchObject({ x: 0, w: 12, h: 14 })
    expect(next.widgets.kpis.visible).toBe(true)
  })

  it('applies drag positions and keeps hidden widgets', () => {
    const hidden = toggleWidget(defaultLayout(), 'monthly')
    const next = applyLayoutChange(hidden, [
      { i: 'price', x: 0, y: 8, w: 12, h: 12 },
      { i: 'unknown', x: 0, y: 0, w: 1, h: 1 },
    ])
    expect(next.widgets.price).toMatchObject({ x: 0, y: 8, w: 12, h: 12, visible: true })
    expect(next.widgets.monthly.visible).toBe(false)
    expect(applyLayoutChange(next, [{ i: 'price', x: 0, y: 8, w: 12, h: 12 }])).toBe(next)
  })
})
