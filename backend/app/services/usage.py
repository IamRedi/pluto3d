import json
import os
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import requests
from fastapi import HTTPException

from app.services.auth import extract_bearer_token, verify_supabase_user
from app.services.plans import resolve_user_plan_details
from app.services.subscriptions import ensure_profile_for_user


BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_STATE_FILE = DATA_DIR / "usage_state.json"
USAGE_TIMEZONE = os.getenv("PLUTO_USAGE_TIMEZONE", "Europe/Berlin").strip() or "Europe/Berlin"

USAGE_RULES = {
    "guest": {
        "aiImage": {"limit": 2, "period": "day"},
        "svgGeneration": {"limit": 1, "period": "day"},
        "toyGeneration": {"limit": 3, "period": "day"},
        "free3dGeneration": {"limit": 1, "period": "day"},
        "reliefStlGeneration": {"limit": 0, "period": "week"},
        "real3dGeneration": {"limit": 0, "period": "month"},
    },
    "free": {
        "aiImage": {"limit": 10, "period": "week"},
        "svgGeneration": {"limit": None, "period": None},
        "toyGeneration": {"limit": 10, "period": "week"},
        "free3dGeneration": {"limit": 3, "period": "week"},
        "reliefStlGeneration": {"limit": 5, "period": "week"},
        "real3dGeneration": {"limit": 0, "period": "month"},
    },
    "premium": {
        "aiImage": {"limit": 50, "period": "month"},
        "svgGeneration": {"limit": None, "period": None},
        "toyGeneration": {"limit": None, "period": None},
        "free3dGeneration": {"limit": None, "period": None},
        "reliefStlGeneration": {"limit": None, "period": None},
        "real3dGeneration": {"limit": 10, "period": "month"},
    },
}

DOWNLOAD_POLICY_RULES = {
    "test3dModelDownload": {
        "guest": "hidden",
        "free": "credit",
        "premium": "allow",
    }
}

FEATURE_LABELS = {
    "aiImage": "AI image generation",
    "svgGeneration": "SVG generation",
    "toyGeneration": "Toy generation",
    "free3dGeneration": "Test 3D generation",
    "reliefStlGeneration": "Relief STL export",
    "real3dGeneration": "Real 3D generation",
}

TRACKED_FEATURE_KEYS = tuple(FEATURE_LABELS.keys())
TRACKED_CREDIT_KEYS = ("test3dDownloadCredit",)


def _get_usage_clock() -> datetime:
    try:
        usage_timezone = ZoneInfo(USAGE_TIMEZONE)
        return datetime.now(usage_timezone)
    except Exception:
        return datetime.now(timezone.utc)


def _resolve_state_file_path(env_key: str, default_path: Path) -> Path:
    configured_value = (os.getenv(env_key, "") or "").strip()
    if not configured_value:
        return default_path

    configured_path = Path(configured_value)
    if configured_path.is_absolute():
        return configured_path

    if configured_path.parts and configured_path.parts[0].lower() == "backend":
        return REPO_ROOT / configured_path

    return BASE_DIR / configured_path


def _ensure_state_file() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    state_file = _resolve_state_file_path("PLUTO_USAGE_STATE_FILE", DEFAULT_STATE_FILE)
    state_file.parent.mkdir(parents=True, exist_ok=True)

    if not state_file.exists():
        state_file.write_text(json.dumps({"buckets": {}}, indent=2), encoding="utf-8")

    return state_file


def _load_state() -> dict:
    state_file = _ensure_state_file()

    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        return {"buckets": {}}


def _save_state(state: dict) -> None:
    state_file = _ensure_state_file()
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _normalize_guest_key(guest_key: Optional[str]) -> str:
    value = (guest_key or "").strip()
    return value or "guest-browser"


def get_usage_store_mode() -> str:
    return (os.getenv("PLUTO_USAGE_STORE", "auto") or "auto").strip().lower()


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


@lru_cache(maxsize=8)
def _supabase_table_exists(table: str) -> bool:
    response = requests.get(
        _get_supabase_rest_url(table),
        headers=_get_supabase_headers(),
        params={"select": "*", "limit": "1"},
        timeout=15,
    )
    return response.status_code == 200


def _is_usage_table_ready() -> bool:
    try:
        return _supabase_table_exists("usage_buckets")
    except Exception:
        return False


def _should_use_supabase_store() -> bool:
    mode = get_usage_store_mode()
    supabase_env_ready = bool(os.getenv("SUPABASE_URL", "").strip()) and bool(
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    )

    if mode == "local" or not supabase_env_ready:
        return False

    return _is_usage_table_ready()


def get_usage_store_status() -> dict:
    supabase_env_ready = bool(os.getenv("SUPABASE_URL", "").strip()) and bool(
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    )
    table_ready = _is_usage_table_ready() if supabase_env_ready else False

    return {
        "mode": get_usage_store_mode(),
        "supabaseEnvReady": supabase_env_ready,
        "usageBucketsReady": table_ready,
        "usingSupabase": supabase_env_ready and table_ready and get_usage_store_mode() != "local",
    }


def _make_bucket_key(*, subject_key: str, bucket_type: str, feature_key: str, window_key: str) -> str:
    return f"{subject_key}::{bucket_type}::{feature_key}::{window_key}"


def _read_local_bucket(
    *,
    subject_key: str,
    bucket_type: str,
    feature_key: str,
    window_key: str,
) -> dict:
    state = _load_state()
    key = _make_bucket_key(
        subject_key=subject_key,
        bucket_type=bucket_type,
        feature_key=feature_key,
        window_key=window_key,
    )
    return (state.get("buckets") or {}).get(key, {})


def _write_local_bucket(
    *,
    subject_key: str,
    subject_type: str,
    user_id: str,
    bucket_type: str,
    feature_key: str,
    period: Optional[str],
    window_key: str,
    count: int,
) -> None:
    state = _load_state()
    buckets = state.setdefault("buckets", {})
    key = _make_bucket_key(
        subject_key=subject_key,
        bucket_type=bucket_type,
        feature_key=feature_key,
        window_key=window_key,
    )
    buckets[key] = {
        "subject_key": subject_key,
        "subject_type": subject_type,
        "user_id": user_id or None,
        "bucket_type": bucket_type,
        "feature_key": feature_key,
        "period": period,
        "window_key": window_key,
        "count": max(0, int(count or 0)),
    }
    _save_state(state)


def _supabase_select_bucket(
    *,
    subject_key: str,
    bucket_type: str,
    feature_key: str,
    window_key: str,
) -> Optional[dict]:
    response = requests.get(
        _get_supabase_rest_url("usage_buckets"),
        headers=_get_supabase_headers(),
        params={
            "select": "id,count",
            "subject_key": f"eq.{subject_key}",
            "bucket_type": f"eq.{bucket_type}",
            "feature_key": f"eq.{feature_key}",
            "window_key": f"eq.{window_key}",
            "limit": "1",
        },
        timeout=15,
    )
    response.raise_for_status()
    rows = response.json()
    return rows[0] if rows else None


def _write_supabase_bucket(
    *,
    subject_key: str,
    subject_type: str,
    user_id: str,
    bucket_type: str,
    feature_key: str,
    period: Optional[str],
    window_key: str,
    count: int,
) -> None:
    existing = _supabase_select_bucket(
        subject_key=subject_key,
        bucket_type=bucket_type,
        feature_key=feature_key,
        window_key=window_key,
    )

    payload = {
        "subject_key": subject_key,
        "subject_type": subject_type,
        "user_id": user_id or None,
        "bucket_type": bucket_type,
        "feature_key": feature_key,
        "period": period,
        "window_key": window_key,
        "count": max(0, int(count or 0)),
    }

    if existing:
        response = requests.patch(
            _get_supabase_rest_url("usage_buckets"),
            headers=_get_supabase_headers(prefer="return=minimal"),
            params={"id": f"eq.{existing.get('id')}"},
            json={"count": payload["count"]},
            timeout=15,
        )
        response.raise_for_status()
        return

    response = requests.post(
        _get_supabase_rest_url("usage_buckets"),
        headers=_get_supabase_headers(prefer="resolution=merge-duplicates,return=minimal"),
        json=[payload],
        timeout=15,
    )
    response.raise_for_status()


def _read_bucket(
    *,
    subject_key: str,
    bucket_type: str,
    feature_key: str,
    window_key: str,
) -> dict:
    if _should_use_supabase_store():
        try:
            return _supabase_select_bucket(
                subject_key=subject_key,
                bucket_type=bucket_type,
                feature_key=feature_key,
                window_key=window_key,
            ) or {}
        except Exception:
            return _read_local_bucket(
                subject_key=subject_key,
                bucket_type=bucket_type,
                feature_key=feature_key,
                window_key=window_key,
            )

    return _read_local_bucket(
        subject_key=subject_key,
        bucket_type=bucket_type,
        feature_key=feature_key,
        window_key=window_key,
    )


def _write_bucket(
    *,
    subject_key: str,
    subject_type: str,
    user_id: str,
    bucket_type: str,
    feature_key: str,
    period: Optional[str],
    window_key: str,
    count: int,
) -> None:
    if _should_use_supabase_store():
        try:
            _write_supabase_bucket(
                subject_key=subject_key,
                subject_type=subject_type,
                user_id=user_id,
                bucket_type=bucket_type,
                feature_key=feature_key,
                period=period,
                window_key=window_key,
                count=count,
            )
            return
        except Exception:
            pass

    _write_local_bucket(
        subject_key=subject_key,
        subject_type=subject_type,
        user_id=user_id,
        bucket_type=bucket_type,
        feature_key=feature_key,
        period=period,
        window_key=window_key,
        count=count,
    )


def get_usage_window_key(period: Optional[str]) -> str:
    if not period:
        return "lifetime"

    now = _get_usage_clock()

    if period == "day":
        return now.strftime("%Y-%m-%d")

    if period == "month":
        return now.strftime("%Y-%m")

    if period == "week":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start = start - timedelta(days=start.weekday())
        return start.strftime("%Y-%m-%d")

    return "lifetime"


def get_usage_rule(plan: str, feature_key: str) -> dict:
    return USAGE_RULES.get(plan or "guest", {}).get(feature_key, {"limit": None, "period": None})


def _get_bucket_count(
    *,
    subject: dict,
    bucket_type: str,
    feature_key: str,
    period: Optional[str],
) -> int:
    window_key = get_usage_window_key(period)
    entry = _read_bucket(
        subject_key=subject["subject_key"],
        bucket_type=bucket_type,
        feature_key=feature_key,
        window_key=window_key,
    )
    return max(0, int(entry.get("count") or 0))


def _set_bucket_count(
    *,
    subject: dict,
    bucket_type: str,
    feature_key: str,
    period: Optional[str],
    count: int,
) -> None:
    _write_bucket(
        subject_key=subject["subject_key"],
        subject_type=subject["subject_type"],
        user_id=subject.get("user_id") or "",
        bucket_type=bucket_type,
        feature_key=feature_key,
        period=period,
        window_key=get_usage_window_key(period),
        count=count,
    )


def get_feature_usage_count(subject: dict, feature_key: str) -> int:
    rule = get_usage_rule(subject["plan"], feature_key)
    return _get_bucket_count(
        subject=subject,
        bucket_type="counter",
        feature_key=feature_key,
        period=rule.get("period"),
    )


def get_credit_count(subject: dict, credit_key: str) -> int:
    return _get_bucket_count(
        subject=subject,
        bucket_type="credit",
        feature_key=credit_key,
        period=None,
    )


def _feature_summary(subject: dict, feature_key: str) -> dict:
    rule = get_usage_rule(subject["plan"], feature_key)
    used = get_feature_usage_count(subject, feature_key)
    limit = rule.get("limit")
    remaining = None if limit is None else max(0, limit - used)

    return {
        "limit": limit,
        "period": rule.get("period"),
        "used": used,
        "remaining": remaining,
    }


def get_download_policy(subject: dict, policy_key: str) -> str:
    return DOWNLOAD_POLICY_RULES.get(policy_key, {}).get(subject["plan"], "allow")


def get_download_access(subject: dict, policy_key: str) -> dict:
    policy = get_download_policy(subject, policy_key)

    if policy == "hidden":
        return {
            "policy": policy,
            "visible": False,
            "allowed": False,
            "reason": "Sign in to download this test model.",
            "remaining": 0,
        }

    if policy == "credit":
        credits = get_credit_count(subject, "test3dDownloadCredit")
        return {
            "policy": policy,
            "visible": True,
            "allowed": credits > 0,
            "reason": "" if credits > 0 else "Your test-model download credit has already been used.",
            "remaining": credits,
        }

    return {
        "policy": policy,
        "visible": True,
        "allowed": True,
        "reason": "",
        "remaining": None,
    }


def build_usage_snapshot(subject: dict) -> dict:
    rules = {
        feature_key: _feature_summary(subject, feature_key)
        for feature_key in TRACKED_FEATURE_KEYS
    }
    credits = {
        credit_key: get_credit_count(subject, credit_key)
        for credit_key in TRACKED_CREDIT_KEYS
    }

    return {
        "plan": subject["plan"],
        "subjectType": subject["subject_type"],
        "subjectKey": subject["subject_key"],
        "rules": rules,
        "credits": credits,
        "downloadAccess": {
            "test3dModelDownload": get_download_access(subject, "test3dModelDownload"),
        },
        "store": get_usage_store_status(),
    }


def _limit_reached_message(feature_key: str, period: Optional[str]) -> str:
    label = FEATURE_LABELS.get(feature_key, feature_key)
    if period:
        return f"{label} limit reached for the current {period}."
    return f"{label} limit reached."


def ensure_feature_allowed(subject: dict, feature_key: str, amount: int = 1) -> dict:
    rule = get_usage_rule(subject["plan"], feature_key)
    limit = rule.get("limit")

    if limit is not None and limit <= 0:
        raise HTTPException(
            status_code=403,
            detail=f"{FEATURE_LABELS.get(feature_key, feature_key)} is not available for the {subject['plan']} plan.",
        )

    used = get_feature_usage_count(subject, feature_key)
    if limit is not None and used + amount > limit:
        raise HTTPException(
            status_code=429,
            detail=_limit_reached_message(feature_key, rule.get("period")),
        )

    return rule


def consume_feature_usage(
    *,
    subject: dict,
    feature_key: str,
    amount: int = 1,
    grant_credits: Optional[dict] = None,
) -> dict:
    rule = ensure_feature_allowed(subject, feature_key, amount=amount)
    used = get_feature_usage_count(subject, feature_key)
    _set_bucket_count(
        subject=subject,
        bucket_type="counter",
        feature_key=feature_key,
        period=rule.get("period"),
        count=used + amount,
    )

    for credit_key, credit_amount in (grant_credits or {}).items():
        if int(credit_amount or 0) <= 0:
            continue
        current_credit_count = get_credit_count(subject, credit_key)
        _set_bucket_count(
            subject=subject,
            bucket_type="credit",
            feature_key=credit_key,
            period=None,
            count=current_credit_count + int(credit_amount),
        )

    return build_usage_snapshot(subject)


def consume_credit_usage(
    *,
    subject: dict,
    credit_key: str,
    amount: int = 1,
) -> dict:
    available = get_credit_count(subject, credit_key)
    if available < amount:
        raise HTTPException(
            status_code=429,
            detail="Your test-model download credit has already been used.",
        )

    _set_bucket_count(
        subject=subject,
        bucket_type="credit",
        feature_key=credit_key,
        period=None,
        count=max(0, available - amount),
    )
    return build_usage_snapshot(subject)


def resolve_usage_subject(authorization: Optional[str], guest_key: Optional[str]) -> dict:
    token = extract_bearer_token(authorization)

    if token:
        user = verify_supabase_user(token)
        if user:
            plan_details = resolve_user_plan_details(user)
            ensure_profile_for_user(user, plan=plan_details["plan"])
            user_id = (user.get("id") or "").strip()
            return {
                "subject_type": "user",
                "subject_key": f"user:{user_id}",
                "user_id": user_id,
                "guest_key": None,
                "plan": plan_details["plan"],
                "user": user,
                "planSource": plan_details["source"],
                "planReason": plan_details["reason"],
            }

    normalized_guest_key = _normalize_guest_key(guest_key)
    return {
        "subject_type": "guest",
        "subject_key": f"guest:{normalized_guest_key}",
        "user_id": "",
        "guest_key": normalized_guest_key,
        "plan": "guest",
        "user": None,
        "planSource": "guest",
        "planReason": "No authenticated user was available.",
    }
