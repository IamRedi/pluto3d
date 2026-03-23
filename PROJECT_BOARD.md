# Pluto3D Studio Project Board

This file is the working memory for the project.
Use it to keep product direction, active tasks, decisions, and next steps in one place.

## Product Summary

Pluto3D Studio is a web app for non-expert users that:

- generates images from prompts
- converts images into SVG
- prepares 3D models for preview and 3D printing
- offers a toy-style editing workflow

Current hosting:

- Frontend: Vercel
- Backend: Railway

Core product direction:

- keep the app simple and premium-looking
- use APIs for expensive generation tasks
- keep editing, cleanup, print-fix, and presentation as Pluto3D's real value

## Current Architecture

### Frontend

- Main UI shell: `frontend/index.html`
- Viewer logic: `frontend/viewer.js`
- Print actions: `frontend/print-mode.js`
- Toy mode logic: `frontend/toy-mode.js`
- Toy Studio controls: `frontend/toy-studio.js`
- Runtime API config: `frontend/runtime-config.js`
- Test models config: `frontend/test-models.js`

### Backend

- FastAPI app entry: `backend/app/main.py`
- AI image route: `backend/app/routes/ai_photo.py`
- SVG route: `backend/app/routes/svg.py`
- Print fix route: `backend/app/routes/print_fix.py`
- Mesh cleanup service: `backend/app/services/mesh_repair.py`

## Stable Product Decisions

- Keep only two local test models:
  - `Robot.glb`
  - `f1car.glb`
- Do not depend on TripoSR in the main product flow
- Toy mode is a lightweight test/demo path
- Real 3D generation can later come from an external API
- Print Fix is a core premium-value feature
- Viewer stays unified for image, SVG, GLB, and STL
- Toy Studio edits should be visible in the main viewer, not inside a second preview viewer

## Current Working Features

- AI image generation
- SVG conversion
- Local toy generation with test models
- 3D free test flow using test models
- Print Fix pipeline:
  - GLB input
  - topology cleanup
  - STL output
- Toy Studio floating control panel
- Viewer modes:
  - Wire
  - Print

## Current UI Direction

- App-style desktop layout
- Fixed viewer panel on the right
- Independent scrolling middle panel
- Mobile layout stacks vertically
- Toy Studio is a compact floating glass panel over the middle column
- Main viewer remains the only live preview surface

## Near-Term Roadmap

### Phase 1: Stabilize The Core Studio

- refine Toy Studio controls
- improve presets and styling behavior
- add part-aware editing when models have multiple meshes
- keep viewer controls minimal and elegant

### Phase 2: Product Platform Layer

- add login and signup
- add Google login
- define user plans:
  - Guest
  - Logged-in Free
  - Premium
- lock premium-only features in frontend and backend

### Phase 3: Monetization Layer

- Stripe subscription flow
- premium activation
- free plan limits
- premium plan with no ads and better access

### Phase 4: Ad / Sponsor Layer

- show sponsor or upgrade panel during generation
- keep ad experience elegant, not noisy
- no ads for premium users

## Recommended Platform Stack

Use the simplest serious stack for this project:

- Auth: Supabase Auth
- Database: Supabase Postgres
- Billing: Stripe
- Backend app logic: FastAPI
- Frontend hosting: Vercel
- Backend hosting: Railway

Why this stack:

- simple enough for a first product
- strong enough for real accounts and plans
- easy to connect to Google login
- easy to connect to subscriptions later
- avoids building risky auth logic from scratch

## Auth Implementation Order

1. Create Supabase project
2. Enable Google auth
3. Add frontend auth entry points
4. Store user profile and plan status
5. Add backend plan checks
6. Add Stripe checkout and webhook
7. Add sponsor/ad loading state for free users

## External Services Needed Later

### Required

- Supabase
- Stripe
- Replicate
- Vercel
- Railway

### Nice To Have Later

- analytics
- email service
- sponsor or ad provider

## Required Future Env Variables

These are not all needed immediately, but this is the expected future shape.

### Frontend

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

### Backend

- `SUPABASE_SERVICE_ROLE_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `REPLICATE_API_TOKEN`

## Suggested Plan Tiers

### Guest

- basic app access
- toy test mode
- SVG tools
- limited AI image generation
- no premium 3D generation

### Logged-in Free

- more generous limits
- toy studio
- print fix
- sponsor or ad panel during generation

### Premium

- premium 3D generation
- no ads
- faster or priority processing
- higher usage limits

## Serious-App Basics To Add

- top navbar
- pricing section
- account section
- support/contact
- privacy policy
- terms of service
- footer
- sponsor/partner area
- upgrade prompts
- polished loading states
- empty states
- beta messaging for early testers

## Current Active Tasks

1. Keep Toy Studio small, stable, and useful
2. Improve styling presets and controls
3. Prepare the app structure for auth and plans
4. Add serious product sections like pricing, footer, and legal pages

## Session Handoff

Current stop point:

- platform surfaces are working
- auth preview scaffold is working
- premium lock preview is working
- usage limits preview is working
- sponsor/ad loading preview is implemented for free plans

Files touched in the current unfinished local step:

- `AUTH_IMPLEMENTATION_PLAN.md`
- `PROJECT_BOARD.md`
- `frontend/auth-scaffold.js`
- `frontend/index.html`
- `frontend/toy-mode.js`

When resuming, start with:

1. test sponsor/ad loading preview in:
   - AI
   - SVG
   - Toy
   - Free 3D
2. confirm premium preview skips sponsor loading
3. commit and push the current local changes
4. begin the real Supabase setup checklist

Recommended next implementation after commit:

1. create Supabase setup checklist
2. prepare frontend auth client scaffold
3. prepare backend auth/plan service scaffold
4. then connect real Supabase session state

## Key Reference Docs

- `PROJECT_BOARD.md`
- `README.md`
- `AUTH_IMPLEMENTATION_PLAN.md`

## Beta Readiness Checklist

The product is considered ready for friend testing when the items below are stable.

### Core App

- [x] Local frontend works
- [x] Local backend works
- [x] Vercel frontend works
- [x] Railway backend works
- [x] AI image generation works with local `.env`
- [x] SVG generation works
- [x] Toy test mode works
- [x] Print Fix works
- [x] Viewer can show SVG, GLB, and STL

### Toy Studio

- [x] Floating control panel opens and closes cleanly
- [x] Changes are visible in the main viewer
- [ ] Presets feel polished and useful
- [ ] Reset behavior is reliable in all toy flows
- [ ] Part-aware editing exists for multi-mesh models

### Product Surface

- [x] Landing/product surface exists inside the app
- [x] Plans section exists
- [ ] Footer exists
- [x] Privacy policy placeholder exists
- [x] Terms placeholder exists
- [x] Support/contact placeholder exists
- [ ] Beta label and tester guidance exist

### Platform Layer

- [x] Auth strategy chosen
- [x] Login/signup UI scaffold exists
- [ ] Google login exists
- [x] Plan gating preview exists
- [x] Premium-only buttons are visually locked
- [x] Usage limits are defined in preview form

### Monetization

- [ ] Stripe plan structure is defined
- [ ] Subscription flow exists
- [ ] Premium activation works
- [x] Free user loading sponsor/ad state preview exists

## Current Sprint: Friend-Test Beta

This is the recommended order for the next work period.

1. Stabilize Toy Studio controls and presets
2. Add a `Night Mode` toggle
3. Build serious product UI sections:
   - navbar
   - hero
   - pricing
   - sponsor strip
   - footer
4. Add basic legal/support pages
5. Define auth and plan architecture
6. Add auth UI scaffold
7. Lock the recommended stack: Supabase + Stripe

## Task Split

### Codex Owns

- code structure
- frontend and backend implementation
- product-board updates
- premium/free flow planning
- UI polishing
- testing guidance

### User Owns

- `git push`
- external dashboards:
  - Vercel
  - Railway
  - Replicate
  - future Supabase
  - future Stripe
- secret keys and env values
- real-world friend testing feedback

## Immediate Next Build Candidates

Choose one of these when continuing:

1. `Toy Studio polish`
   - better preset logic
   - better reset behavior
   - better edit labels
2. `Night Mode`
   - global theme toggle
   - saved preference
3. `Serious landing layer`
   - navbar
   - hero
   - pricing
   - footer
4. `Auth planning scaffold`
   - choose stack
   - define data model
   - prepare UI entry points
5. `Auth integration`
   - Supabase project
   - frontend auth client
   - backend plan checks
   - Stripe hookup

## Next Recommended Tasks

1. Improve Toy Studio presets and part-aware editing
2. Add a `Night Mode` toggle
3. Add a serious landing/product layer:
   - hero
   - pricing
   - sponsor strip
   - footer
4. Add auth system planning and scaffolding

## Decisions Log

### 2026-03-23

- Removed heavy dependence on large local model sets
- Reduced toy test assets to two models
- Split key frontend logic into modular files
- Added local `.env` loading for backend tokens
- Fixed AI token handling
- Built compact Toy Studio panel and kept preview in the main viewer
- Decided to move toward a real product platform with auth, plans, premium access, and sponsor/ad loading states
- Chosen recommended platform stack: Supabase Auth + Supabase Postgres + Stripe

## How To Use This File

Whenever we start a new work session, review:

- Product Summary
- Stable Product Decisions
- Current Active Tasks
- Next Recommended Tasks

Whenever a major decision changes, add it to:

- Decisions Log

Whenever a task is completed, move the board forward instead of keeping old temporary notes in chat.
