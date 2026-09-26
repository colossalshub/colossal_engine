import type { ReactNode } from 'react'
import './emptyState.css'

interface EmptyStateProps {
  icon?: ReactNode
  message: string
  action?: {
    label: string
    onClick: () => void
  }
}

export function EmptyState({ icon, message, action }: EmptyStateProps) {
  return (
    <div className="empty-state">
      {icon ? <div className="empty-state__icon" aria-hidden="true">{icon}</div> : null}
      <div className="empty-state__message">{message}</div>
      {action ? (
        <button
          type="button"
          className="empty-state__action"
          onClick={action.onClick}
        >
          {action.label}
        </button>
      ) : null}
    </div>
  )
}
