/**
 * StateStats - Display 2024 EAVS election administration statistics
 */

function formatNumber(num) {
  if (num === null || num === undefined) return 'N/A'
  return new Intl.NumberFormat('en-US').format(num)
}

function formatPercent(num) {
  if (num === null || num === undefined) return 'N/A'
  return `${num}%`
}

function StatCard({ label, value, detail, accent = 'forest' }) {
  const accentColors = {
    forest: 'var(--forest)',
    rust: 'var(--rust)',
    amber: 'var(--amber)',
  }

  return (
    <div
      className="bg-white p-4 rounded-lg"
      style={{ borderLeft: `4px solid ${accentColors[accent]}` }}
    >
      <p
        className="text-xs font-medium uppercase tracking-wide mb-1"
        style={{ color: 'var(--brown-light)' }}
      >
        {label}
      </p>
      <p
        className="text-2xl font-bold"
        style={{ color: 'var(--brown)', fontFamily: 'Playfair Display, Georgia, serif' }}
      >
        {value}
      </p>
      {detail && (
        <p className="text-xs mt-1" style={{ color: 'var(--brown-light)' }}>
          {detail}
        </p>
      )}
    </div>
  )
}

function StateStats({ stateCode, eavsData }) {
  if (!eavsData?.states) {
    return null
  }

  const stateData = eavsData.states[stateCode?.toUpperCase()]

  if (!stateData) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h2
          className="text-xl font-bold mb-4"
          style={{ color: 'var(--brown)' }}
        >
          2024 Election Administration
        </h2>
        <p style={{ color: 'var(--brown-light)' }} className="text-sm italic">
          EAVS data not available for this jurisdiction.
        </p>
      </div>
    )
  }

  const { voter_registration, mail_voting, polling, provisional, turnout } = stateData

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <h2
        className="text-xl font-bold mb-2"
        style={{ color: 'var(--brown)' }}
      >
        2024 Election Administration
      </h2>
      <p className="text-sm mb-6" style={{ color: 'var(--brown-light)' }}>
        Statistics from the Election Administration and Voting Survey (EAVS)
      </p>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6" style={{ backgroundColor: 'var(--stone)', padding: '1rem', borderRadius: '0.5rem' }}>
        {/* Voter Registration */}
        <StatCard
          label="Active Voters"
          value={formatNumber(voter_registration?.total_active)}
          detail={voter_registration?.total_registered ? `${formatNumber(voter_registration.total_registered)} total registered` : null}
          accent="forest"
        />

        {/* Turnout */}
        <StatCard
          label="Ballots Cast"
          value={formatNumber(turnout?.total_ballots_cast)}
          detail={turnout?.turnout_percentage ? `${turnout.turnout_percentage}% turnout` : null}
          accent="forest"
        />

        {/* Mail Voting */}
        <StatCard
          label="Mail Ballots Sent"
          value={formatNumber(mail_voting?.ballots_transmitted)}
          detail={mail_voting?.return_rate ? `${mail_voting.return_rate}% returned` : null}
          accent="amber"
        />

        <StatCard
          label="Mail Ballots Returned"
          value={formatNumber(mail_voting?.ballots_returned)}
          detail={mail_voting?.rejection_rate !== null ? `${mail_voting.rejection_rate}% rejected` : null}
          accent="amber"
        />

        {/* Polling */}
        <StatCard
          label="Polling Places"
          value={formatNumber(polling?.polling_places)}
          detail={polling?.precincts ? `${formatNumber(polling.precincts)} precincts` : null}
          accent="rust"
        />

        <StatCard
          label="Poll Workers"
          value={formatNumber(polling?.poll_workers)}
          accent="rust"
        />

        {/* Provisional */}
        <StatCard
          label="Provisional Ballots"
          value={formatNumber(provisional?.ballots_submitted)}
          detail={provisional?.count_rate ? `${provisional.count_rate}% counted` : null}
          accent="forest"
        />

        {/* Same-day Registration */}
        {voter_registration?.same_day_registrations > 0 && (
          <StatCard
            label="Same-Day Registrations"
            value={formatNumber(voter_registration.same_day_registrations)}
            accent="amber"
          />
        )}
      </div>

      {/* Source attribution */}
      <div className="text-xs" style={{ color: 'var(--brown-light)' }}>
        <p>
          Source:{' '}
          <a
            href="https://www.eac.gov/research-and-data/studies-and-reports"
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: 'var(--forest)' }}
            className="hover:underline"
          >
            U.S. Election Assistance Commission - 2024 EAVS
          </a>
        </p>
        <p className="mt-1 italic">
          Data aggregated from {stateData.jurisdiction_count} jurisdiction reports.
          Some statistics may be incomplete where jurisdictions did not report.
        </p>
      </div>
    </div>
  )
}

export default StateStats
