import { Database, RefreshCw, Search } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import PageHeading from '../components/PageHeading.jsx'
import SurfaceCard from '../components/SurfaceCard.jsx'
import { getHistoricalAnalytics, getHistoricalRecords } from '../services/weather.js'

const risks = ['low', 'caution', 'extreme_caution', 'danger', 'extreme_danger']
const labels = { low: 'Low', caution: 'Caution', extreme_caution: 'Extreme caution', danger: 'Danger', extreme_danger: 'Extreme danger', not_applicable: 'Not applicable' }
const number = (value, unit = '') => value == null ? '—' : `${Number(value).toFixed(1)}${unit}`
const date = (value) => new Intl.DateTimeFormat('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: '2-digit' }).format(new Date(value))

function RiskBadge({ risk }) { return <span className={`history-risk-badge risk-${risk || 'unavailable'}`}>{labels[risk] ?? labels.not_applicable}</span> }
function Statistic({ label, value, unit }) { return <div className="history-stat-card"><span>{label}</span><strong>{number(value, unit)}</strong></div> }
function Trend({ title, field, color, suffix, data }) {
  return <SurfaceCard className="history-chart-card"><h2>{title}</h2><div className="history-chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={data} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}><CartesianGrid stroke="#e6e8ed" strokeDasharray="3 3" /><XAxis dataKey="label" fontSize={11} tickLine={false} /><YAxis fontSize={11} tickLine={false} width={42} /><Tooltip formatter={(value) => number(value, suffix)} /><Legend /><Line dataKey={field} name={title.replace(' trend', '')} stroke={color} strokeWidth={2.5} dot={false} type="monotone" /></LineChart></ResponsiveContainer></div></SurfaceCard>
}

function HistoricalAnalyticsPage() {
  const [filters, setFilters] = useState({ city: '', start_date: '', end_date: '', risk_level: '' })
  const [applied, setApplied] = useState(filters)
  const [page, setPage] = useState(1)
  const [state, setState] = useState({ loading: true, error: '', records: null, summary: null })
  useEffect(() => {
    let cancelled = false
    const params = Object.fromEntries(Object.entries(applied).filter(([, value]) => value))
    Promise.all([getHistoricalRecords({ ...params, page, page_size: 50 }), getHistoricalAnalytics(params)])
      .then(([records, summary]) => { if (!cancelled) setState({ loading: false, error: '', records, summary }) })
      .catch((error) => { if (!cancelled) setState({ loading: false, error: error.response?.data?.detail ?? 'Historical records are unavailable. Please try again.', records: null, summary: null }) })
    return () => { cancelled = true }
  }, [applied, page])
  const data = useMemo(() => (state.records?.results ?? []).slice().reverse().map((record) => ({ ...record, label: new Intl.DateTimeFormat('en-IN', { day: 'numeric', month: 'short' }).format(new Date(record.recorded_at)), temperature: Number(record.temperature_c), humidity: Number(record.humidity_percent), heatIndex: record.heat_index_c == null ? null : Number(record.heat_index_c) })), [state.records])
  const summary = state.summary
  const totalPages = Math.max(1, Math.ceil((state.records?.count ?? 0) / 50))
  function apply(event) { event.preventDefault(); setPage(1); setState((current) => ({ ...current, loading: true })); setApplied(filters) }
  function reset() { const empty = { city: '', start_date: '', end_date: '', risk_level: '' }; setFilters(empty); setApplied(empty); setPage(1) }
  return <div className="page-container history-page"><PageHeading eyebrow="Historical analytics" title="Review collected weather observations." description="HeatWatch only analyses observations stored by this application; it does not create a meteorological archive." />
    <SurfaceCard className="history-filter-card"><form className="history-filter-form" onSubmit={apply}><label>City<input maxLength={120} onChange={(e) => setFilters({ ...filters, city: e.target.value })} placeholder="Any city" value={filters.city} /></label><label>From<input type="date" onChange={(e) => setFilters({ ...filters, start_date: e.target.value })} value={filters.start_date} /></label><label>To<input type="date" onChange={(e) => setFilters({ ...filters, end_date: e.target.value })} value={filters.end_date} /></label><label>Risk<select onChange={(e) => setFilters({ ...filters, risk_level: e.target.value })} value={filters.risk_level}><option value="">All categories</option>{risks.map((risk) => <option key={risk} value={risk}>{labels[risk]}</option>)}</select></label><button className="history-filter-button" type="submit"><Search aria-hidden="true" size={16} /> Apply</button><button className="history-reset-button" onClick={reset} type="button"><RefreshCw aria-hidden="true" size={16} /> Reset</button></form></SurfaceCard>
    {state.loading && <SurfaceCard className="history-status-card" role="status"><span className="loading-spinner" aria-hidden="true" /> Loading stored observations…</SurfaceCard>}
    {state.error && !state.loading && <SurfaceCard className="history-status-card history-error" role="alert">{state.error}</SurfaceCard>}
    {!state.loading && !state.error && summary?.total_observations === 0 && <SurfaceCard className="history-status-card history-empty"><Database aria-hidden="true" size={24} /><div><h2>No collected observations match these filters</h2><p>Historical analytics will appear after HeatWatch records weather observations.</p></div></SurfaceCard>}
    {!state.loading && !state.error && summary?.total_observations > 0 && <><div className="history-stats-grid"><Statistic label="Observations" value={summary.total_observations} /><Statistic label="Average temperature" value={summary.average_temperature_c} unit="°C" /><Statistic label="Minimum temperature" value={summary.minimum_temperature_c} unit="°C" /><Statistic label="Maximum temperature" value={summary.maximum_temperature_c} unit="°C" /><Statistic label="Average humidity" value={summary.average_humidity_percent} unit="%" /><Statistic label="Maximum Heat Index" value={summary.maximum_heat_index_c} unit="°C" /></div><div className="history-charts-grid"><Trend title="Heat Index trend" field="heatIndex" color="#d95d39" suffix="°C" data={data} /><Trend title="Temperature trend" field="temperature" color="#216869" suffix="°C" data={data} /><Trend title="Humidity trend" field="humidity" color="#3d7ea6" suffix="%" data={data} /></div><SurfaceCard className="history-distribution-card"><h2>Risk-level distribution</h2><div className="history-distribution">{[...risks, 'not_applicable'].map((risk) => <div key={risk}><RiskBadge risk={risk === 'not_applicable' ? null : risk} /><strong>{summary.risk_level_distribution[risk]}</strong></div>)}</div></SurfaceCard><SurfaceCard className="history-records-card"><div className="history-records-heading"><div><p className="eyebrow">Stored records</p><h2>Observation history</h2></div><span>{state.records.count} matching records</span></div><div className="history-table-wrap"><table><thead><tr><th>Observed</th><th>City</th><th>Temperature</th><th>Humidity</th><th>Heat Index</th><th>Risk</th></tr></thead><tbody>{state.records.results.map((record) => <tr key={record.id}><td>{date(record.recorded_at)}</td><td>{[record.city, record.country].filter(Boolean).join(', ')}</td><td>{number(record.temperature_c, '°C')}</td><td>{number(record.humidity_percent, '%')}</td><td>{number(record.heat_index_c, '°C')}</td><td><RiskBadge risk={record.risk_level} /></td></tr>)}</tbody></table></div>{totalPages > 1 && <div className="history-pagination"><button disabled={page === 1} onClick={() => setPage(page - 1)} type="button">Previous</button><span>Page {page} of {totalPages}</span><button disabled={page === totalPages} onClick={() => setPage(page + 1)} type="button">Next</button></div>}</SurfaceCard></>}
  </div>
}
export default HistoricalAnalyticsPage
