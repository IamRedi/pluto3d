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
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

Enable:

- Email auth
- Google auth

What the user will need to do:

- create the Supabase project
- copy the project URL
- copy the anon key
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
- it reports auth readiness in the Login and Profile surfaces
- live Google/email auth calls are still placeholders until the real Supabase client is connected

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

## Step 6: Stripe Integration

Add Stripe for:

- checkout session
- billing portal
- webhook events

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
- `STRIPE_WEBHOOK_SECRET`
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

1. test the sponsor/ad loading preview
2. commit and push current local changes
3. prepare Supabase setup checklist for the user
4. add `frontend/auth-client.js`
5. add frontend env handling for Supabase
6. connect real session state

## Second Real Milestone

The first monetization milestone is complete when:

- users can subscribe with Stripe
- premium status updates automatically
- sponsor loading is hidden for premium
- premium-only routes are validated in FastAPI
