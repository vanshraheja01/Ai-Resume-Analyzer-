# Backend — AI Resume Analyzer API

FastAPI + PostgreSQL backend. See the root [README.md](../README.md) for the full project overview.

## Local setup

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## Structure

```
app/
├── main.py          # FastAPI app entrypoint
├── config.py        # Settings (env vars)
├── api/             # Route handlers
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic request/response schemas
├── services/        # Business logic (AI, parsing, matching, storage)
├── database/        # DB connection/session setup
└── utils/           # Shared helpers
```

Status: Phase 0 complete (scaffolding + health check). Database, auth, resume
processing, AI analysis, matching, and application tracking land in later
phases — see the root README for the roadmap.
