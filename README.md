Supabase migrations

This folder will hold plain-SQL migration files and notes for Supabase schema/policy changes performed during development.

Structure:
- migrations/ - timestamped .sql files
- notes/ - optional markdown notes explaining intent

Applying:
- Review each .sql file and apply in Supabase SQL editor or using the Supabase CLI.

# Gradalyze Backend API

Backend service for the Gradalyze academic profiling and career recommendation platform.

## Features

- Authentication with JWT
- File upload for transcripts and certificates
- OCR-grade extraction (simulated in development)
- Grade validation workflow
- Admin review flow
- Learning archetype computation (K-Means)
- Career prediction (Random Forest)
- Company/job matching
- Dossier (portfolio) generation

## Tech Stack

- Flask 3.x
- PyJWT, Flask-CORS, python-dotenv

## Prerequisites

- Python 3.11+

## Quickstart

1. Create and activate a virtual environment
   ```bash
   python -m venv venv
   # Windows
   venv\\Scripts\\activate
   # macOS/Linux
   # source venv/bin/activate
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment
   Create a `.env` file in `backend/`:
   ```env
   FLASK_APP=app.py
   FLASK_DEBUG=True
   SECRET_KEY=please-change-in-production
   ```

4. Run the API
   ```bash
   python app.py
   # server starts on http://localhost:5000
   ```

## Environment Variables

- `FLASK_APP` – entrypoint file, default `app.py`
- `FLASK_DEBUG` – set `True` for dev reload
- `SECRET_KEY` – JWT/signing secret (use a strong value in prod)

## API Endpoints (summary)

- Auth
  - `POST /api/auth/login` – login and get JWT
  - `GET /api/auth/profile` – fetch current user
- Analysis
  - `POST /api/analysis/upload` – upload documents
  - `POST /api/analysis/extract-grades` – extract grades
  - `POST /api/analysis/validate-grades` – validate extracted data
  - `POST /api/analysis/admin-review` – admin review
  - `POST /api/analysis/compute-archetype` – compute archetype
  - `GET /api/analysis/results` – analysis results
- Dossier
  - `POST /api/dossier/generate` – generate dossier
  - `GET /api/dossier/download` – download PDF
  - `POST /api/dossier/share` – create share link
  - `GET /api/dossier/preview` – preview dossier
- Health
  - `GET /health` – liveness check

### Example: Login

```bash
curl -X POST http://localhost:5000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"email":"john.doe@plm.edu.ph","password":"password123"}'
```

## Project Structure

```
backend/
  app.py
  app/
    routes/          # Flask blueprints and route handlers
    services/        # Business logic and integrations
```

## Notes for Development

- Several ML/OCR parts are simulated for development. Replace with real services/models in production.

## Troubleshooting

- Port already in use: stop existing process on 5000 or set `FLASK_RUN_PORT`.
- Invalid JWT/secret: ensure `SECRET_KEY` is set and consistent.
- Virtualenv issues on Windows: run PowerShell as Administrator and `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` if activation is blocked.


