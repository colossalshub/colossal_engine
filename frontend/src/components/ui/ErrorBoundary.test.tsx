import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ErrorBoundary } from './ErrorBoundary'

function Bomb(): never {
  throw new Error('boom')
}

describe('ErrorBoundary', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <span>child content</span>
      </ErrorBoundary>,
    )
    expect(screen.getByText('child content')).toBeInTheDocument()
  })

  it('renders fallback when a child throws during render', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})

    render(
      <ErrorBoundary>
        <Bomb />
      </ErrorBoundary>,
    )

    expect(
      screen.getByText('Something went wrong rendering this page.'),
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Reload' })).toBeInTheDocument()
  })

  it('uses custom fallbackMessage when provided', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})

    render(
      <ErrorBoundary fallbackMessage="Custom failure message">
        <Bomb />
      </ErrorBoundary>,
    )

    expect(screen.getByText('Custom failure message')).toBeInTheDocument()
  })
})
