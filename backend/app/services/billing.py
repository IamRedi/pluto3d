import os
from typing import Optional
from urllib.parse import urlparse

import requests
from app.services.subscriptions import get_subscription_store_status


def _build_completion_summary(items: list[dict], *, configured_key: str = "configured") -> dict:
    completed = sum(1 for item in items if item.get(configured_key))
    total = len(items)
    percent = int((completed / total) * 100) if total else 0
    return {
        "completed": completed,
        "total": total,
        "percent": percent,
    }


def _resolve_switch_phase(
    *,
    frontend_summary: dict,
    backend_env_summary: dict,
    schema_summary: dict,
    subscription_store_mode: str,
    activation_ready: bool,
) -> dict:
    if frontend_summary["completed"] < frontend_summary["total"]:
        return {
            "key": "frontend_public_config",
            "label": "Awaiting frontend config",
            "detail": "Frontend public install values still need to be finalized.",
        }

    if backend_env_summary["completed"] < backend_env_summary["total"]:
        return {
            "key": "backend_env",
            "label": "Awaiting backend env",
            "detail": "Backend Supabase and Stripe env values still need to be finalized.",
        }

    if schema_summary["completed"] < schema_summary["total"]:
        return {
            "key": "supabase_schema",
            "label": "Awaiting schema",
            "detail": "Supabase billing schema still needs to be fully ready.",
        }

    if subscription_store_mode != "supabase":
        return {
            "key": "subscription_store_switch",
            "label": "Awaiting store switch",
            "detail": "The billing store is still not switched to Supabase mode.",
        }

    if not activation_ready:
        return {
            "key": "activation_blockers",
            "label": "Awaiting final blockers",
            "detail": "Configuration is close, but activation blockers still need to be cleared.",
        }

    return {
        "key": "live_verification",
        "label": "Ready for live verification",
        "detail": "The system is configured and ready for checkout, webhook, and portal smoke tests.",
    }


def get_stripe_secret_key() -> str:
    return os.getenv("STRIPE_SECRET_KEY", "").strip()


def get_stripe_publishable_key() -> str:
    return os.getenv("STRIPE_PUBLISHABLE_KEY", "").strip()


def get_stripe_premium_price_id() -> str:
    return os.getenv("STRIPE_PREMIUM_PRICE_ID", "").strip()


def get_stripe_success_url() -> str:
    return os.getenv("STRIPE_SUCCESS_URL", "").strip()


def get_stripe_cancel_url() -> str:
    return os.getenv("STRIPE_CANCEL_URL", "").strip()


def get_stripe_portal_return_url() -> str:
    return os.getenv("STRIPE_PORTAL_RETURN_URL", "").strip()


def _detect_key_mode(value: str, *, live_prefix: str, test_prefix: str) -> str:
    normalized = (value or "").strip()
    if not normalized:
        return "missing"
    if normalized.startswith(live_prefix):
        return "live"
    if normalized.startswith(test_prefix):
        return "test"
    return "unknown"


def get_stripe_mode() -> dict:
    secret_mode = _detect_key_mode(
        get_stripe_secret_key(),
        live_prefix="sk_live_",
        test_prefix="sk_test_",
    )
    publishable_mode = _detect_key_mode(
        get_stripe_publishable_key(),
        live_prefix="pk_live_",
        test_prefix="pk_test_",
    )

    concrete_modes = {
        mode
        for mode in [secret_mode, publishable_mode]
        if mode in {"live", "test"}
    }

    if not concrete_modes:
        overall = "unconfigured"
    elif len(concrete_modes) > 1:
        overall = "mixed"
    else:
        overall = next(iter(concrete_modes))

    return {
        "mode": overall,
        "secretKeyMode": secret_mode,
        "publishableKeyMode": publishable_mode,
    }


def _classify_return_url_mode(url: str) -> str:
    parsed = urlparse((url or "").strip())
    hostname = (parsed.hostname or "").strip().lower()

    if not hostname:
        return "missing"

    if hostname in {"127.0.0.1", "localhost"}:
        return "local"

    if hostname.endswith(".vercel.app"):
        return "temporary"

    return "custom"


def get_billing_domain_status() -> dict:
    success_mode = _classify_return_url_mode(get_stripe_success_url())
    cancel_mode = _classify_return_url_mode(get_stripe_cancel_url())
    portal_mode = _classify_return_url_mode(get_stripe_portal_return_url())
    concrete_modes = {mode for mode in [success_mode, cancel_mode, portal_mode] if mode != "missing"}

    if not concrete_modes:
        overall = "missing"
    elif len(concrete_modes) > 1:
        overall = "mixed"
    else:
        overall = next(iter(concrete_modes))

    return {
        "mode": overall,
        "successUrlMode": success_mode,
        "cancelUrlMode": cancel_mode,
        "portalReturnUrlMode": portal_mode,
    }


def is_stripe_ready() -> bool:
    return bool(
        get_stripe_secret_key()
        and get_stripe_premium_price_id()
        and get_stripe_success_url()
        and get_stripe_cancel_url()
    )


def get_billing_activation_status() -> dict:
    subscription_store = get_subscription_store_status()
    stripe_mode = get_stripe_mode()
    domain_status = get_billing_domain_status()
    webhook_secret_configured = bool(os.getenv("STRIPE_WEBHOOK_SECRET", "").strip())
    blockers = []
    go_live_blockers = []

    if not get_stripe_secret_key():
        blockers.append("Missing STRIPE_SECRET_KEY")

    if not get_stripe_publishable_key():
        blockers.append("Missing STRIPE_PUBLISHABLE_KEY")

    if not get_stripe_premium_price_id():
        blockers.append("Missing STRIPE_PREMIUM_PRICE_ID")

    if not get_stripe_success_url():
        blockers.append("Missing STRIPE_SUCCESS_URL")

    if not get_stripe_cancel_url():
        blockers.append("Missing STRIPE_CANCEL_URL")

    if not get_stripe_portal_return_url():
        blockers.append("Missing STRIPE_PORTAL_RETURN_URL")

    if not webhook_secret_configured:
        blockers.append("Missing STRIPE_WEBHOOK_SECRET")

    if stripe_mode["mode"] != "live":
        if stripe_mode["mode"] == "test":
            go_live_blockers.append("Stripe is still configured in test mode.")
        elif stripe_mode["mode"] == "mixed":
            go_live_blockers.append("Stripe keys are mixed between test and live modes.")
        else:
            go_live_blockers.append("Stripe mode is not yet ready for live billing.")

    if domain_status["mode"] != "custom":
        if domain_status["mode"] == "temporary":
            go_live_blockers.append("Billing return URLs still point to a temporary Vercel domain.")
        elif domain_status["mode"] == "local":
            go_live_blockers.append("Billing return URLs still point to localhost.")
        elif domain_status["mode"] == "mixed":
            go_live_blockers.append("Billing return URLs are split across temporary and custom domains.")
        else:
            go_live_blockers.append("Billing return URLs still need a final custom domain.")

    if subscription_store["mode"] == "supabase":
        if not subscription_store["supabaseEnvReady"]:
            blockers.append("Supabase env is not fully configured for subscription persistence")
        if not subscription_store["profilesReady"]:
            blockers.append("Supabase profiles table is not ready")
        if not subscription_store["subscriptionsReady"]:
            blockers.append("Supabase subscriptions table is not ready")
        if not subscription_store["webhookEventsReady"]:
            blockers.append("Supabase billing_webhook_events table is not ready")

    next_steps = []

    if not get_stripe_secret_key() or not get_stripe_publishable_key():
        next_steps.append("Add the Stripe secret and publishable keys to backend env.")

    if not get_stripe_premium_price_id():
        next_steps.append("Create the Stripe Premium price and add STRIPE_PREMIUM_PRICE_ID.")

    if not get_stripe_success_url() or not get_stripe_cancel_url() or not get_stripe_portal_return_url():
        next_steps.append("Configure Stripe success, cancel, and portal return URLs.")

    if not webhook_secret_configured:
        next_steps.append("Create the Stripe webhook endpoint secret and add STRIPE_WEBHOOK_SECRET.")

    if subscription_store["mode"] != "supabase":
        next_steps.append("Switch PLUTO_SUBSCRIPTION_STORE to supabase when you are ready for production persistence.")
    elif not subscription_store["schemaReady"]:
        next_steps.append("Apply backend/supabase_billing_schema.sql so the Supabase billing tables are ready.")

    if not next_steps:
        next_steps.append("Run an end-to-end checkout and webhook test in the target environment.")

    checklist = [
        {
            "key": "stripe_secret_key",
            "label": "Stripe secret key configured",
            "done": bool(get_stripe_secret_key()),
        },
        {
            "key": "stripe_publishable_key",
            "label": "Stripe publishable key configured",
            "done": bool(get_stripe_publishable_key()),
        },
        {
            "key": "stripe_price_id",
            "label": "Stripe premium price ID configured",
            "done": bool(get_stripe_premium_price_id()),
        },
        {
            "key": "stripe_success_url",
            "label": "Stripe success URL configured",
            "done": bool(get_stripe_success_url()),
        },
        {
            "key": "stripe_cancel_url",
            "label": "Stripe cancel URL configured",
            "done": bool(get_stripe_cancel_url()),
        },
        {
            "key": "stripe_portal_return_url",
            "label": "Stripe portal return URL configured",
            "done": bool(get_stripe_portal_return_url()),
        },
        {
            "key": "stripe_webhook_secret",
            "label": "Stripe webhook secret configured",
            "done": webhook_secret_configured,
        },
        {
            "key": "subscription_store_mode",
            "label": f"Subscription store mode: {subscription_store['mode']}",
            "done": True,
        },
        {
            "key": "subscription_store_schema",
            "label": "Subscription store schema ready",
            "done": subscription_store["mode"] != "supabase" or subscription_store["schemaReady"],
        },
    ]

    completed_steps = sum(1 for item in checklist if item["done"])
    total_steps = len(checklist)
    progress_percent = int((completed_steps / total_steps) * 100) if total_steps else 0

    if len(blockers) == 0:
        progress_label = "Activation ready"
        progress_detail = "Billing activation requirements are complete. The next step is an end-to-end checkout and webhook verification."
    elif completed_steps == 0:
        progress_label = "Scaffold only"
        progress_detail = "Billing is still in scaffold mode. Live Stripe and persistence settings still need to be configured."
    elif completed_steps < total_steps:
        progress_label = "Activation in progress"
        progress_detail = f"{completed_steps} of {total_steps} billing activation checks are complete."
    else:
        progress_label = "Verification pending"
        progress_detail = "Configuration is present, but blockers still need review before activation."

    return {
        "activationReady": len(blockers) == 0,
        "goLiveReady": len(blockers) == 0 and len(go_live_blockers) == 0,
        "blockers": blockers,
        "goLiveBlockers": go_live_blockers,
        "nextSteps": next_steps,
        "checklist": checklist,
        "progress": {
            "completed": completed_steps,
            "total": total_steps,
            "percent": progress_percent,
            "label": progress_label,
            "detail": progress_detail,
        },
        "subscriptionStore": subscription_store,
        "stripeMode": stripe_mode,
        "domainStatus": domain_status,
    }


def get_billing_public_config() -> dict:
    activation_status = get_billing_activation_status()
    subscription_store = activation_status["subscriptionStore"]
    webhook_secret_configured = bool(os.getenv("STRIPE_WEBHOOK_SECRET", "").strip())

    return {
        "provider": "stripe",
        "ready": is_stripe_ready(),
        "activationReady": activation_status["activationReady"],
        "publishableKeyConfigured": bool(get_stripe_publishable_key()),
        "priceConfigured": bool(get_stripe_premium_price_id()),
        "successUrlConfigured": bool(get_stripe_success_url()),
        "cancelUrlConfigured": bool(get_stripe_cancel_url()),
        "portalReturnUrlConfigured": bool(get_stripe_portal_return_url()),
        "webhookSecretConfigured": webhook_secret_configured,
        "subscriptionStore": subscription_store,
        "activationChecklist": activation_status["checklist"],
        "activationProgress": activation_status["progress"],
        "activationBlockers": activation_status["blockers"],
        "goLiveReady": activation_status["goLiveReady"],
        "goLiveBlockers": activation_status["goLiveBlockers"],
        "activationNextSteps": activation_status["nextSteps"],
        "stripeMode": activation_status["stripeMode"],
        "domainStatus": activation_status["domainStatus"],
        "premiumPlan": {
            "code": "premium-monthly",
            "name": "Pluto3D Premium",
            "priceLabel": "$19 / month target",
        },
    }


def get_billing_activation_handoff() -> dict:
    activation_status = get_billing_activation_status()
    subscription_store = activation_status["subscriptionStore"]
    frontend_public_config = [
        {
            "key": "appName",
            "location": "frontend/app-config.js",
            "required": True,
            "description": "Public product brand name.",
        },
        {
            "key": "studioName",
            "location": "frontend/app-config.js",
            "required": True,
            "description": "Public studio/product title.",
        },
        {
            "key": "siteUrl",
            "location": "frontend/app-config.js",
            "required": True,
            "description": "Public frontend launch domain.",
        },
        {
            "key": "apiBase",
            "location": "frontend/app-config.js",
            "required": True,
            "description": "Public backend API domain.",
        },
        {
            "key": "supportEmail",
            "location": "frontend/app-config.js",
            "required": True,
            "description": "Public support contact for the install.",
        },
        {
            "key": "auth.supabaseUrl",
            "location": "frontend/app-config.js",
            "required": True,
            "description": "Supabase project URL for public auth setup.",
        },
        {
            "key": "auth.supabasePublishableKey",
            "location": "frontend/app-config.js",
            "required": True,
            "description": "Supabase public auth key.",
        },
    ]
    backend_env = [
        {
            "key": "SUPABASE_URL",
            "required": True,
            "configured": bool(os.getenv("SUPABASE_URL", "").strip()),
            "description": "Supabase project URL for backend verification and persistence.",
        },
        {
            "key": "SUPABASE_SERVICE_ROLE_KEY",
            "required": True,
            "configured": bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()),
            "description": "Supabase service role key for backend auth and billing persistence.",
        },
        {
            "key": "STRIPE_SECRET_KEY",
            "required": True,
            "configured": bool(get_stripe_secret_key()),
            "description": "Stripe secret key for checkout, portal, and webhook handling.",
        },
        {
            "key": "STRIPE_PUBLISHABLE_KEY",
            "required": True,
            "configured": bool(get_stripe_publishable_key()),
            "description": "Stripe publishable key used by install/runtime metadata.",
        },
        {
            "key": "STRIPE_PREMIUM_PRICE_ID",
            "required": True,
            "configured": bool(get_stripe_premium_price_id()),
            "description": "Stripe recurring price ID for Pluto3D Premium.",
        },
        {
            "key": "STRIPE_WEBHOOK_SECRET",
            "required": True,
            "configured": bool(os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()),
            "description": "Stripe webhook endpoint secret.",
        },
        {
            "key": "STRIPE_SUCCESS_URL",
            "required": True,
            "configured": bool(get_stripe_success_url()),
            "description": "URL used after successful checkout.",
        },
        {
            "key": "STRIPE_CANCEL_URL",
            "required": True,
            "configured": bool(get_stripe_cancel_url()),
            "description": "URL used after canceled checkout.",
        },
        {
            "key": "STRIPE_PORTAL_RETURN_URL",
            "required": True,
            "configured": bool(get_stripe_portal_return_url()),
            "description": "URL used after leaving Stripe billing portal.",
        },
        {
            "key": "PLUTO_SUBSCRIPTION_STORE",
            "required": True,
            "configured": True,
            "description": "Use local for scaffold or supabase for production persistence.",
            "currentValue": subscription_store["mode"],
        },
    ]
    schema_checks = [
        {
            "key": "profiles",
            "configured": subscription_store["profilesReady"],
            "description": "Supabase profiles table is ready.",
        },
        {
            "key": "subscriptions",
            "configured": subscription_store["subscriptionsReady"],
            "description": "Supabase subscriptions table is ready.",
        },
        {
            "key": "billing_webhook_events",
            "configured": subscription_store["webhookEventsReady"],
            "description": "Supabase billing_webhook_events table is ready.",
        },
    ]
    backend_env_summary = _build_completion_summary(backend_env)
    schema_summary = _build_completion_summary(schema_checks)
    frontend_summary = _build_completion_summary(
        [{**item, "configured": False} for item in frontend_public_config]
    )
    switch_path = [
        {
            "key": "frontend_public_config",
            "label": "Frontend public config",
            "description": "Fill the public brand, API, support, and Supabase values in frontend/app-config.js.",
            "status": "external",
        },
        {
            "key": "backend_env",
            "label": "Backend env",
            "description": "Fill backend Stripe and Supabase env values.",
            "status": "ready" if backend_env_summary["completed"] == backend_env_summary["total"] else "pending",
        },
        {
            "key": "supabase_schema",
            "label": "Supabase schema",
            "description": "Apply the billing schema so profiles, subscriptions, and webhook events are ready.",
            "status": "ready" if schema_summary["completed"] == schema_summary["total"] else "pending",
        },
        {
            "key": "subscription_store_switch",
            "label": "Subscription store switch",
            "description": "Set PLUTO_SUBSCRIPTION_STORE to supabase for production persistence.",
            "status": "ready" if subscription_store["mode"] == "supabase" else "pending",
        },
        {
            "key": "live_verification",
            "label": "Live verification",
            "description": "Run checkout, webhook, account, and portal smoke tests in the target environment.",
            "status": "ready" if activation_status["activationReady"] else "pending",
        },
    ]
    current_phase = _resolve_switch_phase(
        frontend_summary=frontend_summary,
        backend_env_summary=backend_env_summary,
        schema_summary=schema_summary,
        subscription_store_mode=subscription_store["mode"],
        activation_ready=activation_status["activationReady"],
    )
    verification_checklist = [
        {
            "key": "account_smoke_test",
            "label": "Run authenticated /api/account/me smoke test",
            "status": "pending" if activation_status["activationReady"] else "blocked",
        },
        {
            "key": "checkout_smoke_test",
            "label": "Run the first Stripe checkout session test",
            "status": "pending" if activation_status["activationReady"] else "blocked",
        },
        {
            "key": "webhook_persistence_test",
            "label": "Confirm webhook persistence writes the subscription record",
            "status": "pending" if activation_status["activationReady"] else "blocked",
        },
        {
            "key": "portal_smoke_test",
            "label": "Confirm billing portal opens for the subscribed account",
            "status": "pending" if activation_status["activationReady"] else "blocked",
        },
    ]

    return {
        "summary": {
            "activationReady": activation_status["activationReady"],
            "goLiveReady": activation_status["goLiveReady"],
            "storeMode": subscription_store["mode"],
            "progress": activation_status["progress"],
            "currentPhase": current_phase,
            "backendEnv": backend_env_summary,
            "schema": schema_summary,
            "verificationReady": activation_status["activationReady"],
            "stripeMode": activation_status["stripeMode"],
            "domainStatus": activation_status["domainStatus"],
        },
        "frontendPublicConfig": frontend_public_config,
        "backendEnv": backend_env,
        "supabaseActivation": {
            "schemaFile": "backend/supabase_billing_schema.sql",
            "profilesReady": subscription_store["profilesReady"],
            "subscriptionsReady": subscription_store["subscriptionsReady"],
            "webhookEventsReady": subscription_store["webhookEventsReady"],
            "schemaChecklist": schema_checks,
            "summary": schema_summary,
        },
        "switchPath": switch_path,
        "verificationChecklist": verification_checklist,
        "blockers": activation_status["blockers"],
        "goLiveBlockers": activation_status["goLiveBlockers"],
        "nextSteps": activation_status["nextSteps"],
    }


def create_checkout_session(*, email: str, user_id: str, success_url: str, cancel_url: str) -> dict:
    response = requests.post(
        "https://api.stripe.com/v1/checkout/sessions",
        headers={
            "Authorization": f"Bearer {get_stripe_secret_key()}",
        },
        data={
            "mode": "subscription",
            "client_reference_id": user_id,
            "customer_email": email,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items[0][price]": get_stripe_premium_price_id(),
            "line_items[0][quantity]": "1",
            "allow_promotion_codes": "true",
            "metadata[user_id]": user_id,
            "metadata[email]": email,
            "metadata[plan]": "premium",
            "subscription_data[metadata][user_id]": user_id,
            "subscription_data[metadata][email]": email,
            "subscription_data[metadata][plan]": "premium",
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def create_portal_session(*, customer_id: str, return_url: str) -> dict:
    response = requests.post(
        "https://api.stripe.com/v1/billing_portal/sessions",
        headers={
            "Authorization": f"Bearer {get_stripe_secret_key()}",
        },
        data={
            "customer": customer_id,
            "return_url": return_url,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def get_stripe_subscription(subscription_id: str) -> dict:
    response = requests.get(
        f"https://api.stripe.com/v1/subscriptions/{subscription_id}",
        headers={
            "Authorization": f"Bearer {get_stripe_secret_key()}",
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def resolve_billing_urls(origin: Optional[str]) -> tuple[str, str, str]:
    base_origin = (origin or "").strip().rstrip("/")
    success_url = get_stripe_success_url()
    cancel_url = get_stripe_cancel_url()
    portal_return_url = get_stripe_portal_return_url()

    if base_origin:
        success_url = success_url or f"{base_origin}/?billing=success"
        cancel_url = cancel_url or f"{base_origin}/?billing=cancel"
        portal_return_url = portal_return_url or f"{base_origin}/?billing=portal"

    return success_url, cancel_url, portal_return_url
