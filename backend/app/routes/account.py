from fastapi import APIRouter, Body, Header
from pydantic import BaseModel, Field
from fastapi import Request

from app.services.auth import extract_bearer_token, verify_supabase_user
from app.services.plans import get_premium_emails, resolve_user_plan_details
from app.services.subscriptions import (
    ensure_profile_for_user,
    get_activity_summary_for_user,
    get_subscription_summary_for_user,
    get_user_display_name,
    update_guest_activity,
    update_profile_activity_for_user,
)
from app.services.usage import build_usage_snapshot, consume_credit_usage, consume_feature_usage, resolve_usage_subject


router = APIRouter(prefix="/api/account", tags=["account"])


class UsageConsumeRequest(BaseModel):
    featureKey: str
    amount: int = 1
    grantCredits: dict[str, int] = Field(default_factory=dict)


class UsageCreditConsumeRequest(BaseModel):
    creditKey: str
    amount: int = 1


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
            "usage": build_usage_snapshot(resolve_usage_subject(None, None)),
        }

    user = verify_supabase_user(token)

    if not user:
        return {
            "authenticated": False,
            "plan": "guest",
            "user": None,
            "usage": build_usage_snapshot(resolve_usage_subject(None, None)),
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
        "usage": build_usage_snapshot(resolve_usage_subject(authorization, None)),
        "user": {
            "id": user.get("id"),
            "email": user.get("email"),
            "name": get_user_display_name(user),
        },
    }


@router.get("/usage")
def get_account_usage(
    authorization: str | None = Header(default=None),
    x_pluto_guest_key: str | None = Header(default=None, alias="X-Pluto-Guest-Key"),
):
    subject = resolve_usage_subject(authorization, x_pluto_guest_key)
    return build_usage_snapshot(subject)


@router.post("/usage/consume")
def consume_account_usage(
    request: UsageConsumeRequest,
    authorization: str | None = Header(default=None),
    x_pluto_guest_key: str | None = Header(default=None, alias="X-Pluto-Guest-Key"),
):
    subject = resolve_usage_subject(authorization, x_pluto_guest_key)
    usage = consume_feature_usage(
        subject=subject,
        feature_key=request.featureKey,
        amount=max(1, int(request.amount or 1)),
        grant_credits=request.grantCredits or {},
    )
    return {
        "ok": True,
        "usage": usage,
    }


@router.post("/usage/consume-credit")
def consume_account_usage_credit(
    request: UsageCreditConsumeRequest,
    authorization: str | None = Header(default=None),
    x_pluto_guest_key: str | None = Header(default=None, alias="X-Pluto-Guest-Key"),
):
    subject = resolve_usage_subject(authorization, x_pluto_guest_key)
    usage = consume_credit_usage(
        subject=subject,
        credit_key=request.creditKey,
        amount=max(1, int(request.amount or 1)),
    )
    return {
        "ok": True,
        "usage": usage,
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


@router.post("/guest/ping")
def post_guest_activity_ping(
    request: Request,
    payload: dict = Body(default={}),
    x_pluto_guest_key: str | None = Header(default=None, alias="X-Pluto-Guest-Key"),
):
    guest_key = (x_pluto_guest_key or "").strip()
    if not guest_key:
        return {"ok": False, "reason": "guest_key_missing"}

    active_seconds = int(payload.get("activeSeconds") or 0)
    forwarded_for = request.headers.get("x-forwarded-for", "")
    forwarded_ip = forwarded_for.split(",")[0].strip() if forwarded_for else ""
    ip_address = forwarded_ip or (request.client.host if request.client else "")
    user_agent = request.headers.get("user-agent", "")

    try:
        update_guest_activity(
            guest_key=guest_key,
            active_seconds_delta=active_seconds,
            user_agent=user_agent,
            ip_address=ip_address,
        )
    except Exception:
        return {"ok": False, "reason": "guest_tracking_failed"}

    return {"ok": True}
