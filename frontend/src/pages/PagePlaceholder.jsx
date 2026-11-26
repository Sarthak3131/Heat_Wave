import { ArrowLeft, Construction } from 'lucide-react'
import { Link } from 'react-router-dom'
import PageHeading from '../components/PageHeading.jsx'
import SurfaceCard from '../components/SurfaceCard.jsx'

function PagePlaceholder({ eyebrow, title, description, phase }) {
  return (
    <div className="page-container placeholder-page">
      <PageHeading eyebrow={eyebrow} title={title} description={description} />
      <SurfaceCard className="placeholder-card">
        <span className="placeholder-icon">
          <Construction aria-hidden="true" size={24} />
        </span>
        <span className="prototype-pill">{phase}</span>
        <h2>This part is still taking shape.</h2>
        <p>
          HeatWatch is being built step by step. This section will become
          available as its features are completed and verified.
        </p>
        <Link className="text-link" to="/">
          <ArrowLeft aria-hidden="true" size={16} /> Back to overview
        </Link>
      </SurfaceCard>
    </div>
  )
}

export default PagePlaceholder
