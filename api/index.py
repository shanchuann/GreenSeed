from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from api.routers import auth, jobs, applications, companies, admin, seed

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
