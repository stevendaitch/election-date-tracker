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
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: 'var(--cream)' }}
      >
        <p style={{ color: 'var(--brown-light)' }}>Loading election data...</p>
      </div>
    )
  }

  if (!data) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: 'var(--cream)' }}
      >
        <p style={{ color: 'var(--rust)' }}>Failed to load election data</p>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen" style={{ backgroundColor: 'var(--cream)' }}>
        <header
          className="shadow-lg"
          style={{ backgroundColor: 'var(--forest)' }}
        >
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <Link
                to="/"
                className="text-2xl font-bold transition-colors"
                style={{
                  fontFamily: 'Playfair Display, serif',
                  color: 'var(--cream)'
                }}
              >
                Election Date Tracker
              </Link>
              <nav className="flex gap-6">
                <Link
                  to="/"
                  className="transition-colors uppercase tracking-wider text-sm font-medium"
                  style={{ color: 'var(--cream)', opacity: 0.9 }}
                >
                  All States
                </Link>
                <Link
                  to="/upcoming"
                  className="transition-colors uppercase tracking-wider text-sm font-medium"
                  style={{ color: 'var(--cream)', opacity: 0.9 }}
                >
                  Upcoming
                </Link>
                <a
                  href="https://stevedait.ch"
                  className="transition-colors uppercase tracking-wider text-sm font-medium"
                  style={{ color: 'var(--amber)' }}
                >
                  stevedait.ch
                </a>
              </nav>
            </div>
            <p
              className="text-sm mt-1"
              style={{ color: 'var(--amber)', opacity: 0.8 }}
            >
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

        <footer
          className="py-6 mt-12"
          style={{ backgroundColor: 'var(--forest)' }}
        >
          <div className="max-w-7xl mx-auto px-4 text-center text-sm">
            <p style={{ color: 'var(--cream)', opacity: 0.9 }}>
              Regular election dates sourced from state statutes and Secretary of State websites.
            </p>
            <p className="mt-1" style={{ color: 'var(--cream)', opacity: 0.7 }}>
              Special election data may be incomplete. Always verify with your{' '}
              <a
                href="https://www.usa.gov/election-office"
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
                style={{ color: 'var(--amber)' }}
              >
                state election office
              </a>.
            </p>
            <p className="mt-3" style={{ color: 'var(--amber)', opacity: 0.8 }}>
              A project by{' '}
              <a
                href="https://stevedait.ch"
                className="underline"
                style={{ color: 'var(--amber)' }}
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
