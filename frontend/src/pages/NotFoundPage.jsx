import { Link } from 'react-router-dom'
import PageHeading from '../components/PageHeading.jsx'
import SurfaceCard from '../components/SurfaceCard.jsx'

function NotFoundPage() {
  return (
    <div className="page-container placeholder-page">
      <PageHeading eyebrow="Page not found" title="We couldn’t find that page." />
      <SurfaceCard className="placeholder-card">
        <p>The address may be out of date, or the page may have moved.</p>
        <Link className="text-link" to="/">
          Return to HeatWatch
        </Link>
      </SurfaceCard>
    </div>
  )
}

export default NotFoundPage
