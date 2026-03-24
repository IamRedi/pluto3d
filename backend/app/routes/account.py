from fastapi import APIRouter, Header

from app.services.auth import extract_bearer_token, verify_supabase_user
from app.services.plans import get_premium_emails, resolve_user_plan


router = APIRouter(prefix="/api/account", tags=["account"])


@router.get("/me")
def get_account_me(authorization: str | None = Header(default=None)):
    token = extract_bearer_token(authorization)
    debug_payload = {
        "premium_emails": sorted(get_premium_emails()),
    }

    if not token:
        return {
            "authenticated": False,
            "plan": "guest",
            "user": None,
            "debug": debug_payload,
        }

    user = verify_supabase_user(token)

    if not user:
        return {
            "authenticated": False,
            "plan": "guest",
            "user": None,
            "debug": debug_payload,
        }

    return {
        "authenticated": True,
        "plan": resolve_user_plan(user),
        "debug": {
            **debug_payload,
            "matched_email": (user.get("email") or "").strip().lower(),
        },
        "user": {
            "id": user.get("id"),
            "email": user.get("email"),
            "name": (user.get("user_metadata") or {}).get("full_name")
            or (user.get("user_metadata") or {}).get("name")
            or "Pluto User",
        },
    }
