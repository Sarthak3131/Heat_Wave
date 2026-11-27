# Testing

## Final verification — 27 November 2026

- `pip check`: passed.
- `manage.py check`: passed.
- `manage.py makemigrations --check --dry-run`: passed.
- `manage.py test accounts alerts weather`: passed, 73 tests.
- `manage.py migrate`: applied `accounts.0001_create_roles` successfully.
- `npm run lint`: passed with zero errors and zero warnings.
- `npm run build`: passed.

Backend tests cover model constraints, provider parsing, Heat Index logic,
weather/history APIs, analytics, alert generation, duplicate prevention,
active-alert filters, staff-only management, and session login/logout.

## Quality findings

- `AlertsPage.jsx` was hand-compressed rather than generated/minified. It was
  reformatted and split into filter and alert-card components without changing
  its API contract or UI states.
- Route-level lazy loading now defers forecast, map, history, alerts, and login
  code. The production main entry is 391.45 kB before gzip; the Recharts line
  chart is isolated in a 409.05 kB lazy chunk. Vite emitted no 500 kB warning.
- Backend authorization tests confirm anonymous and regular users receive 403
  for staff-only alert management, while staff can list and change alert state.

## Checks not performed

No live browser/console smoke test was run in this pass because no local
frontend/backend server was active in an available browser surface. The
automated API/session/permission tests passed, but manual route and responsive
review should still be performed before public deployment.
