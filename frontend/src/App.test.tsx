import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import App from './App'
import { renderWithProviders } from './test-utils'

function renderAt(path: string) {
  return renderWithProviders(<App />, { route: path })
}

describe('App routing', () => {
  it('renders Command Center at /', () => {
    renderAt('/')
    expect(screen.getByText('Run History')).toBeInTheDocument()
  })

  it('renders Tear Sheet at /runs/:id', () => {
    renderAt('/runs/abc-123')
    expect(screen.getByText('Loading tear sheet…')).toBeInTheDocument()
  })

  it('renders Data Manager at /data', () => {
    renderAt('/data')
    expect(screen.getByRole('heading', { name: 'Coverage' })).toBeInTheDocument()
  })

  it('renders nothing for an unknown route', () => {
    renderAt('/nope')
    expect(screen.queryByText('Run History')).not.toBeInTheDocument()
    expect(screen.queryByText('Loading tear sheet…')).not.toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Coverage' })).not.toBeInTheDocument()
  })
})
