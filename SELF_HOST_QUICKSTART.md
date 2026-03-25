# Pluto3D Self-Host Quickstart

This guide is for the product-distribution version of Pluto3D Studio.

Goal:

- a buyer can point the app to their own domain
- connect their own API/backend
- connect their own Supabase auth
- set a support email
- get the product online fast without changing code structure

## Public Config Philosophy

For the frontend, keep one public config file as the main install surface:

- `frontend/app-config.js`

This file is safe to edit per customer install because it contains only public runtime values:

- app name
- studio name
- brand subtitle
- site URL
- API base URL
- support email
- Supabase public auth values

## Files To Configure

### Frontend

- `frontend/app-config.js`
- optional: `frontend/auth-config.js`

### Backend

- `backend/.env`

## Fastest Setup Shape

The simplest install target is:

1. frontend on customer domain
2. backend on customer API domain
3. Supabase project for auth
4. Stripe account for subscriptions

Example:

- frontend: `https://studio.customer.com`
- backend: `https://api.customer.com`

## Frontend Public Config Example

Use `frontend/app-config.example.js` as the template.

Typical values:

```js
window.PLUTO_APP_CONFIG = {
  appName: "CustomerBrand",
  studioName: "CustomerBrand Studio",
  brandSubtitle: "Creative Print Studio",
  siteUrl: "https://studio.customer.com",
  apiBase: "https://api.customer.com",
  supportEmail: "support@customer.com",
  supportLabel: "Email Support",
  auth: {
    supabaseUrl: "https://your-project-ref.supabase.co",
    supabasePublishableKey: "your_supabase_publishable_key_here"
  }
};
```

## Backend Env Example

At minimum, the backend install needs:

- `REPLICATE_API_TOKEN`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `PLUTO_PREMIUM_EMAILS`

For billing:

- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_PREMIUM_PRICE_ID`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_SUCCESS_URL`
- `STRIPE_CANCEL_URL`
- `STRIPE_PORTAL_RETURN_URL`
- `PLUTO_SUBSCRIPTION_STORE`

Recommended mode progression:

- use `local` while first wiring checkout and webhook flow
- move to `supabase` after applying `backend/supabase_billing_schema.sql`

## Activation Readiness

Before treating billing as production-ready, confirm:

1. Stripe keys and price ID are configured
2. Stripe webhook secret is configured
3. `PLUTO_SUBSCRIPTION_STORE=supabase`
4. `backend/supabase_billing_schema.sql` has been applied
5. billing config reports the store schema as ready

The goal is to avoid a half-live state where checkout exists but subscription persistence is incomplete.

The backend now exposes activation blockers directly in billing config so you can verify what is still missing before going live.
It also exposes ordered next steps so rollout can follow the same sequence every time.
The activation handoff now also reports separate frontend, backend, and schema completion counts so the install state is easy to audit.
It also reports the current switch phase and the pending verification queue for the live activation step.

Reference:

- `backend/.env.example`

## Install Principle

The product should be installable by editing config, not source code.

That means:

- domain changes should live in config
- the public site URL should live in config
- support email should live in config
- auth public values should live in config
- backend private credentials should live in backend env
- auth redirects should follow `siteUrl`, not whichever preview host happens to be open

## Recommended One-Hour Install Order

1. Deploy backend and set `backend/.env`
2. Confirm backend `/docs` loads
3. Edit `frontend/app-config.js`
4. Deploy frontend
5. Confirm auth redirect URLs in Supabase
6. Confirm login works
7. Confirm premium lock state works
8. Confirm billing config loads

## Current Status

Already ready:

- frontend public runtime config layer
- backend env-driven service config
- Supabase auth flow
- backend plan resolution
- billing scaffold

Still to finalize for true plug-and-play distribution:

- replace temporary local subscription-state adapter with Supabase persistence
- add Stripe webhook-driven premium activation
- keep the buyer handoff checklist updated as the install surface matures

Reference:

- `PLUG_AND_PLAY_DEPLOY_CHECKLIST.md`
