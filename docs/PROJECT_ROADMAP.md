# HeatWatch Project Roadmap

## Project

HeatWatch is an educational Django REST Framework and React application for
weather monitoring, indicative heat-risk assessment, forecasts, maps, alerts,
and application-collected weather history. It is not an official emergency
warning service. SQLite is the primary database and Open-Meteo is the weather data provider.

## Phase 0 — Project Inspection and Planning

- **0.1 Inspect workspace and toolchain** — completed. Confirmed the workspace
  is empty and recorded installed tool versions in `PROGRESS.md`.
- **0.2 Check dependency and runtime compatibility** — completed. Python 3.11
  supports the Django 5.2 LTS line; Django 6.1 requires Python 3.12 or newer.
  Node 24 satisfies Vite 8 and React Router 7 runtime requirements. See
  `PROGRESS.md` for checked package metadata and sources.
- **0.3 Finalize architecture and implementation breakdown** — completed.
  Architecture, data flow, persistence intent, API boundary, and verification
  strategy are recorded in `ARCHITECTURE.md`.

## Phase 1 — Project Initialization

- **1.1 Create backend project structure** — completed. Created the empty
  `backend/config`, `backend/weather`, `backend/alerts`, and `backend/tests`
  directories. No project code or dependencies were added.
- **1.2 Create backend virtual environment** — completed. Created and verified
  `backend/.venv` with Python 3.11.4 and pip available inside the environment.
  No project dependencies were installed.
- **1.3 Install and record backend dependencies** — completed. Pinned Django,
  Django REST framework, django-cors-headers, and Requests in
  `backend/requirements.txt`; installed in `backend/.venv` and verified with
  package metadata and `pip check`.
- **1.4 Initialize Django project and backend apps** — completed. Generated the
  `config` project package and `manage.py`, plus the `weather` and `alerts`
  Django app scaffolds in their existing directories. Django checks passed.
- **1.5 Configure SQLite, environment settings, and CORS** — completed.
  Settings require a secret from the environment, load `backend/.env` when
  present, default debug off, configure local hosts/CORS origins, register the
  project apps, and retain SQLite. `.env.example` and root ignore rules are in
  place.
- **1.6 Verify Django configuration and development server** — completed.
  Django system check and CORS preflight passed; the development server
  responded with HTTP 200 on the Django Admin sign-in page and was stopped
  after the smoke test. A test-created empty SQLite file was removed.
- **1.7 Initialize React/Vite frontend and dependencies** — completed. Created
  the Vite/React scaffold, installed the planned routing, HTTP, UI, chart, and
  map libraries, named the document HeatWatch, and verified lint, build, and
  dependency audit.
- **1.8 Configure frontend API base URL and routing** — completed. Added an
  environment-configurable Axios client, Vite `/api` development proxy,
  React Router root/not-found routes, and the frontend environment template.
- **1.9 Verify frontend production build** — completed. Lint and production
  builds passed; dev-server HTTP checks confirmed the API defaults and routes.

**Phase 1 — Project Initialization: complete.**

## Phase 2 — Database and Administration

- **2.1 Finalize model fields, relations, and constraints** — completed.
  Finalized denormalized city/country snapshots, timezone-aware timestamps,
  explicit units, numeric validation, indexes, and conditional active-alert
  uniqueness. No saved-location table is needed.
- **2.2 Implement WeatherRecord model and indexes** — completed.
- **2.3 Implement HeatAlert model and duplicate-prevention constraint** —
  completed.
- **2.4 Create and verify SQLite migrations** — completed. Applied the initial
  weather and alert migrations to SQLite and verified migration state.
- **2.5 Register and configure models in Django Admin** — completed. Added
  searchable/filterable record and alert lists plus authorized alert
  deactivation.
- **2.6 Test model validation, persistence, and admin access** — completed.
  Fifteen Django tests pass, including range validation, database constraints,
  active-alert deduplication, and admin authorization/actions.

**Phase 2 — Database and Administration: complete.**

## Phase 3 — Weather API Integration

Integrate Open-Meteo geocoding, current weather, and forecast services with
validated responses and explicit error handling.

- **3.1 Implement Open-Meteo geocoding** — completed. Added city search with
  input validation, normalized location metadata, and explicit no-match and
  provider-error handling.
- **3.2 Implement current-weather retrieval** — completed. Added metric current
  conditions, timezone metadata, range/type validation, and normalized output.
- **3.3 Implement forecast retrieval** — completed. Added configurable 1–16
  day forecasts (five days by default), aligned hourly/daily series, timestamps,
  sunrise/sunset, and response validation.
- **3.4 Test provider behavior and failure handling** — completed. Fourteen
  mocked tests cover valid results, malformed data, invalid input, network
  failures, rate limits, and HTTP/provider errors. Full backend suite: 29 tests
  passed.

**Phase 3 — Weather API Integration: complete.** This phase provides service
functions only; Django REST endpoints, Heat Index calculations, and database
persistence remain in later phases.

## Phase 4 — Heat Index Engine

Implement and test the applicable NOAA Rothfusz Heat Index calculation,
indicative risk categories, input validation, and category-specific safety
recommendations.

- **4.1 Implement Heat Index calculation and applicability** — completed.
  Added the NOAA Rothfusz regression in Fahrenheit with simple-formula
  applicability check, low- and high-humidity adjustments, Celsius output, and
  validation for numeric inputs and supported ranges.
- **4.2 Implement risk classification and recommendations** — completed.
  Added exact category boundaries at 27, 32, 41, and 54 °C plus conservative
  category-specific safety guidance. Not-applicable conditions return no Heat
  Index, risk, or recommendation.
- **4.3 Test calculations, boundaries, and validation** — completed. Ten
  focused tests pass, including the 90 °F/70% RH reference case and regression
  adjustments. The full backend suite passes all 39 tests.

**Phase 4 — Heat Index Engine: complete.** The calculation is a service only;
weather/forecast API integration remains in Phase 5.

## Phase 5 — Django REST APIs

Implement and test city search, current weather, forecast, historical data, and
alert endpoints, including serializers and API validation.

- **5.1 Add validated, read-only weather and alert endpoints** — completed.
  Added versioned routes for geocoding search, current conditions, hourly/daily
  forecasts, paginated history, and active alerts. Current and hourly forecast
  responses include the Phase 4 heat-risk assessment.
- **5.2 Add request/response serializers, filtering, and pagination** —
  completed. Added query serializers for city, coordinates, forecast days, and
  city filters; read-only model serializers; city filtering; and bounded
  page-size pagination.
- **5.3 Test API validation, permissions, and provider error mapping** —
  completed. Sixteen focused API tests cover valid responses, malformed
  requests, upstream errors, pagination/filtering, and public write rejection.
  Full backend suite: 55 tests passed.
- **5.4 Document API contracts** — completed. Added `API_DOCUMENTATION.md`
  with endpoint parameters, response content, pagination, and error statuses.

**Phase 5 — Django REST APIs: complete.** The API exposes current provider data
and reads existing history/alerts; it does not persist observations or generate
alerts.
## Phase 6 — Alert Management

Generate forecast-based alerts, prevent duplicate active alerts, support
activation state, and test alert behavior and administrative controls.

- **6.1 Generate alerts from hourly forecasts** — completed. Added a reusable
  alert service and `generate_heat_alerts` management command. Danger and
  Extreme Danger periods create alerts with timezone-aware forecast times,
  Heat Index values, and safety recommendations.
- **6.2 Refresh and deactivate forecast alerts** — completed. Repeated runs
  update an existing active alert for the same location and forecast period;
  resolved evaluated periods deactivate, while missing measurement or
  unreturned periods do not deactivate existing alerts.
- **6.3 Prevent duplicates and support activation** — completed. Generation is
  transaction-backed and uses the existing conditional unique constraint.
  Django Admin provides active-state editing and the authorized bulk-deactivate
  action; inactive alerts can be replaced by a later forecast refresh.
- **6.4 Test management and document operations** — completed. Nine new alert
  service/command tests cover severity, timezone conversion, refresh,
  deactivation, missing data, duplicate prevention, validation, and command
  integration. The full backend suite passes 64 tests. API documentation now
  includes the management command invocation.

**Phase 6 — Alert Management: complete.** Forecast alert generation is an
explicit management operation; no unauthenticated API endpoint triggers
provider requests or database writes.

## Phase 7 — React Initialization

Initialize the frontend, configure routing and API access, build shared layout
and UI components, and verify a production build.

- **7.1 Build the shared responsive application shell** — completed. Added the
  sticky brand/navigation header, mobile menu, skip link, content outlet, and
  informational footer/disclaimer.
- **7.2 Add route and reusable component foundations** — completed. Added
  dashboard overview, forecast/map/history/alerts/about placeholders, not-found
  route, shared page heading and surface card components, and active navigation
  state. Feature routes remain clearly marked as under development.
- **7.3 Verify accessibility basics and production delivery** — completed.
  Added visible keyboard focus, skip-to-content navigation, semantic landmarks,
  reduced-motion support, responsive styles, and a document description.
  `npm run lint` and `npm run build` pass.

**Phase 7 — React Initialization: complete.** The app shell and shared UI
foundations are ready; feature-specific screens and API integration remain in
Phases 8–12.

## Phase 8 — Dashboard UI

Build the responsive dashboard and connect weather, Heat Index, risk,
recommendation, forecast, and active-alert views to the backend.

## Phase 9 — Forecast Module

Build the hourly and daily forecast experience, charts, forecast risk
classification, and dangerous-period indicators.

## Phase 10 — Interactive Map

Build the Leaflet/OpenStreetMap multi-city risk map, colored markers, popups,
coordinates, and legend without implying that point observations are a regional
heat map.

## Phase 11 — Historical Analytics

Build city filtering, historical charts and records, pagination, and verify
persisted application-collected observations.

## Phase 12 — Alert UI

Build the alert listing with severity, forecast time, and safety instructions,
connected to the alert API.

## Phase 13 — Administration and Permissions

Finalize Django Admin and role-based permissions, and verify that public users
cannot modify protected records or alerts.

## Phase 14 — Integration and Bug Fixing

Verify the integrated backend and frontend, APIs, database, pages, error states,
and edge cases; fix issues found.

## Phase 15 — Security and Quality Audit

Review validation, CORS, Django security settings, permissions, secrets,
dependency configuration, and production/debug settings.

## Phase 16 — Documentation and Final Delivery

Complete setup, API, architecture, database, testing, and limitation
documentation; provide a final report based only on verified results.

## Incremental delivery rule

Complete one small step per user `NEXT` command. After each step, verify the
work, update `PROGRESS.md` and this roadmap, report results, and wait. Do not
begin the next step automatically.

## Phase status

- Phase 0 — Project Inspection and Planning: **complete**.
- Phase 1 — Project Initialization: **complete**.
- Phase 2 — Database and Administration: **complete**.
- Phase 3 — Weather API Integration: **complete**.
- Phase 4 — Heat Index Engine: **complete**.
- Phase 5 — Django REST APIs: **complete**.
- Phase 6 — Alert Management: **complete**.
- Phase 7 — React Initialization: **complete**.
- Phases 8–16: **not started**.
