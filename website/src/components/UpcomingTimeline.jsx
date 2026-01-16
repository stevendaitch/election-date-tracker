import { Link } from 'react-router-dom'
import { daysUntil, formatDateTimeline as formatDate } from '../utils'

function UpcomingTimeline({ states, specialData }) {
  // Build list of all elections
  const elections = []

  // Regular elections
  states.forEach(state => {
    elections.push({
      state_code: state.state_code,
      state_name: state.state_name,
      date: state.next_primary.date,
      type: 'Primary',
      category: 'regular',
      days: daysUntil(state.next_primary.date)
    })
    elections.push({
      state_code: state.state_code,
      state_name: state.state_name,
      date: state.next_general.date,
      type: 'General',
      category: 'regular',
      days: daysUntil(state.next_general.date)
    })
  })

  // Special elections
  if (specialData?.special_elections) {
    specialData.special_elections.forEach(election => {
      if (election.next_date) {
        elections.push({
          state_code: election.state_code,
          state_name: election.state_name,
          date: election.next_date,
          type: 'Special',
          category: 'special',
          office: election.office,
          district: election.district,
          days: daysUntil(election.next_date)
        })
      }
    })
  }

  // Sort by date and filter out past elections
  elections.sort((a, b) => new Date(a.date) - new Date(b.date))
  const upcomingElections = elections.filter(e => e.days >= 0)

  // Group by month
  const grouped = upcomingElections.reduce((acc, election) => {
    const monthYear = new Date(election.date + 'T00:00:00').toLocaleDateString('en-US', {
      month: 'long',
      year: 'numeric'
    })
    if (!acc[monthYear]) {
      acc[monthYear] = []
    }
    acc[monthYear].push(election)
    return acc
  }, {})

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        Upcoming Elections
      </h1>
      <p className="text-gray-600 mb-4">
        All upcoming primary and general elections across states, sorted by date.
      </p>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-8 text-sm">
        <p className="text-amber-800">
          <strong>Special Elections:</strong> Shown in purple. This data is sourced from official state election offices
          where available and may not include all special elections. Always verify with your
          <a
            href="https://www.usa.gov/election-office"
            target="_blank"
            rel="noopener noreferrer"
            className="text-amber-700 underline ml-1"
          >
            state election office
          </a>.
        </p>
      </div>

      <div className="space-y-8">
        {Object.entries(grouped).map(([month, monthElections]) => (
          <div key={month}>
            <h2 className="text-xl font-bold text-gray-700 mb-4 border-b pb-2">
              {month}
            </h2>
            <div className="space-y-3">
              {monthElections.map((election, idx) => (
                <Link
                  key={`${election.state_code}-${election.type}-${idx}`}
                  to={`/state/${election.state_code}`}
                  className="block"
                >
                  <div className={`flex items-center justify-between p-4 rounded-lg hover:shadow-md transition-shadow ${
                    election.type === 'Primary'
                      ? 'bg-blue-50 border-l-4 border-blue-500'
                      : election.type === 'General'
                      ? 'bg-red-50 border-l-4 border-red-500'
                      : 'bg-purple-50 border-l-4 border-purple-500'
                  }`}>
                    <div className="flex items-center gap-4">
                      <div className={`text-sm font-bold px-2 py-1 rounded ${
                        election.type === 'Primary'
                          ? 'bg-blue-200 text-blue-800'
                          : election.type === 'General'
                          ? 'bg-red-200 text-red-800'
                          : 'bg-purple-200 text-purple-800'
                      }`}>
                        {election.type}
                      </div>
                      <div>
                        <p className="font-medium text-gray-800">
                          {election.state_name} ({election.state_code})
                          {election.category === 'special' && election.office && (
                            <span className="text-purple-600 ml-2 text-sm">
                              {election.office}{election.district && ` - ${election.district}`}
                            </span>
                          )}
                        </p>
                        <p className="text-sm text-gray-600">
                          {formatDate(election.date)}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-bold ${
                        election.days <= 30 ? 'text-orange-600' : 'text-gray-600'
                      }`}>
                        {election.days} days
                      </p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default UpcomingTimeline
