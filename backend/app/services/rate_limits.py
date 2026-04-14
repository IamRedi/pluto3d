import json
import math
import threading
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, Request

from app.services.auth import (
    decode_supabase_jwt_payload,
    extract_bearer_token,
    verify_supabase_user,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
STATE_FILE = DATA_DIR / "usage_state.json"
STATE_LOCK = threading.Lock()

FEATURE_POLICIES = {
    "ai_photo": {
        "label": "AI photo generation",
        "guest": {
            "cooldown_seconds": 20,
            "window_seconds": 600,
            "max_requests": 5,
        },
        "authenticated": {
            "cooldown_seconds": 12,
            "window_seconds": 600,
            "max_requests": 12,
        },
    },
    "svg_generation": {
        "label": "SVG generation",
        "guest": {
            "cooldown_seconds": 8,
            "window_seconds": 600,
            "max_requests": 10,
        },
        "authenticated": {
            "cooldown_seconds": 5,
            "window_seconds": 600,
            "max_requests": 24,
        },
    },
    "premium_3d": {
        "label": "Premium 3D generation",
        "guest": {
            "cooldown_seconds": 45,
            "window_seconds": 600,
            "max_requests": 2,
        },
        "authenticated": {
            "cooldown_seconds": 30,
            "window_seconds": 600,
            "max_requests": 6,
        },
    },
}


def _ensure_state_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        STATE_FILE.write_text(json.dumps({"buckets": {}, "rate_limits": {}}, indent=2), encoding="utf-8")


def _load_state() -> dict:
    _ensure_state_file()
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        state = {}

    if not isinstance(state, dict):
        state = {}

    state.setdefault("buckets", {})
    state.setdefault("rate_limits", {})
    return state


def _save_state(state: dict) -> None:
    _ensure_state_file()
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    forwarded_ip = forwarded_for.split(",")[0].strip() if forwarded_for else ""
    return forwarded_ip or (request.client.host if request.client else "") or "unknown"


def _build_guest_subject_key(request: Request, guest_key: str) -> str:
    if guest_key:
        return f"guest:{guest_key}"

    user_agent = (request.headers.get("user-agent") or "").strip().lower()
    ip_address = _get_client_ip(request)
    return f"guest:{ip_address}:{user_agent[:80]}"


def resolve_rate_limit_subject(
    *,
    request: Request,
    authorization: Optional[str] = None,
    guest_key: Optional[str] = None,
) -> dict:
    token = extract_bearer_token(authorization)
    if token:
        user = verify_supabase_user(token) or decode_supabase_jwt_payload(token) or {}
        user_id = (user.get("id") or "").strip()
        email = (user.get("email") or "").strip().lower()
        if user_id or email:
            return {
                "subject_type": "authenticated",
                "subject_key": f"user:{user_id or email}",
                "user_id": user_id or None,
                "email": email or None,
            }

    return {
        "subject_type": "guest",
        "subject_key": _build_guest_subject_key(request, (guest_key or "").strip()),
        "user_id": None,
        "email": None,
    }


def enforce_rate_limit(
    feature_key: str,
    *,
    request: Request,
    authorization: Optional[str] = None,
    guest_key: Optional[str] = None,
) -> None:
    feature_policy = FEATURE_POLICIES.get(feature_key)
    if not feature_policy:
        return

    subject = resolve_rate_limit_subject(
        request=request,
        authorization=authorization,
        guest_key=guest_key,
    )
    subject_policy = feature_policy[subject["subject_type"]]
    now = datetime.now(UTC)
    window_seconds = int(subject_policy["window_seconds"])
    cooldown_seconds = int(subject_policy["cooldown_seconds"])
    max_requests = int(subject_policy["max_requests"])
    bucket_key = f"{subject['subject_key']}::{feature_key}"

    with STATE_LOCK:
        state = _load_state()
        rate_limits = state.setdefault("rate_limits", {})
        entries = [
            entry
            for entry in rate_limits.get(bucket_key, [])
            if isinstance(entry, str)
        ]

        window_start = now - timedelta(seconds=window_seconds)
        recent_entries = []
        for entry in entries:
            try:
                parsed = datetime.fromisoformat(entry)
            except ValueError:
                continue

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=UTC)

            if parsed >= window_start:
                recent_entries.append(parsed)

        recent_entries.sort()

        if recent_entries:
            seconds_since_last = (now - recent_entries[-1]).total_seconds()
            if seconds_since_last < cooldown_seconds:
                retry_after = max(1, math.ceil(cooldown_seconds - seconds_since_last))
                _raise_rate_limit_error(feature_policy["label"], retry_after)

        if len(recent_entries) >= max_requests:
            retry_after = max(
                1,
                math.ceil(
                    window_seconds - (now - recent_entries[0]).total_seconds()
                ),
            )
            _raise_rate_limit_error(feature_policy["label"], retry_after)

        recent_entries.append(now)
        rate_limits[bucket_key] = [entry.isoformat() for entry in recent_entries]
        _save_state(state)


def _raise_rate_limit_error(feature_label: str, retry_after: int) -> None:
    raise HTTPException(
        status_code=429,
        detail={
            "error": "rate_limited",
            "message": (
                f"{feature_label} is being requested too quickly. "
                f"Wait {retry_after} seconds and try again."
            ),
            "retry_after_seconds": retry_after,
        },
        headers={"Retry-After": str(retry_after)},
    )
