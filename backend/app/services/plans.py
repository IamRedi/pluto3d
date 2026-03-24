import os
from typing import Optional


def get_premium_emails() -> set[str]:
    raw = os.getenv("PLUTO_PREMIUM_EMAILS", "")
    if not raw.strip():
        return set()

    return {
        email.strip().lower()
        for email in raw.split(",")
        if email.strip()
    }


def resolve_user_plan(user: Optional[dict]) -> str:
    if not user:
        return "guest"

    email = (user.get("email") or "").strip().lower()
    if email and email in get_premium_emails():
        return "premium"

    app_plan = (user.get("app_metadata") or {}).get("plan")
    user_plan = (user.get("user_metadata") or {}).get("plan")
    plan = app_plan or user_plan or "free"

    if plan == "premium":
        return "premium"

    return "free"


def is_premium_plan(plan: str) -> bool:
    return plan == "premium"
