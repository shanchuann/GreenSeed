from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import Client
import os

load_dotenv()

from api.routers import auth, jobs, applications, companies, admin, seed
from api.deps import get_supabase_admin

app = FastAPI(
    title="GreenSeed API",
    description="青禾招聘 — 本科生招聘平台后端",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
origins = [frontend_url] if frontend_url != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,         prefix="/api/auth",         tags=["auth"])
app.include_router(jobs.router,         prefix="/api/jobs",         tags=["jobs"])
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
app.include_router(companies.router,    prefix="/api/companies",    tags=["companies"])
app.include_router(admin.router,        prefix="/api/admin",        tags=["admin"])
app.include_router(seed.router,         prefix="/api/seed",         tags=["seed"])


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/stats")
async def public_stats(db: Annotated[Client, Depends(get_supabase_admin)]):
    """公开统计数据，供主页展示，无需登录。"""
    open_jobs     = db.table("jobs").select("id", count="exact").eq("status", "open").execute().count or 0
    company_count = db.table("companies").select("id", count="exact").execute().count or 0
    seeker_count  = db.table("profiles").select("id", count="exact").eq("role", "seeker").execute().count or 0

    jobs_raw = db.table("jobs").select("category").eq("status", "open").execute().data
    cat_counts: dict[str, int] = {}
    for row in jobs_raw:
        cat = row.get("category") or "其他"
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    return {
        "companies": company_count,
        "open_jobs": open_jobs,
        "seekers":   seeker_count,
        "jobs_by_category": cat_counts,
    }
