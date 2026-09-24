# AI Resume Analyzer & Job Matching Platform — Documentation

Complete technical documentation for developers who need to understand, install, maintain, or extend this project. For a quick overview, see [README.md](README.md).

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Project Structure](#4-project-structure)
5. [Frontend Architecture](#5-frontend-architecture)
6. [Backend Architecture](#6-backend-architecture)
7. [Database Design](#7-database-design)
8. [Authentication & Authorization](#8-authentication--authorization)
9. [Resume Upload System](#9-resume-upload-system)
10. [Resume Parsing](#10-resume-parsing)
11. [AI Resume Analysis](#11-ai-resume-analysis)
12. [Job Description Analysis](#12-job-description-analysis)
13. [Resume-to-Job Matching](#13-resume-to-job-matching)
14. [Skill Gap Analysis](#14-skill-gap-analysis)
15. [AI Resume Improvement](#15-ai-resume-improvement)
16. [Job Application Tracker](#16-job-application-tracker)
17. [API Documentation](#17-api-documentation)
18. [Environment Variables](#18-environment-variables)
19. [Local Development Setup](#19-local-development-setup)
20. [Testing](#20-testing)
21. [Error Handling](#21-error-handling)
22. [Security](#22-security)
23. [Deployment](#23-deployment)
24. [Troubleshooting](#24-troubleshooting)
25. [Development Workflow](#25-development-workflow)
26. [Future Improvements](#26-future-improvements)
27. [Project Learning Outcomes](#27-project-learning-outcomes)

---

## 1. Project Overview

**Purpose.** Give job seekers an honest, structured read on their resume and how it stacks up against a specific job — not a generic "ATS score," but a breakdown across skills, experience, projects, structure, and keywords, plus a resume-vs-job match with concrete missing skills.

**Problem statement.** Most people either get no feedback on their resume at all, or feedback that's vague ("make it stronger"). Separately, deciding whether to apply to a job usually comes down to skimming the description once. This project tries to make both steps concrete: a scored breakdown for the resume, and a skill-by-skill comparison against a job description.

**Target users.** Students and early-career job seekers preparing applications — the primary persona this was built around is a final-year CS student building a portfolio while job hunting.

**Main workflow.**

```text
Register / Login
      ↓
Upload resume (PDF/DOCX)
      ↓
Resume parsed into structured fields
      ↓
Run AI analysis → scores + strengths/weaknesses/recommendations
      ↓
Paste a job description → AI extracts required/preferred skills
      ↓
Run matching → match score + matched/missing/partial skills
      ↓
Track the application (status, dates, notes)
      ↓
Dashboard shows aggregate progress
```

**Major capabilities.** Auth, resume upload/parsing, AI scoring with history, job description analysis, resume-job matching, application tracking, and a stats dashboard — see [README.md](README.md#key-features) for the full list.

---

## 2. System Architecture

```text
Next.js Frontend (Client Components)
        ↓  fetch() + JWT Bearer token
FastAPI Backend (routes in app/api/*.py)
        ↓  Pydantic validation
Services (app/services/*.py)
        ↓
   ┌────┴─────┬──────────────┬───────────────┐
   ↓          ↓              ↓               ↓
PostgreSQL  AI Provider   File Storage   Password Hashing
(SQLAlchemy) (Mock/Gemini) (local disk)   (bcrypt)
```

- **Frontend** never queries the database or calls the AI provider directly. It only ever calls the FastAPI REST API, through one typed client (`frontend/lib/api.ts`).
- **API layer** (`app/api/`) parses/validates the HTTP request (via FastAPI + Pydantic) and delegates to a service — routes contain no business logic themselves.
- **Services** (`app/services/`) hold the actual logic: parsing a resume, calling the AI provider, computing a match, hashing a password. They're the only layer that talks to models/DB directly.
- **Database / AI / Storage** are each hidden behind a narrow interface so any one of them can be swapped without touching routes or other services (see §3 for why).

```mermaid
flowchart LR
    FE[Next.js Frontend] -->|HTTPS JSON + JWT| API[FastAPI Routes]
    API --> SVC[Services Layer]
    SVC --> DB[(PostgreSQL)]
    SVC --> AI[AI Provider Abstraction]
    SVC --> ST[Storage Abstraction]
    AI --> MOCK[Mock Provider]
    AI --> GEMINI[Gemini Provider]
    ST --> LOCAL[Local Disk]
```

---

## 3. Technology Stack

### Next.js

Used for the entire frontend (App Router). Chosen over plain React for file-based routing, built-in TypeScript support, and because it's the most common way React is shipped in production today — a directly transferable interview skill. Every interactive page is a Client Component (`"use client"`); there are no Server Components fetching data from the database, since the spec calls for a REST API architecture where the frontend only ever talks to FastAPI.

### TypeScript

Used across the entire frontend. Every backend Pydantic schema has a corresponding TypeScript interface in `frontend/types/index.ts`, kept in sync by hand as the single source of truth for what the API returns — this catches an entire class of "the API changed shape and the UI broke" bugs at compile time instead of runtime.

### Python

Used for the entire backend, specifically because resume parsing (PyMuPDF, python-docx), text processing, and AI integration all have first-class, mature Python libraries — this is the same reason Python dominates NLP/data tooling generally.

### FastAPI

Chosen for the backend framework because it generates OpenAPI docs automatically from the same Pydantic models used for validation (visible at `/docs`), it's fully async-capable, and its dependency-injection system (`Depends(...)`) is what makes `get_current_user` and `get_db` composable across every protected route without repeating auth/session logic.

### PostgreSQL

The system of record for users, resumes (including parsed data and raw text), jobs, matches, and applications. Chosen over SQLite because the schema genuinely needs real relational features this project uses directly: JSONB columns (`parsed_data`, `extracted_data`, score/skill arrays), a native UUID type, a proper ENUM type for application status, and multi-table foreign keys with `ON DELETE CASCADE` / `ON DELETE SET NULL` behavior — SQLite doesn't support several of these without workarounds.

### SQLAlchemy

The ORM layer (2.0-style, using `Mapped[]`/`mapped_column`). Models live in `app/models/`; every query goes through SQLAlchemy's query builder (`select(...)`), which is what makes SQL injection structurally difficult (see §22) and is what Alembic introspects to autogenerate migrations.

### Alembic

Manages schema migrations. `alembic/env.py` is wired to read `DATABASE_URL` from the app's own settings (not a hardcoded URL in `alembic.ini`) so migrations always target whichever database the app itself would connect to.

### AI Provider (Gemini / Mock)

The AI layer is accessed only through an abstract `AIProvider` interface (`app/services/ai_service.py`) with two implementations: `MockAIProvider` (deterministic, content-aware heuristic scoring, zero network calls) and `GeminiAIProvider` (calls Google's Gemini API via the `google-genai` SDK, requesting strict JSON output). Which one runs is chosen entirely by `AI_MODE`/`AI_PROVIDER` environment variables — no route or service code branches on the provider. This is a deliberate Strategy-pattern application: adding OpenAI later means one new class and one `if` branch in `get_ai_provider()`.

### bcrypt / PyJWT

Passwords are hashed with `bcrypt` (never stored or logged in plain text); sessions are stateless JWTs signed with `PyJWT`. See §8 for the full flow.

---

## 4. Project Structure

```text
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, router registration
│   ├── config.py            # Settings (pydantic-settings, reads .env)
│   ├── api/                 # Route handlers — thin, delegate to services
│   │   ├── auth.py            # register, login, /me, profile update
│   │   ├── resumes.py         # upload, list, get, delete, analyze, analyses
│   │   ├── jobs.py            # analyze (create+extract), list, get, delete
│   │   ├── matching.py        # resume-vs-job matching
│   │   ├── applications.py    # application tracker CRUD
│   │   └── dashboard.py       # aggregate stats
│   ├── models/               # SQLAlchemy ORM models (one file per table)
│   ├── schemas/               # Pydantic request/response schemas
│   ├── services/              # Business logic
│   │   ├── auth_service.py     # password hashing, JWT, get_current_user
│   │   ├── resume_parser.py    # PDF/DOCX text extraction + field parsing
│   │   ├── resume_service.py   # resume CRUD + AI analysis orchestration
│   │   ├── job_service.py      # job CRUD + AI extraction orchestration
│   │   ├── matching_service.py # resume-vs-job matching orchestration
│   │   ├── application_service.py
│   │   ├── dashboard_service.py
│   │   ├── ai_service.py       # AIProvider abstraction (Mock + Gemini)
│   │   └── storage_service.py  # StorageBackend abstraction (local disk)
│   ├── database/              # Engine/session setup
│   └── utils/security.py      # bcrypt hash/verify helpers
├── alembic/                  # Migrations
├── tests/                    # Pytest suite + fixtures/ (sample resume/JD)
└── requirements.txt

frontend/
├── app/                      # Next.js App Router routes
│   ├── page.tsx                # Landing page
│   ├── about/                  # Personal "About Me" page
│   ├── login/, register/       # Auth
│   ├── dashboard/               # Stats overview
│   ├── resumes/                 # List, upload; [id]/ = detail + analysis
│   ├── jobs/                    # List, analyze; [id]/ = detail + matching
│   ├── applications/            # Tracker grouped by status
│   └── profile/                 # Editable profile
├── components/
│   ├── ui/                     # Button, Card, Input, Badge, Toast, Dialog, ScrollReveal, states
│   ├── layout/                  # AppShell (sidebar/topbar nav + auth gate)
│   ├── dashboard/                # StatCard, ScoreBar, ScoreRadarChart
│   ├── resume/, jobs/, applications/  # Feature-specific components
├── lib/
│   ├── api.ts                   # Single typed fetch client (source of truth for endpoints)
│   ├── auth.tsx                  # Auth context/hooks
│   └── utils.ts                   # cn(), formatDate, score-color helpers, status labels
└── types/index.ts             # TypeScript interfaces mirroring backend schemas
```

---

## 5. Frontend Architecture

**Routing.** Next.js App Router — one folder per route under `app/`. Dynamic routes (`resumes/[id]`, `jobs/[id]`) use the Next.js 16 pattern: `page.tsx` is an `async` Server Component that `await`s `props.params` (a Promise in Next 16) and renders a co-located `*-client.tsx` Client Component that does the actual data fetching and interactivity — this split exists because Client Components can't `await` in their own function signature.

**Components.** Organized by role: `components/ui/` is generic and reusable (Button, Card, Badge, Toast, ConfirmDialog, ScrollReveal); `components/layout/` holds `AppShell`, the sidebar/topbar navigation wrapper used by every authenticated page; `components/{resume,jobs,applications}/` hold feature-specific pieces (upload form, match result panel, application card, etc.).

**State management.** No Redux/Zustand. `AuthProvider` (React Context, in `lib/auth.tsx`) is the one piece of genuinely cross-cutting state — the logged-in user and their JWT. Every other page manages its own data with local `useState`/`useEffect`, since resume/job/application lists are page-local concerns; a global store would be premature for this scope.

**API communication.** Every network call goes through `frontend/lib/api.ts` — a single `request<T>()` wrapper around `fetch` that attaches `Authorization: Bearer <token>` automatically (token read from `localStorage`) and throws a typed `ApiError` (with the backend's actual `detail` message) on any non-2xx response. Pages call typed functions like `resumesApi.upload(file)` or `dashboardApi.get()`, never `fetch` directly.

**Forms.** Plain controlled React state (`useState` per field) — no form library. Given the form count and field complexity in this app, `react-hook-form` or similar would add a dependency without solving a real problem here.

**Loading / error / empty states.** `components/ui/states.tsx` provides `PageSpinner`, `Skeleton`, `EmptyState`, and `ErrorState`, used consistently across every list page. Action-level feedback (upload succeeded, delete failed, etc.) goes through a toast system (`components/ui/toast.tsx`) rather than page-level banners.

**Authentication handling.** `useRequireAuth()` (in `lib/auth.tsx`) is called at the top of every protected page; it redirects to `/login` once the initial auth check resolves and the user turns out to be unauthenticated. `AuthProvider` bootstraps by checking `localStorage` for a token and, if present, calling `GET /api/auth/me` to load the user — an invalid/expired token clears itself automatically.

**Responsive design.** `AppShell` renders a fixed sidebar on desktop (`md:` breakpoint and up) and a horizontal top tab bar on mobile — not a hidden hamburger menu, since the nav only has five items. All grids use Tailwind's responsive column classes (`grid-cols-2 sm:grid-cols-4`, etc.).

**Data flow example (resume analysis):** user clicks "Analyze with AI" on `/resumes/[id]` → `resumesApi.analyze(id)` → `POST /api/resumes/{id}/analyze` → backend loads the resume, calls the AI provider, validates the result, inserts a new `resume_analyses` row → response flows back and is prepended to local `analyses` state → `ResumeAnalysisPanel` re-renders with the new scores.

---

## 6. Backend Architecture

**FastAPI application.** `app/main.py` creates the `FastAPI()` instance, adds CORS middleware (`CORS_ORIGINS` from settings), and registers six routers (`auth`, `resumes`, `jobs`, `matching`, `applications`, `dashboard`).

**Routes.** Thin — parse the request via a Pydantic schema, call one service function, return the result (FastAPI serializes it via a `response_model`). No business logic lives in a route handler.

**Services.** Hold the actual logic and are the only layer that touches SQLAlchemy models or the AI/storage abstractions directly. Each resource has its own service module (`resume_service.py`, `job_service.py`, etc.); ownership checks ("does this resume belong to this user?") live here, not in routes.

**Models.** SQLAlchemy ORM classes, one per table, in `app/models/`. `app/models/__init__.py` imports every model so `Base.metadata` is fully populated for Alembic autogeneration and so relationship string references resolve.

**Schemas.** Pydantic models in `app/schemas/`, split into request shapes (`UserRegister`, `JobCreate`, ...) and response shapes (`UserResponse`, `ResumeDetail`, ...) — request and response schemas are kept separate on purpose so a response never accidentally leaks a field like `hashed_password`.

**Repositories.** Not used as a separate layer. For this project's size, adding a repository layer between services and SQLAlchemy would be an abstraction without a second implementation to justify it — services call `db.scalar(select(...))` directly.

**Middleware.** Just CORS (`CORSMiddleware`). There's no custom logging/timing middleware.

**Authentication.** `auth_service.get_current_user` is a FastAPI dependency (`Depends(...)`) that decodes the JWT and loads the user; any route that needs auth just adds `current_user: User = Depends(auth_service.get_current_user)` as a parameter.

**Error handling.** Services raise `fastapi.HTTPException` with the appropriate status code and a human-readable message; FastAPI converts this into a JSON `{"detail": "..."}` response the frontend's `ApiError` reads directly.

**Request lifecycle:**

```text
Frontend fetch() with JWT
      ↓
FastAPI route (Pydantic validates request body)
      ↓
Depends(get_current_user) — decodes JWT, loads User, or raises 401
      ↓
Depends(get_db) — yields a request-scoped SQLAlchemy Session
      ↓
Service function (business logic, ownership checks)
      ↓
Database / AI provider / storage backend
      ↓
Pydantic response_model serializes the result
      ↓
JSON response → Frontend
```

---

## 7. Database Design

Six tables, all owned (directly or indirectly) by `users`.

| Table | Key columns | Notes |
|---|---|---|
| `users` | `id` (UUID, PK), `email` (unique), `hashed_password`, `full_name`, `location`, `github_url`, `linkedin_url`, `portfolio_url`, `preferred_role` | |
| `resumes` | `id`, `user_id` (FK → users, CASCADE), `title`, `file_path`, `file_type`, `file_size`, `raw_text`, `parsed_data` (JSONB), `is_active` | |
| `resume_analyses` | `id`, `resume_id` (FK → resumes, CASCADE), 9 score columns, `strengths`/`weaknesses`/`recommendations` (JSONB arrays), `ai_provider_used` | One row per analysis **run** — history, never overwritten |
| `jobs` | `id`, `user_id` (FK → users, CASCADE), `title`, `company`, `description_raw`, `extracted_data` (JSONB), `job_url` | |
| `matches` | `id`, `resume_id` (FK, CASCADE), `job_id` (FK, CASCADE), `match_score`, `matched_skills`/`missing_skills`/`partial_skills`/`recommendations` (JSONB) | **Unique constraint on `(resume_id, job_id)`** — re-matching updates the row instead of duplicating |
| `applications` | `id`, `user_id` (FK, CASCADE), `job_id` (FK → jobs, **SET NULL**, nullable), `resume_id` (FK → resumes, **SET NULL**, nullable), `company`, `position_title`, `status` (Postgres ENUM), `application_date`, `interview_date`, `job_url`, `notes` | `job_id`/`resume_id` are optional — an application can exist with no linked job/resume record |

`applications.status` is a native Postgres ENUM (`application_status`) with seven values: `saved`, `applied`, `interview`, `technical_round`, `offer`, `rejected`, `withdrawn`.

```mermaid
erDiagram
    USERS ||--o{ RESUMES : owns
    USERS ||--o{ JOBS : creates
    USERS ||--o{ APPLICATIONS : tracks
    RESUMES ||--o{ RESUME_ANALYSES : "has history of"
    RESUMES ||--o{ MATCHES : "matched against"
    JOBS ||--o{ MATCHES : "receives matches from"
    RESUMES |o--o{ APPLICATIONS : "optionally linked to"
    JOBS |o--o{ APPLICATIONS : "optionally linked to"
```

**Why `resume_analyses` is append-only.** Re-analyzing a resume inserts a new row rather than updating the existing one, so a user's score progress over time can be shown later — a resume improving after edits is exactly the story this project is meant to tell.

**Why `matches` is upsert-only.** Unlike analyses, a match score should reflect the *current* state of a resume and job, not accumulate history — re-running a match on the same `(resume_id, job_id)` pair updates the existing row (enforced by the unique constraint).

---

## 8. Authentication & Authorization

**Registration** (`POST /api/auth/register`): validates email format + password length (min 8 chars) via Pydantic, checks for an existing account with that email (400 if found), hashes the password with bcrypt, inserts the user.

**Login** (`POST /api/auth/login`): uses FastAPI's `OAuth2PasswordRequestForm` (form-encoded `username`/`password`, where `username` holds the email) specifically so the `/docs` Swagger UI's "Authorize" button works out of the box for manual testing. Verifies the password with `bcrypt.checkpw`, returns a signed JWT.

**Password handling.** Passwords are hashed with `bcrypt` (`app/utils/security.py`) before ever touching the database — never stored, logged, or returned in plain text.

**Session/token handling.** Stateless JWT (HS256, `PyJWT`), payload is just `{"sub": user_id, "exp": ...}` — no sensitive data embedded. Expiry is configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60). The frontend stores the token in `localStorage` and attaches it as `Authorization: Bearer <token>` on every request.

**Protected routes.** Any route depending on `auth_service.get_current_user` requires a valid, non-expired JWT for a user that still exists in the database; otherwise it returns `401 Unauthorized`.

**Authorization (ownership).** Every resource (resume, job, application) is scoped to its owner. Fetching a resource checks `resource.user_id == current_user.id`; a mismatch returns `404 Not Found` (not `403 Forbidden`) so a request for another user's resource doesn't even confirm that resource exists.

**Logout.** Handled entirely client-side (the frontend discards the token) since JWTs are stateless — there's no server-side token blocklist. This is a known simplification, noted honestly rather than glossed over: a production system would want short-lived access tokens plus a refresh-token/blocklist mechanism for real revocation.

**Profile updates** (`PUT /api/auth/me`): full-replace semantics — the frontend always sends every editable field together (unlike the applications tracker's partial-update `PUT`, see §16).

---

## 9. Resume Upload System

1. User selects (or drags in) a PDF/DOCX file in the browser.
2. Frontend validates extension/size client-side for immediate feedback, then uploads via `multipart/form-data` (`resumesApi.upload`).
3. Backend (`resume_service.upload_resume`) re-validates: extension must be `.pdf`/`.docx`, content must be non-empty, size must be under `MAX_UPLOAD_SIZE_MB` (default 5MB) — client-side checks are a UX nicety, never trusted alone.
4. The file is handed to the storage abstraction (`StorageBackend.save`), which returns an opaque key (`LocalStorageBackend` writes it to `storage/uploads/` under a random UUID filename — the original filename is never used as a path, avoiding path-traversal risk).
5. Text is extracted (`resume_parser.extract_text`) and parsed into structured fields (`resume_parser.parse_resume`).
6. A `Resume` row is inserted with the storage key, extracted text, and parsed data.
7. AI analysis is a separate, explicit step (`POST /api/resumes/{id}/analyze`) — upload does not automatically trigger it.

**Supported formats:** PDF and DOCX only (checked by extension, not just content-type header). **Size limit:** 5MB by default, configurable via `MAX_UPLOAD_SIZE_MB`. **Corrupted/unreadable files:** parsing failures return a clean `422` with a human-readable message — never a raw stack trace (see §21).

---

## 10. Resume Parsing

```text
PDF/DOCX file
   ↓
Text extraction (PyMuPDF for PDF, python-docx for DOCX — including table cells)
   ↓
Regex-based contact extraction (email, phone, links)
   ↓
Section-header detection (Education, Skills, Experience, Projects, Certifications, Achievements, Languages)
   ↓
Per-section content splitting (comma/bullet-separated for skills/languages, line-based for the rest)
   ↓
Structured resume data (name, email, phone, location, links, education, skills, experience, projects, certifications, achievements, languages)
```

**Libraries:** `pymupdf` for PDF text extraction, `python-docx` for DOCX (including any tables). Implemented in `app/services/resume_parser.py`.

**This is not AI/NLP-model-based parsing** — it's classic regex and heuristic section detection (`SECTION_HEADERS` alias map + a name/location heuristic based on line position). This is a deliberate, disclosed choice: it's resilient to varied resume layouts but not perfect (an unusually-formatted resume may leave some fields empty). The AI analysis layer (§11) reasons over this output; it doesn't replace it.

**Contact extraction pitfall (fixed):** an early version of the keyword-matching logic used naive substring checks that produced false positives — `"sql" in "postgresql"` and `"java" in "javascript"` are both `True` in plain Python. Fixed with `_contains_keyword()`, which uses alphanumeric-adjacency lookarounds instead of `\b` (word boundaries break on symbol-heavy keywords like `C++` or `CI/CD`). Covered by `tests/test_matching.py`.

---

## 11. AI Resume Analysis

**Flow:** `resume_service.analyze_resume()` calls `AIProvider.analyze_resume(parsed_data, raw_text)`, which returns a `ResumeAnalysisResult` — validated by Pydantic (score fields constrained to `0–100` via `Field(ge=0, le=100)`) before a `ResumeAnalysis` row is ever inserted.

**Mock mode (`AI_MODE=mock`, default):** `MockAIProvider` computes scores from the actual parsed content — e.g. `skills_score = min(95, 45 + len(skills) * 6)`, `experience_score = 85 if experience else 40` — so more content genuinely scores higher rather than returning random numbers. Strengths/weaknesses/recommendations are generated from which sections are present or missing.

**Live mode (`AI_MODE=live`, `AI_PROVIDER=gemini`):** `GeminiAIProvider` sends a prompt asking for **only** a JSON object matching the exact schema, with `response_mime_type="application/json"` set on the request. Sanitized example (no real keys):

```text
Prompt (truncated):
"You are an expert technical resume reviewer. Analyze the following
resume and respond with ONLY a JSON object matching exactly this schema...
{ "overall_score": <0-100 int>, "skills_score": <0-100 int>, ... }

Parsed resume fields: {"skills": ["Python", "React", ...], ...}
Full resume text: <resume text>"

Expected response:
{
  "overall_score": 82, "skills_score": 88, "experience_score": 76,
  "projects_score": 85, "education_score": 80, "structure_score": 84,
  "job_relevance_score": 70, "achievements_score": 65, "keywords_score": 78,
  "strengths": ["Clear, quantified project descriptions", ...],
  "weaknesses": ["No certifications listed", ...],
  "recommendations": ["Add measurable outcomes to experience bullets", ...]
}
```

**JSON validation:** if the response isn't valid JSON, or doesn't validate against `ResumeAnalysisResult`, the request is retried once; if it still fails, `AIProviderError` is raised and the API returns a `502` with a clear message — a malformed AI response never reaches the database.

---

## 12. Job Description Analysis

`POST /api/jobs/analyze` takes a title, optional company, the raw job description text (min. 20 characters), and an optional URL. `AIProvider.analyze_job(description)` returns required skills, preferred skills, minimum experience (years), education requirements, tools/technologies, and general keywords.

**Mock mode:** scans the description against a curated ~50-entry `TECH_KEYWORDS` list (React, Python, Docker, AWS, ...) using the same false-positive-safe `_contains_keyword()` matcher from §10. A "preferred / nice-to-have" section is detected by finding the earliest occurrence of a marker phrase (`"preferred"`, `"nice to have"`, `"bonus"`, `"a plus"`); everything before that split point is treated as required, everything after as preferred. Minimum experience is extracted with a regex (`(\d+)\+?\s*(?:years?|yrs?)`); education requirements are matched against a small marker list (`bachelor`, `master`, `phd`, `degree`, ...).

**Live mode:** same JSON-schema-constrained prompt approach as §11, targeting `JobAnalysisResult`.

The result (`extracted_data`) is stored as JSONB on the `jobs` row, so it only needs computing once per job description even though it may be matched against many resumes later.

---

## 13. Resume-to-Job Matching

`POST /api/matching/analyze` takes `{resume_id, job_id}`, loads both (with ownership checks — see §8), and calls `AIProvider.match_resume_job(resume.parsed_data, job.extracted_data)`.

**This project does not use embeddings or vector similarity.** Matching is deterministic keyword comparison in mock mode, or an LLM-driven comparison in live mode — no `pgvector`, no sentence embeddings. This is stated explicitly so the technique isn't overstated:

- **Matched:** a job skill whose lowercased text exactly appears in the resume's parsed `skills` list.
- **Missing:** a job skill with no match at all.
- **Partial:** a job skill whose "root" (the text before the first `.` or space — e.g. `"node"` from `"Node.js"`) appears inside some resume skill string, but not as an exact match.
- **Match score:** `round(100 * matched_count / total_job_skills)`, or `50` (a neutral default) if the job has no extracted skills to compare against.

**Live mode** delegates the entire comparison to Gemini via a JSON-schema-constrained prompt (`_MATCH_PROMPT` in `ai_service.py`), which explicitly instructs the model not to claim the candidate is "definitely qualified" — this is an analysis, not a hiring guarantee, and the frontend repeats that disclaimer next to every match result.

**Upsert, not duplicate:** re-running a match for the same `(resume_id, job_id)` pair updates the existing `matches` row (see §7) rather than creating a new one — a match score should reflect current state, not accumulate history the way resume analyses intentionally do.

---

## 14. Skill Gap Analysis

The three-way skill breakdown from §13 *is* the skill gap analysis — there's no separate calculation. Given this scenario (matching the spec's own worked example almost exactly, confirmed during manual testing):

```text
Job requires:  React, Node.js, Python, REST APIs, PostgreSQL, Docker
Resume lists:  React, JavaScript, REST APIs, Python, PostgreSQL, Node, TypeScript

✓ Matched:  React, Python, REST APIs, PostgreSQL
~ Partial:  Node.js        (resume has "Node", job wants "Node.js")
✗ Missing:  Docker
```

Recommendations are generated per missing skill: `"Consider adding experience or a project using {skill}."` — capped at the first five missing skills so the list stays actionable rather than overwhelming.

---

## 15. AI Resume Improvement

**Not implemented in the current codebase.** The resume analysis (§11) already returns `recommendations` (e.g. "Add measurable outcomes to experience bullets"), but there is no dedicated feature that rewrites specific weak bullet points, detects repeated words, or shows a "before/after" comparison of resume text. This is tracked as a planned feature — see §26. Any documentation implying this exists elsewhere in this repo's history describes the *target* design, not shipped functionality; this section exists specifically to avoid that ambiguity.

---

## 16. Job Application Tracker

Tracked fields: company, position title, status, an optional link to a stored job/resume, application date, interview date, job URL, and free-text notes.

**Status lifecycle** (`ApplicationStatus` enum): `saved → applied → interview → technical_round → offer` (or `rejected`/`withdrawn` from any point). The frontend renders these as a Kanban-style board grouped by status, with a per-card dropdown to change status directly.

**Application creation** (`POST /api/applications`): `job_id`/`resume_id` are optional but, when provided, are ownership-checked via the existing `resume_service.get_resume`/`job_service.get_job` — you can track an application with no stored job/resume behind it, but never link to someone else's.

**Status changes / edits** (`PUT /api/applications/{id}`): deliberately treated as a **partial update** — the schema (`ApplicationUpdate`) has every field optional, and the service applies `model_dump(exclude_unset=True)`. This matches how the UI actually edits an application (e.g. the status dropdown sends only `{"status": "interview"}`), rather than requiring the whole record resent on every small change. This is a conscious deviation from strict REST `PUT` semantics (which imply a full replace), documented here rather than left implicit.

**Deletion** (`DELETE /api/applications/{id}`): hard delete, ownership-checked.

---

## 17. API Documentation

All routes except register/login require `Authorization: Bearer <token>`. Interactive request/response schemas and a "Try it out" console are auto-generated at `/docs` (Swagger UI) and `/redoc`.

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| POST | `/api/auth/register` | Create an account | No |
| POST | `/api/auth/login` | Get a JWT | No |
| GET | `/api/auth/me` | Current user's profile | Yes |
| PUT | `/api/auth/me` | Update profile (full replace) | Yes |
| POST | `/api/resumes/upload` | Upload + parse a resume | Yes |
| GET | `/api/resumes` | List the user's resumes | Yes |
| GET | `/api/resumes/{id}` | Resume detail (incl. parsed data) | Yes |
| DELETE | `/api/resumes/{id}` | Delete a resume | Yes |
| POST | `/api/resumes/{id}/analyze` | Run AI scoring | Yes |
| GET | `/api/resumes/{id}/analyses` | Analysis history | Yes |
| POST | `/api/jobs/analyze` | Submit + AI-extract a job description | Yes |
| GET | `/api/jobs` | List analyzed jobs | Yes |
| GET | `/api/jobs/{id}` | Job detail | Yes |
| DELETE | `/api/jobs/{id}` | Delete a job | Yes |
| POST | `/api/matching/analyze` | Match a resume against a job | Yes |
| GET | `/api/applications` | List applications (`?status=` filter) | Yes |
| POST | `/api/applications` | Track a new application | Yes |
| GET | `/api/applications/{id}` | Application detail | Yes |
| PUT | `/api/applications/{id}` | Partial update | Yes |
| DELETE | `/api/applications/{id}` | Delete an application | Yes |
| GET | `/api/dashboard` | Aggregate stats | Yes |

### Example: `POST /api/resumes/{id}/analyze`

Request: no body (resume ID is in the path).

Response `201`:

```json
{
  "id": "b2f1...",
  "resume_id": "16cf...",
  "overall_score": 74,
  "skills_score": 75,
  "experience_score": 85,
  "projects_score": 85,
  "education_score": 90,
  "structure_score": 78,
  "job_relevance_score": 70,
  "achievements_score": 45,
  "keywords_score": 65,
  "strengths": ["Lists 5 relevant technical skills.", "..."],
  "weaknesses": ["No achievements/awards section detected."],
  "recommendations": ["Consider adding relevant certifications..."],
  "ai_provider_used": "mock",
  "created_at": "2026-09-24T14:39:12.245747+05:30"
}
```

Error responses: `401` (no/invalid token), `404` (resume not found or not owned), `502` (AI provider failed after retrying).

### Example: `POST /api/matching/analyze`

Request:

```json
{ "resume_id": "16cf...", "job_id": "6eb1..." }
```

Response `201`:

```json
{
  "id": "6b18...",
  "resume_id": "16cf...",
  "job_id": "6eb1...",
  "match_score": 44,
  "matched_skills": ["React", "Python", "PostgreSQL", "Docker"],
  "missing_skills": ["Node.js", "REST APIs", "Redis", "Kubernetes", "AWS"],
  "partial_skills": [],
  "recommendations": ["Consider adding experience or a project using Node.js.", "..."],
  "created_at": "2026-09-24T15:23:10.042513+05:30"
}
```

---

## 18. Environment Variables

**Backend** (`backend/.env`):

```env
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000

DATABASE_URL=postgresql+psycopg://resume_user:resume_pass@localhost:5432/resume_analyzer

JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=./storage/uploads
MAX_UPLOAD_SIZE_MB=5

AI_MODE=mock
AI_PROVIDER=gemini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash
```

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy connection string (psycopg3 dialect) |
| `CORS_ORIGINS` | Comma-separated origins allowed to call the API |
| `JWT_SECRET_KEY` | Signs auth tokens — generate your own (`python -c "import secrets; print(secrets.token_hex(32))"`), never reuse the example |
| `JWT_ALGORITHM` | JWT signing algorithm (HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime |
| `STORAGE_BACKEND` | Only `local` is implemented |
| `LOCAL_STORAGE_PATH` | Where uploaded resumes are written |
| `MAX_UPLOAD_SIZE_MB` | Server-enforced upload size limit |
| `AI_MODE` | `mock` (no key needed) or `live` |
| `AI_PROVIDER` | `gemini` |
| `GEMINI_API_KEY` | Only needed when `AI_MODE=live` |
| `GEMINI_MODEL` | Gemini model name |

**Frontend** (`frontend/.env.local`):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Never commit `.env` or `.env.local` — both are gitignored.

---

## 19. Local Development Setup

**Requirements:** Python 3.11+, Node.js 18+, PostgreSQL 14+ (native install or Docker).

### PostgreSQL

Two options:

**Docker:**
```bash
docker compose up -d
```

**Native install** (Windows/Mac/Linux) — create the role/database once as the `postgres` superuser:
```sql
CREATE ROLE resume_user WITH LOGIN PASSWORD 'resume_pass' CREATEDB;
CREATE DATABASE resume_analyzer OWNER resume_user;
GRANT ALL PRIVILEGES ON DATABASE resume_analyzer TO resume_user;
```

If you'll run the test suite, also create `resume_analyzer_test` (same owner) — tests never touch your real data.

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

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

### Verifying it worked

- Backend: http://localhost:8000/health should return `{"status": "healthy"}`.
- Frontend: http://localhost:3000 should show the landing page.
- Register a user, upload a PDF/DOCX resume, click "Analyze with AI" — with `AI_MODE=mock` (the default), this works with no API key.

---

## 20. Testing

**Backend (Pytest, 59 tests):** run against a dedicated `resume_analyzer_test` database (never the dev one), with `AI_MODE` forced to `mock` so no test needs a real API key or makes a network call. `tests/conftest.py` creates all tables once per session and truncates every table after each test for isolation, and overrides `LOCAL_STORAGE_PATH` to a temp directory so uploaded test files never touch `storage/uploads/`.

- `test_models.py` — schema structure (FKs, cascades, constraints, enum values) via `Base.metadata` inspection, no DB connection needed.
- `test_resume_parser.py` — text extraction and field parsing, including corrupted-file handling.
- `test_ai_service.py` — the mock provider's scoring logic and schema validation.
- `test_matching.py` — job-description keyword extraction and the `_contains_keyword` false-positive fix.
- `test_api_auth.py`, `test_api_resumes.py`, `test_api_jobs_matching.py`, `test_api_applications.py` — full HTTP-level tests via FastAPI's `TestClient`, using real fixture files (`tests/fixtures/sample_resume.pdf`/`.docx`, `sample_job_description.txt`).

Run with:
```bash
pip install -r requirements-dev.txt
pytest
```

**Frontend (Vitest + React Testing Library, 15 tests):** covers pure logic (`lib/utils.ts`) and two components (`ScoreBar`'s score-to-width math including clamping, `Button`'s loading/disabled states). Intentionally modest — most frontend verification during development happened via real browser testing against the live backend, including a flow that automated component tests can't easily cover (native file-picker resume upload).

Run with:
```bash
npm run test
```

---

## 21. Error Handling

| Scenario | Handling |
|---|---|
| Invalid file type/size | `400` before the file ever reaches storage |
| Corrupted/unreadable PDF or DOCX | Caught as `ResumeParsingError`, returned as `422` with a human-readable message — never a raw stack trace |
| AI provider failure or malformed response | Retried once (live mode); on repeated failure, `AIProviderError` → `502` |
| Resource not found / not owned | `404` (never `403`, to avoid confirming another user's resource exists) |
| Invalid credentials | `401` with `WWW-Authenticate: Bearer` |
| Invalid request body | `422` (FastAPI's automatic Pydantic validation) |
| Database unavailable | Connection error propagates as a `500`; no automatic retry/circuit-breaker is implemented (noted as a gap, not a hidden one) |
| Frontend network failure | `lib/api.ts` catches the `fetch` rejection and raises a typed `ApiError("Could not reach the server...")`, which every page displays via `ErrorState` or a toast |

A Windows-specific bug was found and fixed during development: on a failed parse, cleaning up the just-uploaded file could throw `PermissionError` because PyMuPDF/python-docx briefly hold a file handle open after a failed read on Windows. The cleanup is now best-effort (`try/except OSError: pass`) so this never turns into an unrelated `500` on top of the real `422`.

---

## 22. Security

Implemented:

- **Password hashing** — bcrypt, never plain text.
- **Authentication** — JWT (HS256), verified on every protected route via a FastAPI dependency.
- **Authorization** — every resource fetch/mutation checks `user_id` ownership.
- **Environment variables** — secrets never hardcoded; `.env`/`.env.local` gitignored.
- **File validation** — extension allowlist, size limit, empty-file rejection, all enforced server-side (never trusting client-side checks alone).
- **CORS** — configured via `CORS_ORIGINS`, not left wide open (`*`) by default.
- **SQL injection prevention** — every query goes through SQLAlchemy's query builder (`select(...)`, parameter binding); no raw string-interpolated SQL anywhere in the codebase.
- **Input validation** — every request body is a Pydantic schema with explicit constraints (e.g. password `min_length=8`, job description `min_length=20`).
- **Sensitive data handling** — password/token values never appear in log output or API responses (`UserResponse` excludes `hashed_password` by construction, not by after-the-fact filtering).
- **Path traversal prevention** — uploaded files are stored under a server-generated UUID filename, never the user-supplied original filename.

Not implemented (stated plainly, not glossed over):

- No rate limiting on auth endpoints (brute-force protection).
- No email verification on registration.
- No refresh-token/token-revocation mechanism — logout is client-side only.
- No CSRF protection (not applicable to the current Bearer-token setup, but would matter if cookies were introduced).
- No automated dependency vulnerability scanning configured in this repo.

---

## 23. Deployment

**Planned** — no deployment configuration exists in this repository yet. The application currently runs locally only (`uvicorn --reload` for the backend, `next dev` for the frontend). A production deployment would need, at minimum: a managed Postgres instance, environment-specific `CORS_ORIGINS`, a real `JWT_SECRET_KEY` (never the example value), HTTPS termination, and a production ASGI server invocation (`uvicorn app.main:app` without `--reload`, likely behind Gunicorn or run via a platform like Render/Railway/Fly.io for the backend and Vercel for the Next.js frontend). None of this is configured today.

---

## 24. Troubleshooting

```text
"python: command not found" / "python not recognized"
→ Use `python3`, or ensure Python 3.11+ is on PATH. On Windows, the
  py launcher (`py -3.11`) is often more reliable than `python`.

Database connection failed
→ Confirm Postgres is running (`docker compose ps`, or check the native
  service) and DATABASE_URL in backend/.env matches the role/database
  you actually created.

"relation does not exist" errors
→ Migrations haven't been applied. Run `alembic upgrade head` from backend/.

AI API key missing / 502 from analyze endpoints
→ You're on AI_MODE=live without GEMINI_API_KEY set. Either set the key
  or switch back to AI_MODE=mock (the default, needs no key).

CORS error in the browser console
→ CORS_ORIGINS in backend/.env doesn't include the frontend's actual
  origin (default http://localhost:3000).

Frontend cannot reach backend / "Could not reach the server"
→ Confirm the backend is actually running and NEXT_PUBLIC_API_URL in
  frontend/.env.local points at it (default http://localhost:8000).

Resume upload fails immediately
→ Check the file is actually .pdf or .docx and under MAX_UPLOAD_SIZE_MB
  (5MB default) — both are enforced server-side regardless of what the
  file picker allowed client-side.

422 on a resume upload that looks fine
→ The file may be corrupted, password-protected, or (for PDFs) a scanned
  image with no extractable text layer — the parser needs real text, not
  just pixels.
```

---

## 25. Development Workflow

```text
Create/pick up a feature
      ↓
Develop locally (backend + frontend running side by side)
      ↓
Run backend tests (pytest) and frontend tests (npm run test)
      ↓
Manually verify in the browser (esp. anything a test can't reach,
   like real file upload)
      ↓
Type-check + lint frontend (tsc --noEmit, npm run lint)
      ↓
Git commit (scoped, descriptive)
      ↓
Push
```

---

## 26. Future Improvements

Explicitly **not** implemented yet — separated from §Key Features (README) on purpose:

- AI-powered resume improvement: rewriting specific weak bullet points, detecting repeated words, before/after comparisons (§15)
- Additional AI providers (OpenAI, local LLMs via Ollama)
- Cloud storage backend (S3 / Supabase Storage) — the storage abstraction already supports adding one
- Resume version comparison (diff two uploaded versions of the same resume)
- Job board integrations (import a job description automatically from a URL)
- Email notifications for application follow-ups / interview reminders
- Rate limiting and email verification on auth
- Deployment configuration (§23)

---

## 27. Project Learning Outcomes

Built as a BTech final-year portfolio project, this codebase demonstrates:

- Full-stack architecture with a clean frontend/backend separation over a REST API
- React/Next.js (App Router, Client vs. Server Components, the Next.js 16 async-params pattern)
- TypeScript used to mirror a backend contract, not just for its own sake
- Python backend development with FastAPI and Pydantic
- REST API design (resource-oriented routes, consistent auth, meaningful status codes)
- Relational database design (PostgreSQL: JSONB, native ENUM, UUID PKs, cascade/set-null FK behavior, a unique constraint used for upsert semantics)
- SQLAlchemy 2.0-style ORM usage and Alembic migrations
- Authentication (JWT) and password security (bcrypt) implemented from scratch, not via a drop-in auth-as-a-service
- PDF/DOCX processing (PyMuPDF, python-docx) and resilient, disclosed-limitation text parsing
- AI integration via a provider-agnostic abstraction (Strategy pattern), including a mock mode purely so the project runs and is demoable without paid infrastructure
- Structured JSON-schema validation of LLM output (Pydantic), including retry-then-fail-gracefully handling of malformed AI responses
- API design decisions documented and justified (e.g. `PUT` as partial update for the tracker, `404` over `403` for ownership checks)
- Defensive error handling for real failure modes hit during development (a Windows file-lock bug, a keyword-matching false-positive bug), not hypothetical ones
- Software architecture discipline: thin routes, a services layer, and swappable infrastructure (AI provider, storage backend) behind narrow interfaces
- Automated testing across both the backend (pytest, isolated test database, HTTP-level tests) and frontend (Vitest, React Testing Library)
