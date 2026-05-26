from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from api.deps import CurrentUser, get_supabase_admin, require_role
from api.models.schemas import ApplicationCreate, ApplicationOut, ApplicationStatusUpdate

router = APIRouter()

SeekerOnly    = Annotated[dict, Depends(require_role("seeker"))]
RecruiterOnly = Annotated[dict, Depends(require_role("recruiter", "admin"))]


# ── 求职者：投递 ──────────────────────────────────────────────────

@router.post("", response_model=ApplicationOut, status_code=201)
async def apply(
    body: ApplicationCreate,
    user: SeekerOnly,
    db:   Annotated[Client, Depends(get_supabase_admin)],
):
    # 检查职位是否存在且开放
    job_res = db.table("jobs").select("id,status").eq("id", body.job_id).single().execute()
    if not job_res.data:
        raise HTTPException(404, "职位不存在")
    if job_res.data["status"] != "open":
        raise HTTPException(400, "该职位已关闭，无法申请")

    # 检查是否重复申请
    dup = (
        db.table("applications")
        .select("id")
        .eq("job_id", body.job_id)
        .eq("seeker_id", user["id"])
        .execute()
    )
    if dup.data:
        raise HTTPException(409, "已申请过该职位")

    res = db.table("applications").insert({
        "job_id":       body.job_id,
        "seeker_id":    user["id"],
        "cover_letter": body.cover_letter or "",
    }).execute()

    return _full_application(db, res.data[0]["id"])


# ── 求职者：查看自己的申请 ────────────────────────────────────────

@router.get("/mine", response_model=list[ApplicationOut])
async def my_applications(
    user: CurrentUser,
    db:   Annotated[Client, Depends(get_supabase_admin)],
):
    res = (
        db.table("applications")
        .select("*, job:jobs(*, company:companies(*))")
        .eq("seeker_id", user["id"])
        .order("created_at", desc=True)
        .execute()
    )
    return res.data


# ── 招聘方：查看某职位的所有申请 ──────────────────────────────────

@router.get("/job/{job_id}", response_model=list[ApplicationOut])
async def job_applications(
    job_id: str,
    user:   RecruiterOnly,
    db:     Annotated[Client, Depends(get_supabase_admin)],
):
    # 验证该职位属于当前招聘方
    job_res = (
        db.table("jobs")
        .select("id, company:companies(recruiter_id)")
        .eq("id", job_id)
        .single()
        .execute()
    )
    if not job_res.data:
        raise HTTPException(404, "职位不存在")
    if (
        user["role"] != "admin"
        and job_res.data["company"]["recruiter_id"] != user["id"]
    ):
        raise HTTPException(403, "无权查看该职位的申请")

    res = (
        db.table("applications")
        .select("*, seeker:profiles(*)")
        .eq("job_id", job_id)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data


# ── 招聘方：更新申请状态 ──────────────────────────────────────────

@router.patch("/{app_id}/status", response_model=ApplicationOut)
async def update_status(
    app_id: str,
    body:   ApplicationStatusUpdate,
    user:   RecruiterOnly,
    db:     Annotated[Client, Depends(get_supabase_admin)],
):
    app_res = (
        db.table("applications")
        .select("id, job:jobs(company:companies(recruiter_id))")
        .eq("id", app_id)
        .single()
        .execute()
    )
    if not app_res.data:
        raise HTTPException(404, "申请不存在")

    if (
        user["role"] != "admin"
        and app_res.data["job"]["company"]["recruiter_id"] != user["id"]
    ):
        raise HTTPException(403, "无权操作此申请")

    db.table("applications").update({"status": body.status}).eq("id", app_id).execute()
    return _full_application(db, app_id)


# ── Helper ────────────────────────────────────────────────────────

def _full_application(db: Client, app_id: str) -> dict:
    res = (
        db.table("applications")
        .select("*, job:jobs(*, company:companies(*)), seeker:profiles(*)")
        .eq("id", app_id)
        .single()
        .execute()
    )
    return res.data
