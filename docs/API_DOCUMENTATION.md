# HeatWatch API

Base path: `/api/v1`. All endpoints are read-only and available without
authentication. JSON responses use explicit units in field names. Timestamps
retain the provider or record timezone offset where applicable; historical
record timestamps are serialized as timezone-aware ISO 8601 values.

## Weather

### `GET /api/v1/weather/cities/`

Search Open-Meteo geocoding results.

| Query parameter | Required | Constraints |
|---|---:|---|
| `q` | yes | Trimmed city text, 1–100 characters |

Returns `{"results": [...]}`. A result can include the provider location ID,
name, latitude, longitude, country, country code, administrative region, and
timezone when supplied by Open-Meteo.

### `GET /api/v1/weather/current/`

Retrieve current provider conditions and the calculated indicative heat risk.

| Query parameter | Required | Constraints |
|---|---:|---|
| `latitude` | yes | -90 through 90 |
| `longitude` | yes | -180 through 180 |

The response contains provider coordinates, timezone metadata, and a `current`
object with observation time, ambient temperature in Celsius, relative humidity
in percent, provider apparent temperature in Celsius, wind speed in km/h,
weather code, day/night state, and a `heat_risk` object (`heat_index_c`,
`risk_level`, and `recommendation`). Heat risk fields are null when the
calculation is not applicable.

### `GET /api/v1/weather/forecast/`

Retrieve an Open-Meteo hourly and daily forecast with per-hour heat-risk
assessments.

| Query parameter | Required | Constraints |
|---|---:|---|
| `latitude` | yes | -90 through 90 |
| `longitude` | yes | -180 through 180 |
| `days` | no | 1–16; defaults to 5 |

The response includes timezone metadata, the requested day count, hourly rows
with metric weather values and `heat_risk`, and daily rows with temperatures,
sunrise/sunset, and weather code. Daily risk is not calculated because the
provider's daily response does not include relative humidity.

### `GET /api/v1/weather/history/`

List application-collected `WeatherRecord` entries, newest first. Historical
weather is not an external meteorological archive.

| Query parameter | Required | Constraints |
|---|---:|---|
| `city` | no | Trimmed, 1–120 characters; case-insensitive partial match |
| `page` | no | Positive whole page number; invalid values return 400 |
| `page_size` | no | 1–100; defaults to 20; invalid values return 400 |

Uses the standard paginated response envelope: `count`, `next`, `previous`, and
`results`.

## Alerts

### `GET /api/v1/alerts/`

List active forecast-based `HeatAlert` entries only, ordered by forecast time.
Supports the same optional `city`, `page`, and `page_size` filters as history,
with the same pagination envelope and page-size validation. Inactive/admin-
managed alerts are not exposed.

## Errors

Invalid or missing query parameters return HTTP 400 with a field-keyed
validation response; a requested page past the available results returns 404.
A city with no provider match returns 404. Temporary
provider/network failures return 503; rejected or malformed provider responses
return 502. Unsupported methods, including public writes, return 405.

These endpoints do not create observations or alerts. Weather-record history
and alert entries are read from the application database. Current weather
requests do not persist observations. Forecast alerts are generated separately
with the Django management command, run from `backend/`:

```text
python manage.py generate_heat_alerts --city "New Delhi" --country India --latitude 28.6139 --longitude 77.209 --days 5
```

Only forecast hours classified as Danger or Extreme Danger create alerts.
Repeated runs update active alerts for unchanged forecast periods and deactivate
alerts whose forecast risk has resolved.

## Alert management (staff only)

`GET /api/v1/alerts/management/` returns active and/or inactive alerts for a
logged-in staff user. It accepts `city`, `risk_level`, `status` (`active`,
`inactive`, or `all`), `page`, and `page_size`. `PATCH
/api/v1/alerts/management/{id}/` accepts `{"is_active": true}` or `false`.
Anonymous and regular users receive 403. The public `/alerts/` endpoint remains
read-only and active-only.

## Session authentication

- `GET /api/v1/auth/session/` returns the current user or `null` and sets a
  CSRF cookie.
- `POST /api/v1/auth/login/` accepts `username` and `password` and starts a
  Django session.
- `POST /api/v1/auth/logout/` ends the authenticated session.

Credentials are never returned. State-changing session requests require normal
Django CSRF protections.

## Historical Analytics API update (Phase 11, Step 11.2)

`GET /api/v1/weather/history/` additionally accepts these optional filters:

| Query parameter | Constraints |
| --- | --- |
| `start_date` | ISO date (`YYYY-MM-DD`); includes observations on/after this date |
| `end_date` | ISO date (`YYYY-MM-DD`); includes observations on/before this date and cannot precede `start_date` |
| `risk_level` | One of `low`, `caution`, `extreme_caution`, `danger`, or `extreme_danger` |

These filters combine with the existing case-insensitive `city` filter and
pagination. Invalid values return the existing field-keyed HTTP 400 response.
An empty matching dataset returns the standard pagination envelope with a zero
`count` and an empty `results` array.

### `GET /api/v1/weather/history/analytics/`

Returns a `summary` for all stored observations matching the same optional
`city`, `start_date`, `end_date`, and `risk_level` filters. It is not a count
of heatwave days: `total_observations` is the number of stored rows.

The summary contains `average_temperature_c`, `maximum_temperature_c`,
`minimum_temperature_c`, `average_humidity_percent`, `maximum_heat_index_c`,
`total_observations`, and `risk_level_distribution`. The distribution always
has each named risk level plus `not_applicable` for rows without a Heat Index
classification. When no rows match, numeric aggregates are `null`, total is
zero, and all distribution counts are zero.
