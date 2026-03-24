from fastapi import APIRouter, Header

from app.services.auth import extract_bearer_token, verify_supabase_user
from app.services.plans import resolve_user_plan_details
from app.services.subscriptions import ensure_profile_for_user, get_subscription_summary_for_user, get_user_display_name


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

    plan_details = resolve_user_plan_details(user)
    ensure_profile_for_user(user, plan=plan_details["plan"])

    return {
        "authenticated": True,
        "plan": plan_details["plan"],
        "planSource": plan_details["source"],
        "planReason": plan_details["reason"],
        "subscription": get_subscription_summary_for_user(user),
        "user": {
            "id": user.get("id"),
            "email": user.get("email"),
            "name": get_user_display_name(user),
        },
    }
