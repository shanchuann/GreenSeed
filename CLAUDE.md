# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**青禾招聘 GreenSeed** — A Python-based undergraduate recruitment system (本科生招聘系统) built as a university final project. Deployed on Vercel with a cloud database.

Assignment requirements (from `doc/大作业要求.md`):

- Database-backed CRUD for all entities
- Advanced features: sorting, statistics, visualization, cloud deployment
- Interactive web UI with clear navigation

## Tech Stack

- **Backend**: FastAPI as Vercel serverless function (`api/index.py`, exports `app`)
- **Database**: Supabase (PostgreSQL) — accessed via `supabase-py`; auth via Supabase Auth + JWT
- **Frontend**: Vue 3 + TypeScript + Vite, in `frontend/` directory
- **UI**: Custom design system (no component library) — OKLCH tokens in `frontend/src/assets/main.css`
- **State**: Pinia (`stores/auth.ts`)
- **Routing**: Vue Router 4 with role-based guards in `router/index.ts`
- **Deployment**: Vercel — `vercel.json` routes `/api/*` to FastAPI, static frontend from `frontend/dist/`

## Vercel Deployment

Python on Vercel runs as serverless functions. `api/index.py` exports `app` (FastAPI instance). `vercel.json`:

```json
{
  "builds": [
    { "src": "api/index.py", "use": "@vercel/python" },
    { "src": "frontend/dist/**", "use": "@vercel/static" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "api/index.py" },
    { "src": "/(.*)", "dest": "frontend/dist/$1" }
  ]
}
```

Required env vars: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`, `JWT_SECRET`. Set in Vercel project settings; access via `os.environ`.

## Development Commands

```bash
# Frontend
cd frontend
npm install
npm run dev          # starts on http://localhost:5173, proxies /api → localhost:8000
npm run build        # outputs to frontend/dist/

# Backend
pip install -r requirements.txt
uvicorn api.index:app --reload   # starts on http://localhost:8000

# Tests
pytest
pytest tests/test_<module>.py::test_<name>
```

## Architecture

Three user roles: **求职者** (seeker), **招聘方** (recruiter), **管理员** (admin).

### Frontend (`frontend/src/`)
- `assets/main.css` — full design token system (OKLCH colors, spacing, typography). All CSS variables defined here; components use tokens only.
- `components/layout/` — `AppHeader.vue` (sticky, blur backdrop), `AppFooter.vue`
- `components/ui/JobCard.vue` — accepts `Job` interface, two variants: `list` and `grid`
- `views/` — `HomeView.vue`, `JobsView.vue` (search/filter/sort), `JobDetailView.vue`, `auth/LoginView.vue`, `auth/RegisterView.vue`
- `stores/auth.ts` — Pinia store; `login()`, `register()`, `logout()`, `restore()` (reads `gs-token` from localStorage)
- `router/index.ts` — `meta.requiresAuth` + `meta.role` guards; unauthenticated → `/login?redirect=...`

Theme toggle: stored in `localStorage` as `gs-theme`, applied as `data-theme` on `<html>`.

### Backend (`api/`)
- `index.py` — FastAPI app entry, CORS configured for frontend origin
- `routers/` — `auth.py`, `jobs.py`, `applications.py`, `companies.py`, `admin.py`
- `deps.py` — `get_current_user()` decodes JWT; `role_required()` checks role
- `models/schemas.py` — Pydantic models for all request/response bodies

Database access centralised via Supabase client in `deps.py`; never open raw connections in route handlers.

### Visualization
Chart.js client-side, data from `/api/admin/stats` endpoint (GROUP BY aggregates). Three charts: job category distribution (pie), daily applications (line), jobs per company (bar).
