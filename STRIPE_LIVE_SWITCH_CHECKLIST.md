# Pluto3D Stripe Live Switch Checklist

Use this checklist when Pluto3D is ready to move from Stripe test mode to Stripe live mode.

This document assumes:

- the frontend custom domain is already working
- Supabase auth is already live
- Railway env flow is already in place
- Stripe test checkout has already been verified

Do not store private Stripe values in this file.

## Goal

Reach this state:

- Stripe keys are `live`
- Stripe webhook secret is `live`
- Stripe premium price ID is `live`
- billing URLs point to the final custom domain
- billing runtime shows no go-live blockers

## What You Will Need From Stripe Live

Public value:

- `STRIPE_PUBLISHABLE_KEY`

Private values:

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

Billing product value:

- `STRIPE_PREMIUM_PRICE_ID`

## Before Switching

Confirm these are already true:

- `https://www.pluto-3d.com` opens correctly
- Supabase `Site URL` is the final domain
- Supabase redirect URLs include the final domain
- Railway backend is already reading Supabase values correctly
- Stripe test checkout has already succeeded at least once

## Live Stripe Setup Order

1. Open Stripe and switch to `live account`
2. Complete onboarding / verification if Stripe requires it
3. Create the live `Pluto3D Premium` product
4. Create the live recurring premium price
5. Copy the live publishable key
6. Copy the live secret key
7. Create the live webhook endpoint
8. Copy the live webhook signing secret
9. Update Railway variables
10. Verify billing runtime switches from `Stripe Test Mode` to `Stripe Live Mode`

## Railway Variables To Replace

These values must be updated in Railway when going live:

- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_PREMIUM_PRICE_ID`
- `STRIPE_WEBHOOK_SECRET`

These values must already point to the final domain:

- `STRIPE_SUCCESS_URL=https://www.pluto-3d.com/?billing=success`
- `STRIPE_CANCEL_URL=https://www.pluto-3d.com/?billing=cancel`
- `STRIPE_PORTAL_RETURN_URL=https://www.pluto-3d.com/?billing=portal`

## Live Webhook Endpoint

Create the live Stripe webhook with this endpoint:

```text
https://pluto3d-production.up.railway.app/api/billing/webhook
```

Subscribe it to:

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`

## In-Product Verification

After switching to live values, verify in the app:

- `Stripe Live Mode` appears instead of `Stripe Test Mode`
- `Temporary Domain` is gone
- `Launch Target` shows the final domain
- `goLiveBlockers` is empty

## Smoke Tests

### Auth

- login returns to `https://www.pluto-3d.com`
- profile loads real account state

### Billing

- checkout opens from the final domain
- successful checkout returns to the final domain
- webhook writes the live subscription record
- premium resolves from `subscription_record`
- billing portal opens

## Success Standard

Stripe live switch is complete when:

- no billing go-live blockers remain
- a real subscribed account becomes premium
- portal access works
- the final domain stays stable through login and billing redirects

## Current Pluto3D Status

The structural live-switch work is now complete when these are true:

- Railway reports `activationReady=true`
- Railway reports `goLiveReady=true`
- `stripeMode.mode=live`
- `domainStatus.mode=custom`

At that point, the only remaining work is operational verification:

- first real checkout
- first live webhook persistence confirmation
- first live portal test
