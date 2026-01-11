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
      <div className="min-h-screen flex items-center justify-center bg-white">
        <p style={{ color: 'var(--brown-light)' }}>Loading election data...</p>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <p style={{ color: 'var(--rust)' }}>Failed to load election data</p>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-white">
        <header className="border-b border-stone-200">
          <div className="max-w-6xl mx-auto px-6 py-5">
            <div className="flex items-center justify-between">
              <Link
                to="/"
                className="text-xl font-semibold tracking-tight"
                style={{ color: 'var(--brown)' }}
              >
                Election Date Tracker
              </Link>
              <nav className="flex items-center gap-8">
                <Link
                  to="/"
                  className="text-sm transition-colors"
                  style={{ color: 'var(--brown-light)' }}
                >
                  All States
                </Link>
                <Link
                  to="/upcoming"
                  className="text-sm transition-colors"
                  style={{ color: 'var(--brown-light)' }}
                >
                  Upcoming
                </Link>
                <a
                  href="https://stevedait.ch"
                  className="text-sm font-medium"
                  style={{ color: 'var(--forest)' }}
                >
                  stevedait.ch →
                </a>
              </nav>
            </div>
            <p className="text-sm mt-2" style={{ color: 'var(--brown-light)' }}>
              Last updated: {data.metadata.generated_at.split('T')[0]}
            </p>
          </div>
        </header>

        <main className="max-w-6xl mx-auto px-6 py-10">
          <Routes>
            <Route path="/" element={<StateGrid states={data.states} specialData={specialData} />} />
            <Route path="/state/:stateCode" element={<StateDetail states={data.states} specialData={specialData} />} />
            <Route path="/upcoming" element={<UpcomingTimeline states={data.states} specialData={specialData} />} />
          </Routes>
        </main>

        <footer className="border-t border-stone-200 py-8 mt-12">
          <div className="max-w-6xl mx-auto px-6">
            <p className="text-sm" style={{ color: 'var(--brown-light)' }}>
              Election dates sourced from state statutes and Secretary of State websites.
              Special election data may be incomplete.{' '}
              <a
                href="https://www.usa.gov/election-office"
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
                style={{ color: 'var(--forest)' }}
              >
                Verify with your state →
              </a>
            </p>
            <p className="text-sm mt-3" style={{ color: 'var(--brown-light)' }}>
              A project by{' '}
              <a
                href="https://stevedait.ch"
                className="underline"
                style={{ color: 'var(--forest)' }}
              >
                Steve Daitch
              </a>
            </p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  )
}

export default App
