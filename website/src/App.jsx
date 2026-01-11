import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import StateGrid from './components/StateGrid'
import StateDetail from './components/StateDetail'
import UpcomingTimeline from './components/UpcomingTimeline'

function App() {
  const [data, setData] = useState(null)
  const [specialData, setSpecialData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch('/election_dates.json').then(res => res.json()),
      fetch('/special_elections.json').then(res => res.json()).catch(() => ({ special_elections: [], by_state: {} }))
    ])
      .then(([regular, special]) => {
        setData(regular)
        setSpecialData(special)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load data:', err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading election data...</p>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-red-600">Failed to load election data</p>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-blue-900 text-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <Link to="/" className="text-2xl font-bold hover:text-blue-200">
                Election Date Tracker
              </Link>
              <nav className="flex gap-6">
                <Link to="/" className="hover:text-blue-200">All States</Link>
                <Link to="/upcoming" className="hover:text-blue-200">Upcoming</Link>
              </nav>
            </div>
            <p className="text-blue-200 text-sm mt-1">
              Data last updated: {data.metadata.generated_at.split('T')[0]}
            </p>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<StateGrid states={data.states} specialData={specialData} />} />
            <Route path="/state/:stateCode" element={<StateDetail states={data.states} specialData={specialData} />} />
            <Route path="/upcoming" element={<UpcomingTimeline states={data.states} specialData={specialData} />} />
          </Routes>
        </main>

        <footer className="bg-gray-800 text-gray-400 py-6 mt-12">
          <div className="max-w-7xl mx-auto px-4 text-center text-sm">
            <p>Regular election dates sourced from state statutes and Secretary of State websites.</p>
            <p className="mt-1 text-gray-500">
              Special election data may be incomplete. Always verify with your{' '}
              <a
                href="https://www.usa.gov/election-office"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 underline hover:text-gray-300"
              >
                state election office
              </a>.
            </p>
            <p className="mt-2">Built with React + Vite</p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  )
}

export default App
