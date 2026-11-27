import { lazy, Suspense } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import AppLayout from './components/AppLayout.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import PagePlaceholder from './pages/PagePlaceholder.jsx'
import NotFoundPage from './pages/NotFoundPage.jsx'

const ForecastPage = lazy(() => import('./pages/ForecastPage.jsx'))
const MapPage = lazy(() => import('./pages/MapPage.jsx'))
const HistoricalAnalyticsPage = lazy(() => import('./pages/HistoricalAnalyticsPage.jsx'))
const AlertsPage = lazy(() => import('./pages/AlertsPage.jsx'))
const LoginPage = lazy(() => import('./pages/LoginPage.jsx'))

function LazyPage({ children }) {
  return <Suspense fallback={<div className="page-container dashboard-loading">Loading page…</div>}>{children}</Suspense>
}

const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      {
        path: '/',
        element: <DashboardPage />,
      },
      {
        path: '/forecast',
        element: <LazyPage><ForecastPage /></LazyPage>,
      },
      {
        path: '/map',
        element: <LazyPage><MapPage /></LazyPage>,
      },
      {
        path: '/history',
        element: <LazyPage><HistoricalAnalyticsPage /></LazyPage>,
      },
      {
        path: '/alerts',
        element: <LazyPage><AlertsPage /></LazyPage>,
      },
      {
        path: '/login',
        element: <LazyPage><LoginPage /></LazyPage>,
      },
      {
        path: '/about',
        element: (
          <PagePlaceholder
            eyebrow="About HeatWatch"
            title="A learning project for hotter days."
            description="HeatWatch is an educational prototype, not an official emergency warning service."
            phase="Project information"
          />
        ),
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
])

function App() {
  return <RouterProvider router={router} />
}

export default App
