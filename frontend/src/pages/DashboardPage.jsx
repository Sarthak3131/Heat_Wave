import { ArrowRight, ShieldCheck, Waves } from 'lucide-react'
import { Link } from 'react-router-dom'
import PageHeading from '../components/PageHeading.jsx'
import SurfaceCard from '../components/SurfaceCard.jsx'

function DashboardPage() {
  return (
    <div className="page-container dashboard-page">
      <PageHeading
        eyebrow="Heat safety, made clearer"
        title="Understand the heat. Look out for each other."
        description="A learning-focused view of local weather and heat-risk information."
      >
        <span className="prototype-pill">
          <span className="status-dot" aria-hidden="true" />
          Prototype
        </span>
      </PageHeading>

      <SurfaceCard className="welcome-card">
        <div className="welcome-copy">
          <span className="welcome-icon">
            <Waves aria-hidden="true" size={22} />
          </span>
          <p className="eyebrow">Welcome to HeatWatch</p>
          <h2>Small steps can make a hot day safer.</h2>
          <p>
            HeatWatch brings weather conditions and indicative heat guidance
            together to support awareness. Features are being introduced in
            stages, so this dashboard is currently a project overview.
          </p>
          <Link className="text-link" to="/about">
            Learn about the project <ArrowRight aria-hidden="true" size={16} />
          </Link>
        </div>
        <div className="welcome-visual" aria-hidden="true">
          <div className="sun-orbit orbit-one" />
          <div className="sun-orbit orbit-two" />
          <div className="sun-orb" />
          <div className="visual-caption">Awareness starts with information</div>
        </div>
      </SurfaceCard>

      <div className="section-heading">
        <div>
          <p className="eyebrow">Your heat safety companion</p>
          <h2>What you’ll find here</h2>
        </div>
        <span className="section-note">Features are rolling out in phases</span>
      </div>

      <div className="feature-grid">
        <SurfaceCard className="feature-card">
          <span className="feature-icon icon-weather">
            <Waves aria-hidden="true" size={20} />
          </span>
          <h3>Weather at a glance</h3>
          <p>Current conditions and local forecasts, presented with clear units and context.</p>
          <span className="feature-status">Dashboard features upcoming</span>
        </SurfaceCard>
        <SurfaceCard className="feature-card">
          <span className="feature-icon icon-risk">
            <ShieldCheck aria-hidden="true" size={20} />
          </span>
          <h3>Understand heat risk</h3>
          <p>Indicative Heat Index guidance to help make sense of hot and humid weather.</p>
          <span className="feature-status">Guidance is informational</span>
        </SurfaceCard>
        <SurfaceCard className="feature-card">
          <span className="feature-icon icon-alert">
            <ArrowRight aria-hidden="true" size={20} />
          </span>
          <h3>Stay aware</h3>
          <p>Forecast-based alerts and practical recommendations as features are added.</p>
          <span className="feature-status">Alert views upcoming</span>
        </SurfaceCard>
      </div>

      <SurfaceCard className="notice-card">
        <ShieldCheck aria-hidden="true" size={20} />
        <p>
          <strong>Know what this is — and what it isn’t.</strong>
          HeatWatch is an educational prototype. Its indicative Heat Index and
          forecast information are not official warnings or a substitute for
          local emergency guidance.
        </p>
      </SurfaceCard>
    </div>
  )
}

export default DashboardPage
