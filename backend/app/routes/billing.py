import os
import hashlib
import hmac
import json

from fastapi import APIRouter, Header, HTTPException, Request

from app.services.auth import extract_bearer_token, verify_supabase_user
from app.services.billing import (
    get_billing_activation_handoff,
    create_checkout_session,
    create_portal_session,
    get_stripe_subscription,
    get_billing_activation_status,
    get_billing_public_config,
    get_stripe_portal_return_url,
    is_stripe_ready,
    resolve_billing_urls,
)
from app.services.plans import resolve_user_plan, resolve_user_plan_details
from app.services.subscriptions import (
    ensure_profile_for_user,
    get_customer_id_for_user,
    get_subscription_summary_for_user,
    record_customer_link,
    record_subscription_state,
    record_webhook_event,
)


router = APIRouter(prefix="/api/billing", tags=["billing"])


def _get_webhook_secret() -> str:
    return os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()


def _verify_stripe_signature(payload: bytes, stripe_signature: str | None) -> None:
    secret = _get_webhook_secret()

    if not secret:
        raise HTTPException(status_code=503, detail="Stripe webhook secret is not configured yet.")

    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature header.")

    parts = {}
    for item in stripe_signature.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        parts[key] = value

    timestamp = parts.get("t")
    signature = parts.get("v1")

    if not timestamp or not signature:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature header.")

    signed_payload = f"{timestamp}.{payload.decode('utf-8')}".encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=400, detail="Stripe signature verification failed.")


def _handle_checkout_completed(event: dict) -> None:
    data = (event.get("data") or {}).get("object") or {}
    metadata = data.get("metadata") or {}

    customer_id = (data.get("customer") or "").strip()
    user_id = (metadata.get("user_id") or data.get("client_reference_id") or "").strip()
    email = (
        metadata.get("email")
        or ((data.get("customer_details") or {}).get("email"))
        or ""
    ).strip()
    subscription_id = (data.get("subscription") or "").strip()

    record_customer_link(customer_id=customer_id, user_id=user_id, email=email)

    if subscription_id:
        subscription_status = "checkout_completed"
        current_period_end = None

        try:
            subscription = get_stripe_subscription(subscription_id)
            subscription_metadata = subscription.get("metadata") or {}
            metadata = {
                **subscription_metadata,
                **metadata,
            }
            subscription_status = (subscription.get("status") or "").strip() or subscription_status
            current_period_end = subscription.get("current_period_end")
            user_id = (metadata.get("user_id") or user_id).strip()
            email = (metadata.get("email") or email).strip()
        except Exception:
            # Keep the checkout record even if the follow-up Stripe read fails.
            pass

        record_subscription_state(
            subscription_id=subscription_id,
            customer_id=customer_id,
            status=subscription_status,
            plan_code=(metadata.get("plan") or "premium").strip(),
            email=email,
            user_id=user_id,
            current_period_end=current_period_end,
            source_event=event.get("type") or "",
        )


def _handle_subscription_changed(event: dict) -> None:
    data = (event.get("data") or {}).get("object") or {}
    metadata = data.get("metadata") or {}
    record_customer_link(
        customer_id=(data.get("customer") or "").strip(),
        user_id=(metadata.get("user_id") or "").strip(),
        email=(metadata.get("email") or "").strip(),
    )

    record_subscription_state(
        subscription_id=(data.get("id") or "").strip(),
        customer_id=(data.get("customer") or "").strip(),
        status=(data.get("status") or "").strip(),
        plan_code=(metadata.get("plan") or "premium").strip(),
        email=(metadata.get("email") or "").strip(),
        user_id=(metadata.get("user_id") or "").strip(),
        current_period_end=data.get("current_period_end"),
        source_event=event.get("type") or "",
    )


def _handle_subscription_deleted(event: dict) -> None:
    data = (event.get("data") or {}).get("object") or {}
    metadata = data.get("metadata") or {}
    record_customer_link(
        customer_id=(data.get("customer") or "").strip(),
        user_id=(metadata.get("user_id") or "").strip(),
        email=(metadata.get("email") or "").strip(),
    )

    record_subscription_state(
        subscription_id=(data.get("id") or "").strip(),
        customer_id=(data.get("customer") or "").strip(),
        status="canceled",
        plan_code=(metadata.get("plan") or "premium").strip(),
        email=(metadata.get("email") or "").strip(),
        user_id=(metadata.get("user_id") or "").strip(),
        current_period_end=data.get("current_period_end"),
        source_event=event.get("type") or "",
    )


def _get_authenticated_user(authorization: str | None) -> dict:
    token = extract_bearer_token(authorization)
    user = verify_supabase_user(token) if token else None

    if not user:
        raise HTTPException(status_code=401, detail="Authentication required.")

    return user


@router.get("/config")
def get_billing_config():
    return get_billing_public_config()


@router.get("/activation-status")
def get_billing_activation_status_route():
    return get_billing_activation_status()


@router.get("/activation-handoff")
def get_billing_activation_handoff_route():
    return get_billing_activation_handoff()


@router.get("/status")
def get_billing_status(authorization: str | None = Header(default=None)):
    user = _get_authenticated_user(authorization)
    plan_details = resolve_user_plan_details(user)
    ensure_profile_for_user(user, plan=plan_details["plan"])
    customer_id = get_customer_id_for_user(user)
    subscription = get_subscription_summary_for_user(user)
    return {
        "authenticated": True,
        "plan": plan_details["plan"],
        "planSource": plan_details["source"],
        "planReason": plan_details["reason"],
        "billing": get_billing_public_config(),
        "customerPortalAvailable": bool(customer_id),
        "subscription": subscription,
    }


@router.post("/checkout-session")
def create_billing_checkout_session(
    request: Request,
    authorization: str | None = Header(default=None),
):
    user = _get_authenticated_user(authorization)
    plan = resolve_user_plan(user)
    ensure_profile_for_user(user, plan=plan)

    if plan == "premium":
        raise HTTPException(status_code=409, detail="Premium is already active for this account.")

    if not is_stripe_ready():
        raise HTTPException(
            status_code=503,
            detail="Stripe checkout is not configured yet.",
        )

    origin = request.headers.get("origin")
    success_url, cancel_url, _portal_return_url = resolve_billing_urls(origin)

    if not success_url or not cancel_url:
        raise HTTPException(
            status_code=503,
            detail="Stripe redirect URLs are not configured yet.",
        )

    session = create_checkout_session(
        email=(user.get("email") or "").strip(),
        user_id=(user.get("id") or "").strip(),
        success_url=success_url,
        cancel_url=cancel_url,
    )

    return {
        "provider": "stripe",
        "checkoutUrl": session.get("url"),
        "sessionId": session.get("id"),
    }


@router.post("/portal-session")
def create_billing_portal_session(
    request: Request,
    authorization: str | None = Header(default=None),
):
    user = _get_authenticated_user(authorization)
    plan_details = resolve_user_plan_details(user)
    ensure_profile_for_user(user, plan=plan_details["plan"])
    customer_id = get_customer_id_for_user(user)

    if not customer_id:
        raise HTTPException(
            status_code=409,
            detail="No Stripe customer is linked to this account yet.",
        )

    if not is_stripe_ready():
        raise HTTPException(
            status_code=503,
            detail="Stripe billing portal is not configured yet.",
        )

    origin = request.headers.get("origin")
    _success_url, _cancel_url, portal_return_url = resolve_billing_urls(origin)
    portal_return_url = portal_return_url or get_stripe_portal_return_url()

    if not portal_return_url:
        raise HTTPException(
            status_code=503,
            detail="Stripe portal return URL is not configured yet.",
        )

    session = create_portal_session(
        customer_id=customer_id,
        return_url=portal_return_url,
    )

    return {
        "provider": "stripe",
        "portalUrl": session.get("url"),
    }


@router.post("/webhook")
async def handle_billing_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
):
    payload = await request.body()
    _verify_stripe_signature(payload, stripe_signature)

    try:
        event = json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook payload.") from exc

    event_id = (event.get("id") or "").strip()
    event_type = (event.get("type") or "").strip()

    if event_id and not record_webhook_event(event_id=event_id, event_type=event_type):
        return {
            "received": True,
            "duplicate": True,
            "eventType": event_type,
        }

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(event)
    elif event_type == "customer.subscription.created":
        _handle_subscription_changed(event)
    elif event_type == "customer.subscription.updated":
        _handle_subscription_changed(event)
    elif event_type == "customer.subscription.deleted":
        _handle_subscription_deleted(event)

    return {
        "received": True,
        "duplicate": False,
        "eventType": event_type,
    }
