# Pluto3D Production Activation Runbook

Use this when we are ready to switch Pluto3D billing from scaffold mode to live production persistence.

This runbook is designed for the exact moment when you provide:

- public frontend domain/config values
- backend API domain
- Supabase live values
- Stripe live values

## Activation Goal

Reach this target state:

- `PLUTO_SUBSCRIPTION_STORE=supabase`
- Supabase billing schema applied
- Stripe checkout active
- Stripe webhook active
- backend plan resolution driven by persisted subscription records

## System Truth Sources

Use these as the live activation sources of truth:

- `GET /api/billing/config`
- `GET /api/billing/activation-status`
- `GET /api/billing/activation-handoff`

The activation handoff now also exposes a phase-based `switchPath` so rollout can be followed as an ordered go-live sequence.
It also exposes a current switch phase and a verification queue so the team can see what is blocked versus what is ready for smoke testing.

## What The User Will Need To Provide

### Frontend Public Config

Put these in:

- `frontend/app-config.js`

Values:

- `appName`
- `studioName`
- `apiBase`
- `supportEmail`
- `auth.supabaseUrl`
- `auth.supabasePublishableKey`

### Backend Env

Put these in:

- `backend/.env`

Values:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_PREMIUM_PRICE_ID`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_SUCCESS_URL`
- `STRIPE_CANCEL_URL`
- `STRIPE_PORTAL_RETURN_URL`
- `PLUTO_SUBSCRIPTION_STORE=supabase`

## Activation Order

1. Apply `backend/supabase_billing_schema.sql`
2. Add/update backend env values
3. Set `PLUTO_SUBSCRIPTION_STORE=supabase`
4. Update `frontend/app-config.js`
5. Verify `GET /api/billing/config`
6. Verify `GET /api/billing/activation-status`
7. Run one real checkout test
8. Confirm webhook updates subscription persistence
9. Confirm `/api/account/me` resolves premium from persisted subscription state
10. Confirm billing portal opens for the subscribed user

## Activation Notes

- `GET /api/account/me` and `GET /api/billing/status` now auto-sync the authenticated user's `profiles` row when Supabase persistence is active
- this means profile persistence begins as soon as the user is recognized by the backend, not only after the first Stripe webhook

## Success Criteria

Activation is considered complete when:

- `activationReady` is `true`
- `activationBlockers` is empty
- checkout creates a real Stripe subscription
- webhook writes or updates the subscription record
- account resolves `premium`
- premium UI locks open correctly

## Notes

- Until that point, we keep the rollout controlled and reversible
- The goal is not only “it works once”, but “it is repeatable and supportable”
