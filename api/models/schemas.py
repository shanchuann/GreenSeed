from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, field_validator


# ── Auth ──────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Literal["seeker", "recruiter"]

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密码至少 8 位")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class WorkExperience(BaseModel):
    company: str
    position: str
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None


class ProjectExperience(BaseModel):
    project_name: str
    project_link: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    tech_stack: Optional[list[str]] = None
    description: Optional[str] = None
    results: Optional[str] = None


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    role: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[list[str]] = None
    education: Optional[str] = None
    desired_position: Optional[list[str]] = None
    desired_salary_min: Optional[int] = None
    desired_salary_max: Optional[int] = None
    desired_city: Optional[str] = None
    available_date: Optional[str] = None
    work_experience: Optional[list[dict]] = None
    project_experience: Optional[list[dict]] = None
    resume_url: Optional[str] = None
    gender: Optional[str] = None
    job_status: Optional[str] = None
    birth_year: Optional[int] = None
    birth_month: Optional[int] = None
    wechat: Optional[str] = None
    created_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str = ""
    token_type: str = "bearer"
    user: UserOut


# ── Company ───────────────────────────────────────────────────────

class CompanyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None


class CompanyOut(BaseModel):
    id: str
    recruiter_id: str
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    verified: bool
    created_at: datetime


# ── Job ───────────────────────────────────────────────────────────

class JobCreate(BaseModel):
    company_id: str
    title: str
    description: str
    requirements: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Literal["full", "part", "intern"] = "full"
    location: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Optional[Literal["full", "part", "intern"]] = None
    location: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    status: Optional[Literal["open", "closed"]] = None


class JobOut(BaseModel):
    id: str
    company_id: str
    title: str
    description: str
    requirements: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: str
    location: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    status: str
    source_platform: str = "local"
    source_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    company: Optional[CompanyOut] = None


# ── Application ───────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    job_id: str
    cover_letter: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    status: Literal["reviewing", "accepted", "rejected"]


class ApplicationOut(BaseModel):
    id: str
    job_id: str
    seeker_id: str
    status: str
    cover_letter: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    job: Optional[JobOut] = None
    seeker: Optional[UserOut] = None


# ── Admin stats ───────────────────────────────────────────────────

class PlatformStats(BaseModel):
    total_users: int
    total_jobs: int
    total_applications: int
    total_companies: int
    jobs_by_category: list[dict]
    applications_by_day: list[dict]
    jobs_by_company: list[dict]
