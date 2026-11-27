# Phase 11 Onwards Audit

## Scope and status

This audit records the repository state at the beginning of Phase 11. It is a
source-level audit of the existing implementation. Runtime database inspection
and Django verification could not be performed in this workspace because
`backend/.env`, `backend/db.sqlite3`, and a Python launcher are absent.

## Existing implementation confirmed

- The backend is a Django/DRF project with `weather` and `alerts` apps, SQLite
  configured in `config/settings.py`, and versioned routes under `/api/v1`.
- `WeatherRecord` is implemented in `backend/weather/models.py` and has an
  initial migration (`weather/migrations/0001_initial.py`).
- Public weather endpoints provide city search, current conditions, forecasts,
  and paginated stored-record history. The current and forecast endpoints do
  not persist records.
- Heat Index calculation and indicative risk categorisation are implemented in
  the weather service. Alert generation and Django Admin management exist.
- The React application has dashboard, forecast, and map pages, routing, a
  shared layout, Leaflet/OpenStreetMap integration, Axios, and Recharts.
  History and alerts routes are still placeholders, consistent with the
  completed Phase 10 roadmap.
- Focused backend tests exist for models, weather API behaviour, provider
  handling, Heat Index calculation, alerts, and alert management.

## Step 11.1 — WeatherRecord database audit

### Available historical fields

`WeatherRecord` stores the following observation facts:

| Area | Fields |
| --- | --- |
| Location | `city`, optional `country`, `latitude`, `longitude` |
| Measurements | `temperature_c`, `humidity_percent`, optional `apparent_temperature_c`, optional `heat_index_c` |
| Classification | optional `risk_level` using the shared `RiskLevel` choices |
| Time | `recorded_at` (observation time) and `created_at` (row creation time) |

`recorded_at` defaults to Django's timezone-aware `timezone.now`; project
settings have `USE_TZ=True` and use `Asia/Kolkata`. `created_at` is automatic.
Analytics must use `recorded_at`, not the database insertion time.

The model has composite indexes for `(city, recorded_at)` and
`(risk_level, recorded_at)`, which support the planned city/date/risk filters.
Model validators and database check constraints guard coordinates, temperature,
humidity, optional Heat Index, and risk values. The migration matches the
currently inspected model source, so no model change or migration is justified
by this audit.

### Data-collection finding

There is currently no application code path that saves a `WeatherRecord` after
a current-weather request. Records can exist only if entered through Django
Admin or another external/administrative process. Consequently, the future
Historical Analytics page must accurately show an empty state when no records
have been collected; it must never fabricate history.

### Known gaps for later Phase 11 steps

- The existing `/weather/history/` endpoint supports city filtering and
  pagination only; date-range and risk-category filters remain Phase 11 work.
- Aggregate analytics (averages, extremes, count, and risk distribution) and
  the history UI are not implemented.
- The present workspace cannot establish migration application status, inspect
  actual SQLite rows, or run the test suite until the local backend runtime
  configuration and Python interpreter are restored.

## Files reviewed

- `backend/weather/models.py`
- `backend/weather/migrations/0001_initial.py`
- `backend/weather/serializers.py`
- `backend/weather/views.py`
- `backend/weather/urls.py`
- `backend/weather/admin.py`
- `backend/weather/test_api.py`
- `backend/config/settings.py`
- `frontend/src/App.jsx` and existing route/component inventory
- `docs/PROJECT_ROADMAP.md`, `docs/PROGRESS.md`, `docs/ARCHITECTURE.md`, and
  `docs/API_DOCUMENTATION.md`

## Verification performed

- Repository inventory: passed; confirmed the expected backend/frontend source
  structure and only initial migrations for `weather` and `alerts`.
- Source/migration comparison: passed; `WeatherRecord` fields, indexes, and
  constraints agree with `weather.0001_initial`.
- History API/test inspection: passed; existing tests cover city filtering,
  pagination, invalid city/page inputs, and public-write rejection.
- Runtime checks: not run. `python` is not available in PATH, and no Python
  launcher was detected. `backend/.env` and `backend/db.sqlite3` are absent.

## Next recommended action

Phase 11, Step 11.2: design and implement validated date-range and risk-level
filters plus a bounded, consistent historical API response, after restoring a
usable backend runtime for test execution.
