import json
import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from fastapi.testclient import TestClient


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
SMOKE_DIR = BACKEND_DIR / "data" / "_smoke"


def _load_backend_env() -> None:
    load_dotenv(BACKEND_DIR / ".env", override=True)


def _patch_auth_mocks() -> None:
    from app.routes import account
    from app.services import usage

    def mock_verify_supabase_user(token: str | None):
        normalized = (token or "").strip()
        if normalized == "smoke-free":
            return {
                "id": "smoke-free-user",
                "email": "free-smoke@pluto3d.app",
                "user_metadata": {"full_name": "Smoke Free"},
            }
        if normalized == "smoke-premium":
            return {
                "id": "smoke-premium-user",
                "email": "premium-smoke@pluto3d.app",
                "user_metadata": {"full_name": "Smoke Premium"},
            }
        return None

    def mock_plan_details(user: dict) -> dict:
        email = (user.get("email") or "").strip().lower()
        if email == "premium-smoke@pluto3d.app":
            return {
                "plan": "premium",
                "source": "smoke_mock",
                "reason": "Smoke script forced premium plan.",
            }
        return {
            "plan": "free",
            "source": "smoke_mock",
            "reason": "Smoke script forced free plan.",
        }

    def mock_ensure_profile_for_user(_user: dict, plan: str = "free") -> None:
        return

    usage.verify_supabase_user = mock_verify_supabase_user
    usage.resolve_user_plan_details = mock_plan_details
    usage.ensure_profile_for_user = mock_ensure_profile_for_user

    account.verify_supabase_user = mock_verify_supabase_user
    account.resolve_user_plan_details = mock_plan_details
    account.ensure_profile_for_user = mock_ensure_profile_for_user


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _run_quota_smoke() -> dict:
    _load_backend_env()

    original_usage_store = os.getenv("PLUTO_USAGE_STORE", "")
    original_usage_state_file = os.getenv("PLUTO_USAGE_STATE_FILE", "")
    original_subscription_store = os.getenv("PLUTO_SUBSCRIPTION_STORE", "")

    temp_state_file = SMOKE_DIR / "usage_state.json"
    shutil.rmtree(SMOKE_DIR, ignore_errors=True)
    SMOKE_DIR.mkdir(parents=True, exist_ok=True)

    try:
        os.environ["PLUTO_USAGE_STORE"] = "local"
        os.environ["PLUTO_USAGE_STATE_FILE"] = str(temp_state_file)
        os.environ["PLUTO_SUBSCRIPTION_STORE"] = "local"

        from app.main import app
        from app.services import usage

        usage._supabase_table_exists.cache_clear()
        _patch_auth_mocks()

        client = TestClient(app)

        guest_headers = {"X-Pluto-Guest-Key": "smoke-guest"}
        guest_usage = client.get("/api/account/usage", headers=guest_headers)
        _assert(guest_usage.status_code == 200, "Guest usage snapshot should load.")
        guest_data = guest_usage.json()
        _assert(guest_data["plan"] == "guest", "Guest plan should resolve to guest.")

        first_guest_consume = client.post(
            "/api/account/usage/consume",
            headers=guest_headers,
            json={
                "featureKey": "free3dGeneration",
                "grantCredits": {"test3dDownloadCredit": 1},
            },
        )
        _assert(first_guest_consume.status_code == 200, "Guest test 3D consume should succeed once.")
        first_guest_usage = first_guest_consume.json()["usage"]
        _assert(
            first_guest_usage["rules"]["free3dGeneration"]["used"] == 1,
            "Guest test 3D usage should increment to 1.",
        )
        _assert(
            first_guest_usage["credits"]["test3dDownloadCredit"] == 1,
            "Guest download credit grant should persist.",
        )

        guest_credit_consume = client.post(
            "/api/account/usage/consume-credit",
            headers=guest_headers,
            json={"creditKey": "test3dDownloadCredit"},
        )
        _assert(guest_credit_consume.status_code == 200, "Guest credit consume should succeed after grant.")
        _assert(
            guest_credit_consume.json()["usage"]["credits"]["test3dDownloadCredit"] == 0,
            "Guest download credit should decrement back to 0.",
        )

        for _index in range(2):
            response = client.post(
                "/api/account/usage/consume",
                headers=guest_headers,
                json={"featureKey": "aiImage"},
            )
            _assert(response.status_code == 200, "Guest AI image consume should succeed within limit.")

        guest_limit = client.post(
            "/api/account/usage/consume",
            headers=guest_headers,
            json={"featureKey": "aiImage"},
        )
        _assert(guest_limit.status_code == 429, "Guest AI image limit should block the third consume.")

        free_headers = {"Authorization": "Bearer smoke-free"}
        free_me = client.get("/api/account/me", headers=free_headers)
        _assert(free_me.status_code == 200, "Free account /api/account/me smoke should succeed.")
        free_me_data = free_me.json()
        _assert(free_me_data["authenticated"] is True, "Free account should resolve as authenticated.")
        _assert(free_me_data["plan"] == "free", "Free account plan should resolve to free.")

        for _index in range(3):
            response = client.post(
                "/api/account/usage/consume",
                headers=free_headers,
                json={"featureKey": "free3dGeneration"},
            )
            _assert(response.status_code == 200, "Free account test 3D consume should stay within weekly quota.")

        free_limit = client.post(
            "/api/account/usage/consume",
            headers=free_headers,
            json={"featureKey": "free3dGeneration"},
        )
        _assert(free_limit.status_code == 429, "Free account test 3D should block after 3 weekly uses.")

        premium_headers = {"Authorization": "Bearer smoke-premium"}
        premium_usage = client.get("/api/account/usage", headers=premium_headers)
        _assert(premium_usage.status_code == 200, "Premium usage snapshot should load.")
        premium_data = premium_usage.json()
        _assert(premium_data["plan"] == "premium", "Premium account plan should resolve to premium.")
        _assert(
            premium_data["rules"]["toyGeneration"]["limit"] is None,
            "Premium toy generation should remain unlimited.",
        )
        _assert(
            premium_data["downloadAccess"]["test3dModelDownload"]["allowed"] is True,
            "Premium download access should stay allowed.",
        )

        return {
            "guest": {
                "plan": guest_data["plan"],
                "free3dUsed": first_guest_usage["rules"]["free3dGeneration"]["used"],
                "downloadCreditsAfterGrant": first_guest_usage["credits"]["test3dDownloadCredit"],
                "aiImageThirdConsumeStatus": guest_limit.status_code,
            },
            "free": {
                "plan": free_me_data["plan"],
                "authenticated": free_me_data["authenticated"],
                "free3dFourthConsumeStatus": free_limit.status_code,
            },
            "premium": {
                "plan": premium_data["plan"],
                "toyGenerationLimit": premium_data["rules"]["toyGeneration"]["limit"],
                "downloadAllowed": premium_data["downloadAccess"]["test3dModelDownload"]["allowed"],
            },
        }
    finally:
        if original_usage_store:
            os.environ["PLUTO_USAGE_STORE"] = original_usage_store
        else:
            os.environ.pop("PLUTO_USAGE_STORE", None)

        if original_usage_state_file:
            os.environ["PLUTO_USAGE_STATE_FILE"] = original_usage_state_file
        else:
            os.environ.pop("PLUTO_USAGE_STATE_FILE", None)

        if original_subscription_store:
            os.environ["PLUTO_SUBSCRIPTION_STORE"] = original_subscription_store
        else:
            os.environ.pop("PLUTO_SUBSCRIPTION_STORE", None)

        shutil.rmtree(SMOKE_DIR, ignore_errors=True)


def _run_billing_readiness_snapshot() -> dict:
    _load_backend_env()

    from app.services.billing import get_billing_activation_handoff, get_billing_activation_status

    activation_status = get_billing_activation_status()
    activation_handoff = get_billing_activation_handoff()

    return {
        "activationReady": activation_status["activationReady"],
        "goLiveReady": activation_status["goLiveReady"],
        "stripeMode": activation_status["stripeMode"],
        "domainStatus": activation_status["domainStatus"],
        "subscriptionStore": activation_status["subscriptionStore"],
        "goLiveBlockers": activation_status["goLiveBlockers"],
        "currentPhase": activation_handoff["summary"]["currentPhase"],
        "verificationChecklist": activation_handoff["verificationChecklist"],
    }


def main() -> None:
    quota = _run_quota_smoke()
    billing = _run_billing_readiness_snapshot()
    print(
        json.dumps(
            {
                "quotaSmoke": quota,
                "billingReadiness": billing,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
