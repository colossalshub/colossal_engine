import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { ErrorDisplay } from './ErrorDisplay'

describe('ErrorDisplay', () => {
  it('renders the message', () => {
    render(<ErrorDisplay message="Something failed" />)
    expect(screen.getByText('Something failed')).toBeInTheDocument()
  })

  it('renders a Retry button when onRetry is provided', () => {
    render(<ErrorDisplay message="Failed" onRetry={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument()
  })

  it('calls onRetry when the button is clicked', async () => {
    const onRetry = vi.fn()
    const user = userEvent.setup()
    render(<ErrorDisplay message="Failed" onRetry={onRetry} />)
    await user.click(screen.getByRole('button', { name: 'Retry' }))
    expect(onRetry).toHaveBeenCalledOnce()
  })

  it('omits the Retry button when onRetry is not provided', () => {
    render(<ErrorDisplay message="Failed" />)
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })
})
