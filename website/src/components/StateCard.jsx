import { daysUntil, formatDate } from '../utils'

function StateCard({ state, specialCount = 0 }) {
  const primaryDays = daysUntil(state.next_primary.date)
  const generalDays = daysUntil(state.next_general.date)
  const nextElection = primaryDays < generalDays ? 'primary' : 'general'
  const daysToNext = Math.min(primaryDays, generalDays)

  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow border-l-4 border-blue-600">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-bold text-gray-800">
          {state.state_code}
        </h3>
        <div className="flex gap-1">
          {specialCount > 0 && (
            <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded">
              {specialCount} Special
            </span>
          )}
          <span className={`text-xs px-2 py-1 rounded ${
            state.next_primary.confidence === 'High'
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {state.next_primary.confidence}
          </span>
        </div>
      </div>

      <p className="text-sm text-gray-600 mb-3">{state.state_name}</p>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">Primary:</span>
          <span className="font-medium">{formatDate(state.next_primary.date)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">General:</span>
          <span className="font-medium">{formatDate(state.next_general.date)}</span>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-gray-100">
        <p className="text-xs text-gray-500">
          {daysToNext} days until {nextElection}
        </p>
      </div>
    </div>
  )
}

export default StateCard
