import { LogIn } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeading from '../components/PageHeading.jsx'
import SurfaceCard from '../components/SurfaceCard.jsx'
import { login } from '../services/auth.js'

function LoginPage() {
  const [username, setUsername] = useState(''); const [password, setPassword] = useState(''); const [error, setError] = useState(''); const [loading, setLoading] = useState(false); const navigate = useNavigate()
  async function submit(event) { event.preventDefault(); setLoading(true); setError(''); try { await login(username, password); navigate('/') } catch (requestError) { setError(requestError.response?.data?.detail ?? 'Sign in is unavailable. Please try again.') } finally { setLoading(false) } }
  return <div className="page-container login-page"><PageHeading eyebrow="Account access" title="Sign in to HeatWatch." description="Regular users can view information. Staff accounts can manage alert records in Django Admin." /><SurfaceCard className="login-card"><form onSubmit={submit}><label>Username<input autoComplete="username" onChange={(e) => setUsername(e.target.value)} required value={username} /></label><label>Password<input autoComplete="current-password" onChange={(e) => setPassword(e.target.value)} required type="password" value={password} /></label>{error && <p className="history-error" role="alert">{error}</p>}<button disabled={loading} type="submit"><LogIn aria-hidden="true" size={17} /> {loading ? 'Signing in…' : 'Sign in'}</button></form></SurfaceCard></div>
}
export default LoginPage
