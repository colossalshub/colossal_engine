import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import App from './App'

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  )
}

describe('App routing', () => {
  it('renders Command Center at /', () => {
    renderAt('/')
    expect(screen.getByText('Command Center placeholder')).toBeInTheDocument()
  })

  it('renders Tear Sheet at /runs/:id', () => {
    renderAt('/runs/abc-123')
    expect(screen.getByText('Tear Sheet placeholder')).toBeInTheDocument()
  })

  it('renders Data Manager at /data', () => {
    renderAt('/data')
    expect(screen.getByText('Data Manager placeholder')).toBeInTheDocument()
  })

  it('renders nothing for an unknown route', () => {
    renderAt('/nope')
    expect(screen.queryByText('Command Center placeholder')).not.toBeInTheDocument()
    expect(screen.queryByText('Tear Sheet placeholder')).not.toBeInTheDocument()
    expect(screen.queryByText('Data Manager placeholder')).not.toBeInTheDocument()
  })
})
