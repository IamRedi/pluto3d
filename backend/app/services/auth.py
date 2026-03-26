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

    try:
        response = requests.get(
            f"{supabase_url}/auth/v1/user",
            headers={
                "apikey": service_role_key,
                "Authorization": f"Bearer {access_token}",
            },
            timeout=15,
        )
    except requests.RequestException:
        return None

    if response.status_code == 200:
        user = response.json()
        claims = decode_supabase_jwt_payload(access_token)
        user = _merge_verified_user_with_token_claims(user, claims)
        user["_auth_source"] = "supabase_api"
        return user

    return None


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


def _merge_verified_user_with_token_claims(user: dict, claims: Optional[dict]) -> dict:
    if not claims:
        return user

    merged_user = dict(user)

    if not merged_user.get("email") and claims.get("email"):
        merged_user["email"] = claims["email"]

    if not merged_user.get("id") and claims.get("id"):
        merged_user["id"] = claims["id"]

    if not merged_user.get("app_metadata") and claims.get("app_metadata"):
        merged_user["app_metadata"] = claims["app_metadata"]

    if not merged_user.get("user_metadata") and claims.get("user_metadata"):
        merged_user["user_metadata"] = claims["user_metadata"]

    return merged_user
