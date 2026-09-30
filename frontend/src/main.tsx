import { provideGlobalGridOptions } from 'ag-grid-community'

import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'

import App from './App'
import { ErrorBoundary } from './components/ui/ErrorBoundary'
import 'react-grid-layout/css/styles.css'
import 'react-resizable/css/styles.css'
import './styles/theme.css'
import './index.css'

ModuleRegistry.registerModules([AllCommunityModule])

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

provideGlobalGridOptions({ theme: 'legacy' })

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  </StrictMode>,
)
