import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import type { ReactElement } from 'react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import App from './App'

export function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
    },
  })
}

export function renderWithProviders(
  ui: ReactElement,
  options: { route?: string; client?: QueryClient } = {},
) {
  const { route = '/', client = makeQueryClient() } = options
  // <App/> already owns its own top-level <Routes>; wrapping it in another
  // routed <Route> here would shadow its internal route matching. Only
  // standalone page/component renders need the outer match below so that
  // useParams() (e.g. TearSheet's :id) resolves without a full <App/> tree.
  const isFullApp = ui.type === App
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[route]}>
        {isFullApp ? (
          ui
        ) : (
          <Routes>
            <Route path="/runs/:id" element={ui} />
            <Route path="*" element={ui} />
          </Routes>
        )}
      </MemoryRouter>
    </QueryClientProvider>,
  )
}
