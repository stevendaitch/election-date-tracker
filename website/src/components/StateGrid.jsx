import { useState } from 'react'
import { Link } from 'react-router-dom'
import StateCard from './StateCard'
import USMap from './USMap'

function StateGrid({ states, specialData }) {
  const [viewMode, setViewMode] = useState('map') // 'map' or 'grid'

  // Get special election count by state
  const getSpecialCount = (stateCode) => {
    if (!specialData?.by_state) return 0
    return specialData.by_state[stateCode]?.length || 0
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">
            2026 Election Dates
          </h1>
          <p className="text-gray-600 mt-1">
            Click on a state to see detailed election information and sources.
          </p>
        </div>

        {/* View Toggle */}
        <div className="flex gap-2 mt-4 sm:mt-0">
          <button
            onClick={() => setViewMode('map')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              viewMode === 'map'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Map View
          </button>
          <button
            onClick={() => setViewMode('grid')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              viewMode === 'grid'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Grid View
          </button>
        </div>
      </div>

      {viewMode === 'map' ? (
        <div className="bg-white rounded-lg shadow-lg p-4">
          <USMap states={states} specialData={specialData} />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {states.map(state => (
            <Link key={state.state_code} to={`/state/${state.state_code}`}>
              <StateCard state={state} specialCount={getSpecialCount(state.state_code)} />
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default StateGrid
