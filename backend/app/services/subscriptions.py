import json
import os
from pathlib import Path
from datetime import UTC, datetime
from typing import Optional

import requests


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_STATE_FILE = DATA_DIR / "billing_state.json"
ACTIVE_SUBSCRIPTION_STATUSES = {"active", "trialing"}


def _ensure_state_file() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    state_file = Path(os.getenv("PLUTO_BILLING_STATE_FILE", DEFAULT_STATE_FILE))
    state_file.parent.mkdir(parents=True, exist_ok=True)

    if not state_file.exists():
        state_file.write_text(
            json.dumps(
                {
                    "customers": {},
                    "subscriptions": {},
                    "events": [],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    return state_file


def _load_state() -> dict:
    state_file = _ensure_state_file()

    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        return {
            "customers": {},
            "subscriptions": {},
            "events": [],
        }


def _save_state(state: dict) -> None:
    state_file = _ensure_state_file()
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


def normalize_email(email: Optional[str]) -> str:
    return (email or "").strip().lower()


def _normalize_user_id(user_id: Optional[str]) -> str:
    return (user_id or "").strip()


def get_user_display_name(user: Optional[dict]) -> str:
    metadata = (user or {}).get("user_metadata") or {}
    return (
        metadata.get("full_name")
        or metadata.get("name")
        or "Pluto User"
    ).strip()


def get_subscription_store_mode() -> str:
    return (os.getenv("PLUTO_SUBSCRIPTION_STORE", "local") or "local").strip().lower()


def _can_use_supabase_store() -> bool:
    return (
        get_subscription_store_mode() == "supabase"
        and bool(os.getenv("SUPABASE_URL", "").strip())
        and bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip())
    )


def get_subscription_store_status() -> dict:
    mode = get_subscription_store_mode()
    supabase_env_ready = bool(os.getenv("SUPABASE_URL", "").strip()) and bool(
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    )

    status = {
        "mode": mode,
        "supabaseEnvReady": supabase_env_ready,
        "usingSupabase": False,
        "schemaReady": False,
        "profilesReady": False,
        "subscriptionsReady": False,
        "webhookEventsReady": False,
    }

    if mode != "supabase" or not supabase_env_ready:
        return status

    profiles_ready = _supabase_table_exists("profiles")
    subscriptions_ready = _supabase_table_exists("subscriptions")
    webhook_events_ready = _supabase_table_exists("billing_webhook_events")

    status.update(
        {
            "usingSupabase": profiles_ready and subscriptions_ready and webhook_events_ready,
            "schemaReady": profiles_ready and subscriptions_ready and webhook_events_ready,
            "profilesReady": profiles_ready,
            "subscriptionsReady": subscriptions_ready,
            "webhookEventsReady": webhook_events_ready,
        }
    )
    return status


def _get_supabase_rest_url(table: str) -> str:
    base = os.getenv("SUPABASE_URL", "").rstrip("/")
    return f"{base}/rest/v1/{table}"


def _get_supabase_headers(*, prefer: str = "") -> dict:
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json",
    }

    if prefer:
        headers["Prefer"] = prefer

    return headers


def _to_period_end_value(current_period_end: Optional[int]) -> Optional[str]:
    if current_period_end in (None, ""):
        return None

    try:
        return datetime.fromtimestamp(int(current_period_end), tz=UTC).isoformat()
    except Exception:
        return None


def _can_use_stripe_api() -> bool:
    return bool(os.getenv("STRIPE_SECRET_KEY", "").strip())


def _fetch_stripe_subscription(subscription_id: str) -> Optional[dict]:
    if not subscription_id or not _can_use_stripe_api():
        return None

    response = requests.get(
        f"https://api.stripe.com/v1/subscriptions/{subscription_id}",
        headers={
            "Authorization": f"Bearer {os.getenv('STRIPE_SECRET_KEY', '').strip()}",
        },
        timeout=15,
    )

    if response.status_code != 200:
        return None

    return response.json()


def _refresh_checkout_completed_record(record: Optional[dict]) -> Optional[dict]:
    if not record or record.get("status") != "checkout_completed":
        return record

    subscription_id = (record.get("subscription_id") or "").strip()
    customer_id = (record.get("customer_id") or "").strip()
    subscription = _fetch_stripe_subscription(subscription_id)
    if not subscription:
        return record

    metadata = subscription.get("metadata") or {}
    refreshed_status = (subscription.get("status") or "").strip() or "checkout_completed"
    refreshed_record = {
        "customer_id": customer_id or (subscription.get("customer") or "").strip(),
        "subscription_id": subscription_id,
        "status": refreshed_status,
        "plan_code": (metadata.get("plan") or record.get("plan_code") or "premium").strip(),
        "current_period_end": subscription.get("current_period_end"),
    }

    record_subscription_state(
        subscription_id=subscription_id,
        customer_id=refreshed_record["customer_id"],
        status=refreshed_status,
        plan_code=refreshed_record["plan_code"],
        email=(metadata.get("email") or record.get("email") or "").strip(),
        user_id=(metadata.get("user_id") or record.get("user_id") or "").strip(),
        current_period_end=subscription.get("current_period_end"),
        source_event="subscription_refresh",
    )

    return refreshed_record


def _supabase_select_single(table: str, params: dict) -> Optional[dict]:
    response = requests.get(
        _get_supabase_rest_url(table),
        headers=_get_supabase_headers(),
        params=params,
        timeout=15,
    )
    response.raise_for_status()
    rows = response.json()
    return rows[0] if rows else None


def _supabase_table_exists(table: str) -> bool:
    response = requests.get(
        _get_supabase_rest_url(table),
        headers=_get_supabase_headers(),
        params={"select": "*", "limit": "1"},
        timeout=15,
    )
    return response.status_code == 200


def _supabase_upsert_profile(
    *,
    user_id: str,
    email: str = "",
    stripe_customer_id: str = "",
    plan: str = "free",
    display_name: str = "",
) -> None:
    if not user_id:
        return

    payload = {
        "id": user_id,
        "email": normalize_email(email) or None,
        "plan": plan or "free",
    }

    if display_name:
        payload["display_name"] = display_name

    if stripe_customer_id:
        payload["stripe_customer_id"] = stripe_customer_id

    requests.post(
        _get_supabase_rest_url("profiles"),
        headers=_get_supabase_headers(prefer="resolution=merge-duplicates,return=minimal"),
        json=[payload],
        timeout=15,
    ).raise_for_status()


def _supabase_upsert_subscription(
    *,
    user_id: str,
    email: str,
    customer_id: str,
    subscription_id: str,
    status: str,
    plan_code: str,
    current_period_end: Optional[int],
    source_event: str,
) -> None:
    if not user_id or not subscription_id or not customer_id:
        return

    payload = {
        "user_id": user_id,
        "email": normalize_email(email) or None,
        "stripe_customer_id": customer_id,
        "stripe_subscription_id": subscription_id,
        "status": status or "inactive",
        "plan": plan_code or "premium",
        "current_period_end": _to_period_end_value(current_period_end),
        "source_event": source_event or None,
    }

    requests.post(
        _get_supabase_rest_url("subscriptions"),
        headers=_get_supabase_headers(prefer="resolution=merge-duplicates,return=minimal"),
        json=[payload],
        timeout=15,
    ).raise_for_status()


def _supabase_record_webhook_event(*, event_id: str, event_type: str) -> bool:
    existing = _supabase_select_single(
        "billing_webhook_events",
        {
            "select": "event_id",
            "event_id": f"eq.{event_id}",
            "limit": "1",
        },
    )

    if existing:
        return False

    requests.post(
        _get_supabase_rest_url("billing_webhook_events"),
        headers=_get_supabase_headers(prefer="return=minimal"),
        json=[
            {
                "event_id": event_id,
                "event_type": event_type or None,
            }
        ],
        timeout=15,
    ).raise_for_status()
    return True


def _get_customer_bucket(state: dict) -> dict:
    return state.setdefault("customers", {})


def _get_subscription_bucket(state: dict) -> dict:
    return state.setdefault("subscriptions", {})


def _get_event_bucket(state: dict) -> list:
    return state.setdefault("events", [])


def record_customer_link(*, customer_id: str, user_id: str = "", email: str = "") -> None:
    customer_id = (customer_id or "").strip()

    if not customer_id:
        return

    if _can_use_supabase_store():
        _supabase_upsert_profile(
            user_id=_normalize_user_id(user_id),
            email=email,
            stripe_customer_id=customer_id,
        )
        return

    state = _load_state()
    customers = _get_customer_bucket(state)
    existing = customers.get(customer_id, {})

    customers[customer_id] = {
        **existing,
        "customer_id": customer_id,
        "user_id": _normalize_user_id(user_id) or existing.get("user_id", ""),
        "email": normalize_email(email) or existing.get("email", ""),
    }
    _save_state(state)


def record_subscription_state(
    *,
    subscription_id: str,
    customer_id: str,
    status: str,
    plan_code: str = "premium",
    email: str = "",
    user_id: str = "",
    current_period_end: Optional[int] = None,
    source_event: str = "",
) -> None:
    subscription_id = (subscription_id or "").strip()

    if not subscription_id:
        return

    if _can_use_supabase_store():
        normalized_user_id = _normalize_user_id(user_id)
        status_value = (status or "").strip() or "inactive"
        plan_value = "premium" if status_value in ACTIVE_SUBSCRIPTION_STATUSES else "free"

        _supabase_upsert_profile(
            user_id=normalized_user_id,
            email=email,
            stripe_customer_id=(customer_id or "").strip(),
            plan=plan_value,
        )
        _supabase_upsert_subscription(
            user_id=normalized_user_id,
            email=email,
            customer_id=(customer_id or "").strip(),
            subscription_id=subscription_id,
            status=status_value,
            plan_code=plan_code or "premium",
            current_period_end=current_period_end,
            source_event=source_event,
        )
        return

    state = _load_state()
    subscriptions = _get_subscription_bucket(state)
    existing = subscriptions.get(subscription_id, {})

    subscriptions[subscription_id] = {
        **existing,
        "subscription_id": subscription_id,
        "customer_id": (customer_id or "").strip() or existing.get("customer_id", ""),
        "user_id": _normalize_user_id(user_id) or existing.get("user_id", ""),
        "email": normalize_email(email) or existing.get("email", ""),
        "status": (status or "").strip() or existing.get("status", "inactive"),
        "plan_code": (plan_code or "").strip() or existing.get("plan_code", "premium"),
        "current_period_end": current_period_end if current_period_end is not None else existing.get("current_period_end"),
        "source_event": source_event or existing.get("source_event", ""),
    }
    _save_state(state)


def record_webhook_event(*, event_id: str, event_type: str) -> bool:
    if not event_id:
        return False

    if _can_use_supabase_store():
        return _supabase_record_webhook_event(event_id=event_id, event_type=event_type)

    state = _load_state()
    events = _get_event_bucket(state)

    if any(item.get("event_id") == event_id for item in events):
        return False

    events.append(
        {
            "event_id": event_id,
            "event_type": event_type,
        }
    )
    state["events"] = events[-100:]
    _save_state(state)
    return True


def get_profile_record_for_user(user: Optional[dict]) -> Optional[dict]:
    if not user:
        return None

    user_id = _normalize_user_id(user.get("id"))
    email = normalize_email(user.get("email"))

    if _can_use_supabase_store():
        params = {
            "select": "id,email,display_name,plan,stripe_customer_id,updated_at",
            "limit": "1",
        }

        if user_id:
            params["id"] = f"eq.{user_id}"
        elif email:
            params["email"] = f"eq.{email}"
        else:
            return None

        return _supabase_select_single("profiles", params)

    return None


def get_customer_id_for_user(user: Optional[dict]) -> str:
    if not user:
        return ""

    user_id = _normalize_user_id(user.get("id"))
    email = normalize_email(user.get("email"))

    if _can_use_supabase_store():
        params = {
            "select": "stripe_customer_id",
            "limit": "1",
        }

        if user_id:
            params["id"] = f"eq.{user_id}"
        elif email:
            params["email"] = f"eq.{email}"
        else:
            return ""

        record = get_profile_record_for_user(user)
        return (record or {}).get("stripe_customer_id") or ""

    state = _load_state()

    for customer in _get_customer_bucket(state).values():
        if user_id and customer.get("user_id") == user_id:
            return customer.get("customer_id", "")
        if email and customer.get("email") == email:
            return customer.get("customer_id", "")

    return ""


def get_subscription_record_for_user(user: Optional[dict]) -> Optional[dict]:
    if not user:
        return None

    user_id = _normalize_user_id(user.get("id"))
    email = normalize_email(user.get("email"))
    customer_id = get_customer_id_for_user(user)

    if _can_use_supabase_store():
        params = {
            "select": "stripe_customer_id,stripe_subscription_id,status,plan,current_period_end",
            "order": "updated_at.desc",
            "limit": "1",
        }

        if user_id:
            params["user_id"] = f"eq.{user_id}"
        elif email:
            params["email"] = f"eq.{email}"
        elif customer_id:
            params["stripe_customer_id"] = f"eq.{customer_id}"
        else:
            return None

        record = _supabase_select_single("subscriptions", params)
        if not record:
            return None

        return _refresh_checkout_completed_record(
            {
            "customer_id": record.get("stripe_customer_id"),
            "subscription_id": record.get("stripe_subscription_id"),
            "status": record.get("status"),
            "plan_code": record.get("plan"),
            "current_period_end": record.get("current_period_end"),
            }
        )

    state = _load_state()

    for subscription in _get_subscription_bucket(state).values():
        if user_id and subscription.get("user_id") == user_id:
            return _refresh_checkout_completed_record(subscription)
        if email and subscription.get("email") == email:
            return _refresh_checkout_completed_record(subscription)
        if customer_id and subscription.get("customer_id") == customer_id:
            return _refresh_checkout_completed_record(subscription)

    return None


def resolve_subscription_plan_details(user: Optional[dict]) -> Optional[dict]:
    record = get_subscription_record_for_user(user)
    if record:
        if record.get("status") in ACTIVE_SUBSCRIPTION_STATUSES:
            return {
                "plan": "premium",
                "source": "subscription_record",
                "reason": "Plan resolved from an active subscription record.",
            }

        return {
            "plan": "free",
            "source": "subscription_record",
            "reason": "Plan resolved from a non-active subscription record.",
        }

    profile = get_profile_record_for_user(user)
    profile_plan = ((profile or {}).get("plan") or "").strip().lower()
    if profile_plan in {"free", "premium"}:
        return {
            "plan": profile_plan,
            "source": "profile_snapshot",
            "reason": "Plan resolved from the Supabase profile snapshot.",
        }

    return None


def resolve_subscription_plan(user: Optional[dict]) -> Optional[str]:
    details = resolve_subscription_plan_details(user)
    return details["plan"] if details else None


def ensure_profile_for_user(user: Optional[dict], *, plan: str = "free") -> None:
    if not user:
        return

    if not _can_use_supabase_store() or not _supabase_table_exists("profiles"):
        return

    user_id = _normalize_user_id(user.get("id"))
    if not user_id:
        return

    customer_id = get_customer_id_for_user(user)
    _supabase_upsert_profile(
        user_id=user_id,
        email=user.get("email") or "",
        stripe_customer_id=customer_id,
        plan=plan,
        display_name=get_user_display_name(user),
    )


def get_subscription_summary_for_user(user: Optional[dict]) -> dict:
    record = get_subscription_record_for_user(user)
    profile = get_profile_record_for_user(user)
    customer_id = (profile or {}).get("stripe_customer_id") or get_customer_id_for_user(user)

    if not record:
        return {
            "customerId": customer_id or None,
            "subscriptionId": None,
            "status": None,
            "plan": (profile or {}).get("plan") or None,
            "currentPeriodEnd": None,
        }

    return {
        "customerId": customer_id or record.get("customer_id") or None,
        "subscriptionId": record.get("subscription_id") or None,
        "status": record.get("status") or None,
        "plan": record.get("plan_code") or None,
        "currentPeriodEnd": record.get("current_period_end"),
    }
