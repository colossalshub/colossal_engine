import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import App from '../../App'
import { renderWithProviders } from '../../test-utils'

function renderAt(path: string) {
  return renderWithProviders(<App />, { route: path })
}

describe('Shell', () => {
  it('renders sidebar nav with both items', () => {
    renderAt('/')
    expect(screen.getByRole('link', { name: 'Command Center' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Data Manager' })).toBeInTheDocument()
  })

  it('renders the logo', () => {
    renderAt('/')
    expect(screen.getByText('colossal')).toBeInTheDocument()
  })

  it('renders topbar breadcrumb matching the route', () => {
    renderAt('/runs/abc')
    expect(screen.getByText('Tear Sheet')).toBeInTheDocument()
  })

  it('marks the active nav item', () => {
    renderAt('/data')
    const dataLink = screen.getByRole('link', { name: 'Data Manager' })
    expect(dataLink.className).toContain('sidebar__item--active')
  })

  it('does not mark Command Center active when on /data', () => {
    renderAt('/data')
    const cmdLink = screen.getByRole('link', { name: 'Command Center' })
    expect(cmdLink.className).not.toContain('sidebar__item--active')
  })

  it('renders the page content inside the shell', () => {
    renderAt('/')
    expect(screen.getByText('Run History')).toBeInTheDocument()
  })

  it('navigates when a nav item is clicked', async () => {
    const user = userEvent.setup()
    renderAt('/')
    await user.click(screen.getByRole('link', { name: 'Data Manager' }))
    expect(screen.getByRole('heading', { name: 'Coverage' })).toBeInTheDocument()
    expect(screen.queryByText('Run History')).not.toBeInTheDocument()
  })
})
