import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { act, renderHook, waitFor } from '@testing-library/react'
import { applyTheme, getStoredTheme, useTheme } from './theme'

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

  it('useTheme returns light when attribute is missing', () => {
    const { result } = renderHook(() => useTheme())
    expect(result.current).toBe('light')
  })

  it('useTheme returns light when attribute is light', () => {
    document.documentElement.setAttribute('data-theme', 'light')
    const { result } = renderHook(() => useTheme())
    expect(result.current).toBe('light')
  })

  it('useTheme returns dark when attribute is dark', () => {
    document.documentElement.setAttribute('data-theme', 'dark')
    const { result } = renderHook(() => useTheme())
    expect(result.current).toBe('dark')
  })

  it('useTheme updates when the attribute changes', async () => {
    const { result } = renderHook(() => useTheme())
    expect(result.current).toBe('light')
    await act(async () => {
      document.documentElement.setAttribute('data-theme', 'dark')
    })
    await waitFor(() => expect(result.current).toBe('dark'))
    await act(async () => {
      document.documentElement.setAttribute('data-theme', 'light')
    })
    await waitFor(() => expect(result.current).toBe('light'))
  })

  it('applyTheme swallows localStorage write errors', () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('quota')
    })
    expect(() => applyTheme('dark')).not.toThrow()
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })
})
