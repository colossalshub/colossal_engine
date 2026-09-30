import { beforeEach, describe, expect, it } from 'vitest'

import { chartOptionsFor, readTheme } from './chartOptions'

describe('chartOptions', () => {
  beforeEach(() => {
    document.documentElement.removeAttribute('data-theme')
  })

  it('readTheme returns light when no attribute is set', () => {
    expect(readTheme()).toBe('light')
  })

  it('readTheme returns dark when data-theme is dark', () => {
    document.documentElement.setAttribute('data-theme', 'dark')
    expect(readTheme()).toBe('dark')
  })

  it('chartOptionsFor(dark) uses the dark background', () => {
    expect(chartOptionsFor('dark').layout?.background).toEqual({ color: '#131722' })
  })

  it('chartOptionsFor(light) uses the light background', () => {
    expect(chartOptionsFor('light').layout?.background).toEqual({ color: '#ffffff' })
  })
})
