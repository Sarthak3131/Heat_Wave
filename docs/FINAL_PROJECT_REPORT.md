# HeatWatch Final Project Report

## Abstract and problem

Extreme heat can be difficult to interpret from temperature alone. HeatWatch
combines weather conditions, an indicative Heat Index, forecasts, point maps,
stored-observation analytics, and forecast alerts to make heat information
clearer for an educational demonstration.

## Solution and architecture

A React client calls a Django REST API. Django validates requests, obtains
current/forecast data from Open-Meteo, calculates Heat Index values, stores
only explicit application records, and uses SQLite through the ORM. Recharts
renders historical trends and Leaflet renders discrete city points.

## Modules

Dashboard, forecast, map, historical analytics, active-alert list, Django
Admin, protected alert management, and session authentication are implemented.
Historical summaries report averages, extremes, observation count, and risk
distribution for filtered stored rows. They do not claim heatwave-day counts.

## Testing and limitations

Backend checks and 73 tests passed; frontend lint and the production build also
passed; see `TESTING.md`. HeatWatch does not automatically collect
observations, offer SMS/email delivery, provide official warnings, perform
spatial interpolation, or replace local emergency guidance. Future work could
add scheduled authorised collection, notification delivery, broader
accessibility/browser testing, and production deployment controls.
