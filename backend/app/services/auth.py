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

    if response.status_code != 200:
        return None

    return response.json()
