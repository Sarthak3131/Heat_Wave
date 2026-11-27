# Installation Guide

## Requirements

- Python 3.13 (the workspace uses 3.13.17).
- Node.js and npm.

## Backend

1. Open a terminal in `backend/`.
2. Create the virtual environment: `python -m venv .venv`.
3. Install packages: `.venv\Scripts\python.exe -m pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and set a private `DJANGO_SECRET_KEY`.
5. Apply schema changes: `.venv\Scripts\python.exe manage.py migrate`.
6. Create an administrator: `.venv\Scripts\python.exe manage.py createsuperuser`.
7. Run the API: `.venv\Scripts\python.exe manage.py runserver`.

Use `/admin/` for authorised management of users, weather records, and alerts.
The migration creates `Administrator` and `Regular User` groups. Staff status
is required for the protected alert-management API and Django Admin.

## Frontend

1. Open a second terminal in `frontend/`.
2. Restore locked packages: `npm ci`.
3. Start development: `npm run dev`.
4. Open the shown local URL (normally `http://localhost:5173`).

The default frontend API path is `/api/v1`; Vite proxies it to the local Django
server. Set `VITE_API_BASE_URL` only when deploying behind a different API URL.

## Testing

Run backend tests from `backend/`:

```text
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.venv\Scripts\python.exe manage.py test
```

Run `npm run lint` and `npm run build` from `frontend/` after `npm ci`.
