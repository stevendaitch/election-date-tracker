import { daysUntil, formatDate } from '../utils'

function StateCard({ state, specialCount = 0 }) {
  const primaryDays = daysUntil(state.next_primary.date)
  const generalDays = daysUntil(state.next_general.date)
  const nextElection = primaryDays < generalDays ? 'primary' : 'general'
  const daysToNext = Math.min(primaryDays, generalDays)

  return (
    <div className="border-b border-stone-200 py-4 hover:bg-stone-50 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div>
          <h3
            className="text-lg font-semibold"
            style={{ color: 'var(--brown)' }}
          >
            {state.state_code}
          </h3>
          <p className="text-sm" style={{ color: 'var(--brown-light)' }}>
            {state.state_name}
          </p>
        </div>
        <div className="flex gap-2">
          {specialCount > 0 && (
            <span
              className="text-xs font-medium px-2 py-1 rounded"
              style={{ backgroundColor: 'var(--rust)', color: 'white' }}
            >
              {specialCount} Special
            </span>
          )}
          <span
            className="text-xs px-2 py-1 rounded"
            style={{
              backgroundColor: state.next_primary.confidence === 'High' ? 'var(--forest)' : 'var(--amber)',
              color: 'white'
            }}
          >
            {state.next_primary.confidence}
          </span>
        </div>
      </div>

      <div className="flex gap-8 text-sm">
        <div>
          <span style={{ color: 'var(--brown-light)' }}>Primary: </span>
          <span style={{ color: 'var(--brown)' }}>{formatDate(state.next_primary.date)}</span>
        </div>
        <div>
          <span style={{ color: 'var(--brown-light)' }}>General: </span>
          <span style={{ color: 'var(--brown)' }}>{formatDate(state.next_general.date)}</span>
        </div>
      </div>

      <p className="text-xs mt-2" style={{ color: 'var(--brown-light)' }}>
        {daysToNext} days until {nextElection}
      </p>
    </div>
  )
}

export default StateCard
