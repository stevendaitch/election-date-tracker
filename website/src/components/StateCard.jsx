import { daysUntil, formatDate } from '../utils'

function StateCard({ state, specialCount = 0 }) {
  const primaryDays = daysUntil(state.next_primary.date)
  const generalDays = daysUntil(state.next_general.date)
  const nextElection = primaryDays < generalDays ? 'primary' : 'general'
  const daysToNext = Math.min(primaryDays, generalDays)

  return (
    <div
      className="rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow border-l-4"
      style={{
        backgroundColor: 'var(--cream-dark)',
        borderLeftColor: 'var(--forest)'
      }}
    >
      <div className="flex items-center justify-between mb-2">
        <h3
          className="text-lg font-bold"
          style={{
            fontFamily: 'Playfair Display, serif',
            color: 'var(--brown)'
          }}
        >
          {state.state_code}
        </h3>
        <div className="flex gap-1">
          {specialCount > 0 && (
            <span
              className="text-xs px-2 py-1 rounded font-medium"
              style={{
                backgroundColor: 'var(--rust)',
                color: 'var(--cream)'
              }}
            >
              {specialCount} Special
            </span>
          )}
          <span
            className="text-xs px-2 py-1 rounded font-medium"
            style={{
              backgroundColor: state.next_primary.confidence === 'High' ? 'var(--forest)' : 'var(--amber)',
              color: 'var(--cream)'
            }}
          >
            {state.next_primary.confidence}
          </span>
        </div>
      </div>

      <p className="text-sm mb-3" style={{ color: 'var(--brown-light)' }}>
        {state.state_name}
      </p>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span style={{ color: 'var(--brown-light)' }}>Primary:</span>
          <span className="font-medium" style={{ color: 'var(--brown)' }}>
            {formatDate(state.next_primary.date)}
          </span>
        </div>
        <div className="flex justify-between">
          <span style={{ color: 'var(--brown-light)' }}>General:</span>
          <span className="font-medium" style={{ color: 'var(--brown)' }}>
            {formatDate(state.next_general.date)}
          </span>
        </div>
      </div>

      <div
        className="mt-3 pt-3 border-t"
        style={{ borderColor: 'var(--amber-light)' }}
      >
        <p className="text-xs" style={{ color: 'var(--brown-light)' }}>
          {daysToNext} days until {nextElection}
        </p>
      </div>
    </div>
  )
}

export default StateCard
