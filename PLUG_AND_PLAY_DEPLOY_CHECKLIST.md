# Pluto3D Plug-And-Play Deploy Checklist

This checklist is for the packaged/self-host version of Pluto3D Studio.

Use it when:

- delivering the product to a buyer
- setting up a new branded install
- moving from preview setup to customer-ready deployment

The goal is simple:

- change config
- set env
- connect domain/auth/billing
- verify the install

Do not put private secrets in this file.

## Accounts The Buyer Needs

- GitHub or direct project files
- Vercel account for frontend hosting
- Railway account for backend hosting
- Supabase project for auth and subscription persistence
- Stripe account for subscriptions
- DNS provider access for the chosen domain
- Replicate account if AI generation is included in the install

## Values To Collect First

### Public Values

- frontend domain
- backend API domain
- support email
- Supabase project URL
- Supabase publishable key
- Stripe publishable key

### Private Values

- Supabase service role key
- Stripe secret key
- Stripe webhook secret
- Replicate API token

## Files And Platforms To Update

### Frontend

File:

- `frontend/app-config.js`

Set:

- `appName`
- `studioName`
- `brandSubtitle`
- `siteUrl`
- `apiBase`
- `supportEmail`
- `supportLabel`
- `auth.supabaseUrl`
- `auth.supabasePublishableKey`

### Backend

Location:

- Railway variables
- local `backend/.env` if needed for backup/local use

Set:

- `REPLICATE_API_TOKEN`
- `MESHY_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `PLUTO_PREMIUM_EMAILS`
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_PREMIUM_PRICE_ID`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_SUCCESS_URL`
- `STRIPE_CANCEL_URL`
- `STRIPE_PORTAL_RETURN_URL`
- `PLUTO_SUBSCRIPTION_STORE=supabase`

### Supabase

Configure:

- `Site URL`
- auth redirect URLs
- Google auth provider if needed
- SQL schema from `backend/supabase_billing_schema.sql`

### Stripe

Configure:

- product
- recurring premium price
- webhook endpoint
- live/test keys as needed

### DNS / Domain

Configure:

- root domain record
- `www` record
- SSL/domain validation path through Vercel

## One-Hour Install Flow

1. Deploy backend to Railway
2. Set backend env vars
3. Apply Supabase billing schema
4. Configure Supabase auth redirect URLs
5. Create Stripe product + premium price
6. Create Stripe webhook
7. Edit `frontend/app-config.js`
8. Deploy frontend to Vercel
9. Attach custom domain
10. Verify login
11. Verify plan resolution
12. Verify checkout
13. Verify webhook persistence
14. Verify billing portal

## Validation Checklist

### Domain

- frontend domain opens
- SSL is valid
- custom domain is preferred over preview domain

### Auth

- Google login works
- email login works if enabled
- logout works
- redirects return to the final domain

### Billing

- `/api/billing/activation-status` returns ready
- billing surfaces show the correct stripe/domain mode
- checkout opens
- successful checkout returns to the app
- account resolves premium
- portal opens for subscribed user

### Product Basics

- workspace opens
- SVG path works
- toy mode works
- print fix works
- premium locks reflect backend truth

## What To Hand Off To The Buyer

- repository or packaged source
- `frontend/app-config.example.js`
- `backend/.env.example`
- `SELF_HOST_QUICKSTART.md`
- `PRODUCTION_ACTIVATION_RUNBOOK.md`
- `INFRASTRUCTURE_INVENTORY.md`
- this checklist

## Secret Handling Rules

Share with the buyer privately, never in repo docs:

- Supabase service role key
- Stripe secret key
- Stripe webhook secret
- Replicate API token

Public values may live in config and docs:

- site URL
- backend API URL
- Supabase URL
- Supabase publishable key
- Stripe publishable key

## Success Standard

The install is considered handoff-ready when:

- the buyer can change domain/auth/billing through config and platform settings
- the app works on the buyer domain
- auth works
- billing works
- premium gating works
- the operator inventory is understandable without tribal knowledge
