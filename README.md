# HeatWatch

HeatWatch is an educational Django REST Framework and React application for
monitoring weather, calculating an indicative Heat Index, reviewing
application-collected observations, and viewing forecast-based heat alerts.
It is not an official warning system, meteorological archive, or medical tool.

## Features

- Open-Meteo city search, current weather, and hourly/daily forecasts.
- NOAA-style Heat Index calculation with clear risk categories and safety text.
- Leaflet city-point map; it does not interpolate a regional heat map.
- Historical analytics from records actually stored by HeatWatch.
- Forecast alert generation with duplicate prevention and staff-only management.
- Django session login, built-in Administrator and Regular User groups, and
  Django Admin for protected user/record management.

## Stack and layout

- Backend: Python, Django, DRF, SQLite.
- Frontend: React, Vite, Axios, React Router, Recharts, Leaflet.
- `backend/` contains the API, models, migrations, tests, and `.env`.
- `frontend/` contains the browser interface.
- `docs/` contains API, database, setup, test, architecture, and final-report
  documentation.

## Run locally

See [the installation guide](docs/INSTALLATION_GUIDE.md). Start the backend
from `backend/` with `.venv\Scripts\python.exe manage.py runserver`, then run
the frontend from `frontend/` with `npm run dev` after dependencies are
installed. Create an administrator with `manage.py createsuperuser`.

## Known limitations

Current-provider requests are not automatically persisted as historical
observations. Historical charts remain empty until records are entered through
Django Admin or another authorised collection workflow. Alerts are not email or
SMS notifications; they are in-app forecast records.
