from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from api.deps import CurrentUser, get_supabase_admin, require_role
from api.models.schemas import JobCreate, JobOut, JobUpdate

router = APIRouter()

AdminOrRecruiter = Annotated[dict, Depends(require_role("recruiter", "admin"))]


# ── List / Search ─────────────────────────────────────────────────

@router.get("", response_model=list[JobOut])
async def list_jobs(
    db: Annotated[Client, Depends(get_supabase_admin)],
    q:        Optional[str] = Query(None, description="关键词（标题/公司/标签）"),
    city:     Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    job_type: Optional[Literal["full", "part", "intern"]] = Query(None),
    sort_by:  Literal["newest", "salary"] = Query("newest"),
    limit:    int = Query(20, ge=1, le=100),
    offset:   int = Query(0, ge=0),
):
    query = (
        db.table("jobs")
        .select("*, company:companies(*)")
        .eq("status", "open")
    )

    if city:
        query = query.eq("location", city)
    if category:
        query = query.eq("category", category)
    if job_type:
        query = query.eq("job_type", job_type)

    # Keyword search via PostgREST full-text / ilike
    if q:
        query = query.or_(f"title.ilike.%{q}%,tags.cs.{{{q}}}")

    if sort_by == "salary":
        query = query.order("salary_max", desc=True, nulls_last=True)
    else:
        query = query.order("created_at", desc=True)

    res = query.range(offset, offset + limit - 1).execute()
    return res.data


# ── Get single ────────────────────────────────────────────────────

@router.get("/{job_id}", response_model=JobOut)
async def get_job(
    job_id: str,
    db: Annotated[Client, Depends(get_supabase_admin)],
):
    res = (
        db.table("jobs")
        .select("*, company:companies(*)")
        .eq("id", job_id)
        .single()
        .execute()
    )
    if not res.data:
        raise HTTPException(404, "职位不存在")
    return res.data


# ── Create ────────────────────────────────────────────────────────

@router.post("", response_model=JobOut, status_code=201)
async def create_job(
    body: JobCreate,
    user: AdminOrRecruiter,
    db:   Annotated[Client, Depends(get_supabase_admin)],
):
    # Verify the company belongs to this recruiter
    company_res = (
        db.table("companies")
        .select("id")
        .eq("id", body.company_id)
        .eq("recruiter_id", user["id"])
        .single()
        .execute()
    )
    if not company_res.data:
        raise HTTPException(403, "无权在该公司下发布职位")

    res = db.table("jobs").insert(body.model_dump(exclude_none=True)).execute()
    job_id = res.data[0]["id"]

    full = (
        db.table("jobs")
        .select("*, company:companies(*)")
        .eq("id", job_id)
        .single()
        .execute()
    )
    return full.data


# ── Update ────────────────────────────────────────────────────────

@router.patch("/{job_id}", response_model=JobOut)
async def update_job(
    job_id: str,
    body:   JobUpdate,
    user:   AdminOrRecruiter,
    db:     Annotated[Client, Depends(get_supabase_admin)],
):
    _assert_job_owner(db, job_id, user)

    patch = body.model_dump(exclude_none=True)
    if not patch:
        raise HTTPException(400, "无可更新字段")

    db.table("jobs").update(patch).eq("id", job_id).execute()

    full = (
        db.table("jobs")
        .select("*, company:companies(*)")
        .eq("id", job_id)
        .single()
        .execute()
    )
    return full.data


# ── Delete ────────────────────────────────────────────────────────

@router.delete("/{job_id}", status_code=204)
async def delete_job(
    job_id: str,
    user:   AdminOrRecruiter,
    db:     Annotated[Client, Depends(get_supabase_admin)],
):
    _assert_job_owner(db, job_id, user)
    db.table("jobs").delete().eq("id", job_id).execute()


# ── Helper ────────────────────────────────────────────────────────

def _assert_job_owner(db: Client, job_id: str, user: dict) -> None:
    if user["role"] == "admin":
        return
    res = (
        db.table("jobs")
        .select("id, company:companies(recruiter_id)")
        .eq("id", job_id)
        .single()
        .execute()
    )
    if not res.data:
        raise HTTPException(404, "职位不存在")
    if res.data["company"]["recruiter_id"] != user["id"]:
        raise HTTPException(403, "无权操作此职位")
