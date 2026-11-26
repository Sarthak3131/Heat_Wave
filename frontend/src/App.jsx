import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import AppLayout from './components/AppLayout.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import PagePlaceholder from './pages/PagePlaceholder.jsx'
import NotFoundPage from './pages/NotFoundPage.jsx'

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
        element: (
          <PagePlaceholder
            eyebrow="Forecast"
            title="Plan ahead for the heat."
            description="Hourly and daily forecast insights will appear here."
            phase="Phase 9"
          />
        ),
      },
      {
        path: '/map',
        element: (
          <PagePlaceholder
            eyebrow="City map"
            title="Explore local conditions."
            description="City-level weather and heat-risk locations will appear here."
            phase="Phase 10"
          />
        ),
      },
      {
        path: '/history',
        element: (
          <PagePlaceholder
            eyebrow="History"
            title="Review recorded conditions."
            description="Weather observations collected by HeatWatch will appear here."
            phase="Phase 11"
          />
        ),
      },
      {
        path: '/alerts',
        element: (
          <PagePlaceholder
            eyebrow="Alerts"
            title="Stay informed about forecast risk."
            description="Active forecast-based heat alerts will appear here."
            phase="Phase 12"
          />
        ),
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
