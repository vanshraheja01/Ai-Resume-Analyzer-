# Frontend — AI Resume Analyzer

Next.js (App Router) + TypeScript + Tailwind CSS. See the root [README.md](../README.md) for the full project overview.

## Local setup

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

App: http://localhost:3000 — requires the backend running at the URL in `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).

## How it talks to the backend

Every API call goes through `lib/api.ts` — a thin typed wrapper around `fetch`, one function per backend endpoint (`authApi`, `resumesApi`, `jobsApi`, `matchingApi`, `applicationsApi`, `dashboardApi`). No component calls `fetch` directly. Auth is a JWT stored in `localStorage`, attached as `Authorization: Bearer <token>` by `request()`; `lib/auth.tsx` (`AuthProvider`/`useAuth`/`useRequireAuth`) tracks the current user and redirects unauthenticated visitors to `/login`. Errors from the API surface as `ApiError` with the backend's `detail` message, so every page can show the real reason a request failed instead of a generic error.

Dynamic routes (`/resumes/[id]`, `/jobs/[id]`) follow the Next.js 16 pattern: `page.tsx` is an async Server Component that awaits `props.params`, then renders a co-located `*-client.tsx` Client Component that does the actual data fetching/interactivity — this is required because `params` is a Promise in Next 16, and Client Components can't `await` directly in their function signature.

## Structure

```
app/                    # Routes (App Router)
├── page.tsx             # Landing page
├── login/, register/    # Auth
├── dashboard/           # Stats overview
├── resumes/             # List, upload, detail + AI analysis
├── jobs/                # List, analyze, detail + matching
├── applications/        # Tracker (grouped by status)
└── profile/             # Editable user profile
components/
├── ui/                   # Button, Input, Card, Badge, Toast, Dialog, states
├── layout/               # AppShell (sidebar nav + auth gate)
├── dashboard/            # StatCard, ScoreBar
├── resume/               # Upload form, card, analysis panel
├── jobs/                 # Job form, card, match result panel
└── applications/         # Application form, card
lib/
├── api.ts                # Typed fetch client (source of truth for endpoints)
├── auth.tsx              # Auth context + hooks
└── utils.ts               # cn(), formatDate, score color helpers, status labels
types/                    # TypeScript interfaces mirroring backend Pydantic schemas
```

## Notes for interview explainability

- **State management**: no Redux/Zustand — React context (`AuthProvider`) for auth, local `useState`/`useEffect` per page for data fetching. Justified by scope: this app has one piece of cross-cutting state (the logged-in user); adding a global store for page-local resume/job/application lists would be premature.
- **Why a JWT in `localStorage` instead of an httpOnly cookie**: simpler to reason about for a portfolio project talking to a separate FastAPI origin, at the cost of XSS exposure a cookie-based session would avoid — a real production app would prefer httpOnly cookies + CSRF protection.
- **Partial updates**: the applications tracker's status dropdown calls `PUT /api/applications/{id}` with only `{ status }` — the backend treats `PUT` as a deliberate partial update (see backend README) so this doesn't require resending the whole record.

Status: Phase 7 complete — all pages wired to the live backend, verified via
real browser interaction (register, dashboard, job analysis, matching,
application tracking, profile editing all confirmed end-to-end).
