import os
from functools import lru_cache
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from supabase import Client, create_client

load_dotenv()

bearer = HTTPBearer()

# ── Supabase clients ──────────────────────────────────────────────

@lru_cache
def get_supabase() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_ANON_KEY"]
    return create_client(url, key)


@lru_cache
def get_supabase_admin() -> Client:
    """Service-role client — bypasses RLS, for admin operations only."""
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return create_client(url, key)


# ── JWT verification ──────────────────────────────────────────────

def _decode_token(token: str) -> dict:
    secret = os.environ["JWT_SECRET"]
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# ── Current-user dependency ───────────────────────────────────────

def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    db: Annotated[Client, Depends(get_supabase_admin)],
) -> dict:
    payload = _decode_token(creds.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="令牌中缺少用户标识")

    res = db.table("profiles").select("*").eq("id", user_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=401, detail="用户不存在")
    return res.data


CurrentUser = Annotated[dict, Depends(get_current_user)]


# ── Role guard factory ────────────────────────────────────────────

def require_role(*roles: str):
    def _guard(user: CurrentUser) -> dict:
        if user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要角色：{', '.join(roles)}",
            )
        return user
    return _guard
