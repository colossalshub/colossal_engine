import { fireEvent, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'

import { renderWithProviders } from '../../test-utils'
import { ThemeToggle } from './ThemeToggle'

describe('ThemeToggle', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
  })

  it('renders a button with an accessible label', () => {
    renderWithProviders(<ThemeToggle />)
    expect(screen.getByRole('button', { name: /switch to/i })).toBeInTheDocument()
  })

  it('defaults to light and offers switching to dark', () => {
    renderWithProviders(<ThemeToggle />)
    expect(
      screen.getByRole('button', { name: 'Switch to dark theme' }),
    ).toBeInTheDocument()
    expect(document.documentElement.getAttribute('data-theme')).toBe('light')
  })

  it('toggles to dark on click and persists', () => {
    renderWithProviders(<ThemeToggle />)
    fireEvent.click(screen.getByRole('button', { name: 'Switch to dark theme' }))
    expect(
      screen.getByRole('button', { name: 'Switch to light theme' }),
    ).toBeInTheDocument()
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
    expect(localStorage.getItem('quant-theme')).toBe('dark')
  })

  it('toggles back to light on second click', () => {
    renderWithProviders(<ThemeToggle />)
    fireEvent.click(screen.getByRole('button', { name: 'Switch to dark theme' }))
    fireEvent.click(screen.getByRole('button', { name: 'Switch to light theme' }))
    expect(
      screen.getByRole('button', { name: 'Switch to dark theme' }),
    ).toBeInTheDocument()
    expect(document.documentElement.getAttribute('data-theme')).toBe('light')
    expect(localStorage.getItem('quant-theme')).toBe('light')
  })
})
