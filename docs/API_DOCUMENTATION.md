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
and alert entries are read from the application database; persistence and
forecast-alert generation are handled by their respective later-phase flows.
