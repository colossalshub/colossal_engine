import { Component, type ErrorInfo, type ReactNode } from 'react'
import { EmptyState } from './EmptyState'

interface ErrorBoundaryProps {
  children: ReactNode
  fallbackMessage?: string
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // In a local tool, console is the right sink. Future: send to a logger.
    // eslint-disable-next-line no-console
    console.error('ErrorBoundary caught:', error, info.componentStack)
  }

  reset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      return (
        <EmptyState
          icon="⚠"
          message={this.props.fallbackMessage ?? 'Something went wrong rendering this page.'}
          action={{ label: 'Reload', onClick: () => window.location.reload() }}
        />
      )
    }
    return this.props.children
  }
}
