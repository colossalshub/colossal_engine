import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { EmptyState } from './EmptyState'

describe('EmptyState', () => {
  it('renders the message', () => {
    render(<EmptyState message="No data" />)
    expect(screen.getByText('No data')).toBeInTheDocument()
  })

  it('renders the icon when provided', () => {
    const { container } = render(<EmptyState icon="⚠" message="Warning" />)
    const iconEl = container.querySelector('.empty-state__icon')
    expect(iconEl).toBeInTheDocument()
    expect(iconEl).toHaveTextContent('⚠')
  })

  it('does not render an icon element when icon is omitted', () => {
    const { container } = render(<EmptyState message="No data" />)
    expect(container.querySelector('.empty-state__icon')).not.toBeInTheDocument()
  })

  it('renders an action button when provided', () => {
    render(
      <EmptyState
        message="Failed"
        action={{ label: 'Retry', onClick: vi.fn() }}
      />,
    )
    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument()
  })

  it('clicking the action calls onClick', async () => {
    const onClick = vi.fn()
    const user = userEvent.setup()
    render(
      <EmptyState
        message="Failed"
        action={{ label: 'Retry', onClick }}
      />,
    )
    await user.click(screen.getByRole('button', { name: 'Retry' }))
    expect(onClick).toHaveBeenCalledOnce()
  })

  it('does not render an action when omitted', () => {
    render(<EmptyState message="No data" />)
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })
})
