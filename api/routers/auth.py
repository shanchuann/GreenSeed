import os
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client

from pydantic import BaseModel, EmailStr

from api.deps import CurrentUser, _decode_token, get_supabase, get_supabase_admin
from api.models.schemas import AuthResponse, LoginRequest, RegisterRequest, UserOut


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    password: str

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    body: RegisterRequest,
    anon_db: Annotated[Client, Depends(get_supabase)],
    admin_db: Annotated[Client, Depends(get_supabase_admin)],
):
    # 1. Supabase Auth 创建用户
    try:
        auth_res = anon_db.auth.sign_up({
            "email": body.email,
            "password": body.password,
        })
    except Exception as exc:
        raise HTTPException(400, f"注册失败：{exc}") from exc

    if not auth_res.user:
        raise HTTPException(400, "注册失败，请检查邮箱格式")

    # 2. 用 service role 写入 profiles（绕过 RLS 避免冷启动权限问题）
    try:
        profile_res = admin_db.table("profiles").insert({
            "id":    auth_res.user.id,
            "email": body.email,
            "name":  body.name,
            "role":  body.role,
        }).execute()
    except Exception as exc:
        # 回滚：删除刚创建的 Auth 用户
        admin_db.auth.admin.delete_user(auth_res.user.id)
        raise HTTPException(500, f"创建用户资料失败：{exc}") from exc

    profile = profile_res.data[0]

    # 若启用了邮件确认，session 为 None，返回空 token 提示用户验邮箱
    if not auth_res.session:
        return AuthResponse(
            access_token="",
            user=UserOut(**profile),
        )

    return AuthResponse(
        access_token=auth_res.session.access_token,
        user=UserOut(**profile),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    db: Annotated[Client, Depends(get_supabase)],
    admin_db: Annotated[Client, Depends(get_supabase_admin)],
):
    try:
        auth_res = db.auth.sign_in_with_password({
            "email": body.email,
            "password": body.password,
        })
    except Exception as exc:
        raise HTTPException(401, "邮箱或密码错误") from exc

    if not auth_res.user or not auth_res.session:
        raise HTTPException(401, "邮箱或密码错误")

    profile_res = admin_db.table("profiles").select("*").eq("id", auth_res.user.id).single().execute()
    if not profile_res.data:
        raise HTTPException(404, "用户资料不存在")

    return AuthResponse(
        access_token=auth_res.session.access_token,
        user=UserOut(**profile_res.data),
    )


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser):
    return UserOut(**user)


@router.patch("/me", response_model=UserOut)
async def update_me(
    body: dict,
    user: CurrentUser,
    admin_db: Annotated[Client, Depends(get_supabase_admin)],
):
    allowed = {
        "name", "phone", "avatar_url", "bio", "skills", "education",
        "desired_position", "desired_salary_min", "desired_salary_max",
        "desired_city", "available_date", "work_experience", "resume_url",
    }
    patch = {k: v for k, v in body.items() if k in allowed}
    if not patch:
        raise HTTPException(400, "无可更新字段")

    res = admin_db.table("profiles").update(patch).eq("id", user["id"]).execute()
    return UserOut(**res.data[0])


@router.post("/me/resume", response_model=UserOut)
async def upload_resume(
    file: Annotated[UploadFile, File(description="PDF 或 Word 简历文件")],
    user: CurrentUser,
    admin_db: Annotated[Client, Depends(get_supabase_admin)],
):
    ext = (file.filename or "resume").rsplit(".", 1)[-1].lower()
    if ext not in {"pdf", "doc", "docx"}:
        raise HTTPException(400, "仅支持 PDF / DOC / DOCX 格式")

    content = await file.read()
    path = f"{user['id']}/{uuid.uuid4()}.{ext}"

    try:
        admin_db.storage.from_("resumes").upload(
            path, content,
            file_options={"content-type": file.content_type or "application/octet-stream"},
        )
    except Exception as exc:
        raise HTTPException(500, f"文件上传失败：{exc}") from exc

    public_url = admin_db.storage.from_("resumes").get_public_url(path)
    res = admin_db.table("profiles").update({"resume_url": public_url}).eq("id", user["id"]).execute()
    return UserOut(**res.data[0])


@router.post("/forgot-password", status_code=204)
async def forgot_password(
    body:    ForgotPasswordRequest,
    anon_db: Annotated[Client, Depends(get_supabase)],
):
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    try:
        anon_db.auth.reset_password_for_email(
            body.email,
            options={"redirect_to": f"{frontend_url}/reset-password"},
        )
    except Exception:
        pass  # 不暴露邮箱是否存在


_bearer = HTTPBearer()

@router.post("/reset-password", status_code=204)
async def reset_password(
    body:     ResetPasswordRequest,
    admin_db: Annotated[Client, Depends(get_supabase_admin)],
    creds:    Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
):
    if len(body.password) < 8:
        raise HTTPException(400, "密码至少 8 位")
    payload = _decode_token(creds.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(401, "无效令牌")
    admin_db.auth.admin.update_user_by_id(user_id, {"password": body.password})


@router.post("/logout", status_code=204)
async def logout(
    user: CurrentUser,
    db: Annotated[Client, Depends(get_supabase)],
):
    try:
        db.auth.sign_out()
    except Exception:
        pass
