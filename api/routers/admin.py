from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from api.deps import get_supabase_admin, require_role
from api.models.schemas import PlatformStats, UserOut

router = APIRouter()

AdminOnly = Annotated[dict, Depends(require_role("admin"))]


# ── 用户管理 ──────────────────────────────────────────────────────

@router.get("/users", response_model=list[UserOut])
async def list_users(
    _:  AdminOnly,
    db: Annotated[Client, Depends(get_supabase_admin)],
):
    res = db.table("profiles").select("*").order("created_at", desc=True).execute()
    return res.data


@router.patch("/users/{user_id}/role")
async def set_user_role(
    user_id: str,
    role:    str,
    _:       AdminOnly,
    db:      Annotated[Client, Depends(get_supabase_admin)],
):
    if role not in ("seeker", "recruiter", "admin"):
        raise HTTPException(400, "无效角色")
    res = db.table("profiles").update({"role": role}).eq("id", user_id).execute()
    if not res.data:
        raise HTTPException(404, "用户不存在")
    return {"ok": True}


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    _:       AdminOnly,
    db:      Annotated[Client, Depends(get_supabase_admin)],
):
    db.auth.admin.delete_user(user_id)
    db.table("profiles").delete().eq("id", user_id).execute()


# ── 企业审核 ──────────────────────────────────────────────────────

@router.get("/companies/pending")
async def pending_companies(
    _:  AdminOnly,
    db: Annotated[Client, Depends(get_supabase_admin)],
):
    res = (
        db.table("companies")
        .select("*, recruiter:profiles(id,name,email)")
        .eq("verified", False)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data


@router.patch("/companies/{company_id}/verify")
async def verify_company(
    company_id: str,
    verified:   bool,
    _:          AdminOnly,
    db:         Annotated[Client, Depends(get_supabase_admin)],
):
    res = db.table("companies").update({"verified": verified}).eq("id", company_id).execute()
    if not res.data:
        raise HTTPException(404, "企业不存在")
    return {"ok": True, "verified": verified}


# ── 平台统计 ──────────────────────────────────────────────────────

@router.get("/stats", response_model=PlatformStats)
async def platform_stats(
    _:  AdminOnly,
    db: Annotated[Client, Depends(get_supabase_admin)],
):
    # 总计数
    users_count   = db.table("profiles").select("id", count="exact").execute().count or 0
    jobs_count    = db.table("jobs").select("id", count="exact").execute().count or 0
    apps_count    = db.table("applications").select("id", count="exact").execute().count or 0
    company_count = db.table("companies").select("id", count="exact").execute().count or 0

    # 职位按分类分布（用于饼图）
    jobs_raw = db.table("jobs").select("category").execute().data
    cat_counts: dict[str, int] = {}
    for row in jobs_raw:
        cat = row["category"] or "其他"
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    jobs_by_category = [{"category": k, "count": v} for k, v in cat_counts.items()]

    # 近 14 天每日新增申请（用于折线图）
    apps_raw = (
        db.table("applications")
        .select("created_at")
        .order("created_at", desc=False)
        .execute()
        .data
    )
    day_counts: dict[str, int] = {}
    for row in apps_raw:
        day = row["created_at"][:10]  # YYYY-MM-DD
        day_counts[day] = day_counts.get(day, 0) + 1
    applications_by_day = [{"date": k, "count": v} for k, v in sorted(day_counts.items())[-14:]]

    # 各公司发布职位数（用于柱状图，取前 10）
    companies_raw = db.table("companies").select("id,name").execute().data
    company_map   = {c["id"]: c["name"] for c in companies_raw}
    jobs_all      = db.table("jobs").select("company_id").execute().data
    company_job_counts: dict[str, int] = {}
    for row in jobs_all:
        cid = row["company_id"]
        company_job_counts[cid] = company_job_counts.get(cid, 0) + 1
    jobs_by_company = sorted(
        [{"company": company_map.get(k, k), "count": v} for k, v in company_job_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:10]

    return PlatformStats(
        total_users=users_count,
        total_jobs=jobs_count,
        total_applications=apps_count,
        total_companies=company_count,
        jobs_by_category=jobs_by_category,
        applications_by_day=applications_by_day,
        jobs_by_company=jobs_by_company,
    )
