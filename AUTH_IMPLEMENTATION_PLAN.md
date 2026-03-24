# Pluto3D Auth Integration Plan

This file is the technical plan for turning the current auth preview UI into a real account and subscription system.

## Goal

Connect:

- Supabase Auth
- Supabase Postgres
- FastAPI backend checks
- Stripe subscriptions

So Pluto3D can support:

- guest users
- logged-in free users
- premium subscribers

## Current Progress Before Real Integration

Already built in the frontend as preview scaffolding:

- login surface
- profile surface
- plans surface
- guest/free/premium preview states
- premium lock preview
- usage limits preview
- sponsor/ad loading preview for free plans

This means the product UX is already shaped before the real auth backend is connected.

## Recommended Stack

- Frontend auth: Supabase JS client
- Auth provider: Supabase Auth
- Social login: Google
- Database: Supabase Postgres
- Billing: Stripe
- Backend app logic: FastAPI

## Implementation Order

### Step 1: Supabase Project

Create a new Supabase project and collect:

- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

Enable:

- Email auth
- Google auth

What the user will need to do:

- create the Supabase project
- copy the project URL
- copy the publishable key
- copy the service role key
- enable Google provider

Reference checklist:

- `SUPABASE_SETUP_CHECKLIST.md`

### Step 2: Frontend Session Scaffold

Add a frontend auth module that can:

- create Supabase client
- sign in with Google
- sign up with email
- sign in with email
- sign out
- read current session

Suggested future frontend file:

- `frontend/auth-client.js`
- `frontend/auth-config.js`

Expected first frontend integration tasks:

- install Supabase JS client
- create Supabase client with `frontend/auth-config.js`
- replace preview login buttons with real calls
- read live session on startup
- update header/profile/plans from session state

Current scaffold status:

- `frontend/auth-client.js` now exists as a safe runtime scaffold
- it detects whether `frontend/auth-config.js` is present
- it accepts either `supabasePublishableKey` or the older `supabaseAnonKey`
- it reports auth readiness in the Login and Profile surfaces
- live Google/email auth is now connected through the Supabase JS client
- live session state is now visible in the header, Login, and Profile surfaces

## Step 3: User Data Model

Recommended initial tables:

### `profiles`

- `id` UUID, same as auth user id
- `email`
- `display_name`
- `plan`
- `created_at`
- `updated_at`

### `usage_events`

- `id`
- `user_id`
- `feature_key`
- `created_at`

### `subscriptions`

- `id`
- `user_id`
- `stripe_customer_id`
- `stripe_subscription_id`
- `status`
- `plan`
- `current_period_end`
- `created_at`

## Step 4: Frontend Auth State

Replace the current preview-only UI state with real state from Supabase:

- guest if no session
- free if logged in and no premium subscription
- premium if logged in and subscription is active

Things that should update from real auth state:

- header badge
- login/account button
- profile surface
- plans surface
- premium lock state
- sponsor/ad loading behavior

## Step 5: Backend Plan Checks

Backend should not trust the frontend alone.

FastAPI should receive the user identity and resolve the plan server-side for premium actions.

Suggested backend work:

- verify Supabase user on protected requests
- resolve plan from `profiles` or `subscriptions`
- allow or block premium features
- later apply real usage limits

Suggested future backend files:

- `backend/app/services/auth.py`
- `backend/app/services/plans.py`

Expected first backend integration tasks:

- verify Supabase user token
- resolve current plan from database
- protect premium endpoints
- prepare usage tracking hooks

Current backend scaffold status:

- `backend/app/services/auth.py` verifies Supabase user tokens
- `backend/app/services/plans.py` resolves `guest/free/premium`
- `backend/app/routes/account.py` exposes `/api/account/me`
- invalid or expired auth transitions are treated as `guest` for cleaner frontend refresh behavior
- premium can now be assigned temporarily through `PLUTO_PREMIUM_EMAILS` in `backend/.env`

## Temporary Premium Assignment Path

Before Stripe is connected, Pluto3D can mark selected tester accounts as premium using:

- `PLUTO_PREMIUM_EMAILS`

Example:

```env
PLUTO_PREMIUM_EMAILS=your-email@example.com,another-premium-user@example.com
```

This allows:

- testing premium locks with a real logged-in user
- verifying the premium UI path before billing is added
- keeping the backend as the source of truth for plan checks

## Step 6: Stripe Integration

Add Stripe for:

- checkout session
- billing portal
- webhook events

Current scaffold status:

- `backend/app/routes/billing.py` now exposes:
  - `GET /api/billing/config`
  - `GET /api/billing/status`
  - `POST /api/billing/checkout-session`
  - `POST /api/billing/portal-session`
  - `POST /api/billing/webhook`
- `backend/app/services/billing.py` now holds the first Stripe-ready service helpers
- `backend/app/services/subscriptions.py` now normalizes customer and subscription state
- Supabase schema now also includes:
  - `billing_webhook_events`
  - webhook replay / duplicate protection for the production persistence path
- `frontend/billing-client.js` now loads billing runtime state and provides:
  - `startPremiumCheckout()`
  - `openBillingPortal()`
  - authenticated billing status sync for subscription and portal availability
- `frontend/app-config.js` now acts as the public install surface for:
  - API base URL
  - support email
  - app branding
  - Supabase public auth config
- `frontend/index.html` now shows billing entry points in:
  - `Plans`
  - `Shop`
  - `Profile`
- `Profile` now also surfaces the live activation handoff map so the production values have a visible destination inside the app
- the frontend now handles Stripe return states (`success`, `cancel`, `portal`) so billing redirects feel product-grade
- `PRODUCTION_ACTIVATION_RUNBOOK.md` now documents the exact live activation sequence

Current transition architecture:

- premium UI gating reads backend-owned plan resolution
- backend plan resolution now checks:
  - normalized subscription state
  - tester premium email fallback
  - Supabase metadata fallback
- subscription state is temporarily stored in a local JSON scaffold for development:
  - `backend/data/billing_state.json`
- this local store is an adapter layer, not the final source of truth
- the intended production replacement is Supabase-backed `profiles` and `subscriptions` tables
- first schema draft now lives in:
  - `backend/supabase_billing_schema.sql`
- adapter mode is controlled by:
  - `PLUTO_SUBSCRIPTION_STORE=local|supabase`
- billing config now reports activation readiness separately from basic Stripe key readiness
- billing config now also reports explicit activation blockers so rollout can follow a deterministic checklist
- billing config now also reports ordered next steps for activation handoff
- billing config now also reports measurable activation progress (`completed/total/percent`) so rollout readiness is visible in-product
- authenticated account and billing routes now auto-sync the Supabase `profiles` row so production persistence does not depend on the first webhook alone
- backend plan resolution can now fall back to the Supabase `profiles.plan` snapshot when a fresh subscription row is not yet available
- Supabase mode is considered activation-ready only when:
  - Supabase env is present
  - `profiles` exists
  - `subscriptions` exists
  - `billing_webhook_events` exists
- frontend now reads backend subscription status so the account surface can show real billing state instead of only plan labels
- backend now reports plan source and plan reason so account and billing debugging can trace where premium/free resolution came from

What is still intentionally missing before live activation:

- Stripe customer persistence in Supabase
- subscription row sync into `profiles` or `subscriptions`
- automatic premium activation after webhook confirmation
- portal availability based on real persisted customer records across environments

Important Stripe events:

- `checkout.session.completed`
- `customer.subscription.updated`
- `customer.subscription.deleted`

Stripe should update the user's plan in the database.

## Step 7: Replace Preview Logic

After auth is connected:

- remove or disable preview login controls
- remove preview-only plan switching
- keep usage preview only as a local dev helper if needed

## Required Env Variables

### Frontend

- `frontend/auth-config.js`

### Backend

- `SUPABASE_SERVICE_ROLE_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_PREMIUM_PRICE_ID`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_SUCCESS_URL`
- `STRIPE_CANCEL_URL`
- `STRIPE_PORTAL_RETURN_URL`
- `REPLICATE_API_TOKEN`

## First Real Milestone

The first production-grade auth milestone is complete when:

- users can sign in with Google
- users can sign out
- the header reflects the real session
- profile surface shows real account info
- premium buttons are locked based on real plan state

## Resume Checklist

When continuing from the current stopping point:

1. verify login/logout locally with live Supabase auth
2. verify `/api/account/me` state during guest and logged-in flows
3. connect premium/free gating to backend-backed account state
4. prepare first real plan assignment path
5. verify billing scaffold endpoints and frontend upgrade entry points
6. replace the local subscription-state adapter with Supabase persistence
7. add webhook-driven premium activation from real subscription records

## Second Real Milestone

The first monetization milestone is complete when:

- users can subscribe with Stripe
- premium status updates automatically
- sponsor loading is hidden for premium
- premium-only routes are validated in FastAPI
