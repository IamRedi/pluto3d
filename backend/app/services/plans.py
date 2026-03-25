import os
from typing import Optional

from app.services.subscriptions import resolve_subscription_plan_details as resolve_subscription_plan_details_from_store


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
    return resolve_user_plan_details(user)["plan"]


def resolve_user_plan_details(user: Optional[dict]) -> dict:
    if not user:
        return {
            "plan": "guest",
            "source": "guest",
            "reason": "No authenticated user was available.",
        }

    subscription_details = resolve_subscription_plan_details_from_store(user)
    if subscription_details and subscription_details["source"] == "subscription_record":
        return {
            "plan": subscription_details["plan"],
            "source": subscription_details["source"],
            "reason": subscription_details["reason"],
        }

    email = (user.get("email") or "").strip().lower()
    if email and email in get_premium_emails():
        return {
            "plan": "premium",
            "source": "tester_email",
            "reason": "Plan resolved from PLUTO_PREMIUM_EMAILS fallback.",
        }

    if subscription_details:
        return {
            "plan": subscription_details["plan"],
            "source": subscription_details["source"],
            "reason": subscription_details["reason"],
        }

    app_plan = (user.get("app_metadata") or {}).get("plan")
    user_plan = (user.get("user_metadata") or {}).get("plan")
    plan = app_plan or user_plan or "free"

    if plan == "premium":
        return {
            "plan": "premium",
            "source": "supabase_metadata",
            "reason": "Plan resolved from Supabase auth metadata.",
        }

    return {
        "plan": "free",
        "source": "default_free",
        "reason": "No premium subscription or premium fallback matched.",
    }


def is_premium_plan(plan: str) -> bool:
    return plan == "premium"
