import base64
import json
import os
from typing import Optional

import requests


def get_supabase_url() -> str:
    return os.getenv("SUPABASE_URL", "").rstrip("/")


def get_supabase_service_role_key() -> str:
    return os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


def extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None

    parts = authorization.strip().split(" ", 1)

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1].strip()
    return token or None


def verify_supabase_user(access_token: str) -> Optional[dict]:
    supabase_url = get_supabase_url()
    service_role_key = get_supabase_service_role_key()

    if not supabase_url or not service_role_key or not access_token:
        return None

    response = requests.get(
        f"{supabase_url}/auth/v1/user",
        headers={
            "apikey": service_role_key,
            "Authorization": f"Bearer {access_token}",
        },
        timeout=15,
    )

    if response.status_code == 200:
        user = response.json()
        user["_auth_source"] = "supabase_api"
        return user

    return decode_supabase_jwt_payload(access_token)


def decode_supabase_jwt_payload(access_token: str) -> Optional[dict]:
    try:
        parts = access_token.split(".")
        if len(parts) != 3:
            return None

        payload = parts[1]
        padding = "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding)
        data = json.loads(decoded.decode("utf-8"))
    except Exception:
        return None

    email = (data.get("email") or "").strip()
    user_id = data.get("sub")

    if not email and not user_id:
        return None

    return {
        "id": user_id,
        "email": email,
        "app_metadata": data.get("app_metadata") or {},
        "user_metadata": data.get("user_metadata") or {},
        "_auth_source": "jwt_fallback",
    }
