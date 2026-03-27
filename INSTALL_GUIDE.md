# Pluto3D Install Guide

This guide is the canonical setup reference for Pluto3D.
Use it for both local development and plug-and-play deployment.

## Install Modes

Pluto3D supports two practical setup modes:

- local development and testing
- branded plug-and-play deployment

## What You Need

### For Local Development

- project source code
- Python environment for the backend
- local copy of `frontend/app-config.js`
- local copy of `backend/.env`

### For Hosted / Plug-And-Play Deployment

- GitHub repository or packaged source
- Vercel account for frontend hosting
- Railway account for backend hosting
- Supabase project for auth and subscription persistence
- Stripe account for billing
- DNS/domain access
- Replicate and Meshy credentials if those features are enabled

## Files You Configure

### Public Frontend Config

Use:

- `frontend/app-config.example.js` as the template
- `frontend/app-config.js` as the real file

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

Optional legacy fallback:

- `frontend/auth-config.js`

### Private Backend Config

Use:

- `.env.example` as the canonical template

Copy it to:

- `backend/.env`

Set the required private/runtime values there before starting the backend.

## Local Development Setup

### 1. Prepare frontend config

Create or update:

- `frontend/app-config.js`

Start from:

- `frontend/app-config.example.js`

### 2. Prepare backend env

Copy:

- `.env.example`

To:

- `backend/.env`

Then fill at least:

- `REPLICATE_API_TOKEN`
- `MESHY_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `PLUTO_PREMIUM_EMAILS`

If billing is part of the local test flow, also fill:

- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_PREMIUM_PRICE_ID`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_SUCCESS_URL`
- `STRIPE_CANCEL_URL`
- `STRIPE_PORTAL_RETURN_URL`
- `PLUTO_SUBSCRIPTION_STORE`

### 3. Install backend dependencies

From the project root:

```powershell
python -m venv backend\venv
.\backend\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Start the backend

From the project root:

```powershell
.\backend\venv\Scripts\Activate.ps1
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 5. Start the frontend

Use a second terminal from the project root:

```powershell
cd frontend
python -m http.server 5500
```

### 6. Open the app

- frontend:
  - `http://127.0.0.1:5500` when the server is started inside `frontend`
  - `http://127.0.0.1:5500/frontend/` if the server is started from the repo root instead
- backend docs: `http://127.0.0.1:8000/docs`

## Local Verification Checklist

Confirm these after startup:

- frontend opens
- backend docs open
- viewer handles image, SVG, GLB, and STL states
- `3D Generator` loads and keeps the shared source preview working
- `SVG` conversion path works
- `Relief` preview and STL export path work
- auth/account surfaces load without breaking the workspace

## Plug-And-Play Deployment Setup

### 1. Deploy backend

Recommended target:

- Railway

Set all required backend values from `.env.example` into Railway variables.

### 2. Configure Supabase

Set:

- `Site URL`
- redirect URLs
- Google provider if needed

Apply:

- `backend/supabase_billing_schema.sql`

### 3. Configure Stripe

Create:

- premium product
- recurring premium price
- webhook endpoint

Use webhook endpoint:

```text
https://your-backend-domain.com/api/billing/webhook
```

### 4. Configure frontend public runtime

Edit:

- `frontend/app-config.js`

Set the final:

- brand values
- frontend site URL
- backend API URL
- support email
- Supabase public auth values

### 5. Deploy frontend

Recommended target:

- Vercel

Then attach the final custom domain.

### 6. Validate hosted install

Confirm:

- frontend domain opens
- auth redirects return to the final domain
- `/api/billing/activation-status` reports ready when production persistence is intended
- checkout opens
- successful checkout returns to the app
- premium plan resolution works
- billing portal opens for subscribed users

## Production Readiness Notes

- use `PLUTO_SUBSCRIPTION_STORE=local` only for temporary scaffold mode
- switch to `PLUTO_SUBSCRIPTION_STORE=supabase` for production persistence
- keep frontend values public and backend secrets private
- keep private keys out of repo docs and source-controlled config files
- update `CURRENT_STATE.md` and `CHANGELOG.md` whenever the install path or activation shape changes
