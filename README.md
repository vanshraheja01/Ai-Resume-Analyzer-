# AI Resume Analyzer & Job Matching Platform

A production-style, portfolio-grade full-stack application: upload a resume,
get an AI-generated quality analysis, match it against a job description,
track applications, and manage multiple resume versions.

Built as a BTech 4th-year Computer Science portfolio project to demonstrate
frontend, backend, database, auth, NLP/document processing, AI integration,
and clean software architecture end to end.

> **Status: Phase 0 (scaffolding) complete.** Database, auth, resume
> processing, AI analysis, matching, and application tracking land in the
> phases below — this README's feature list describes the target state, not
> what's implemented yet.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Next.js (App Router), TypeScript, Tailwind CSS, Recharts, Lucide React |
| Backend | Python 3.11+, FastAPI, Pydantic, SQLAlchemy |
| Database | PostgreSQL |
| AI | Provider-agnostic abstraction — Gemini or a mock (no API key needed) |
| Storage | Provider-agnostic abstraction — local disk for dev, swappable for S3/Supabase |

## Architecture

```
┌─────────────────────┐         HTTPS/JSON (JWT)        ┌──────────────────────────┐
│   Next.js Frontend   │ ───────────────────────────────▶│   FastAPI Backend        │
│  (TypeScript, React) │◀─────────────────────────────── │   (Python 3.11+)         │
└─────────────────────┘                                  └───────────┬──────────────┘
                                                                      │
                                        ┌─────────────────────────────┼──────────────────────┐
                                        │                              │                      │
                              ┌─────────▼─────────┐        ┌───────────▼──────────┐  ┌────────▼────────┐
                              │  Resume Parser      │        │   AI Service          │  │ Storage Service │
                              │  (PyMuPDF/          │        │   Abstraction         │  │ Abstraction     │
                              │   python-docx)       │        │  (Gemini / Mock)      │  │ (Local/S3 later)│
                              └─────────────────────┘        └───────────────────────┘  └─────────────────┘
                                        │
                              ┌─────────▼─────────┐
                              │  PostgreSQL         │
                              │  (SQLAlchemy ORM)   │
                              └─────────────────────┘
```

The frontend never talks to the database or AI provider directly — every
interaction goes through the FastAPI REST API over JSON, authenticated with
a JWT bearer token. The AI provider and storage backend are both hidden
behind interfaces (`app/services/ai_service.py`, `app/services/storage_service.py`)
so either can be swapped without touching route or business logic.

## Folder structure

```
backend/
├── app/
│   ├── main.py          # FastAPI entrypoint
│   ├── config.py         # Settings from env vars
│   ├── api/               # Route handlers (auth, resumes, jobs, matching, applications)
│   ├── models/            # SQLAlchemy ORM models
│   ├── schemas/           # Pydantic request/response schemas
│   ├── services/          # Business logic (parser, AI, matching, storage)
│   ├── database/          # DB connection/session setup
│   └── utils/
├── tests/
├── requirements.txt
└── .env.example

frontend/
├── app/                   # Next.js App Router pages
│   ├── login/ register/ dashboard/ resumes/ jobs/ applications/ profile/
├── components/
│   ├── ui/ dashboard/ resume/ jobs/ applications/
├── lib/                   # api.ts, auth.ts, utils.ts
├── types/
└── public/
```

## Database schema (ER overview)

```
users ──1:N── resumes ──1:N── resume_analyses
users ──1:N── jobs
resumes, jobs ──N:N (via matches)── matches
users ──1:N── applications (references jobs/resumes optionally)
```

See [backend/README.md](backend/README.md) for column-level detail as models land.

## Local development

### Database (PostgreSQL, no paid services)

Two options — pick whichever you already have:

**Option A — Docker** (if you have Docker Desktop running):

```bash
docker compose up -d
```

**Option B — Native PostgreSQL for Windows/Mac/Linux** (no virtualization needed):
Install from [postgresql.org/download](https://www.postgresql.org/download/),
then create the app's role and database once, using the `postgres` superuser:

```sql
CREATE ROLE resume_user WITH LOGIN PASSWORD 'resume_pass' CREATEDB;
CREATE DATABASE resume_analyzer OWNER resume_user;
GRANT ALL PRIVILEGES ON DATABASE resume_analyzer TO resume_user;
```

Either way, Postgres ends up reachable at `localhost:5432` with credentials
matching `backend/.env.example` (`resume_user` / `resume_pass` / `resume_analyzer`).

### Backend

```bash
cd backend
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

```bash
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

API: http://localhost:8000 — interactive docs at http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

App: http://localhost:3000

## Environment variables

**Backend** (`backend/.env`, see `backend/.env.example`):

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres connection string |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins |
| `JWT_SECRET_KEY` | Signs auth tokens — generate your own, never reuse the example value |
| `STORAGE_BACKEND` | `local` (only option currently implemented) |
| `LOCAL_STORAGE_PATH` | Where uploaded resumes are stored on disk |
| `MAX_UPLOAD_SIZE_MB` | Upload size limit, enforced server-side |
| `AI_MODE` | `mock` (no API key needed) or `live` (Phase 4) |
| `AI_PROVIDER` | `gemini` (Phase 4) |
| `GEMINI_API_KEY` | Only needed when `AI_MODE=live` |

**Frontend** (`frontend/.env.local`, see `frontend/.env.local.example`):

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_API_URL` | Base URL of the FastAPI backend |

`.env` / `.env.local` are gitignored — never commit real secrets.

## Implementation roadmap

| Phase | Deliverable |
|---|---|
| 0 | ✅ Repo scaffolding, backend/frontend skeletons, docker-compose Postgres |
| 1 | ✅ Database: SQLAlchemy models, Alembic migrations, applied to a live Postgres |
| 2 | ✅ Auth: register/login, JWT, bcrypt password hashing, protected `/me` route |
| 3 | ✅ Resume upload + parser (PyMuPDF/python-docx), storage abstraction |
| 4 | AI resume analysis (provider abstraction + mock mode) |
| 5 | Job description analyzer + resume-job matching engine |
| 6 | Application tracker + stats |
| 7 | Frontend build-out, wired to the real API |
| 8 | Polish: loaders, empty/error states, responsive pass |
| 9 | Tests (backend + frontend) |
| 10 | Documentation pass |

## AI functionality

AI calls are isolated behind a single interface so the provider can change
without touching any route or business logic:

```python
class AIProvider(ABC):
    def analyze_resume(self, resume_data: dict) -> ResumeAnalysis: ...
    def analyze_job(self, job_description: str) -> JobAnalysis: ...
    def match_resume_job(self, resume: dict, job: dict) -> MatchResult: ...
    def improve_resume(self, resume_data: dict) -> ImprovementSuggestions: ...
```

`AI_MODE=mock` returns deterministic, realistic sample data with zero API
calls — the whole app runs and is demoable without any API key.
`AI_MODE=live` with `AI_PROVIDER=gemini` calls the real Gemini API. Every AI
response is validated against a Pydantic schema before it reaches the
database or the frontend; malformed model output never propagates as-is.

## Future improvements

- Additional AI providers (OpenAI, local LLMs via Ollama)
- Cloud storage backend (S3 / Supabase Storage)
- Resume-to-job auto-recommendations based on tracked applications
- Team/recruiter-facing view
