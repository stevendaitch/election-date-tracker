import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup
} from 'react-simple-maps'
import * as topojson from 'topojson-client'
import usAtlas from 'us-atlas/states-10m.json'
import { daysUntil, formatDate, getColorByDays } from '../utils'

// Convert TopoJSON to GeoJSON for react-simple-maps
const geoData = topojson.feature(usAtlas, usAtlas.objects.states)

// FIPS code to state abbreviation mapping
const FIPS_TO_STATE = {
  "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA",
  "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL",
  "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN",
  "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME",
  "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS",
  "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
  "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND",
  "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
  "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT",
  "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI",
  "56": "WY"
}

function USMap({ states, specialData }) {
  const navigate = useNavigate()
  const [tooltipContent, setTooltipContent] = useState(null)
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 })

  // Create lookup by state code
  const stateData = {}
  states.forEach(state => {
    stateData[state.state_code] = state
  })

  // Get special elections for a state
  const getStateSpecials = (stateCode) => {
    if (!specialData?.special_elections) return []
    return specialData.special_elections.filter(e => e.state_code === stateCode)
  }

  // Get the earliest upcoming election (primary, general, or special)
  const getNextElection = (stateCode) => {
    const state = stateData[stateCode]
    if (!state) return null

    const elections = [
      { type: 'Primary', date: state.next_primary.date, days: daysUntil(state.next_primary.date) },
      { type: 'General', date: state.next_general.date, days: daysUntil(state.next_general.date) },
    ]

    // Add special elections
    const specials = getStateSpecials(stateCode)
    specials.forEach(special => {
      if (special.next_date) {
        elections.push({
          type: 'Special',
          date: special.next_date,
          days: daysUntil(special.next_date),
          office: special.office,
          district: special.district
        })
      }
    })

    // Find the earliest
    const upcoming = elections.filter(e => e.days >= 0).sort((a, b) => a.days - b.days)
    return upcoming[0] || elections[0]
  }

  const handleMouseEnter = (geo, event) => {
    const fips = geo.id
    const stateCode = FIPS_TO_STATE[fips]
    const state = stateData[stateCode]

    if (state) {
      const next = getNextElection(stateCode)
      const specials = getStateSpecials(stateCode)

      setTooltipContent({
        name: state.state_name,
        code: state.state_code,
        nextType: next.type,
        nextDate: formatDate(next.date),
        nextDays: next.days,
        specialInfo: next.type === 'Special' ? `${next.office}${next.district ? ` - ${next.district}` : ''}` : null,
        specialCount: specials.length
      })
    }
  }

  const handleMouseMove = (event) => {
    setTooltipPos({ x: event.clientX, y: event.clientY })
  }

  const handleMouseLeave = () => {
    setTooltipContent(null)
  }

  const handleClick = (geo) => {
    const fips = geo.id
    const stateCode = FIPS_TO_STATE[fips]
    if (stateCode && stateData[stateCode]) {
      navigate(`/state/${stateCode}`)
    }
  }

  return (
    <div className="relative">
      <ComposableMap
        projection="geoAlbersUsa"
        className="w-full h-auto"
        style={{ maxHeight: '600px' }}
      >
        <ZoomableGroup>
          <Geographies geography={geoData}>
            {({ geographies }) =>
              geographies.map((geo) => {
                const fips = geo.id
                const stateCode = FIPS_TO_STATE[fips]
                const state = stateData[stateCode]

                let fillColor = "#d1d5db" // gray for unknown
                if (state) {
                  const next = getNextElection(stateCode)
                  fillColor = getColorByDays(next.days)
                }

                return (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    onMouseEnter={(e) => handleMouseEnter(geo, e)}
                    onMouseMove={handleMouseMove}
                    onMouseLeave={handleMouseLeave}
                    onClick={() => handleClick(geo)}
                    style={{
                      default: {
                        fill: fillColor,
                        stroke: "#ffffff",
                        strokeWidth: 0.5,
                        outline: "none",
                      },
                      hover: {
                        fill: "#1e40af",
                        stroke: "#ffffff",
                        strokeWidth: 1,
                        outline: "none",
                        cursor: "pointer",
                      },
                      pressed: {
                        fill: "#1e3a8a",
                        stroke: "#ffffff",
                        strokeWidth: 1,
                        outline: "none",
                      },
                    }}
                  />
                )
              })
            }
          </Geographies>
        </ZoomableGroup>
      </ComposableMap>

      {/* Tooltip */}
      {tooltipContent && (
        <div
          className="fixed bg-gray-900 text-white px-3 py-2 rounded-lg shadow-lg text-sm pointer-events-none z-50"
          style={{
            left: tooltipPos.x + 10,
            top: tooltipPos.y - 10,
          }}
        >
          <p className="font-bold">{tooltipContent.name} ({tooltipContent.code})</p>
          <p className={tooltipContent.nextType === 'Special' ? 'text-purple-300' : 'text-gray-300'}>
            Next: {tooltipContent.nextType} - {tooltipContent.nextDate}
          </p>
          {tooltipContent.specialInfo && (
            <p className="text-purple-400 text-xs">{tooltipContent.specialInfo}</p>
          )}
          <p className="text-gray-400 text-xs">
            {tooltipContent.nextDays} days away
          </p>
          {tooltipContent.specialCount > 0 && tooltipContent.nextType !== 'Special' && (
            <p className="text-purple-300 text-xs mt-1">
              + {tooltipContent.specialCount} special election{tooltipContent.specialCount > 1 ? 's' : ''}
            </p>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="mt-4 flex flex-wrap justify-center gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: "#C65D3D" }}></div>
          <span style={{ color: 'var(--brown-light)' }}>&lt; 30 days</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: "#D4A574" }}></div>
          <span style={{ color: 'var(--brown-light)' }}>30-60 days</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: "#8B7355" }}></div>
          <span style={{ color: 'var(--brown-light)' }}>60-90 days</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: "#3D7A52" }}></div>
          <span style={{ color: 'var(--brown-light)' }}>90-180 days</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: "#2D5A3D" }}></div>
          <span style={{ color: 'var(--brown-light)' }}>&gt; 180 days</span>
        </div>
      </div>

      {/* Special elections note */}
      <p className="mt-3 text-center text-xs" style={{ color: 'var(--brown-light)' }}>
        Special election data may be incomplete. Click a state for details and verification links.
      </p>
    </div>
  )
}

export default USMap
