import {
  createBrowserRouter,
  Link,
  RouterProvider,
} from 'react-router-dom'

function HomePage() {
  return (
    <main className="container min-vh-100 d-flex align-items-center py-5">
      <section className="mx-auto w-100" style={{ maxWidth: '46rem' }}>
        <p className="text-uppercase fw-semibold text-primary mb-2">
          Disaster management | Educational prototype
        </p>
        <h1 className="display-4 fw-bold text-dark">HeatWatch</h1>
        <p className="lead text-secondary">
          Extreme heat monitoring and early warning.
        </p>
        <p className="text-secondary mb-0">
          The application foundation is ready. Weather monitoring, forecasts,
          heat-risk assessments, maps, and alerts will be added in subsequent
          development phases. This prototype is not an official emergency
          warning service.
        </p>
      </section>
    </main>
  )
}

function NotFoundPage() {
  return (
    <main className="container min-vh-100 d-flex align-items-center py-5">
      <section className="mx-auto w-100" style={{ maxWidth: '46rem' }}>
        <p className="text-uppercase fw-semibold text-primary mb-2">
          Page not found
        </p>
        <h1 className="display-5 fw-bold text-dark">
          That page is unavailable.
        </h1>
        <Link className="btn btn-primary mt-3" to="/">
          Return to HeatWatch
        </Link>
      </section>
    </main>
  )
}

const router = createBrowserRouter([
  {
    path: '/',
    element: <HomePage />,
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
])

function App() {
  return <RouterProvider router={router} />
}

export default App
