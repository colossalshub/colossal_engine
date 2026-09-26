import './errorDisplay.css'

interface ErrorDisplayProps {
  message: string
  onRetry?: () => void
}

export function ErrorDisplay({ message, onRetry }: ErrorDisplayProps) {
  return (
    <div className="error-display" role="alert">
      <span className="error-display__message">{message}</span>
      {onRetry ? (
        <button
          type="button"
          className="error-display__retry"
          onClick={onRetry}
        >
          Retry
        </button>
      ) : null}
    </div>
  )
}
