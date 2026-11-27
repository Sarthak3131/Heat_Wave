# Database Documentation

## WeatherRecord

`WeatherRecord` is an application-collected observation: city/country,
latitude/longitude, `temperature_c`, `humidity_percent`, optional
`apparent_temperature_c`, optional `heat_index_c`, optional `risk_level`,
`recorded_at`, and `created_at`. Coordinates, temperature, humidity, Heat
Index, and risk values have model and database constraints. City/time and
risk/time indexes support historical filtering.

## HeatAlert

`HeatAlert` stores a forecast snapshot: location, temperature, humidity, Heat
Index, risk level, message, recommendation, forecast time, creation/update
timestamps, and `is_active`. A conditional uniqueness constraint prevents two
active alerts for the same city/country/forecast timestamp. An active/time
index supports listings.

## Authentication

Django's built-in `User`, `Group`, session, and permission tables are used.
The `accounts.0001_create_roles` migration creates `Administrator` and
`Regular User` groups. Django Admin and management endpoints use staff status
for server-side protection; client-side hiding alone is not security.
