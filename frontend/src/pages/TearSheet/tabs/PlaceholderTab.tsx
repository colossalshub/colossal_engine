import { EmptyState } from '../../../components/ui/EmptyState'

interface PlaceholderTabProps {
  title: string
  phase: string
}

export default function PlaceholderTab({ title, phase }: PlaceholderTabProps) {
  return (
    <div className="tear-sheet-tab">
      <section className="tear-sheet-tab__section">
        <h2 className="tear-sheet-tab__heading">{title}</h2>
        <EmptyState
          icon="◦"
          message={`${title} analysis requires ${phase}.`}
        />
      </section>
    </div>
  )
}
