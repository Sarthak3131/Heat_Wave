import { AlertTriangle, RefreshCw, ShieldCheck } from 'lucide-react'
import { useEffect, useState } from 'react'
import PageHeading from '../components/PageHeading.jsx'
import SurfaceCard from '../components/SurfaceCard.jsx'
import { getAlerts } from '../services/weather.js'

const RISK_LABELS = {
  low: 'Low',
  caution: 'Caution',
  extreme_caution: 'Extreme caution',
  danger: 'Danger',
  extreme_danger: 'Extreme danger',
}

function formatDateTime(value) {
  return new Intl.DateTimeFormat('en-IN', {
    weekday: 'short', day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit',
  }).format(new Date(value))
}

function AlertFilters({ city, onCityChange, onRefresh, onRiskChange, risk }) {
  return (
    <SurfaceCard className="alert-filter-card">
      <label>
        City
        <input maxLength={120} onChange={onCityChange} placeholder="Filter by city" value={city} />
      </label>
      <label>
        Severity
        <select onChange={onRiskChange} value={risk}>
          <option value="">All severities</option>
          {Object.entries(RISK_LABELS).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </label>
      <button onClick={onRefresh} type="button">
        <RefreshCw aria-hidden="true" size={16} /> Refresh
      </button>
    </SurfaceCard>
  )
}

function AlertCard({ alert }) {
  const riskLabel = RISK_LABELS[alert.risk_level] ?? 'Heat risk'
  return (
    <SurfaceCard className="alert-card">
      <div className={`alert-level-marker risk-${alert.risk_level}`} />
      <div>
        <div className="alert-card-heading">
          <div>
            <span className={`history-risk-badge risk-${alert.risk_level}`}>{riskLabel}</span>
            <h2>{[alert.city, alert.country].filter(Boolean).join(', ')}</h2>
          </div>
          <AlertTriangle aria-hidden="true" size={22} />
        </div>
        <p>{alert.message}</p>
        <dl>
          <div><dt>Forecast time</dt><dd>{formatDateTime(alert.forecast_time)}</dd></div>
          <div><dt>Temperature</dt><dd>{Number(alert.temperature_c).toFixed(1)}°C</dd></div>
          <div><dt>Heat Index</dt><dd>{alert.heat_index_c == null ? 'Not applicable' : `${Number(alert.heat_index_c).toFixed(1)}°C`}</dd></div>
          <div><dt>Created</dt><dd>{formatDateTime(alert.created_at)}</dd></div>
        </dl>
        <p className="alert-recommendation"><strong>Safety recommendation:</strong> {alert.recommendation}</p>
      </div>
    </SurfaceCard>
  )
}

function AlertsPage() {
  const [city, setCity] = useState('')
  const [risk, setRisk] = useState('')
  const [refreshToken, setRefreshToken] = useState(0)
  const [state, setState] = useState({ loading: true, error: '', alerts: [] })

  useEffect(() => {
    let cancelled = false
    getAlerts({ ...(city && { city }), ...(risk && { risk_level: risk }) })
      .then((data) => {
        if (!cancelled) setState({ loading: false, error: '', alerts: data.results })
      })
      .catch((error) => {
        if (!cancelled) setState({ loading: false, error: error.response?.data?.detail ?? 'Active alerts are unavailable.', alerts: [] })
      })
    return () => { cancelled = true }
  }, [city, risk, refreshToken])

  function beginLoad(update) {
    setState((current) => ({ ...current, loading: true, error: '' }))
    update()
  }

  return (
    <div className="page-container alerts-page">
      <PageHeading eyebrow="Heatwave alerts" title="Active forecast heat alerts." description="Alerts are based on forecast periods classified as Danger or Extreme Danger. They are informational, not official emergency warnings." />
      <AlertFilters city={city} onCityChange={(event) => beginLoad(() => setCity(event.target.value))} onRefresh={() => beginLoad(() => setRefreshToken((value) => value + 1))} onRiskChange={(event) => beginLoad(() => setRisk(event.target.value))} risk={risk} />
      {state.loading && <p className="dashboard-loading"><span className="loading-spinner" /> Loading alerts…</p>}
      {state.error && <SurfaceCard className="history-error" role="alert">{state.error}</SurfaceCard>}
      {!state.loading && !state.error && state.alerts.length === 0 && (
        <SurfaceCard className="history-status-card"><ShieldCheck aria-hidden="true" size={24} /><div><h2>No active alerts match</h2><p>Check local guidance during extreme heat.</p></div></SurfaceCard>
      )}
      <div className="alerts-list">{state.alerts.map((alert) => <AlertCard alert={alert} key={alert.id} />)}</div>
    </div>
  )
}

export default AlertsPage
