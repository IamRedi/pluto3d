# Pluto3D Infrastructure Inventory

This document is the operator-facing map of everything that powers Pluto3D Studio.

Use it for:

- owner visibility
- buyer/self-host handoff
- cost awareness
- credential hygiene
- domain and service troubleshooting

Do not store private keys in this file.
Keep secrets in your secure password manager or private local vault.

## Product Identity

- Product name: `Pluto3D Studio`
- Public frontend domain target: `https://www.pluto-3d.com`
- Temporary frontend domain: `https://pluto3d.vercel.app`
- Backend API domain: `https://pluto3d-production.up.railway.app`

## Service Map

### GitHub

Role:

- source code
- deploy source for Vercel
- deploy source for Railway

Why it matters:

- every production deploy starts from the GitHub repo
- if code is not pushed, Vercel/Railway stay behind local work

Likely paid surface:

- only if private repo/team features exceed free limits

### Vercel

Role:

- frontend hosting
- serves the static Pluto3D Studio app

Current domains:

- `pluto3d.vercel.app`
- `pluto-3d.com`
- `www.pluto-3d.com`

Why it matters:

- this is the public face of the app
- domain attachment and SSL happen here

Likely paid surface:

- Vercel plan if traffic, bandwidth, team, or project limits exceed free tier

### Railway

Role:

- backend hosting for FastAPI
- serves the API used by frontend auth, billing, SVG, 3D, and print flows

Current API:

- `https://pluto3d-production.up.railway.app`

Why it matters:

- all backend env vars live here
- Stripe and Supabase private integration depends on Railway variables

Likely paid surface:

- monthly usage/compute/runtime costs

### Supabase

Role:

- authentication
- session management
- Google login
- billing persistence tables:
  - `profiles`
  - `subscriptions`
  - `billing_webhook_events`

Current project URL:

- `https://jnpqcpsxyzhhsrceqepk.supabase.co`

Why it matters:

- account identity truth
- backend plan resolution
- premium persistence

Likely paid surface:

- project/database/auth/storage usage if free limits are exceeded

### Stripe

Role:

- subscription checkout
- billing portal
- webhook events
- premium monetization path

Current state:

- live mode keys are now configured
- the next step is a first end-to-end live checkout and webhook verification

Why it matters:

- premium payments and billing lifecycle depend on Stripe
- final go-live requires live verification / onboarding

Likely paid surface:

- Stripe takes payment-processing fees only when real live payments happen
- test mode itself is not a bill you pay

### Cloudflare

Role:

- DNS management for `pluto-3d.com`

Current DNS direction:

- root domain points to Vercel via `A @`
- `www` points to Vercel via `CNAME`

Why it matters:

- domain routing starts here
- if DNS is wrong, Vercel domains show invalid configuration

Likely paid surface:

- usually free unless advanced add-ons/features are enabled

### Replicate

Role:

- AI generation backend dependency

Why it matters:

- powers paid/remote model generation where local compute is not practical

Likely paid surface:

- usage-based billing tied to API consumption

## Current Domain And Routing Map

### Frontend

- primary target: `https://www.pluto-3d.com`
- root redirect domain: `https://pluto-3d.com`
- fallback preview domain: `https://pluto3d.vercel.app`

### Backend

- API: `https://pluto3d-production.up.railway.app`

### Auth Redirects

Configured in Supabase:

- `https://pluto3d.vercel.app`
- `https://pluto3d.vercel.app/`
- `https://pluto-3d.com`
- `https://www.pluto-3d.com`
- local dev URLs

### Billing Redirects

Configured in Railway env:

- success URL
- cancel URL
- portal return URL

These should now point to:

- `https://www.pluto-3d.com/?billing=success`
- `https://www.pluto-3d.com/?billing=cancel`
- `https://www.pluto-3d.com/?billing=portal`

## Secrets And Sensitive Values

Do not store these in repo docs:

- `SUPABASE_SERVICE_ROLE_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `REPLICATE_API_TOKEN`
- any Google OAuth private credential

Public-safe values:

- frontend site URL
- frontend API base URL
- Supabase project URL
- Supabase publishable key
- Stripe publishable key

## Where Config Lives

### Public Frontend Config

File:

- `frontend/app-config.js`

Contains:

- app/studio name
- brand subtitle
- `siteUrl`
- `apiBase`
- support email
- Supabase public auth values

### Private Backend Config

Location:

- Railway variables
- local `backend/.env`

Contains:

- Supabase private key
- Stripe private key
- webhook secret
- Replicate token
- billing return URLs
- subscription store mode

## Buyer / Self-Host Handoff Surfaces

Primary install docs:

- `SELF_HOST_QUICKSTART.md`
- `PRODUCTION_ACTIVATION_RUNBOOK.md`
- `backend/.env.example`
- `frontend/app-config.example.js`

Core plug-and-play rule:

- buyers should change config, not source code

That means:

- domain lives in `frontend/app-config.js`
- API base lives in `frontend/app-config.js`
- auth public values live in `frontend/app-config.js`
- backend secrets live in env

## Payment / Plan Awareness

Expect likely recurring services:

- Vercel
- Railway
- Supabase
- Cloudflare
- Replicate

Stripe is different:

- Stripe is usually fee-based on real payment processing, not a normal fixed monthly hosting bill

## Current Go-Live Status

Already working:

- live frontend
- live backend
- live Supabase auth
- Google login
- backend plan resolution
- premium tester fallback
- Stripe test checkout path
- Supabase billing persistence
- Stripe live keys
- Stripe live webhook secret
- Stripe live premium price
- custom-domain billing return URLs

Still external / operator-driven:

- first end-to-end live checkout verification
- first live webhook persistence verification
- first live billing-portal verification

## Operator Checklist

When reviewing the health of Pluto3D, check:

1. Vercel domains are valid
2. Railway app is deployed from latest GitHub commit
3. Supabase auth redirect URLs match the current frontend domain
4. billing activation status is ready
5. go-live blockers are visible and understood
6. private secrets are stored outside repo docs

## Notes

- Keep this file as the business-operator inventory
- Keep private secrets separate
- Update this file whenever a new paid service, domain, or external dependency is added
