import {
  AlertTriangle,
  MapPin,
  Plus,
  RefreshCw,
  Search,
  ShieldAlert,
  Thermometer,
  X,
} from 'lucide-react'
import {
  lazy,
  Suspense,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'
import PageHeading from '../components/PageHeading.jsx'
import SurfaceCard from '../components/SurfaceCard.jsx'
import { getCurrentWeather, searchCities } from '../services/weather.js'

const CityRiskMap = lazy(() => import('../components/CityRiskMap.jsx'))

const DEFAULT_CITIES = [
  { id: 'new-delhi', name: 'New Delhi', country: 'India', latitude: 28.6139, longitude: 77.209 },
  { id: 'mumbai', name: 'Mumbai', admin1: 'Maharashtra', country: 'India', latitude: 19.076, longitude: 72.8777 },
  { id: 'bengaluru', name: 'Bengaluru', admin1: 'Karnataka', country: 'India', latitude: 12.9716, longitude: 77.5946 },
  { id: 'chennai', name: 'Chennai', admin1: 'Tamil Nadu', country: 'India', latitude: 13.0827, longitude: 80.2707 },
  { id: 'kolkata', name: 'Kolkata', admin1: 'West Bengal', country: 'India', latitude: 22.5726, longitude: 88.3639 },
  { id: 'hyderabad', name: 'Hyderabad', admin1: 'Telangana', country: 'India', latitude: 17.385, longitude: 78.4867 },
  { id: 'jaipur', name: 'Jaipur', admin1: 'Rajasthan', country: 'India', latitude: 26.9124, longitude: 75.7873 },
  { id: 'ahmedabad', name: 'Ahmedabad', admin1: 'Gujarat', country: 'India', latitude: 23.0225, longitude: 72.5714 },
]

const RISK_ORDER = ['low', 'caution', 'extreme_caution', 'danger', 'extreme_danger']
const RISK_LABELS = {
  low: 'Low',
  caution: 'Caution',
  extreme_caution: 'Extreme caution',
  danger: 'Danger',
  extreme_danger: 'Extreme danger',
}
const MAX_CITIES = 12

function cityId(city) {
  return `${city.latitude.toFixed(3)}:${city.longitude.toFixed(3)}`
}

function riskLabel(risk) {
  return RISK_LABELS[risk] ?? 'Not applicable'
}

function MapCitySearch({ onAdd, cities }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [error, setError] = useState('')
  const [searching, setSearching] = useState(false)

  async function submit(event) {
    event.preventDefault()
    if (!query.trim()) {
      setResults([])
      setError('Enter a city name to search.')
      return
    }
    setSearching(true)
    setError('')
    setResults([])
    try {
      const matches = await searchCities(query.trim())
      setResults(matches)
      if (!matches.length) setError('No matching cities were found.')
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ??
          'City search is unavailable. Please try again.',
      )
    } finally {
      setSearching(false)
    }
  }

  function add(city) {
    const location = {
      id: cityId(city),
      name: city.name,
      admin1: city.admin1 ?? '',
      country: city.country ?? '',
      latitude: city.latitude,
      longitude: city.longitude,
    }
    if (
      cities.some(
        (item) =>
          Math.abs(item.latitude - location.latitude) < 0.02 &&
          Math.abs(item.longitude - location.longitude) < 0.02,
      )
    ) {
      setError(`${city.name} is already on the map.`)
      return
    }
    if (cities.length >= MAX_CITIES) {
      setError(`The map is limited to ${MAX_CITIES} locations at a time.`)
      return
    }
    onAdd(location)
    setQuery('')
    setResults([])
    setError('')
  }

  return (
    <div className="map-city-search">
      <form className="map-city-search-form" onSubmit={submit} role="search">
        <label className="visually-hidden" htmlFor="map-city-query">
          Search for a city to add to the map
        </label>
        <MapPin aria-hidden="true" size={17} />
        <input
          autoComplete="off"
          id="map-city-query"
          maxLength={100}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Add a city to compare"
          value={query}
        />
        <button aria-label="Search cities to add" disabled={searching} type="submit">
          <Search aria-hidden="true" size={17} />
        </button>
      </form>
      {error && <p className="map-search-message" role="status">{error}</p>}
      {results.length > 0 && (
        <ul aria-label="Map city search results" className="map-city-results">
          {results.map((city, index) => (
            <li key={`${city.id ?? city.name}-${city.latitude}-${index}`}>
              <button onClick={() => add(city)} type="button">
                <span>
                  <strong>{city.name}</strong>
                  <small>{[city.admin1, city.country].filter(Boolean).join(', ')}</small>
                </span>
                <Plus aria-hidden="true" size={17} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function MapPage() {
  const [cities, setCities] = useState(DEFAULT_CITIES)
  const [weatherById, setWeatherById] = useState({})
  const [selectedId, setSelectedId] = useState(DEFAULT_CITIES[0].id)
  const [refreshToken, setRefreshToken] = useState(0)
  const requestedIds = useRef(new Set())
  const previousRefreshToken = useRef(refreshToken)

  useEffect(() => {
    const refreshAll = previousRefreshToken.current !== refreshToken
    previousRefreshToken.current = refreshToken
    const requestedCities = refreshAll
      ? cities
      : cities.filter((city) => !requestedIds.current.has(city.id))
    if (!requestedCities.length) return

    const loadingState = Object.fromEntries(
      requestedCities.map((city) => [city.id, { loading: true }]),
    )
    requestedCities.forEach((city) => requestedIds.current.add(city.id))
    setWeatherById((current) => ({ ...current, ...loadingState }))
    Promise.allSettled(
      requestedCities.map(async (city) => ({
        id: city.id,
        data: await getCurrentWeather(city),
      })),
    ).then((results) => {
      setWeatherById((current) => {
        const next = { ...current }
        results.forEach((result, index) => {
          const city = requestedCities[index]
          next[city.id] =
            result.status === 'fulfilled'
              ? { data: result.value.data }
              : {
                  error:
                    result.reason.response?.data?.detail ??
                    'Current weather is unavailable. Retry to try again.',
                }
        })
        return next
      })
    })
  }, [cities, refreshToken])

  function addCity(city) {
    setCities((current) => [...current, city])
    setSelectedId(city.id)
  }

  const selectedCity = cities.find((city) => city.id === selectedId)
  const loadedCount = cities.filter(
    (city) => weatherById[city.id]?.data,
  ).length
  const notApplicableCount = cities.filter((city) => {
    const record = weatherById[city.id]
    return record?.data && !record.data.current?.heat_risk?.risk_level
  }).length
  const riskCounts = useMemo(
    () =>
      RISK_ORDER.reduce((counts, risk) => {
        counts[risk] = cities.filter(
          (city) =>
            weatherById[city.id]?.data?.current?.heat_risk?.risk_level === risk,
        ).length
        return counts
      }, {}),
    [cities, weatherById],
  )
  const selectedWeather = selectedCity ? weatherById[selectedCity.id] : null
  const current = selectedWeather?.data?.current
  const currentRisk = current?.heat_risk

  return (
    <div className="page-container map-page">
      <PageHeading
        eyebrow="City map"
        title="Compare local heat risk."
        description="Explore current conditions at individual locations. Markers represent city points, not a continuous regional heat map."
      >
        <div className="map-page-actions">
          <MapCitySearch cities={cities} onAdd={addCity} />
          <button
            aria-label="Refresh map weather"
            className="map-refresh-button"
            onClick={() => setRefreshToken((value) => value + 1)}
            type="button"
          >
            <RefreshCw aria-hidden="true" size={17} />
            <span>Refresh</span>
          </button>
        </div>
      </PageHeading>

      <div aria-label="Current city risk totals" className="map-summary" role="group">
        <span className="map-summary-total">
          <MapPin aria-hidden="true" size={16} />
          {loadedCount} of {cities.length} locations loaded
        </span>
        {RISK_ORDER.map((risk) => (
          <span className={`map-summary-risk risk-${risk}`} key={risk}>
            <i aria-hidden="true" />
            {RISK_LABELS[risk]} <strong>{riskCounts[risk]}</strong>
          </span>
        ))}
        <span className="map-summary-risk risk-unavailable">
          <i aria-hidden="true" />
          Not applicable <strong>{notApplicableCount}</strong>
        </span>
        {cities.some((city) => weatherById[city.id]?.error) && (
          <span className="map-summary-error">
            {cities.filter((city) => weatherById[city.id]?.error).length} unavailable
          </span>
        )}
      </div>

      <div className="map-content-grid">
        <SurfaceCard className="map-card">
          <div className="map-section-heading">
            <div>
              <p className="eyebrow">Point observations</p>
              <h2>City-level conditions</h2>
            </div>
            <span className="map-city-total">{cities.length} / {MAX_CITIES} cities</span>
          </div>
          <div className="map-canvas-frame">
            <Suspense
              fallback={
                <div className="map-loading-state" role="status">
                  Loading interactive map…
                </div>
              }
            >
              <CityRiskMap
                cities={cities}
                onSelect={setSelectedId}
                selectedId={selectedId}
                weatherById={weatherById}
              />
            </Suspense>
          </div>
          <div aria-label="Heat risk marker legend" className="map-legend">
            {RISK_ORDER.map((risk) => (
              <span className={`map-legend-item risk-${risk}`} key={risk}>
                <i aria-hidden="true" />
                {RISK_LABELS[risk]}
              </span>
            ))}
            <span className="map-legend-item risk-unavailable">
              <i aria-hidden="true" />
              Not applicable / unavailable
            </span>
          </div>
          <p className="map-attribution-note">
            Map tiles © OpenStreetMap contributors. Weather values are fetched
            from the HeatWatch API and are indicative only.
          </p>
        </SurfaceCard>

        <aside aria-label="Locations on the map" className="map-sidebar">
          <SurfaceCard className="map-city-list-card">
            <div className="map-section-heading">
              <div>
                <p className="eyebrow">Locations</p>
                <h2>Compare cities</h2>
              </div>
              <span className="map-city-total">{cities.length}</span>
            </div>
            <div className="map-city-list">
              {cities.map((city) => {
                const record = weatherById[city.id]
                const cityWeather = record?.data?.current
                const risk = cityWeather?.heat_risk
                const level = risk?.risk_level
                return (
                  <div
                    className={`map-city-row ${city.id === selectedId ? 'is-selected' : ''}`}
                    key={city.id}
                  >
                    <button
                      aria-pressed={city.id === selectedId}
                      className="map-city-select"
                      onClick={() => setSelectedId(city.id)}
                      type="button"
                    >
                      <span className={`map-city-marker risk-${level ?? 'unavailable'}`}>
                        <MapPin aria-hidden="true" size={16} />
                      </span>
                      <span className="map-city-copy">
                        <strong>{city.name}</strong>
                        <small>{city.admin1 || city.country}</small>
                      </span>
                      {record?.loading ? (
                        <span className="loading-spinner spinner-small" aria-label="Loading weather" />
                      ) : record?.error ? (
                        <AlertTriangle aria-label="Weather unavailable" className="map-city-error-icon" size={16} />
                      ) : cityWeather ? (
                        <span className="map-city-temperature">
                          {cityWeather.temperature_c.toFixed(0)}°
                        </span>
                      ) : (
                        <span className="map-city-temperature">—</span>
                      )}
                    </button>
                    {city.id !== DEFAULT_CITIES[0].id && (
                      <button
                        aria-label={`Remove ${city.name} from map`}
                        className="map-city-remove"
                        onClick={() => {
                          setCities((currentCities) =>
                            currentCities.filter((item) => item.id !== city.id),
                          )
                          setWeatherById((currentWeather) => {
                            const next = { ...currentWeather }
                            delete next[city.id]
                            return next
                          })
                          requestedIds.current.delete(city.id)
                          if (selectedId === city.id) {
                            setSelectedId(DEFAULT_CITIES[0].id)
                          }
                        }}
                        type="button"
                      >
                        <X aria-hidden="true" size={15} />
                      </button>
                    )}
                  </div>
                )
              })}
            </div>
          </SurfaceCard>

          <SurfaceCard aria-label="Selected city current conditions" className="map-detail-card">
            <div className="map-section-heading">
              <div>
                <p className="eyebrow">Selected location</p>
                <h2>{selectedCity?.name ?? 'City details'}</h2>
              </div>
              <span className="map-detail-icon">
                <Thermometer aria-hidden="true" size={18} />
              </span>
            </div>
            {selectedWeather?.loading ? (
              <p className="map-detail-message">Loading current conditions…</p>
            ) : selectedWeather?.error ? (
              <div className="map-detail-error" role="alert">
                <AlertTriangle aria-hidden="true" size={17} />
                <p>{selectedWeather.error}</p>
              </div>
            ) : current ? (
              <>
                <div className="map-detail-temperature">
                  {current.temperature_c.toFixed(1)} <small>°C</small>
                </div>
                <p className="map-detail-apparent">
                  Feels like {current.apparent_temperature_c.toFixed(1)} °C
                </p>
                <div className={`map-detail-risk risk-${currentRisk?.risk_level ?? 'unavailable'}`}>
                  <ShieldAlert aria-hidden="true" size={17} />
                  <span>
                    {currentRisk?.heat_index_c == null
                      ? 'Heat Index not applicable'
                      : `${riskLabel(currentRisk.risk_level)} · Heat Index ${currentRisk.heat_index_c.toFixed(1)} °C`}
                  </span>
                </div>
                <p className="map-detail-coordinates">
                  {selectedCity.latitude.toFixed(3)}°, {selectedCity.longitude.toFixed(3)}°
                </p>
              </>
            ) : (
              <p className="map-detail-message">Current conditions are not available.</p>
            )}
          </SurfaceCard>
        </aside>
      </div>

      <p className="map-disclaimer">
        Heat Index values are informational estimates, not official warnings or
        medical advice. Follow local emergency guidance.
      </p>
    </div>
  )
}

export default MapPage
