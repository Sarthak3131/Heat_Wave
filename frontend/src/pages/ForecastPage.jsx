import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  CalendarDays,
  Cloud,
  CloudDrizzle,
  CloudFog,
  CloudLightning,
  CloudRain,
  CloudSun,
  MapPin,
  Search,
  ShieldAlert,
  Sun,
} from 'lucide-react'
import { lazy, Suspense, useEffect, useMemo, useState } from 'react'
import PageHeading from '../components/PageHeading.jsx'
import SurfaceCard from '../components/SurfaceCard.jsx'
import { getForecast, searchCities } from '../services/weather.js'

const ForecastTrendChart = lazy(
  () => import('../components/ForecastTrendChart.jsx'),
)

const DEFAULT_LOCATION = {
  name: 'New Delhi',
  country: 'India',
  latitude: 28.6139,
  longitude: 77.209,
}

const DAYS_OPTIONS = [1, 3, 5, 7, 10, 14]
const EMPTY_HOURLY = []
const RISK_LABELS = {
  low: 'Low',
  caution: 'Caution',
  extreme_caution: 'Extreme caution',
  danger: 'Danger',
  extreme_danger: 'Extreme danger',
}
const RISK_ORDER = ['low', 'caution', 'extreme_caution', 'danger', 'extreme_danger']
const RISK_SCORE = Object.fromEntries(RISK_ORDER.map((risk, index) => [risk, index]))
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

function weatherDetails(code) {
  return WEATHER_CODES.find(({ match }) => match(code)) ?? {
    label: 'Conditions unavailable',
    Icon: CloudSun,
  }
}

function formatForecastTime(value, timezone, options = {}) {
  if (!value) return '—'
  const hasTimezone = /(Z|[+-]\d{2}:\d{2})$/.test(value)
  const timePart = value.includes('T') ? value.slice(11, 16) : '00:00'
  const date = hasTimezone
    ? new Date(value)
    : new Date(`${value.slice(0, 10)}T${timePart}:00Z`)
  return new Intl.DateTimeFormat('en-IN', {
    timeZone: hasTimezone ? timezone || 'UTC' : 'UTC',
    ...options,
  }).format(date)
}

function formatDay(value, timezone) {
  return formatForecastTime(value, timezone, {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  })
}

function formatHour(value, timezone) {
  return formatForecastTime(value, timezone, {
    hour: 'numeric',
    minute: '2-digit',
  })
}

function groupDangerPeriods(hourly) {
  const groups = []
  for (const hour of hourly) {
    const level = hour.heat_risk?.risk_level
    if (!['danger', 'extreme_danger'].includes(level)) continue
    const previous = groups.at(-1)
    if (
      previous &&
      forecastHourDifference(hour.time, previous.last.time) <= 1.5
    ) {
      previous.last = hour
      previous.count += 1
      if (RISK_SCORE[level] > RISK_SCORE[previous.riskLevel]) {
        previous.riskLevel = level
      }
    } else {
      groups.push({
        first: hour,
        last: hour,
        count: 1,
        riskLevel: level,
      })
    }
  }
  return groups
}

function forecastHourDifference(later, earlier) {
  const normalize = (value) =>
    /(Z|[+-]\d{2}:\d{2})$/.test(value) ? value : `${value}Z`
  return (Date.parse(normalize(later)) - Date.parse(normalize(earlier))) / 3600000
}

function CitySearch({ onSelect }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(event) {
    event.preventDefault()
    if (!query.trim()) {
      setResults([])
      setError('Enter a city name to search.')
      return
    }
    setLoading(true)
    setError('')
    setResults([])
    try {
      const cities = await searchCities(query.trim())
      setResults(cities)
      if (!cities.length) setError('No matching cities were found.')
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ??
          'City search is unavailable. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  function choose(city) {
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
    <div className="forecast-city-search">
      <form className="forecast-city-form" onSubmit={submit} role="search">
        <label className="visually-hidden" htmlFor="forecast-city-query">
          Search forecast city
        </label>
        <MapPin aria-hidden="true" size={17} />
        <input
          autoComplete="off"
          id="forecast-city-query"
          maxLength={100}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search a city"
          value={query}
        />
        <button aria-label="Search cities" disabled={loading} type="submit">
          <Search aria-hidden="true" size={17} />
        </button>
      </form>
      {error && <p className="forecast-search-error" role="status">{error}</p>}
      {results.length > 0 && (
        <ul aria-label="City search results" className="forecast-city-results">
          {results.map((city, index) => (
            <li key={`${city.id ?? city.name}-${city.latitude}-${index}`}>
              <button onClick={() => choose(city)} type="button">
                <strong>{city.name}</strong>
                <span>{[city.admin1, city.country].filter(Boolean).join(', ')}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function ForecastPage() {
  const [location, setLocation] = useState(DEFAULT_LOCATION)
  const [days, setDays] = useState(5)
  const [forecast, setForecast] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [page, setPage] = useState(0)
  const [refresh, setRefresh] = useState(0)

  useEffect(() => {
    let active = true
    async function load() {
      setLoading(true)
      setForecast(null)
      setError('')
      setPage(0)
      try {
        const result = await getForecast(location, days)
        if (active) setForecast(result)
      } catch (requestError) {
        if (active) {
          setError(
            requestError.response?.data?.detail ??
              'The forecast is temporarily unavailable. Please try again.',
          )
        }
      } finally {
        if (active) setLoading(false)
      }
    }
    load()
    return () => {
      active = false
    }
  }, [location, days, refresh])

  const timezone = forecast?.timezone?.name
  const hourly = forecast?.hourly ?? EMPTY_HOURLY
  const daily = forecast?.daily ?? []
  const pageCount = Math.max(1, Math.ceil(hourly.length / 24))
  const visibleHours = hourly.slice(page * 24, (page + 1) * 24)
  const chartData = useMemo(
    () =>
      visibleHours.map((hour) => ({
        ...hour,
        label: formatHour(hour.time, timezone),
        temperature: hour.temperature_c,
      })),
    [visibleHours, timezone],
  )
  const dangerPeriods = useMemo(() => groupDangerPeriods(hourly), [hourly])
  const elevatedHours = hourly.filter((hour) =>
    ['extreme_caution', 'danger', 'extreme_danger'].includes(
      hour.heat_risk?.risk_level,
    ),
  ).length

  return (
    <div className="page-container forecast-page">
      <PageHeading
        eyebrow="Plan ahead"
        title="Forecast your heat risk."
        description="Explore hourly conditions, daily outlooks, and periods that may need extra care."
      >
        <CitySearch onSelect={setLocation} />
      </PageHeading>

      <div className="forecast-location-bar">
        <div className="forecast-location-name">
          <MapPin aria-hidden="true" size={17} />
          <strong>{location.name}</strong>
          {location.admin1 && <span>{location.admin1}</span>}
          {location.country && <span>{location.country}</span>}
          {timezone && <small>{timezone}</small>}
        </div>
        <div aria-label="Forecast length" className="forecast-range-control">
          <span>Days</span>
          {DAYS_OPTIONS.map((option) => (
            <button
              aria-pressed={days === option}
              className={days === option ? 'is-selected' : ''}
              key={option}
              onClick={() => setDays(option)}
              type="button"
            >
              {option}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <SurfaceCard className="forecast-state-card" role="status">
          <span className="loading-spinner" aria-hidden="true" />
          <p>Loading {days}-day forecast for {location.name}…</p>
        </SurfaceCard>
      ) : error ? (
        <SurfaceCard className="forecast-state-card forecast-state-error" role="alert">
          <AlertTriangle aria-hidden="true" size={22} />
          <p>{error}</p>
          <button onClick={() => setRefresh((value) => value + 1)} type="button">
            Try again
          </button>
        </SurfaceCard>
      ) : forecast ? (
        <>
          <div className="forecast-summary-grid">
            <SurfaceCard className="forecast-summary-card">
              <span className="forecast-summary-icon"><CalendarDays aria-hidden="true" size={19} /></span>
              <span><small>Forecast coverage</small><strong>{daily.length} days</strong></span>
            </SurfaceCard>
            <SurfaceCard className="forecast-summary-card">
              <span className="forecast-summary-icon"><ShieldAlert aria-hidden="true" size={19} /></span>
              <span><small>Elevated risk hours</small><strong>{elevatedHours}</strong></span>
            </SurfaceCard>
            <SurfaceCard className="forecast-summary-card">
              <span className="forecast-summary-icon"><AlertTriangle aria-hidden="true" size={19} /></span>
              <span><small>Danger periods</small><strong>{dangerPeriods.length}</strong></span>
            </SurfaceCard>
          </div>

          <SurfaceCard className="forecast-main-card">
            <div className="forecast-section-heading">
              <div>
                <p className="eyebrow">Hourly conditions</p>
                <h2>Temperature and indicative heat risk</h2>
                <p>Compare air temperature with provider-reported apparent temperature.</p>
              </div>
              <span className="forecast-timezone-pill">{timezone}</span>
            </div>
            <div className="forecast-chart-legend">
              <span><i className="legend-dot ambient" />Air temperature</span>
              <span><i className="legend-dot apparent" />Feels like</span>
              <span><i className="risk-legend-dot" />Elevated Heat Index risk</span>
            </div>
            <div aria-label={`Hourly forecast chart for ${location.name}`} className="forecast-full-chart" role="img">
              <Suspense fallback={<div className="forecast-chart-loading">Loading chart…</div>}>
                <ForecastTrendChart data={chartData} />
              </Suspense>
            </div>
            <div
              aria-label="Hourly heat-risk classifications"
              className="hourly-risk-list"
              role="list"
            >
              {visibleHours.map((hour) => {
                const risk = hour.heat_risk?.risk_level
                const label = risk ? RISK_LABELS[risk] : 'Not applicable'
                return (
                  <div
                    aria-label={`${formatHour(hour.time, timezone)}: ${label}`}
                    className={`hourly-risk-item ${risk ? `risk-${risk}` : 'risk-unavailable'}`}
                    key={hour.time}
                    role="listitem"
                    title={`${formatHour(hour.time, timezone)}: ${label}`}
                  >
                    <span className="hourly-risk-time">{formatHour(hour.time, timezone)}</span>
                    <span className="hourly-risk-meter" />
                    <span className="hourly-risk-name">{label}</span>
                    {hour.heat_risk?.heat_index_c != null && (
                      <strong>{hour.heat_risk.heat_index_c.toFixed(1)}°</strong>
                    )}
                  </div>
                )
              })}
            </div>
            <div className="forecast-page-controls">
              <button
                aria-label="Previous 24 hours"
                disabled={page === 0}
                onClick={() => setPage((value) => Math.max(0, value - 1))}
                type="button"
              >
                <ArrowLeft aria-hidden="true" size={16} /> Previous 24 hours
              </button>
              <span>
                {formatDay(visibleHours[0]?.time, timezone)} –{' '}
                {formatDay(visibleHours.at(-1)?.time, timezone)} · Day {page + 1} of {pageCount}
              </span>
              <button
                aria-label="Next 24 hours"
                disabled={page >= pageCount - 1}
                onClick={() => setPage((value) => Math.min(pageCount - 1, value + 1))}
                type="button"
              >
                Next 24 hours <ArrowRight aria-hidden="true" size={16} />
              </button>
            </div>
          </SurfaceCard>

          <SurfaceCard className="danger-periods-card">
            <div className="forecast-section-heading">
              <div>
                <p className="eyebrow">Periods to watch</p>
                <h2>Higher-risk forecast windows</h2>
              </div>
              <span className="danger-period-count">{dangerPeriods.length} periods</span>
            </div>
            {dangerPeriods.length ? (
              <div className="danger-period-list">
                {dangerPeriods.map((period) => (
                  <article
                    className={`danger-period-item ${period.riskLevel}`}
                    key={`${period.first.time}-${period.last.time}`}
                  >
                    <span className="danger-period-icon">
                      <AlertTriangle aria-hidden="true" size={18} />
                    </span>
                    <div className="danger-period-copy">
                      <strong>{RISK_LABELS[period.riskLevel]}</strong>
                      <span>
                        {formatDay(period.first.time, timezone)} ·{' '}
                        {formatHour(period.first.time, timezone)}
                        {period.count > 1 && `–${formatHour(period.last.time, timezone)}`}
                      </span>
                    </div>
                    <p>
                      Peak Heat Index{' '}
                      {Math.max(
                        ...hourly
                          .filter(
                            (hour) =>
                              hour.time >= period.first.time &&
                              hour.time <= period.last.time,
                          )
                          .map((hour) => hour.heat_risk.heat_index_c ?? -Infinity),
                      ).toFixed(1)} °C
                    </p>
                    <span className="danger-period-hours">
                      {period.count} {period.count === 1 ? 'hour' : 'hours'}
                    </span>
                  </article>
                ))}
              </div>
            ) : (
              <div className="no-danger-periods">
                <span><ShieldAlert aria-hidden="true" size={21} /></span>
                <div>
                  <strong>No Danger-level periods identified</strong>
                  <p>
                    No forecast hours in the Danger or Extreme Danger categories
                    were returned. Conditions can change; check updated forecasts
                    and local guidance.
                  </p>
                </div>
              </div>
            )}
          </SurfaceCard>

          <SurfaceCard className="daily-forecast-card">
            <div className="forecast-section-heading">
              <div>
                <p className="eyebrow">Day by day</p>
                <h2>Daily outlook</h2>
              </div>
              <span className="daily-risk-note">
                Daily Heat Index is unavailable without daily humidity data.
              </span>
            </div>
            <div className="daily-forecast-table">
              {daily.map((day) => {
                const { Icon, label } = weatherDetails(day.weather_code)
                return (
                  <div className="forecast-day-row" key={day.date}>
                    <strong className="forecast-day-name">{formatDay(day.date, timezone)}</strong>
                    <span className="forecast-day-condition">
                      <Icon aria-hidden="true" size={19} />
                      {label}
                    </span>
                    <span className="forecast-day-sunrise">
                      <Sun aria-hidden="true" size={15} />
                      {formatHour(day.sunrise, timezone)}
                      <small>Sunrise</small>
                    </span>
                    <span className="forecast-day-sunset">
                      <Sun aria-hidden="true" size={15} />
                      {formatHour(day.sunset, timezone)}
                      <small>Sunset</small>
                    </span>
                    <span className="forecast-day-temperatures">
                      <strong>{day.temperature_max_c == null ? '—' : `${Math.round(day.temperature_max_c)}°`}</strong>
                      <span>{day.temperature_min_c == null ? '—' : `${Math.round(day.temperature_min_c)}°`}</span>
                    </span>
                  </div>
                )
              })}
            </div>
          </SurfaceCard>
        </>
      ) : null}

      <p className="forecast-disclaimer">
        Forecasts are estimates. Heat Index categories are indicative only, not
        official warnings or medical advice. Follow local emergency guidance.
      </p>
    </div>
  )
}

export default ForecastPage
