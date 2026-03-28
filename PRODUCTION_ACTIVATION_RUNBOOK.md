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
- Stripe checkout active in `live` mode
- Stripe webhook active
- billing return URLs moved off temporary preview domains and onto the final custom domain
- backend plan resolution driven by persisted subscription records

## System Truth Sources

Use these as the live activation sources of truth:

- `GET /api/billing/config`
- `GET /api/billing/activation-status`
- `GET /api/billing/activation-handoff`

The activation handoff now also exposes a phase-based `switchPath` so rollout can be followed as an ordered go-live sequence.
It also exposes a current switch phase and a verification queue so the team can see what is blocked versus what is ready for smoke testing.
Billing runtime now also exposes Stripe mode and billing-domain status so test-vs-live rollout gaps are visible in-product.

## Historical Note

Older project notes may mention earlier live-switch attempts or previous Stripe/Supabase states.
Before a real rollout, trust these in order:

1. current Git branch and commit
2. current `frontend/app-config.js`
3. current Railway / Vercel dashboard state
4. live runtime endpoints listed above

Treat older handoff notes as history, not as deployment truth.

## What The User Will Need To Provide

### Frontend Public Config

Put these in:

- `frontend/app-config.js`

Values:

- `appName`
- `studioName`
- `siteUrl`
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

## Controlled v1.1 Rollout

Use this rollout shape when `v1.1` is ready to replace the frozen `v1` production path while keeping rollback easy.

### Recommended Git Shape

1. Keep `main` as the production baseline until rollout is explicitly approved.
2. Keep `develop` as the active implementation branch.
3. Create one release candidate branch from `develop`, for example:
   - `release/v1.1-rail-candidate`
4. Record the current production point before any rollout move:
   - tag the current production commit, for example:
     - `prod-v1.0-before-v1.1-2026-03-28`

### Recommended Deploy Order

1. Prepare and push the release-candidate branch.
2. Confirm Railway points to the intended commit or branch.
3. Deploy backend first.
4. Run backend and billing smoke checks.
5. Only after backend looks healthy, deploy the frontend.
6. Keep the rollout private to the current testers for one short observation window before broader promotion.

### Actual March 28, 2026 Rollout Path

This is the exact path that was used successfully for the `v1.1` production rollout:

1. Push `release/v1.1-rail-candidate` plus rollback tags to GitHub.
2. In Railway:
   - open the backend service settings
   - go to `Source`
   - change `Branch connected to production` from `main` to `release/v1.1-rail-candidate`
   - wait for the backend deploy to finish
3. Verify backend directly on Railway before touching frontend:
   - `GET /api/billing/activation-status`
   - `GET /api/account/usage`
4. In Vercel:
   - use the preview deployment created from `release/v1.1-rail-candidate`
   - verify the preview visually and functionally before promoting anything
5. Because direct `Promote to Production` was not exposed in the Vercel UI during this rollout:
   - switch local Git to `main`
   - merge `release/v1.1-rail-candidate` into `main`
   - push `main`
6. Let Vercel production update from `main`.

This is now the preferred fallback procedure when Vercel preview deployment exists but the UI does not expose a direct production-promotion action.

### Why This Order

- backend problems are the higher-risk production failure class for auth, quota, billing, and premium 3D
- frontend rollback is easier when backend state is already known-good
- a release-candidate branch keeps `develop` free for follow-up fixes without changing the exact rollout candidate under test

## Pre-Rollout Snapshot

Before touching Railway or Vercel, record these:

- current production Git commit
- current Railway deployment ID / timestamp
- current Vercel deployment ID / timestamp
- current `main` head commit
- current `develop` head commit
- current `/api/billing/activation-status` result
- current `/api/billing/config` result

If rollback becomes necessary, these snapshots remove guesswork.

## Production Test Matrix

Run these in order after the new backend deploy is live.

### Phase 1: Health

- `GET /`
- `GET /docs`
- `GET /api/billing/activation-status`
- `GET /api/billing/config`
- open the frontend and confirm no immediate auth/runtime failure

### Phase 2: Guest Flow

- open the app in a clean browser session
- generate one AI image
- generate one SVG
- run one test 3D flow
- run one Relief STL flow
- confirm usage/account UI still loads cleanly
- if owned test models are large, explicitly run one `Test 3D` flow with `bike` from the preview deployment before promoting the frontend, so static asset weight problems surface before the live switch

### Phase 3: Auth Flow

- sign in with Google
- open `Profile`
- confirm account state loads
- confirm `/api/account/me` resolves correctly for the signed-in user
- confirm backend usage sync still appears in the UI

### Phase 4: Premium 3D

- run one real premium 3D generation from an uploaded source
- run one real premium 3D generation from a generated source image if available
- confirm polling, final model load, and download behavior

### Phase 5: Billing

Run this last so a billing problem does not hide more basic production regressions.

- open checkout
- complete one real controlled payment
- confirm return to the app
- confirm webhook persistence
- confirm `/api/account/me` resolves `premium`
- confirm billing portal opens

## User-Only Checks

These require dashboard or service access that must be done manually:

### Railway

- confirm the project deployed the intended branch or commit
- confirm startup logs show FastAPI boot completed
- confirm env vars match the intended rollout state
- confirm the previous healthy deployment is still available for rollback

### Vercel

- confirm the intended production deployment is active
- confirm domain routing still points to the right deployment
- confirm `www.pluto-3d.com` serves the expected `app-config.js`
- if `Promote to Production` is not visible for the preview deployment, use the verified release-candidate branch as the source for a merge into `main`, then let Vercel production rebuild from `main`

### Supabase

- confirm `usage_buckets`, `profiles`, `subscriptions`, and `billing_webhook_events` exist in the target project
- confirm `Site URL` and redirect URLs still match the production domain

### Stripe

- confirm the intended mode is active (`test` or `live`)
- confirm the webhook endpoint points to the current Railway backend
- confirm the webhook is subscribed to the required events

## Rollback Trigger Rules

Rollback immediately if any of these happen and a fast fix is not obvious:

- app does not load for testers
- login breaks
- `/api/account/me` or `/api/billing/status` stops resolving correctly
- guest or free generation paths fail broadly
- premium 3D path fails broadly
- checkout returns but premium does not persist
- webhook handling is broken

Cosmetic-only issues can stay in the rollout candidate if core flows remain stable.

## Rollback Procedure

If the rollout fails and the fix is not immediately obvious:

1. Roll back Railway to the last known healthy `v1.0` deployment.
2. If frontend was also changed, roll back Vercel to the last known healthy `v1.0` deployment.
3. Re-check:
   - `/`
   - `/docs`
   - login
   - one guest flow
4. Keep `main` on the `v1.0` line until the issue is fully understood.
5. Return to `develop` for diagnosis and a careful follow-up fix.
6. Prepare a fresh release-candidate branch for the next rollout attempt instead of reusing an uncertain deployment snapshot.

## Rollback Success Criteria

Rollback is complete when:

- production behaves like the previous `v1.0` baseline again
- testers can log in and use the app
- no new production-only blocker remains active
- follow-up work is isolated back on `develop`

## Final Go-Live Checks

Before calling the rollout production-ready, confirm:

- Stripe keys are `live`, not `test`
- Stripe success/cancel/portal URLs point to the final custom domain, not `vercel.app`
- `goLiveBlockers` is empty in the billing runtime

Reference:

- `STRIPE_LIVE_SWITCH_CHECKLIST.md`

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
