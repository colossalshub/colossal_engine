import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { applyTheme, getStoredTheme } from './theme'

describe('theme', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('getStoredTheme returns light when storage is empty', () => {
    expect(getStoredTheme()).toBe('light')
  })

  it('getStoredTheme returns dark when storage has dark', () => {
    localStorage.setItem('quant-theme', 'dark')
    expect(getStoredTheme()).toBe('dark')
  })

  it('getStoredTheme returns light for garbage values', () => {
    localStorage.setItem('quant-theme', 'blue')
    expect(getStoredTheme()).toBe('light')
  })

  it('applyTheme(dark) sets attribute and persists', () => {
    applyTheme('dark')
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
    expect(localStorage.getItem('quant-theme')).toBe('dark')
  })

  it('applyTheme(light) sets attribute and persists', () => {
    applyTheme('light')
    expect(document.documentElement.getAttribute('data-theme')).toBe('light')
    expect(localStorage.getItem('quant-theme')).toBe('light')
  })

  it('applyTheme swallows localStorage write errors', () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('quota')
    })
    expect(() => applyTheme('dark')).not.toThrow()
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })
})
