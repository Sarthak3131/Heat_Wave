import {
  AlertTriangle,
  Clock3,
  Cloud,
  CloudDrizzle,
  CloudFog,
  CloudLightning,
  CloudRain,
  CloudSun,
  Droplets,
  MapPin,
  RefreshCw,
  Search,
  ShieldCheck,
  Sun,
  Thermometer,
  Wind,
} from 'lucide-react'
import { lazy, Suspense, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import PageHeading from '../components/PageHeading.jsx'
import SurfaceCard from '../components/SurfaceCard.jsx'
import {
  getActiveAlerts,
  getCurrentWeather,
  getForecast,
  searchCities,
} from '../services/weather.js'

const ForecastChart = lazy(() => import('../components/ForecastChart.jsx'))

const DEFAULT_LOCATION = {
  name: 'New Delhi',
  country: 'India',
  latitude: 28.6139,
  longitude: 77.209,
}

const RISK_LABELS = {
  low: 'Low',
  caution: 'Caution',
  extreme_caution: 'Extreme caution',
  danger: 'Danger',
  extreme_danger: 'Extreme danger',
}

const WEATHER_CODES = [
  { match: (code) => code === 0, label: 'Clear sky', Icon: Sun },
  { match: (code) => [1, 2].includes(code), label: 'Mostly clear', Icon: CloudSun },
  { match: (code) => code === 3, label: 'Overcast', Icon: Cloud },
  { match: (code) => [45, 48].includes(code), label: 'Fog', Icon: CloudFog },
  {
    match: (code) => [51, 53, 55, 56, 57].includes(code),
    label: 'Drizzle',
    Icon: CloudDrizzle,
  },
  {
    match: (code) => [61, 63, 65, 66, 67, 80, 81, 82].includes(code),
    label: 'Rain',
    Icon: CloudRain,
  },
  {
    match: (code) => [71, 73, 75, 77, 85, 86].includes(code),
    label: 'Snow',
    Icon: CloudFog,
  },
  {
    match: (code) => [95, 96, 99].includes(code),
    label: 'Thunderstorm',
    Icon: CloudLightning,
  },
]

function weatherDescription(code) {
  return WEATHER_CODES.find(({ match }) => match(code))?.label ?? 'Conditions'
}

function WeatherIcon({ code, size = 28, ...props }) {
  const Icon =
    WEATHER_CODES.find(({ match }) => match(code))?.Icon ?? CloudSun
  return <Icon aria-hidden="true" size={size} {...props} />
}

function formatLocalTime(value, timezone, options = {}) {
  if (!value) return '—'
  const hasTimezone = /(Z|[+-]\d{2}:\d{2})$/.test(value)
  const [datePart, timePart = '00:00'] = value.split('T')
  const [year, month, day] = datePart.split('-').map(Number)
  const [hour, minute] = timePart.slice(0, 5).split(':').map(Number)
  const wallClockDate = hasTimezone
    ? new Date(value)
    : new Date(Date.UTC(year, month - 1, day, hour, minute))
  return new Intl.DateTimeFormat('en-IN', {
    timeZone: hasTimezone ? timezone || 'UTC' : 'UTC',
    ...options,
  }).format(wallClockDate)
}

function formatDate(value, timezone) {
  if (value && !value.includes('T')) {
    const [year, month, day] = value.split('-').map(Number)
    return new Intl.DateTimeFormat('en-IN', {
      timeZone: 'UTC',
      weekday: 'short',
      day: 'numeric',
      month: 'short',
    }).format(new Date(Date.UTC(year, month - 1, day)))
  }
  return formatLocalTime(value, timezone, {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  })
}

function formatHour(value, timezone) {
  return formatLocalTime(value, timezone, {
    hour: 'numeric',
    minute: '2-digit',
  })
}

function riskClass(riskLevel) {
  return riskLevel ? `risk-${riskLevel}` : 'risk-unavailable'
}

function LoadingLine({ label }) {
  return (
    <div aria-live="polite" className="dashboard-loading">
      <span className="loading-spinner" aria-hidden="true" />
      {label}
    </div>
  )
}

function Metric({ Icon, label, value, unit }) {
  return (
    <div className="weather-metric">
      <span className="metric-icon">
        <Icon aria-hidden="true" size={17} />
      </span>
      <span className="metric-copy">
        <span className="metric-label">{label}</span>
        <strong>{value}{unit && <small>{unit}</small>}</strong>
      </span>
    </div>
  )
}

function CitySearch({ onSelect }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    const searchTerm = query.trim()
    if (!searchTerm) {
      setError('Enter a city name to search.')
      setResults([])
      return
    }

    setSearching(true)
    setError('')
    setResults([])
    try {
      const cities = await searchCities(searchTerm)
      setResults(cities)
      if (cities.length === 0) setError('No matching cities were found.')
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ??
          'City search is unavailable right now. Please try again.',
      )
    } finally {
      setSearching(false)
    }
  }

  function chooseCity(city) {
    onSelect({
      name: city.name,
      country: city.country ?? '',
      admin1: city.admin1 ?? '',
      latitude: city.latitude,
      longitude: city.longitude,
    })
    setQuery('')
    setResults([])
    setError('')
  }

  return (
    <div className="city-search">
      <form className="city-search-form" onSubmit={handleSubmit} role="search">
        <label className="visually-hidden" htmlFor="city-search-input">
          Search for a city
        </label>
        <MapPin aria-hidden="true" className="search-location-icon" size={17} />
        <input
          autoComplete="off"
          id="city-search-input"
          maxLength={100}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search a city"
          value={query}
        />
        <button
          aria-label="Search cities"
          className="search-submit"
          disabled={searching}
          type="submit"
        >
          {searching ? (
            <span className="loading-spinner spinner-small" aria-hidden="true" />
          ) : (
            <Search aria-hidden="true" size={18} />
          )}
        </button>
      </form>
      {error && (
        <p aria-live="polite" className="search-error" role="status">
          {error}
        </p>
      )}
      {results.length > 0 && (
        <ul aria-label="City search results" className="city-results">
          {results.map((city, index) => (
            <li key={`${city.id ?? city.name}-${city.latitude}-${index}`}>
              <button onClick={() => chooseCity(city)} type="button">
                <MapPin aria-hidden="true" size={17} />
                <span>
                  <strong>{city.name}</strong>
                  <small>
                    {[city.admin1, city.country].filter(Boolean).join(', ')}
                  </small>
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function DashboardPage() {
  const [location, setLocation] = useState(DEFAULT_LOCATION)
  const [weather, setWeather] = useState(null)
  const [forecast, setForecast] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(true)
  const [refreshToken, setRefreshToken] = useState(0)

  useEffect(() => {
    let active = true
    async function load() {
      setLoading(true)
      setWeather(null)
      setForecast(null)
      setAlerts([])
      setErrors({})
      const requests = await Promise.allSettled([
        getCurrentWeather(location),
        getForecast(location, 5),
        getActiveAlerts(location.name),
      ])
      if (!active) return
      setWeather(requests[0].status === 'fulfilled' ? requests[0].value : null)
      setForecast(requests[1].status === 'fulfilled' ? requests[1].value : null)
      setAlerts(requests[2].status === 'fulfilled' ? requests[2].value : [])
      setErrors({
        current:
          requests[0].status === 'rejected'
            ? errorMessage(requests[0].reason)
            : '',
        forecast:
          requests[1].status === 'rejected'
            ? errorMessage(requests[1].reason)
            : '',
        alerts:
          requests[2].status === 'rejected'
            ? errorMessage(requests[2].reason)
            : '',
      })
      setLoading(false)
    }
    load()
    return () => {
      active = false
    }
  }, [location, refreshToken])

  const hourlyChart = useMemo(
    () =>
      (forecast?.hourly ?? []).slice(0, 24).map((hour) => ({
        ...hour,
        label: formatHour(hour.time, forecast?.timezone?.name),
        temperature: hour.temperature_c,
      })),
    [forecast],
  )

  const current = weather?.current
  const currentRisk = current?.heat_risk
  const timezone = weather?.timezone?.name ?? forecast?.timezone?.name
  const upcomingAlerts = alerts.slice(0, 3)
  const reloadDashboard = () => setRefreshToken((token) => token + 1)

  return (
    <div className="page-container dashboard-page">
      <PageHeading
        eyebrow="Heat safety, made clearer"
        title="Local weather. Clearer heat guidance."
        description="Understand current conditions and what the forecast may bring."
      >
        <div className="dashboard-toolbar">
          <CitySearch onSelect={setLocation} />
          <button
            aria-label="Refresh weather and alerts"
            className="refresh-button"
            disabled={loading}
            onClick={() => setRefreshToken((token) => token + 1)}
            title="Refresh dashboard"
            type="button"
          >
            <RefreshCw aria-hidden="true" size={17} />
            <span>Refresh</span>
          </button>
        </div>
      </PageHeading>

      <div className="location-strip">
        <MapPin aria-hidden="true" size={17} />
        <strong>{location.name}</strong>
        {location.admin1 && <span>{location.admin1}</span>}
        {location.country && <span>{location.country}</span>}
        {weather && (
          <span className="location-coordinates">
            {weather.latitude.toFixed(2)}°, {weather.longitude.toFixed(2)}°
          </span>
        )}
        {timezone && <span className="timezone-label">{timezone}</span>}
      </div>

      <div className="dashboard-overview-grid">
        <SurfaceCard aria-label="Current weather" className="current-weather-card">
          <div className="card-heading">
            <div>
              <p className="eyebrow">Right now</p>
              <h2>Current conditions</h2>
            </div>
            {current && (
              <span className="observed-time">
                <Clock3 aria-hidden="true" size={14} />
                {formatHour(current.time, timezone)}
              </span>
            )}
          </div>
          {loading && !current ? (
            <LoadingLine label="Loading current conditions…" />
          ) : errors.current ? (
            <ErrorPanel message={errors.current} onRetry={reloadDashboard} />
          ) : current ? (
            <>
              <div className="current-weather-main">
                <WeatherIcon
                  className="current-weather-icon"
                  code={current.weather_code}
                  size={42}
                />
                <div>
                  <div className="current-temperature">
                    {Math.round(current.temperature_c)}
                    <span>°C</span>
                  </div>
                  <p>{weatherDescription(current.weather_code)}</p>
                </div>
              </div>
              <div className="weather-metrics-grid">
                <Metric
                  Icon={Droplets}
                  label="Humidity"
                  value={Math.round(current.relative_humidity_percent)}
                  unit="%"
                />
                <Metric
                  Icon={Thermometer}
                  label="Feels like"
                  value={Math.round(current.apparent_temperature_c)}
                  unit="°C"
                />
                <Metric
                  Icon={Wind}
                  label="Wind"
                  value={Math.round(current.wind_speed_kmh)}
                  unit="km/h"
                />
              </div>
            </>
          ) : (
            <EmptyPanel message="Current weather is not available for this location." />
          )}
        </SurfaceCard>

        <SurfaceCard aria-label="Indicative heat risk" className="risk-card">
          <div className="card-heading">
            <div>
              <p className="eyebrow">Heat Index</p>
              <h2>Indicative heat risk</h2>
            </div>
            <span className="risk-shield">
              <ShieldCheck aria-hidden="true" size={19} />
            </span>
          </div>
          {loading && !current ? (
            <LoadingLine label="Assessing conditions…" />
          ) : errors.current ? (
            <ErrorPanel message={errors.current} onRetry={reloadDashboard} />
          ) : currentRisk ? (
            <div className={`risk-content ${riskClass(currentRisk.risk_level)}`}>
              {currentRisk.heat_index_c == null ? (
                <div className="risk-unavailable-message">
                  <span className="risk-category">Not applicable</span>
                  <p>
                    Conditions are outside the Heat Index calculation’s
                    applicability range.
                  </p>
                </div>
              ) : (
                <>
                  <div className="heat-index-reading">
                    <span>{currentRisk.heat_index_c.toFixed(1)}</span>
                    <small>°C</small>
                  </div>
                  <span className={`risk-category ${riskClass(currentRisk.risk_level)}`}>
                    {RISK_LABELS[currentRisk.risk_level] ?? 'Unclassified'}
                  </span>
                  <div className="risk-scale" aria-label="Indicative risk category">
                    {['low', 'caution', 'extreme_caution', 'danger', 'extreme_danger'].map(
                      (risk) => (
                        <span
                          aria-label={RISK_LABELS[risk]}
                          className={`risk-scale-segment ${risk} ${
                            risk === currentRisk.risk_level ? 'is-selected' : ''
                          }`}
                          key={risk}
                        />
                      ),
                    )}
                  </div>
                  <p className="risk-recommendation">
                    {currentRisk.recommendation}
                  </p>
                </>
              )}
              <p className="risk-footnote">
                Indicative Heat Index — not a medical assessment or official warning.
              </p>
            </div>
          ) : (
            <EmptyPanel message="Heat-risk assessment is not available." />
          )}
        </SurfaceCard>
      </div>

      <div className="dashboard-section-header">
        <div>
          <p className="eyebrow">Looking ahead</p>
          <h2>Forecast and active alerts</h2>
        </div>
        {forecast && (
          <span className="forecast-timezone">
            Times shown in {forecast.timezone.name}
          </span>
        )}
      </div>

      <div className="dashboard-lower-grid">
        <SurfaceCard className="forecast-card">
          <div className="card-heading forecast-card-heading">
            <div>
              <p className="eyebrow">Next 24 hours</p>
              <h2>Temperature outlook</h2>
            </div>
            {forecast && (
              <span className="forecast-current-temp">
                {forecast.forecast_days}-day forecast
              </span>
            )}
          </div>
          {loading && !forecast ? (
            <LoadingLine label="Loading forecast…" />
          ) : errors.forecast ? (
            <ErrorPanel message={errors.forecast} onRetry={reloadDashboard} />
          ) : forecast ? (
            <>
              <div className="chart-legend">
                <span><i className="legend-dot ambient" />Air temperature</span>
                <span><i className="legend-dot apparent" />Feels like</span>
              </div>
              <div
                aria-label="Hourly forecast temperature chart"
                className="forecast-chart"
                role="img"
              >
                <Suspense fallback={<LoadingLine label="Loading chart…" />}>
                  <ForecastChart data={hourlyChart} />
                </Suspense>
              </div>
              <div className="daily-forecast-list">
                {forecast.daily.slice(0, 5).map((day) => (
                  <div className="daily-forecast-item" key={day.date}>
                    <span className="daily-date">{formatDate(day.date, timezone)}</span>
                    <WeatherIcon
                      className="daily-weather-icon"
                      code={day.weather_code}
                      size={18}
                    />
                    <span className="daily-condition">
                      {weatherDescription(day.weather_code)}
                    </span>
                    <span className="daily-temperature">
                      <strong>{day.temperature_max_c == null ? '—' : `${Math.round(day.temperature_max_c)}°`}</strong>
                      <small>{day.temperature_min_c == null ? '—' : `${Math.round(day.temperature_min_c)}°`}</small>
                    </span>
                  </div>
                ))}
              </div>
              <p className="forecast-note">
                Forecast values are estimates. Heat-risk assessments are shown
                for hourly periods where temperature and humidity are available.
              </p>
            </>
          ) : (
            <EmptyPanel message="Forecast is not available for this location." />
          )}
        </SurfaceCard>

        <SurfaceCard className="alerts-card">
          <div className="card-heading">
            <div>
              <p className="eyebrow">Forecast-based</p>
              <h2>Active heat alerts</h2>
            </div>
            <span className="alerts-icon">
              <AlertTriangle aria-hidden="true" size={18} />
            </span>
          </div>
          {loading && alerts.length === 0 && !errors.alerts ? (
            <LoadingLine label="Checking active alerts…" />
          ) : errors.alerts ? (
            <ErrorPanel message={errors.alerts} onRetry={reloadDashboard} />
          ) : upcomingAlerts.length > 0 ? (
            <div className="active-alert-list">
              {upcomingAlerts.map((alert) => (
                <article className="active-alert-item" key={alert.id}>
                  <div className={`alert-level-marker ${riskClass(alert.risk_level)}`} />
                  <div className="active-alert-copy">
                    <div className="active-alert-heading">
                      <strong>{RISK_LABELS[alert.risk_level] ?? 'Heat risk'}</strong>
                      <span>
                        {formatDate(alert.forecast_time, timezone)} ·{' '}
                        {formatHour(alert.forecast_time, timezone)}
                      </span>
                    </div>
                    <p>{alert.message}</p>
                    <small>{alert.recommendation}</small>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-alert-state">
              <span><ShieldCheck aria-hidden="true" size={21} /></span>
              <strong>No active alerts for {location.name}</strong>
              <p>
                Active forecast alerts will appear here when available. Check
                local guidance during extreme heat.
              </p>
            </div>
          )}
          <p className="alert-disclaimer">
            These alerts are informational and are not official emergency warnings.
          </p>
          <Link className="dashboard-alert-link" to="/alerts">
            View alert section
          </Link>
        </SurfaceCard>
      </div>
    </div>
  )
}

function errorMessage(error) {
  return (
    error.response?.data?.detail ??
    'This information is temporarily unavailable. Please try again.'
  )
}

function ErrorPanel({ message, onRetry }) {
  return (
    <div aria-live="polite" className="dashboard-error" role="status">
      <p>{message}</p>
      <button onClick={onRetry} type="button">Try again</button>
    </div>
  )
}

function EmptyPanel({ message }) {
  return <p className="dashboard-empty">{message}</p>
}

export default DashboardPage
