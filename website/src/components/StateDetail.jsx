import { useParams, Link } from 'react-router-dom'
import { daysUntil, formatDateLong as formatDate } from '../utils'
import StateStats from './StateStats'

function StateDetail({ states, specialData, eavsData }) {
  const { stateCode } = useParams()
  const state = states.find(s => s.state_code === stateCode.toUpperCase())

  // Get special elections for this state
  const stateSpecials = specialData?.special_elections?.filter(
    e => e.state_code === stateCode.toUpperCase()
  ) || []

  if (!state) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">State Not Found</h2>
        <p className="text-gray-600 mb-4">
          The state "{stateCode}" was not found in our database.
        </p>
        <Link to="/" className="text-blue-600 hover:underline">
          Back to all states
        </Link>
      </div>
    )
  }

  const primaryDays = daysUntil(state.next_primary.date)
  const generalDays = daysUntil(state.next_general.date)

  return (
    <div>
      <Link to="/" className="text-blue-600 hover:underline text-sm mb-4 inline-block">
        &larr; Back to all states
      </Link>

      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold text-gray-800">
            {state.state_name} ({state.state_code})
          </h1>
          <span className={`px-3 py-1 rounded text-sm font-medium ${
            state.next_primary.confidence === 'High'
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {state.next_primary.confidence} Confidence
          </span>
        </div>

        <p className="text-gray-600 mb-6">{state.notes}</p>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Primary Election */}
          <div className="bg-blue-50 rounded-lg p-5">
            <h2 className="text-xl font-bold text-blue-900 mb-3">Primary Election</h2>
            <div className="space-y-2">
              <p className="text-2xl font-bold text-blue-800">
                {formatDate(state.next_primary.date)}
              </p>
              <p className="text-blue-600">
                {primaryDays} days from now
              </p>
              <p className="text-sm text-gray-600 mt-3">
                <strong>Rule:</strong> {state.next_primary.date_rule}
              </p>
              <p className="text-sm text-gray-600">
                <strong>Statute:</strong> {state.next_primary.statute_reference}
              </p>
            </div>
          </div>

          {/* General Election */}
          <div className="bg-red-50 rounded-lg p-5">
            <h2 className="text-xl font-bold text-red-900 mb-3">General Election</h2>
            <div className="space-y-2">
              <p className="text-2xl font-bold text-red-800">
                {formatDate(state.next_general.date)}
              </p>
              <p className="text-red-600">
                {generalDays} days from now
              </p>
              <p className="text-sm text-gray-600 mt-3">
                <strong>Rule:</strong> {state.next_general.date_rule}
              </p>
              <p className="text-sm text-gray-600">
                <strong>Statute:</strong> {state.next_general.statute_reference}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 2024 EAVS Statistics */}
      <StateStats stateCode={stateCode} eavsData={eavsData} />

      {/* Special Elections */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">
          Special Elections
          {stateSpecials.length > 0 && (
            <span className="ml-2 bg-purple-100 text-purple-800 text-sm px-2 py-1 rounded">
              {stateSpecials.length}
            </span>
          )}
        </h2>

        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-4 text-sm">
          <p className="text-amber-800">
            <strong>Note:</strong> Special election data is sourced from official Secretary of State websites where available.
            Some states may have additional special elections not listed here.
            <a
              href={`https://www.google.com/search?q=${state.state_name}+special+elections+2026+site:.gov`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-amber-700 underline ml-1"
            >
              Verify with your state election office
            </a>
          </p>
        </div>

        {stateSpecials.length > 0 ? (
          <div className="space-y-4">
            {stateSpecials.map((election) => (
              <div key={election.id} className="bg-purple-50 rounded-lg p-4 border-l-4 border-purple-500">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-bold text-purple-900">
                      {election.office}
                      {election.district && ` - ${election.district}`}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {election.reason}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <span className={`text-xs px-2 py-1 rounded ${
                      election.confidence === 'High'
                        ? 'bg-green-100 text-green-800'
                        : election.confidence === 'Medium'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {election.confidence}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded ${
                      election.status === 'scheduled'
                        ? 'bg-blue-100 text-blue-800'
                        : election.status === 'runoff_pending'
                        ? 'bg-orange-100 text-orange-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {election.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>

                <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                  {election.dates.primary && (
                    <div>
                      <span className="text-gray-500">Primary:</span>
                      <p className="font-medium">{formatDate(election.dates.primary)}</p>
                    </div>
                  )}
                  {election.dates.general && (
                    <div>
                      <span className="text-gray-500">General:</span>
                      <p className="font-medium">{formatDate(election.dates.general)}</p>
                    </div>
                  )}
                  {election.dates.runoff && (
                    <div>
                      <span className="text-gray-500">Runoff:</span>
                      <p className="font-medium">{formatDate(election.dates.runoff)}</p>
                    </div>
                  )}
                </div>

                {election.notes && (
                  <p className="text-sm text-gray-600 mt-2 italic">{election.notes}</p>
                )}

                {election.source_url && (
                  <a
                    href={election.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-purple-600 hover:underline mt-2 inline-block"
                  >
                    View source
                  </a>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">
            No special elections currently tracked for {state.state_name}.
          </p>
        )}
      </div>

      {/* Sources */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Sources</h2>
        <div className="space-y-4">
          {state.sources.map((source, idx) => (
            <div key={idx} className="border-l-4 border-gray-300 pl-4">
              <p className="font-medium text-gray-800 capitalize">
                {source.type.replace('_', ' ')}
              </p>
              {source.reference && (
                <p className="text-sm text-gray-600">{source.reference}</p>
              )}
              {source.url && (
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:underline break-all"
                >
                  {source.url}
                </a>
              )}
              {source.last_verified && (
                <p className="text-xs text-gray-500 mt-1">
                  Last verified: {source.last_verified}
                </p>
              )}
            </div>
          ))}
        </div>

        {state.validation.discrepancies.length > 0 && (
          <div className="mt-6 p-4 bg-yellow-50 rounded-lg">
            <h3 className="font-bold text-yellow-800 mb-2">Validation Notes</h3>
            <ul className="text-sm text-yellow-700 space-y-1">
              {state.validation.discrepancies.map((d, idx) => (
                <li key={idx}>
                  {d.field}: {d.resolution}
                </li>
              ))}
            </ul>
          </div>
        )}

        <p className="text-sm text-gray-500 mt-6">
          Data last updated: {state.last_updated}
        </p>
      </div>
    </div>
  )
}

export default StateDetail
