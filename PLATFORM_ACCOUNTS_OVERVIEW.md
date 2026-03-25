# Pluto3D Platform Accounts Overview

This document is the plain-language operator summary of the external platforms that power Pluto3D Studio.

Use it when you want to understand:

- which account does what
- which domain points where
- which services may cost money
- which services hold public config
- which services hold private secrets

Do not store private secrets in this file.

## Current Public Entry Points

- Main frontend target: `https://www.pluto-3d.com`
- Root redirect/frontend domain: `https://pluto-3d.com`
- Temporary frontend domain: `https://pluto3d.vercel.app`
- Backend API: `https://pluto3d-production.up.railway.app`

## Platform Map

### GitHub

Purpose:

- source code
- deployment source for Vercel
- deployment source for Railway

What depends on it:

- frontend deploys
- backend deploys
- version history

What you may pay for:

- usually free unless you move beyond free repo/team limits

What it should not store:

- private production secrets

### Vercel

Purpose:

- frontend hosting
- custom-domain attachment for the app
- SSL for the public site

Current domains:

- `pluto3d.vercel.app`
- `pluto-3d.com`
- `www.pluto-3d.com`

What depends on it:

- the public website opening at all
- final domain routing for the frontend

What you may pay for:

- bandwidth
- team/project limits
- plan upgrade if traffic grows

What lives here:

- frontend deployments
- domain settings

What should not live here:

- backend private credentials

### Railway

Purpose:

- FastAPI backend hosting
- API runtime
- backend environment variables

Current backend:

- `https://pluto3d-production.up.railway.app`

What depends on it:

- auth-backed account state
- billing/session/account APIs
- SVG
- print-fix
- generation endpoints

What you may pay for:

- compute/runtime usage
- memory/network usage depending on plan

What lives here:

- backend deploys
- private env vars

Important private values here:

- `SUPABASE_SERVICE_ROLE_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `REPLICATE_API_TOKEN`

### Supabase

Purpose:

- auth
- Google login
- session handling
- account/billing persistence

Current project:

- `https://jnpqcpsxyzhhsrceqepk.supabase.co`

What depends on it:

- login/logout
- Google OAuth
- account identity
- `profiles`
- `subscriptions`
- `billing_webhook_events`

What you may pay for:

- database usage
- auth usage
- storage/compute if limits are exceeded

What lives here:

- users
- auth provider config
- redirect URLs
- billing persistence tables

Public-safe value:

- Supabase URL
- Supabase publishable key

Private value:

- service role key

### Stripe

Purpose:

- subscriptions
- checkout
- billing portal
- subscription lifecycle events

Current status:

- test mode is active
- live mode is not finalized yet

What depends on it:

- real premium payments
- self-serve billing management
- live subscription activation

What you may pay for:

- payment-processing fees on real live transactions

Important note:

- Stripe test-mode dashboard numbers are not bills
- test gross volume is only simulated payment activity

What lives here:

- products
- prices
- webhook endpoints
- publishable/secret keys

### Cloudflare

Purpose:

- DNS management for the public domain

Current domain zone:

- `pluto-3d.com`

What depends on it:

- whether Vercel can validate the domain
- whether `www.pluto-3d.com` opens correctly

What you may pay for:

- usually free unless advanced features are enabled

What lives here:

- DNS records only

Current important records:

- `A @ -> 216.198.79.1`
- `CNAME www -> cname.vercel-dns.com`

### Replicate

Purpose:

- external AI generation provider

What depends on it:

- remote generation features where local compute is not practical

What you may pay for:

- usage-based API costs

Private value:

- `REPLICATE_API_TOKEN`

## Where To Change What

### Change frontend brand/domain/public runtime

File:

- `frontend/app-config.js`

Use it for:

- app name
- studio name
- support email
- public site URL
- backend API URL
- Supabase public auth values

### Change backend private integrations

Platform:

- Railway Variables

Use it for:

- Supabase private key
- Stripe private key
- Stripe webhook secret
- Replicate token
- billing return URLs

### Change auth redirect behavior

Platform:

- Supabase Authentication settings

Use it for:

- `Site URL`
- redirect URLs
- Google provider config

### Change public domain routing

Platform:

- Cloudflare DNS
- Vercel Domains

Use it for:

- root domain
- `www`
- domain validation

### Change billing products and pricing

Platform:

- Stripe

Use it for:

- premium product
- recurring price
- webhook endpoint
- live/test billing mode

## Likely Paid Surfaces To Track

These are the places you should expect to review over time for cost:

- Vercel
- Railway
- Supabase
- Stripe
- Cloudflare
- Replicate

## Simple Mental Model

Think of Pluto3D like this:

- GitHub = source truth
- Vercel = website
- Railway = backend brain
- Supabase = accounts and identity
- Stripe = subscriptions and payments
- Cloudflare = domain traffic/signpost
- Replicate = AI compute provider

## Secret Hygiene Rule

Keep these only in secure private storage:

- Supabase service role key
- Stripe secret key
- Stripe webhook secret
- Replicate API token
- private Google OAuth credentials

Keep these safe to show in config/docs:

- site URL
- backend API URL
- Supabase URL
- Supabase publishable key
- Stripe publishable key

## Current Strategic Status

Already strong:

- custom domain works
- backend is live
- auth is live
- premium resolution works
- Stripe test path works
- product is structurally plug-and-play

Still external/operator-driven:

- Stripe live onboarding
- Stripe live keys
- live product/price creation
- live webhook creation

## Recommended Owner Routine

When operating Pluto3D, check these first:

1. `www.pluto-3d.com` opens
2. Railway latest deploy is healthy
3. Supabase login returns to the correct domain
4. billing/account state loads in Profile
5. Vercel domains are valid
6. secrets are stored privately outside repo docs
