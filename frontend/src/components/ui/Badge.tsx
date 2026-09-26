import type { RunStatus } from '../../api/types'
import './badge.css'

interface BadgeProps {
  status: RunStatus
}

const LABELS: Record<RunStatus, string> = {
  queued: 'queued',
  running: 'running',
  done: 'done',
  failed: 'failed',
  archived: 'archived',
}

export function Badge({ status }: BadgeProps) {
  return (
    <span className={`badge badge--${status}`}>
      <span className="badge__dot" aria-hidden="true" />
      <span className="badge__label">{LABELS[status]}</span>
    </span>
  )
}
