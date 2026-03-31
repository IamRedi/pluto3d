from fastapi import APIRouter, Body, Header

from app.services.auth import extract_bearer_token, verify_supabase_user
from app.services.plans import get_premium_emails, resolve_user_plan_details
from app.services.subscriptions import (
    ensure_profile_for_user,
    get_activity_summary_for_user,
    get_subscription_summary_for_user,
    get_user_display_name,
    update_profile_activity_for_user,
)


router = APIRouter(prefix="/api/account", tags=["account"])


def _fallback_plan_details(user: dict) -> dict:
    email = (user.get("email") or "").strip().lower()
    if email and email in get_premium_emails():
        return {
            "plan": "premium",
            "source": "tester_email",
            "reason": "Plan resolved from PLUTO_PREMIUM_EMAILS fallback after a backend sync recovery.",
        }

    return {
        "plan": "free",
        "source": "default_free",
        "reason": "Plan fell back to free after a backend sync recovery.",
    }


def _resolve_plan_details_safely(user: dict) -> dict:
    try:
        return resolve_user_plan_details(user)
    except Exception:
        return _fallback_plan_details(user)


def _ensure_profile_safely(user: dict, plan: str) -> None:
    try:
        ensure_profile_for_user(user, plan=plan)
    except Exception:
        return


def _update_profile_activity_safely(user: dict, *, plan: str, active_seconds_delta: int = 0) -> None:
    try:
        update_profile_activity_for_user(
            user,
            plan=plan,
            active_seconds_delta=active_seconds_delta,
        )
    except Exception:
        return


def _get_subscription_summary_safely(user: dict) -> dict:
    try:
        return get_subscription_summary_for_user(user)
    except Exception:
        return {
            "customerId": None,
            "subscriptionId": None,
            "status": None,
            "plan": None,
            "currentPeriodEnd": None,
        }


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

    plan_details = _resolve_plan_details_safely(user)
    _ensure_profile_safely(user, plan=plan_details["plan"])
    _update_profile_activity_safely(user, plan=plan_details["plan"], active_seconds_delta=0)

    return {
        "authenticated": True,
        "plan": plan_details["plan"],
        "planSource": plan_details["source"],
        "planReason": plan_details["reason"],
        "subscription": _get_subscription_summary_safely(user),
        "activity": get_activity_summary_for_user(user),
        "user": {
            "id": user.get("id"),
            "email": user.get("email"),
            "name": get_user_display_name(user),
        },
    }


@router.post("/activity/ping")
def post_account_activity_ping(
    payload: dict = Body(default={}),
    authorization: str | None = Header(default=None),
):
    token = extract_bearer_token(authorization)
    if not token:
        return {"ok": False, "reason": "unauthenticated"}

    user = verify_supabase_user(token)
    if not user:
        return {"ok": False, "reason": "unauthenticated"}

    plan_details = _resolve_plan_details_safely(user)
    active_seconds = int(payload.get("activeSeconds") or 0)
    _update_profile_activity_safely(
        user,
        plan=plan_details["plan"],
        active_seconds_delta=active_seconds,
    )
    return {"ok": True}
