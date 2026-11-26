# HeatWatch Architecture

## Status and scope

This document records the intended architecture and implementation status
through Phase 8. Backend provider, Heat Index, API, alert, shared frontend
shell, and live dashboard foundations are implemented; other feature screens
remain planned until their phases are completed.
Changes to this design should be reflected here and in `PROJECT_ROADMAP.md`.

HeatWatch is an educational heat-risk monitoring prototype. Its calculated
Heat Index, indicative categories, forecasts, and alerts are informational;
they are not WBGT measurements or official government warnings.

## Runtime and top-level layout

Keep the browser client and API server independent:

```text
Heat_Wave/
  backend/
    manage.py
    config/           Django settings, root URLs, WSGI/ASGI
    weather/          provider client, calculations, weather API, records
    alerts/           forecast alert generation, API, Django Admin
    locations/        optional saved-location model, if required by the UI
    tests/            focused backend tests where they improve discoverability
    requirements.txt
    .env.example
  frontend/
    src/
      components/     shared layout and reusable presentation
      pages/          dashboard, forecast, map, history, alerts, about
      services/       Axios client and API functions
      hooks/          shared request/state behavior when useful
      App.jsx
      main.jsx
      index.css
    package.json
    index.html
  docs/
    PROJECT_ROADMAP.md
    PROGRESS.md
    ARCHITECTURE.md
    API_DOCUMENTATION.md
    TESTING.md
```

Keep the structure proportionate: add modules only when they have a real
responsibility. Django migrations live in their respective apps. Do not add a
separate database server, Node backend, cache, or container layer.

## Responsibilities and dependencies

- **Django configuration (`config`)** owns environment-based settings, SQLite
  connection, installed apps, CORS policy, root URL routing, and server entry
  points.
- **Weather domain (`weather`)** owns Open-Meteo HTTP access, geocoding/current/
  forecast response validation, Heat Index and risk calculations, read-only
  weather endpoints, and persisted observations. Provider integration,
  Heat-Index/risk services, and read-only endpoints are implemented.
- **Alert domain (`alerts`)** owns forecast-risk alert creation, duplicate
  prevention, active state, public read access, and privileged Django Admin
  management. A transaction-backed service and management command create and
  refresh severe forecast alerts; activation state remains managed through
  Django Admin.
- **Locations (`locations`, optional)** is introduced only if saved/reusable
  locations need their own lifecycle or relations. Otherwise use validated
  geocoding results directly and store a city name and coordinates on records.
- **React frontend** owns navigation, responsive screens, client-side loading
  and error states, visualization, and requests to the configured API base URL.
  The shared app shell and a live dashboard for city search, current weather,
  heat risk, forecast, and active alerts are implemented. Forecast, map,
  history, and dedicated alert screens remain future work.
  An Axios service reads `VITE_API_BASE_URL` (default `/api/v1`); the Vite
  development server proxies `/api` to the configured backend origin. It does
  not reimplement provider access or treat browser-computed values as
  authoritative.
- **Open-Meteo** provides geocoding, current, and forecast data. A server-side
  Requests client keeps provider parsing and network failure handling in one
  place. The validated client is implemented in
  `backend/weather/services/open_meteo.py` and uses bounded request timeouts,
  explicit metric units, timezone metadata, and distinct input/provider/
  availability exceptions. No API key is assumed.
- **SQLite** is the single primary database and Django ORM is the persistence
  boundary. Python's bundled SQLite is sufficient for local development.

## Request and data flow

1. A page asks the shared frontend API service for a city search, current
   conditions, forecast, history, or alerts.
2. Django validates query parameters and calls a domain/service function.
3. Weather services make bounded-timeout requests to Open-Meteo, validate the
   provider payload and units/timezone, and surface provider/network errors as
   explicit service errors. Geocoding, current conditions, hourly/daily
   forecasts, and their read-only API endpoints are implemented and tested.
4. The backend calculates the applicable NOAA Rothfusz Heat Index and
   indicative risk category from ambient temperature and relative humidity.
   The calculation and recommendations are implemented in
   `backend/weather/services/heat_index.py`; no result is returned when the
   initial NOAA applicability estimate is below 80 °F. Apparent temperature
   remains a separately named provider field; neither it nor Heat Index is
   described as WBGT.
5. Current observations selected for persistence are saved as application-
   collected `WeatherRecord` entries with city, coordinates, measurements,
   risk, and observation timestamp. Forecast periods are not silently presented
   as observed history.
6. The `generate_heat_alerts` management command evaluates a location forecast
   and creates or refreshes `HeatAlert` rows for Danger and Extreme Danger
   forecast hours. Resolved alerts are deactivated for returned forecast
   periods. The conditional database uniqueness rule and transactional service
   prevent duplicate active alerts for the same city and forecast timestamp.
7. API responses contain validated, frontend-ready values. The client renders
   timestamps with their timezone and labels warnings as forecast-based, not
   official government alerts.

The map displays discrete, city-level markers and coordinates. It does not
interpolate those points or imply spatial coverage that the data does not
provide. History is limited to observations collected and stored by this
application; it is not a meteorological archive.

## Persistence

The Phase 2 schema is implemented in the `weather` and `alerts` apps. There is
no saved-location entity: both record types retain a city/country and
coordinates snapshot, so a separate location table is not needed for this
prototype.

- **`WeatherRecord`** stores `city`, optional `country`, `latitude`,
  `longitude`, `temperature_c`, `humidity_percent`, optional
  `apparent_temperature_c`, optional `heat_index_c`, optional `risk_level`,
  `recorded_at`, and `created_at`. Observation timestamps default to the
  current timezone-aware time; records order newest first. City/time and
  risk/time composite indexes support the planned history filters.
- **`HeatAlert`** stores `city`, optional `country`, coordinates,
  `temperature_c`, `humidity_percent`, optional `heat_index_c`, `risk_level`,
  `message`, `recommendation`, `forecast_time`, `created_at`, `updated_at`,
  and `is_active`. A conditional database unique constraint prevents more than
  one active alert for an exact city/country/forecast timestamp; a deactivated
  alert can be replaced. An active/time index supports alert listings.
- Both models validate coordinate ranges (latitude -90..90, longitude
  -180..180), Celsius temperature bounds, and relative humidity (0..100) in
  model validation and enforce database check constraints for the critical
  numeric bounds. City labels are trimmed and required by model validation.
- `risk_level` shares `weather.models.RiskLevel` categories. A blank Heat Index
  is allowed when a calculation is not applicable; a missing calculation is
  not silently substituted with apparent temperature.
- All units are explicit in field names/help text. Timestamps are timezone
  aware and stored by Django with `USE_TZ=True`.

The schema is captured by the initial weather and alert migrations and has
been applied to the local SQLite database. Changes to these fields/constraints
require new migrations and updated model tests.

Use explicit units in API contracts and model field documentation. Use timezone-
aware timestamps. Validate coordinate, humidity, and temperature ranges at
input boundaries. Avoid storing credentials or unnecessary personal data.

## API boundary

The versioned API is read-only and anonymously accessible. Implemented
resources under `/api/v1` are `GET /weather/cities/`, `/weather/current/`,
`/weather/forecast/`, `/weather/history/`, and `/alerts/`. Weather endpoints
accept validated city or coordinate parameters and map provider/network
failures to explicit HTTP responses. Current and hourly forecast results
include calculated heat-risk details; historical records and active alerts
are paginated, with an optional city filter. See `API_DOCUMENTATION.md` for
query constraints, response fields, pagination, and status codes.

Django Admin is the privileged management interface. The API has no public
write operations; unsupported methods return 405. Any future write endpoint
requires an explicit permission policy and tests.

## Configuration and error handling

- Load backend environment variables from `backend/.env` when present and
  support direct environment overrides. Require `DJANGO_SECRET_KEY`; keep
  `.env` out of version control and provide only a blank secret in
  `.env.example`. Read the debug flag, allowed hosts, CORS origins, frontend API
  base URL, and development proxy target from environment/configuration.
  Supply safe defaults only where appropriate; never commit real secrets.
- Bound provider connect/read timeouts. Do not hide network, invalid-payload,
  or upstream-service failures behind success-shaped placeholder responses.
- Return stable, useful client errors for invalid user input and explicit
  service errors for unavailable or malformed provider responses. Do not expose
  traceback or secret configuration in API responses.
- Restrict CORS to configured frontend origins; do not use unrestricted origins
  with credentials.
- Keep public informational endpoints separate from admin-authenticated
  management. Apply Django's built-in staff/superuser checks in Admin and
  verify protected actions.

## Heat-risk semantics

- Use the NOAA Rothfusz regression with its applicability checks and adjustments;
  return unavailable/not-applicable rather than extrapolating outside valid
  conditions.
- Keep ambient temperature, apparent temperature, Heat Index, and WBGT distinct
  in names, display labels, API fields, and help text.
- Use the specified indicative Celsius categories: below 27 low; 27–below 32
  caution; 32–below 41 extreme caution; 41–below 54 danger; 54 and above
  extreme danger. Confirm boundary behavior with tests before implementation.
- Label categories as indicative, not official Indian disaster-warning
  thresholds. Safety text should be conservative and not imply medical advice
  or guaranteed protection.

## Verification strategy

- **Backend:** Django checks, migration consistency, Django/DRF tests for
  validators, provider payload parsing, heat-index reference cases and
  applicability, API status and response shape, permissions, history filtering
  and pagination, and alert duplicate prevention. Mock provider HTTP calls in
  deterministic tests; run a bounded live API smoke check only when network
  access is available.
- **Frontend:** npm production build; component tests for key loading, error,
  empty, and populated states where practical; verify API integration and
  responsive layouts during integration.
- **Cross-cutting:** verify timezone/units, invalid city and provider failures,
  anonymous read versus protected write behavior, and no credentials in tracked
  files.
- Record only commands actually run and outcomes in `TESTING.md` and
  `PROGRESS.md`. No tests have been run during this planning step.

## Phase-to-component implementation order

1. Initialize backend/frontend and environment configuration (Phase 1).
2. Add and verify persistence/Admin (Phase 2).
3. Build provider services, then independently test Heat Index logic (Phases 3
   and 4).
4. Expose read APIs and test contracts/permissions (Phase 5).
5. Generate forecast alerts and verify uniqueness (Phase 6).
6. Initialize frontend and deliver screens in the roadmap order (Phases 7–12).
7. Finalize permissions, end-to-end integration, security review, and
   implementation documentation (Phases 13–16).

Keep each user-approved `NEXT` operation to one small step; this ordering does
not authorize implementation of later phases without approval.
