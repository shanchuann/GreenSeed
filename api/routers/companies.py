from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from api.deps import CurrentUser, get_supabase_admin, require_role
from api.models.schemas import CompanyCreate, CompanyOut, CompanyUpdate

router = APIRouter()

RecruiterOrAdmin = Annotated[dict, Depends(require_role("recruiter", "admin"))]


@router.get("", response_model=list[CompanyOut])
async def list_companies(db: Annotated[Client, Depends(get_supabase_admin)]):
    res = db.table("companies").select("*").order("created_at", desc=True).execute()
    return res.data


@router.get("/mine", response_model=list[CompanyOut])
async def my_companies(
    user: RecruiterOrAdmin,
    db:   Annotated[Client, Depends(get_supabase_admin)],
):
    res = (
        db.table("companies")
        .select("*")
        .eq("recruiter_id", user["id"])
        .order("created_at", desc=True)
        .execute()
    )
    return res.data


@router.get("/{company_id}", response_model=CompanyOut)
async def get_company(
    company_id: str,
    db: Annotated[Client, Depends(get_supabase_admin)],
):
    res = db.table("companies").select("*").eq("id", company_id).single().execute()
    if not res.data:
        raise HTTPException(404, "公司不存在")
    return res.data


@router.post("", response_model=CompanyOut, status_code=201)
async def create_company(
    body: CompanyCreate,
    user: RecruiterOrAdmin,
    db:   Annotated[Client, Depends(get_supabase_admin)],
):
    res = db.table("companies").insert({
        **body.model_dump(exclude_none=True),
        "recruiter_id": user["id"],
    }).execute()
    return res.data[0]


@router.patch("/{company_id}", response_model=CompanyOut)
async def update_company(
    company_id: str,
    body: CompanyUpdate,
    user: RecruiterOrAdmin,
    db:   Annotated[Client, Depends(get_supabase_admin)],
):
    _assert_owner(db, company_id, user)

    patch = body.model_dump(exclude_none=True)
    if not patch:
        raise HTTPException(400, "无可更新字段")

    res = db.table("companies").update(patch).eq("id", company_id).execute()
    return res.data[0]


@router.delete("/{company_id}", status_code=204)
async def delete_company(
    company_id: str,
    user: RecruiterOrAdmin,
    db:   Annotated[Client, Depends(get_supabase_admin)],
):
    _assert_owner(db, company_id, user)
    db.table("companies").delete().eq("id", company_id).execute()


def _assert_owner(db: Client, company_id: str, user: dict) -> None:
    if user["role"] == "admin":
        return
    res = db.table("companies").select("recruiter_id").eq("id", company_id).single().execute()
    if not res.data:
        raise HTTPException(404, "公司不存在")
    if res.data["recruiter_id"] != user["id"]:
        raise HTTPException(403, "无权操作该公司")
