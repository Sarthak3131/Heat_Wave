# HeatWatch Progress

## Current position

- **Current phase:** Phase 10 — Interactive Map
- **Current step:** Phase 10 complete; Phase 11 — Historical Analytics is next
- **Status:** Phases 0–10 complete

## Completed

- **Phase 0, Step 0.1:** Inspected `E:\LPU live\Project\Heat_Wave`; it contains
  no visible or hidden items. No existing project files were overwritten.
- Recorded the available toolchain:
  - Python 3.11.4
  - pip 23.1.2
  - Node.js v24.14.0
  - npm 11.7.0
  - Git 2.43.0.windows.1
  - curl 8.23.0
  - `sqlite3` command-line utility not found
- Created the initial roadmap and progress tracker.
- **Phase 0, Step 0.2:** Checked package metadata and runtime requirements
  without installing packages or creating application files.
  - Python 3.11.4 is compatible with Django 5.2; Django 6.1.3 requires Python
    3.12 or newer. The latest Django 5.2 patch shown by the configured package
    index is 5.2.19. Prefer the latest maintained Python 3.11 patch when
    setting up the project because Django officially supports the latest
    micro-release in each Python series.
  - Django REST framework 3.18.3 requires Python >=3.10 and Django >=5.2;
    `django-cors-headers` 4.9.0 requires Python >=3.9 and Django >=4.2;
    Requests 2.34.2 requires Python >=3.10. These requirements align with
    Python 3.11 and Django 5.2.
  - Node.js 24.14.0 satisfies Vite 8.3.8's `^20.19.0 || >=22.12.0` requirement
    and React Router DOM 7.18.7's Node >=20 requirement.
  - React Leaflet 5.0.0 peers with React/React DOM 19 and Leaflet ^1.9;
    registry metadata for React 19.3.1 and Leaflet 1.9.4 aligns. Recharts
    3.11.1 requires Node >=18. The queried Bootstrap 5.3.9, Axios 1.21.1, and
    Lucide React 1.81.0 packages showed no conflicting runtime constraint.
  - Python's SQLite runtime is 3.42.0; no separate SQLite installation is
    indicated by the compatibility checks.
- Compatibility sources checked on 2026-11-26:
  - [Django 6.0 release notes](https://docs.djangoproject.com/en/6.0/releases/6.0/)
    and [Django installation FAQ](https://docs.djangoproject.com/en/6.0/faq/install/)
  - [Django REST framework](https://www.django-rest-framework.org/)
    and its [3.16 announcement](https://www.django-rest-framework.org/community/3.16-announcement/)
  - [Vite guide](https://vite.dev/guide/),
    [React Router](https://reactrouter.com/), and
    [React Leaflet installation](https://react-leaflet.js.org/docs/start-installation/)
  - PyPI and npm registry package metadata queried directly for the versions
    recorded above.
- **Phase 0, Step 0.3:** Finalized the planned application boundaries, request
  and data flow, initial persistence model, public/admin API boundary,
  configuration and error handling principles, heat-risk semantics, testing
  strategy, and implementation order in `ARCHITECTURE.md`. No application
  implementation was started.
- **Phase 1, Step 1.1:** Re-inspected the workspace, then created the empty
  `backend`, `backend/config`, `backend/weather`, `backend/alerts`, and
  `backend/tests` directories. Verified each directory exists and confirmed no
  files were created inside the backend. No virtual environment, packages, or
  Django project were created.
- **Phase 1, Step 1.2:** Confirmed neither `backend/.venv` nor
  `backend/venv` existed, then created `backend/.venv` with Python's built-in
  `venv` module. Verified the environment interpreter is Python 3.11.4, its
  `sys.prefix` points to `backend/.venv`, and pip is available inside it. No
  project dependencies were installed.
- **Phase 1, Step 1.3:** Created `backend/requirements.txt` with pinned
  versions of Django 5.2.19, Django REST framework 3.18.3,
  django-cors-headers 4.9.0, and Requests 2.34.2. Installed them into
  `backend/.venv`. Verified all four installed versions using Python package
  metadata/imports and confirmed `pip check` reports no broken requirements.
  Transitive dependencies were resolved by pip. No Django project or app code
  was created.
- **Phase 1, Step 1.4:** Generated the Django `config` project package and
  `backend/manage.py`, and scaffolded the `weather` and `alerts` apps with
  Django's `startapp` command. Verified project and app files, ran Django's
  system check (no issues), ran test discovery (0 tests found; no project tests
  exist yet), and compiled Python sources successfully. Removed generated
  project `__pycache__` artifacts after verification. SQLite, CORS, environment
  configuration, and app registration remain for Step 1.5.
- **Phase 1, Step 1.5:** Replaced the generated insecure settings key with a
  required `DJANGO_SECRET_KEY`; configured `.env` loading and environment
  overrides, `DEBUG` defaulting to false, local allowed hosts, explicit
  localhost CORS origins, CORS middleware ordering, app registration, SQLite,
  and the `Asia/Kolkata` timezone. Added `backend/.env.example`, root
  `.gitignore` rules for local secrets, virtual environments, caches, SQLite,
  and frontend build output, and pinned/installed `python-dotenv` 1.2.4.
  Settings assertions, missing-secret rejection, Django system check, and pip
  dependency consistency all passed. No database or real secret was created.
- **Phase 1, Step 1.6:** Since `backend/.env` did not exist, generated a
  local-only Django development secret and enabled debug only in that ignored
  local configuration. Verified its required values without displaying the
  secret, ran `manage.py check` with no issues, and verified a CORS preflight
  for the configured frontend origin. Started the server on
  `127.0.0.1:8000`; `/admin/login/` returned HTTP 200 and rendered the Django
  Admin sign-in page. Stopped the server after the smoke test. Django created
  an empty SQLite file during the check; confirmed it was 0 bytes and test-
  generated, then removed it. No migrations or application tests were run.
  The root `.gitignore` includes `backend/.env`; this workspace has no Git
  repository, so Git's `check-ignore` could not be used to verify exclusion.
- **Phase 1, Step 1.7:** Confirmed the `frontend` path did not exist, then
  scaffolded it with Vite's React template (`create-vite` 9.3.4; Vite 8.3.8).
  Installed React 19.3.1, React DOM 19.3.1, React Router DOM 7.18.7, Axios
  1.21.1, Lucide React 1.81.0, Bootstrap 5.3.9, Recharts 3.11.1, Leaflet
  1.9.4, and React Leaflet 5.0.0. npm generated and installed the lockfile.
  Changed the default HTML document title to HeatWatch. `npm run lint`,
  `npm run build`, and `npm audit --audit-level=moderate` all passed; audit
  reported zero vulnerabilities. The generated scaffold is not yet wired to
  backend APIs or routes; that is the next step. A first scaffolder command
  used the Vite runtime package version for the separate scaffolder package and
  failed before creating files; retried successfully with the published
  `create-vite` version.
- **Phase 1, Step 1.8:** Replaced the Vite demo screen with an honest HeatWatch
  project landing page and a router not-found route. Added the Axios client in
  `frontend/src/services/api.js` with environment-configurable
  `VITE_API_BASE_URL` (default `/api/v1`), JSON accept header, and 10-second
  request timeout. Added Vite `/api` development proxy configuration, default
  backend target, `frontend/.env.example`, and Bootstrap CSS entry. No API
  endpoints or monitoring features are claimed or implemented.
- **Phase 1, Step 1.9:** Ran `npm run lint` and `npm run build`; both passed.
  `npm audit --audit-level=moderate` reported zero vulnerabilities. Started
  Vite on port 5174 because port 5173 was already occupied; HTTP checks
  confirmed the HeatWatch document title, Axios base path and timeout, React
  Router root and catch-all route modules, and global styles all served
  successfully. Stopped the dev server and confirmed the port was released.
  The production build output exists in ignored `frontend/dist`.
- **Phase 1 complete:** Backend project and environment initialized, frontend
  initialized, and both Django and frontend setup verified. No product modules
  beyond the introductory frontend route are implemented.
- **Phase 2, Step 2.1:** Finalized a denormalized city/country and coordinate
  snapshot for weather records and alerts, with no separate SavedLocation
  table. Chose timezone-aware observation/forecast timestamps, explicit Celsius
  and percent fields, nullable Heat Index values, and shared indicative risk
  categories. Defined coordinate, temperature, humidity, Heat Index, and risk
  validation; city/time and risk/time indexes; active/forecast index; and
  uniqueness for an active city/country/forecast timestamp.
- **Phase 2, Steps 2.2–2.3:** Implemented `WeatherRecord` and `HeatAlert` with
  field validators, database check constraints, useful indexes, ordering,
  location trimming/validation, and the conditional unique constraint that
  allows a replacement alert after deactivation.
- **Phase 2, Step 2.4:** Generated `weather.0001_initial` and
  `alerts.0001_initial`, applied all migrations to the project SQLite database,
  verified both app migrations are applied, and confirmed
  `makemigrations --check --dry-run` reports no model changes.
- **Phase 2, Step 2.5:** Registered both models in Django Admin. Weather records
  support city/country search, risk/time filters, and date navigation. Alerts
  support city/country/message search, active/risk/time filters, status editing,
  and a staff change-permission-protected deactivate action.
- **Phase 2, Step 2.6:** Added 15 focused Django tests covering persistence,
  location normalization, bounds validation, database constraints, indexes,
  active-alert duplicate prevention/replacement, admin access restrictions,
  superuser access, and alert deactivation. Full backend test suite passed.
- **Phase 2 complete:** Database schema, migrations, admin management, and
  focused validation/authorization tests are implemented. Weather provider
  integration and APIs are not implemented yet.
- **Phase 3, Steps 3.1–3.3:** Added `OpenMeteoClient` in
  `backend/weather/services/open_meteo.py`. It searches and normalizes city
  locations, retrieves validated current conditions, and retrieves aligned
  hourly and daily forecasts (five days by default; 1–16 days supported).
  Requests use bounded connect/read timeouts and metric units; results include
  timezone metadata. Invalid caller input, no city match, provider errors, and
  temporary provider/network failures use distinct explicit exceptions.
- **Phase 3, Step 3.4:** Added 14 mocked tests covering geocoding/current/
  forecast results, input and payload validation, array alignment, malformed
  JSON, provider errors, HTTP failures, timeouts, and rate limits. All 14
  focused tests and all 29 backend tests passed; Django system checks passed.
- **Phase 3 complete:** Provider service integration is implemented and tested.
  No REST endpoints, Heat Index calculation, or observation persistence were
  added; these remain later-phase work.
- **Phase 4, Steps 4.1–4.2:** Implemented `calculate_heat_index_c`,
  `risk_level_for_heat_index`, `safety_recommendation_for_risk`, and
  `assess_heat_risk` in `backend/weather/services/heat_index.py`. The
  Rothfusz regression runs in Fahrenheit and converts its result to Celsius;
  the initial simple estimate gates use of the regression at 80 °F, and the
  NOAA low-/high-humidity adjustments are applied. Results are rounded to two
  decimal places. Invalid/non-finite values and out-of-range temperature,
  humidity, or Heat Index inputs raise an explicit validation exception.
  Indicative category boundaries are exactly 27, 32, 41, and 54 °C. Each
  category has conservative safety guidance; not-applicable results contain
  no Heat Index, category, or recommendation.
- **Phase 4, Step 4.3:** Added 10 focused tests for the 90 °F/70% RH reference
  case, applicability, both humidity adjustments, input validation, exact
  category boundaries, recommendations, and combined assessment output.
  Focused tests passed (10); the full backend suite passed (39); Django system
  checks passed. No database migration was needed. Calculation guidance was
  checked against the
  [NOAA Weather Prediction Center Heat Index Equation](https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml).
- **Phase 4 complete:** The independently tested Heat Index/risk service is
  ready for API integration in Phase 5. It does not itself persist data or
  create weather/forecast endpoints.
- **Phase 5, Steps 5.1–5.2:** Added public read-only versioned APIs:
  `GET /api/v1/weather/cities/`, `/weather/current/`, `/weather/forecast/`,
  `/weather/history/`, and `/api/v1/alerts/`. Query serializers validate city
  text, coordinate bounds, forecast days, and city filters. Current conditions
  and hourly forecasts include Heat Index/risk/recommendation results when
  applicable. History and active alerts use a 20-item default page size,
  optional city filtering, and a maximum page size of 100. Model serializers
  return stored history and active alert records.
- **Phase 5, Step 5.3:** Added 16 focused API tests for provider-backed
  responses and error mapping, input validation, heat-risk integration,
  history/alert filtering and pagination, and rejection of public writes.
  Pagination now rejects non-integer and out-of-range page sizes. Focused API
  tests passed (16); full backend suite passed (55); Django system checks
  passed. No database migration was needed.
- **Phase 5, Step 5.4:** Added `docs/API_DOCUMENTATION.md` describing endpoint
  parameters, response content, pagination, and error statuses.
- **Phase 5 complete:** Read-only REST APIs are implemented and tested. History
  and alert endpoints read existing database entries; current weather requests
  do not persist observations, and no alert generation was added.
- **Phase 6, Steps 6.1–6.2:** Implemented `generate_forecast_alerts` in
  `backend/alerts/services.py`. It creates alerts only for forecast hours with
  Danger or Extreme Danger risk, stores temperature, humidity, Heat Index,
  timezone-aware forecast time, and conservative recommendation, refreshes
  existing active alerts without duplicates, and deactivates alerts only when
  returned periods have evaluable measurements and no longer meet the alert
  threshold. Missing or unreturned forecast periods do not deactivate alerts.
- **Phase 6, Step 6.3:** Added the `generate_heat_alerts` Django management
  command for an explicit city/coordinate forecast refresh. The existing
  conditional unique constraint prevents concurrent duplicate active alerts;
  Django Admin keeps activation state editable and supports its protected
  deactivation action. No public API write endpoint or public provider-fetch
  trigger was added.
- **Phase 6, Step 6.4:** Added nine service/management-command tests for
  severity filtering, IANA timezone conversion, idempotent update, forecast
  resolution, preserving unreturned/missing-data periods, replacement after
  deactivation, input validation, and command wiring. Focused alert/admin/
  command tests passed (17); full backend suite passed (64); Django system
  checks passed. No database migration was needed. Added the command example
  and trigger threshold to `docs/API_DOCUMENTATION.md`.
- **Phase 6 complete:** Forecast alerts can be refreshed explicitly per
  location using the documented command. Scheduling recurring runs is not
  configured in this phase.
- **Phase 7, Steps 7.1–7.2:** Replaced the initial standalone landing route with
  a responsive shared app shell, sticky navigation, mobile menu, skip link,
  semantic main/footer, and shared `PageHeading` and `SurfaceCard` components.
  Added a dashboard overview, about page, and named route placeholders for
  forecast, map, history, and alerts; feature pages accurately indicate that
  their feature work is pending.
- **Phase 7, Step 7.3:** Added responsive layout styling, keyboard focus
  visibility, reduced-motion support, prototype/disclaimer messaging, and
  document description metadata. Removed starter styles and the unused
  Bootstrap CSS import so custom component styles are the sole app styling
  foundation. `npm run lint` and `npm run build` both passed.
- **Phase 7 complete:** Shared React routing, layout, and presentation
  primitives are ready for dashboard and feature implementations. This phase
  does not add feature-specific API calls or claim that forecast/map/history/
  alert screens are complete.
- **Phase 8, Steps 8.1–8.3:** Replaced the dashboard overview with a live
  weather dashboard. Added city search and selection, current conditions,
  timezone/local observation time, Heat Index/risk/recommendation, interactive
  hourly ambient/apparent temperature chart, five-day daily outlook, and
  location-filtered active alerts. Added loading, empty, retry/error, and manual
  refresh states; current, forecast, and alert API calls fail independently.
  Weather and alert content remain informational and read-only.
- **Phase 8, Step 8.4:** Verified in the browser against the local Django API
  and Open-Meteo: the default New Delhi location returned current conditions,
  an applicable/not-applicable heat-risk state, five daily forecast rows, and
  an active-alert empty state. City search returned Mumbai; selecting it
  updated location, timezone, weather, risk, and daily forecast without
  endpoint errors. `npm run lint` and `npm run build` passed; the forecast
  chart is lazy-loaded to keep it out of the initial JS chunk.
- **Phase 8 complete:** The dashboard uses existing read APIs only. It does
  not save weather observations or automatically generate alerts.
- **Phase 9, Steps 9.1–9.3:** Replaced the forecast placeholder with a live
  forecast page. Added city search, selectable 1–14 day ranges, hourly
  temperature/apparent-temperature chart, separate per-hour Heat Index risk
  strip, grouped Danger/Extreme Danger periods, daily conditions, and loading,
  error, and retry states. Forecast-local timestamps preserve their provider
  wall-clock values; offset-bearing timestamps are localized using the
  provider timezone.
- **Phase 9, Step 9.4:** Verified live New Delhi forecast data, 24 hourly risk
  entries, five daily rows, and the no-danger-period state. Searched for and
  selected Mumbai, changed the range to 14 days, advanced to day 2, and
  confirmed 24 hourly entries and 14 daily rows. At a mobile viewport, the
  forecast rendered without horizontal overflow or API error. `npm run lint`
  and `npm run build` passed.
- **Phase 9 complete:** The chart presents temperature and apparent
  temperature on a shared Celsius scale; risk categories remain separate and
  are not plotted on that temperature scale. Forecast data remains
  informational and read-only.
- **Phase 10, Steps 10.1–10.3:** Replaced the map placeholder with a
  lazy-loaded Leaflet/OpenStreetMap city map. Added eight initial Indian
  locations, API-backed current temperature and Heat Index risk markers,
  independent per-location loading/error states, refresh, geocoding search to
  add a city, and removal of user-added locations (maximum 12). Marker
  popups include current temperature, applicable risk, and coordinates; a
  selectable city list and details panel, risk counts/legend, and responsive
  layout complete the screen. Added accessible search labels and prominent
  point-data/informational disclaimers.
- **Phase 10, Step 10.4:** Verified all eight live current-weather requests,
  markers, OpenStreetMap tiles, popup values, city selection, search/add/remove
  flow, and narrow-screen layout without horizontal overflow. `npm run lint`
  and `npm run build` passed.
- **Phase 10 complete:** Risk colors represent individual city observations
  returned by the existing API. The map does not spatially interpolate values
  or imply regional coverage.

## Pending

- Phase 0: complete (steps 0.1–0.3).
- Phase 1: complete (steps 1.1–1.9).
- Phase 2: complete (steps 2.1–2.6).
- Phase 3: complete (steps 3.1–3.4).
- Phase 4: complete (steps 4.1–4.3).
- Phase 5: complete (steps 5.1–5.4).
- Phase 6: complete (steps 6.1–6.4).
- Phase 7: complete (steps 7.1–7.3).
- Phase 8: complete (steps 8.1–8.4).
- Phase 9: complete (steps 9.1–9.4).
- Phase 10: complete (steps 10.1–10.4).
- Phases 11–16: not started.

## Verification

- Workspace inventory: passed; confirmed empty, including hidden items.
- Tool availability/version check: passed for the listed available tools.
- Package metadata and runtime requirement checks: passed for Python 3.11,
  Node.js 24, and the planned dependency stack.
- Architecture and tracker documents: reviewed after creation/update.
- Backend structure: all five planned directories exist; no backend files
  created in this step.
- Virtual environment: creation and interpreter/pip verification passed.
- Backend dependencies: pinned manifest reviewed, installed versions verified,
  and dependency consistency check passed.
- Django system check: passed.
- Django test discovery: command passed, but found 0 tests.
- Python syntax compilation: passed; generated project cache files were
  removed afterward.
- Step 1.5 settings checks: passed for SQLite, registered apps, CORS ordering
  and environment overrides, secure defaults, `.env.example`, required-secret
  enforcement, and dependency consistency.
- Step 1.6: `manage.py check` passed; CORS preflight passed; local development
  server responded HTTP 200 at `/admin/login/`; server stopped and generated
  zero-byte SQLite file removed.
- Step 1.7: Vite React scaffold generated; `npm run lint` passed;
  `npm run build` passed; `npm audit --audit-level=moderate` reported zero
  vulnerabilities.
- Step 1.8: Vite-served API and router modules returned HTTP 200; checked the
  configured `/api/v1` default, 10-second timeout, root route, catch-all route,
  and global styles.
- Step 1.9: Final lint/build passed; dependency audit reported zero
  vulnerabilities; dev server stopped after HTTP smoke checks.
- Phase 2: all 15 Django tests passed; `makemigrations --check --dry-run`
  reported no changes; `manage.py check` passed; `pip check` reported no broken
  requirements; both app migrations show applied in SQLite.
- Phase 3: focused Open-Meteo suite passed (14 tests); full backend suite
  passed (29 tests); Django system checks passed. Provider HTTP interactions
  were mocked; no live provider smoke request was made.
- Phase 4: focused Heat Index suite passed (10 tests); full backend suite
  passed (39 tests); Django system checks passed; no migration was required.
- Phase 5: focused API suite passed (16 tests); full backend suite passed (55
  tests); Django system checks passed; migration check reported no changes.
- Phase 6: focused alert generation/admin/command suite passed (17 tests);
  full backend suite passed (64 tests); Django system checks passed; migration
  check reported no changes.
- Phase 7: `npm run lint` passed; `npm run build` passed.
- Phase 8: `npm run lint` passed; `npm run build` passed; browser smoke test
  passed against local frontend/backend with live city search, current weather,
  forecast, risk, and empty-alert state.
- Phase 9: `npm run lint` passed; `npm run build` passed; live browser smoke
  test verified forecast load, hourly risk strip, daily outlook, city search,
  14-day selection, 24-hour pagination, empty danger periods, and responsive
  mobile layout without horizontal overflow.
- Phase 10: `npm run lint` passed; `npm run build` passed; live browser smoke
  test verified eight city observations, map tiles and markers, popup details,
  city selection, geocoding/add/remove flow, and mobile layout without
  horizontal overflow.
- **Checks passed:** Backend directory existence and empty-file checks;
  virtual-environment interpreter and pip checks; installed dependency
  version checks; `pip check`; Django system check; Python syntax compilation;
  CORS preflight; local HTTP smoke test.
- **Application tests:** None exist yet. Two initial ad hoc settings probes
  failed due to verification-command setup/expectation errors (missing
  `DJANGO_SETTINGS_MODULE`, then expecting a blank dotenv value to parse as
  `None`); corrected probes passed, with no application defect found.
- **Tests passed:** 15 Django model/admin tests; 14 Open-Meteo service tests;
  10 Heat Index service tests; 16 API tests; 17 alert/admin/command tests;
  64 tests in the full backend
  suite.
- **Frontend checks passed:** `npm run lint`; `npm run build`.
- **Frontend live smoke test:** New Delhi dashboard data and Mumbai city
  selection refreshed successfully with no API errors.
- **Tests failed:** None in the final Phase 2 run.

## Known issues and notes

- The standalone `sqlite3` CLI is unavailable. Python includes SQLite support;
  database setup and verification can use Django/Python rather than relying on
  that CLI.
- Python 3.11.4 is an older patch release; use the latest maintained 3.11 patch
  when practical.
- Architecture is a design baseline; model constraints and API schemas must be
  confirmed when implemented and tested.
- `backend/.env` contains a locally generated development-only secret and
  `DJANGO_DEBUG=true`; never share or commit it. The `.env.example` template
  intentionally contains no secret. The local env file is not tracked.
- The project SQLite database now contains the applied Django and Phase 2
  migrations; it is local and ignored by `.gitignore`.

## Next recommended action

On the next authorized phase, begin Phase 11 — Historical Analytics.
