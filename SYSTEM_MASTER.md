# Pluto3D System Master

This file is the canonical high-level reference for Pluto3D.
Use it first when the project goal, stack, service ownership, environment model, or system rules are unclear.

## Canonical Documentation Set

The active documentation system is:

- `SYSTEM_MASTER.md`
- `CURRENT_STATE.md`
- `CHANGELOG.md`
- `INSTALL_GUIDE.md`
- `PROJECT_MAP.md`
- `AI_RULES.md`
- `.env.example`

Legacy documents are intentionally kept in the repo as migration sources and detailed historical notes.
They should support this system, not replace it.

## Working Method

These are the standing workflow rules for Pluto3D:

- communicate with the user in Albanian
- keep code, comments, file names, and documentation in English
- before any meaningful change:
  - explain what will change
  - explain why it is being changed
  - make clear whether the change belongs to `v1` or `v1.1`
- ask the user only for important product, workflow, or risk decisions
- after every meaningful change, update:
  - `CURRENT_STATE.md`
  - `CHANGELOG.md`
- keep important project memory inside the repo, not only in chat

## Product Goal

Pluto3D is a premium-looking studio app that helps non-expert users:

- generate concept images
- convert images into SVG
- create or preview 3D outputs
- prepare printer-friendly outputs
- move from idea to printable asset through a simple customer-facing flow

The product should hide technical complexity and feel clean, visual, and trustworthy.

## Version Model

### Frozen Production

- product version: `v1`
- protected branch baseline: `main`
- frozen release branch: `release/v1-launch`
- frozen release tag: `v1-launch-2026-03-26`
- live frontend target: `https://www.pluto-3d.com`

`v1` should stay stable and receive only targeted production bug fixes.

### Active Development

- working version: `v1.1`
- active branch: `develop`

`v1.1` is the active local/test line for remodel work, UI polish, and future production adaptation.

## Core Product Scope

Current system responsibilities include:

- `3D Generator`
  - prompt or upload source handling
  - concept-image generation
  - owned test-model flow
  - premium real 3D generation path
- `SVG Generator`
  - prompt/upload source prep
  - SVG conversion
  - viewer-based output handling
- `Photo Relief`
  - local relief preview
  - browser-side STL export
- unified viewer
  - image
  - SVG
  - GLB
  - STL
- account and billing surfaces
  - Supabase auth
  - plan resolution
  - Stripe billing lifecycle

## Stack

### Frontend

- Vanilla HTML/CSS/JavaScript
- main shell in `frontend/index.html`
- viewer logic in `frontend/viewer.js`
- runtime config in `frontend/runtime-config.js`
- public install config in `frontend/app-config.js`
- local/test model registry in `frontend/test-models.js`

### Backend

- FastAPI
- app entry in `backend/app/main.py`
- routes under `backend/app/routes/`
- services under `backend/app/services/`

### External Services

- GitHub
  - source control
  - deploy source for hosted environments
- Vercel
  - frontend hosting
- Railway
  - backend hosting
- Supabase
  - auth
  - account identity
  - subscription persistence
- Stripe
  - checkout
  - billing portal
  - subscription webhooks
- Replicate
  - AI image generation provider
- Meshy
  - premium real 3D generation provider
- Cloudflare
  - DNS for the public domain

## Environment Structure

### Public Frontend Runtime Config

Public install-time values live in:

- `frontend/app-config.js`

This file is the public configuration surface for:

- app name
- studio name
- brand subtitle
- `siteUrl`
- `apiBase`
- support email
- Supabase public auth values

Optional legacy auth fallback:

- `frontend/auth-config.js`

### Private Backend Environment

Private backend values live in:

- `backend/.env`

The canonical template is:

- `.env.example`

Main backend variable groups:

- generation
  - `REPLICATE_API_TOKEN`
  - `MESHY_API_KEY`
- auth and plan resolution
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `PLUTO_PREMIUM_EMAILS`
- billing
  - `STRIPE_SECRET_KEY`
  - `STRIPE_PUBLISHABLE_KEY`
  - `STRIPE_PREMIUM_PRICE_ID`
  - `STRIPE_WEBHOOK_SECRET`
  - `STRIPE_SUCCESS_URL`
  - `STRIPE_CANCEL_URL`
  - `STRIPE_PORTAL_RETURN_URL`
  - `PLUTO_SUBSCRIPTION_STORE`
  - `PLUTO_BILLING_STATE_FILE`

## License And Asset Rules

These rules are mandatory for sale readiness and long-term safety:

- keep `COMMERCIAL_LICENSE_AUDIT.md` current when dependencies, assets, or external services change
- keep `OWNED_MODEL_ASSETS.md` current when owned test assets change
- do not copy GPL-licensed lithophane code into Pluto3D
- keep Meshy ownership assumptions tied to paid-plan usage and documented provenance
- verify the exact Replicate model license before treating AI output paths as commercially cleared
- replace or document any asset with unclear provenance before sale
- keep private keys and OAuth secrets out of repo docs

## Performance And Stability Rules

- do not destabilize frozen production `v1` for normal feature work
- keep heavy backend `print-fix` out of the active public path unless a proven need justifies it
- prefer browser-side STL/export flows when they stay stable
- keep new dependencies minimal and commercially safe
- review owned-model asset weight before `v1.1` production release
- normalize staging asset paths before release if they remain user-facing or operationally confusing
- keep deployments config-driven wherever possible

## Source Of Truth Order

When the current project state is unclear, use this order:

1. `SYSTEM_MASTER.md`
2. `CURRENT_STATE.md`
3. `CHANGELOG.md`
4. `INSTALL_GUIDE.md`
5. `PROJECT_MAP.md`
6. `AI_RULES.md`

Use legacy files only when deeper historical detail is needed.

## Legacy Source Material Kept In Repo

The following files remain useful as detailed migration sources:

- `VERSION_WORKFLOW.md`
- `PROJECT_BOARD.md`
- `V11_REMODEL_PLAN.md`
- `V11_PRODUCTION_ADAPTATION.md`
- `FRONTEND_V11_BLOCKS.md`
- `AUTH_IMPLEMENTATION_PLAN.md`
- `SUPABASE_SETUP_CHECKLIST.md`
- `PRODUCTION_ACTIVATION_RUNBOOK.md`
- `SELF_HOST_QUICKSTART.md`
- `INFRASTRUCTURE_INVENTORY.md`
- `PLATFORM_ACCOUNTS_OVERVIEW.md`
- `PLUG_AND_PLAY_DEPLOY_CHECKLIST.md`
- `STRIPE_LIVE_SWITCH_CHECKLIST.md`
- `COMMERCIAL_LICENSE_AUDIT.md`
- `OWNED_MODEL_ASSETS.md`
