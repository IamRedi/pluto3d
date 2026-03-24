from fastapi import APIRouter, Header

from app.services.auth import extract_bearer_token, verify_supabase_user
from app.services.plans import resolve_user_plan


router = APIRouter(prefix="/api/account", tags=["account"])


@router.get("/me")
def get_account_me(authorization: str | None = Header(default=None)):
    token = extract_bearer_token(authorization)

    if not token:
        return {
            "authenticated": False,
            "plan": "guest",
            "user": None,
        }

    user = verify_supabase_user(token)

    if not user:
        return {
            "authenticated": False,
            "plan": "guest",
            "user": None,
        }

    return {
        "authenticated": True,
        "plan": resolve_user_plan(user),
        "user": {
            "id": user.get("id"),
            "email": user.get("email"),
            "name": (user.get("user_metadata") or {}).get("full_name")
            or (user.get("user_metadata") or {}).get("name")
            or "Pluto User",
        },
    }
