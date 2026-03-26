# Pluto3D Studio Project Board

This file is the working memory for the project.
Use it to keep product direction, active tasks, decisions, and next steps in one place.

## Product Summary

Pluto3D Studio is a web app for non-expert users that:

- generates images from prompts
- converts images into SVG
- prepares 3D models for preview and 3D printing
- offers a toy-style editing workflow
- is being structured both as:
  - Pluto3D's own flagship studio platform
  - a future plug-and-play installable product for customers

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
- public install-time values should live in a simple frontend config layer
- private credentials should stay in backend env only
- the product should be deployable by configuration, not source edits, wherever possible

## Current Working Features

- AI image generation
- SVG conversion
- Local toy generation with test models
- 3D test flow using local demo models
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

- `frontend/app-config.js`

### Backend

- `SUPABASE_SERVICE_ROLE_KEY`
- `PLUTO_PREMIUM_EMAILS`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `REPLICATE_API_TOKEN`

## Suggested Plan Tiers

### Guest

- basic app access
- toy test mode
- SVG tools
- limited AI image generation
- no real 3D generation
- only 3D test/demo generation

### Logged-in Free

- more generous limits
- toy studio
- print fix
- sponsor or ad panel during generation
- 3D stays in test/demo mode only

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
5. Keep live auth surfaces clean once Supabase is active and hide preview-only controls
6. Use backend-owned plan resolution as the base for future premium gating
7. Build a plug-and-play deployment foundation for buyer installs

## Working Board

### Now

- keep SVG stable with only:
  - `Detail`
  - `Clean Background`
- keep Toy Studio compact and visually clean
- keep platform surfaces serious but lightweight
- position 3D clearly as:
  - `Generate Test`
  - `Generate 3D PRO`
- position Toy clearly as:
  - `Generate Test Toy`
  - `Generate Toy PRO`
- avoid heavy backend dependencies unless they clearly improve quality

### Next

- polish Toy Studio presets so they feel more useful
- improve Toy Studio reset behavior
- add clearer Toy Studio feedback/status messaging
- expand Toy Studio into part-aware editing lite
- test sponsor/ad loading preview in all major flows
- prepare real auth runtime scaffold before live keys arrive
- wire the first live Supabase session into Login and Profile
- add backend auth and plan service scaffold
- sync frontend live session with backend account route
- reduce preview-only auth controls once live auth is stable
- remove preview-heavy wording from Login/Profile where live auth already exists
- add a temporary backend premium assignment path before Stripe goes live
- keep 3D and Toy product language aligned with:
  - `Test`
  - `PRO`
- keep env example files ready for auth and billing keys
- use a frontend auth config file instead of frontend env injection

### Later

- Stripe subscriptions
- real plan validation in FastAPI
- gallery/history backed by real user data

### Parked

- YOLO / Ultralytics auto-focus for SVG
- any heavy segmentation pipeline on Railway

## Latest Product Decisions

- live Supabase auth works locally with Google login
- `Login` and `Profile` should feel like real account surfaces, not preview labs
- premium testing should move to backend-owned plan resolution
- before Stripe, selected tester emails can be marked premium through backend env
- second preview viewer inside Toy Studio

### Needs From User Later

- Supabase project
- Google auth enablement
- Stripe account and keys
- final domain connection
- production testing feedback from friends

## Recommended Next Task

The best next task is:

- `Toy Studio preset polish`

Why:

- it improves the product’s core editing value
- it is visible immediately in the main viewer
- it does not require new infrastructure
- it is safer than jumping to real auth integration too early

Suggested scope for that task:

- make presets feel more distinct
- improve labels so they are easier to understand
- make reset behavior more reliable
- give Toy Studio lightweight status feedback for preset/apply/reset actions
- add a first part-target selector for head/body/all edits
- optionally add one extra simple control like `Tilt` or `Cute`

## Deferred / Difficult Tasks

- SVG subject isolation with YOLO / Ultralytics is deferred.
- Reason:
  - it did not improve results enough in current tests
  - it adds backend weight and deployment risk for Railway
  - a weak auto-focus feature is worse than a clean simple SVG flow
- Current decision:
  - keep `Detail` and `Clean Background`
  - do not expose YOLO-based auto focus in the UI for now
  - revisit only if we later need a stronger object-isolation pipeline
  - keep the active SVG backend free of YOLO dependencies for stability

## Latest Product Decisions

- Keep the active SVG flow simple and clear instead of over-stylized
- Prefer preprocessing changes before SVG conversion, not fake post-effects after conversion
- Keep difficult computer-vision ideas parked until they clearly improve quality
- Keep real 3D generation positioned as a premium feature, with test/demo generation only on free surfaces
- Keep Toy generation positioned the same way: free test flow, premium real generation
- Use `PROJECT_BOARD.md` as the main project memory and session handoff file
- Treat invalid frontend auth transitions as `guest` in `/api/account/me` to avoid noisy 401 logs during login/logout refresh cycles

## Session Handoff

Current stop point:

- platform surfaces are working
- auth preview scaffold is working
- premium lock preview is working
- usage limits preview is working
- sponsor/ad loading preview is implemented for free plans
- SVG currently uses:
  - `Detail`
  - `Clean Background`
- YOLO-based focus crop is removed from the active flow

Files touched in the current unfinished local step:

- `AUTH_IMPLEMENTATION_PLAN.md`
- `PROJECT_BOARD.md`
- `frontend/auth-scaffold.js`
- `frontend/index.html`
- `frontend/toy-mode.js`

When resuming, start with:

1. open this board and check:
   - `Working Board`
   - `Recommended Next Task`
   - `Latest Product Decisions`
2. decide whether we are in:
   - studio polish
   - platform/auth work
   - SVG refinement
3. if unclear, review the current changed files before coding

Recommended next implementation after commit:

1. create Supabase setup checklist
2. prepare frontend auth client scaffold
3. prepare backend auth/plan service scaffold
4. then connect real Supabase session state

Current implementation note:

- `SUPABASE_SETUP_CHECKLIST.md` is the user-facing setup guide for the first real auth step
- `frontend/app-config.example.js` and `backend/.env.example` are now the main reference config files for the next integration phase
- `frontend/auth-client.js` is now the runtime scaffold that detects frontend auth config and prepares the UI for live Supabase wiring
- `frontend/auth-config.js` remains only as a legacy optional fallback; the main install surface is `frontend/app-config.js`

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
2. Keep SVG simple and reliable
3. Keep platform surfaces serious and presentable
4. Prepare auth integration in a controlled way
5. Avoid heavy features until beta feedback proves they are worth it

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
2. `Sponsor flow testing`
   - AI
   - SVG
   - Toy
   - Free 3D
3. `Supabase setup checklist`
   - completed and documented
4. `Auth integration`
   - Supabase project
   - frontend auth client
   - backend plan checks
   - Stripe hookup

## Next Recommended Tasks

1. Add Stripe webhook handling and persistent subscription state
2. Define the first Supabase-backed billing/subscription data model
3. Test sponsor/ad preview in all main flows against real free vs premium state
4. Return to Toy Studio polish after billing path is structurally safe

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

## Current Session Note

- Supabase project is live and Google auth is enabled.
- Local frontend auth config and backend service key are set.
- Live Google login/logout works in the app.
- Backend premium resolution now works using:
  - Supabase user verification when available
  - JWT payload fallback when the user endpoint does not return the email cleanly
- The active premium test user resolves correctly as `Premium`.
- Login/Profile UI has been cleaned up to feel more product-like and less preview-oriented.
- Backend auth debug output has been removed from the profile-facing flow.
- Premium-only UI locks now follow backend account plan resolution when live auth is active.
- Usage limits still use the local beta counter path until server-side quotas and Stripe are added.
- First Stripe billing scaffold now exists in backend and frontend.
- Plans, Shop, and Profile now expose premium billing entry points.
- Live Stripe activation is still blocked on keys, price ID, webhook sync, and customer persistence.
- Subscription lifecycle scaffold now exists with a temporary local state adapter.
- Backend plan resolution now checks normalized subscription state before tester fallback.
- First Supabase billing schema draft now exists for `profiles` and `subscriptions`.
- Supabase billing schema now also covers webhook event idempotency.
- Frontend now has a public install config layer for brand, API base, support email, and auth public values.
- Product distribution direction now explicitly includes self-host / plug-and-play installs.
- Subscription persistence now supports a controlled mode switch:
  - `local` for scaffold stability
  - `supabase` for production persistence after schema setup
- Billing readiness is now treated as a separate activation concept:
  - Stripe configured
  - webhook secret configured
  - subscription store schema ready
- Frontend billing surfaces now sync authenticated subscription state from the backend.
- Billing config now exposes explicit activation blockers for safer rollout.
- Billing config now exposes ordered next steps for activation handoff.
- Account and billing flows now expose plan source and plan reason for rollout/debug traceability.
- Profile now exposes a visible activation handoff map for live config values.
- Billing return states now surface clean in-product feedback after Stripe redirects.
- Billing activation now exposes measurable progress so readiness can be tracked as a rollout checklist, not just a blocker list.
- Authenticated account/billing flows now auto-sync the Supabase `profiles` row so profile persistence starts before the first Stripe webhook arrives.
- Plan resolution now treats `profiles.plan` as a stable production snapshot behind the subscription layer.
- Activation handoff now reports separate frontend/backend/schema completion counts for cleaner production rollout.
- Activation handoff now exposes a phase-based switch path for go-live sequencing.
- Activation handoff now exposes the current switch phase and verification queue for the final live step.

## Work Log

### 2026-03-24

- Collected activation value: frontend domain `https://pluto3d.vercel.app`.
- Collected activation value: backend API URL `https://pluto3d-production.up.railway.app`.
- Collected activation value: Supabase URL `https://jnpqcpsxyzhhsrceqepk.supabase.co`.
- Collected activation value: Supabase publishable key `sb_publishable_yu8iT7e3ocTl7CCjpWFPNw_qeoGerPo`.
- Collected activation secret: Supabase service role key received in chat and intentionally not stored in repo docs.
- Stripe dashboard access is now ready; next activation values will be collected from Stripe one by one.
- Collected activation value: Stripe publishable key received in test mode (`pk_test_...`).
- Collected activation secret: Stripe secret key received in chat and intentionally not stored in repo docs.
- Collected activation value: Stripe premium price ID received in test mode (`price_1TEcsCE38yXShlb4rri0c6kW`).
- Collected activation secret: Stripe webhook secret received in chat and intentionally not stored in repo docs.
- Local backend `.env` has now been synced with the collected Supabase and Stripe test values.
- Local billing activation now resolves as ready in `local` store mode with the collected test keys.
- Applied `backend/supabase_billing_schema.sql` successfully in Supabase SQL Editor.
- Local backend store mode has now been switched from `local` to `supabase`.
- Verified with Supabase connectivity that `profiles`, `subscriptions`, and `billing_webhook_events` are all ready in `supabase` mode.
- Billing activation status now resolves as `activationReady=true` in local `supabase` mode; the next step is end-to-end checkout/webhook verification.
- Railway backend env rollout is now in progress with Supabase + Stripe test values.
- Live Railway verification is currently blocked because the billing/Supabase implementation changes are still local and not yet deployed from GitHub.
- Live Railway `/api/billing/activation-status` now returns `activationReady=true` with `storeMode=supabase` and no blockers.
- The backend production path is now structurally live; the next step is an end-to-end Stripe checkout/webhook smoke test.
- Smoke test observation: after Stripe return to the site, the frontend can appear as `guest`, so live auth restore after checkout needs verification.
- Found a plan-resolution edge case in `supabase` mode: `profile_snapshot=free` could override `PLUTO_PREMIUM_EMAILS`; tester-email fallback now needs to stay ahead of profile-snapshot fallback.
- Likely live auth blocker: Supabase OAuth/site redirect configuration may still point to `http://127.0.0.1:5500`, which would explain post-login return to localhost instead of the Vercel app.
- Supabase live auth redirect URLs were updated to include `https://pluto3d.vercel.app` and `https://pluto3d.vercel.app/`; `Site URL` was then checked in the same live config before retesting the Vercel login flow.
- Live checkout smoke test found the next real billing issue: a subscription could be stored as `checkout_completed` instead of its real Stripe status, so `/api/account/me` still resolved `free` while the billing panel showed a subscription record.
- Billing hardening update: `checkout.session.completed` now fetches the real Stripe subscription status immediately, webhook handling now accepts `customer.subscription.created`, and stale `checkout_completed` rows can self-refresh from Stripe on the next plan lookup.
- Live verification now shows both premium paths working independently:
  - Stripe-backed subscription accounts can resolve `premium` from `subscription_record`.
  - Tester fallback accounts can resolve `premium` from `PLUTO_PREMIUM_EMAILS`.
- Remaining live blocker is narrower now: one expected tester account still resolves `free`, so the next check is the exact authenticated email string shown in Profile versus the Railway `PLUTO_PREMIUM_EMAILS` value.
- Added a production safeguard for legacy Supabase rows: `/api/account/me` and `/api/billing/status` now fall back to `tester_email/default_free` instead of leaving the frontend stuck on `session_default` when profile/subscription sync hits an inconsistent row.
- Billing UX moved past raw debug-style chips: `Profile` and `Plans` now show human-readable subscription status, current billing-period date when available, clearer tester-vs-Stripe lifecycle copy, and smarter `Upgrade` vs `Manage Billing` actions.
- Billing runtime now exposes launch-awareness for the final rollout: `Stripe test/live mode`, `temporary/custom domain` status, and go-live blockers now surface in both backend status payloads and the frontend billing surfaces.
- Public install config now includes `siteUrl`, so the final launch domain is an explicit config value and can be surfaced in billing/account UI without depending only on the current host.
- Added the first real `pluto-3d.com` DNS records in Cloudflare for the final domain rollout:
  - root `A @ -> 216.198.79.1`
  - `CNAME www -> cname.vercel-dns.com`
  - proxy kept on `DNS only` for the Vercel connection path
- Vercel now validates `pluto-3d.com`; `www.pluto-3d.com` is attached in production with only a DNS-change recommendation remaining, so the launch target can move from `pluto3d.vercel.app` to `https://www.pluto-3d.com`.
- Supabase `Site URL` and the main production redirect URLs were updated for the `pluto-3d.com` rollout path, Railway billing return URLs were switched to `https://www.pluto-3d.com`, and the launch-target config change was pushed.
- Final handoff requirement from the user: deliver a clean infrastructure/account summary that lists every connected platform, domain, backend/service, auth/billing dependency, and likely recurring paid surface (for example Vercel, Railway, Supabase, Stripe, Cloudflare), while keeping private secrets separate from the inventory itself.
- Added `INFRASTRUCTURE_INVENTORY.md` as the operator-facing map of domains, services, paid surfaces, config locations, and secret boundaries so Pluto3D is easier to operate and easier to sell as a plug-and-play stack.
- Added `PLATFORM_ACCOUNTS_OVERVIEW.md` as the plain-language owner summary of which external account does what, which services may cost money, and where public config versus private secrets belong.
- Billing activation handoff now counts `siteUrl` as a first-class frontend config item, so the final custom-domain launch target is part of readiness tracking instead of being an implied value.
- Added `PLUG_AND_PLAY_DEPLOY_CHECKLIST.md` and aligned `backend/.env.example` with custom-domain production examples so buyer installs follow a cleaner real-world checklist instead of localhost-style defaults.
- Added `STRIPE_LIVE_SWITCH_CHECKLIST.md` so the final `Stripe test -> live` step is documented as an operator runbook instead of being left to memory when onboarding/verification is complete.
- Frontend auth redirects now prefer the public `siteUrl` config value, so login/signup callbacks follow the canonical install domain instead of whichever preview host is open.
- Frontend auth bootstrap now prefers `frontend/app-config.js` directly and only falls back to `frontend/auth-config.js` for legacy installs, reducing plug-and-play setup friction.
- Billing/profile surfaces now also show whether the operator is viewing the canonical launch host or a preview host, making domain-rollout checks easier during support and handoff.
- Stripe live mode is now structurally configured in Railway with live keys, live price ID, live webhook secret, Supabase persistence, and custom-domain billing URLs. The remaining step is the first end-to-end live checkout/webhook/portal smoke test.
- Removed temporary backend auth debug output from `/api/account/me`.
- Removed the temporary backend plan debug card from the `Profile` surface.
- Switched live premium locking to a backend-resolved plan flow instead of trusting frontend auth metadata.
- Kept usage-limit preview behavior local on purpose as a temporary beta implementation.
- Added the first Stripe-ready billing scaffold in FastAPI with checkout and portal session endpoints.
- Added frontend billing runtime handling and premium upgrade entry points in `Plans`, `Shop`, and `Profile`.
- Expanded backend env examples for Stripe publishable key, price ID, and redirect URLs.
- Added Stripe webhook scaffold plus normalized customer/subscription state handling.
- Chosen a temporary local JSON adapter for subscription state so the billing contract can stabilize before Supabase persistence is wired.
- Added the first Supabase SQL schema draft for billing-ready `profiles` and `subscriptions`.
- Added `frontend/app-config.js` as the public runtime install surface for buyer-friendly deployment.
- Added `SELF_HOST_QUICKSTART.md` to document the one-hour-style install path.
- Added a subscription storage adapter so billing state can move from local scaffold storage to Supabase without changing API contracts.
- Added webhook event persistence support for the Supabase production path.
- Added activation-readiness checks so billing can distinguish between scaffold-ready and production-ready.
- Connected frontend billing runtime to backend subscription status and portal availability.
- Added `PRODUCTION_ACTIVATION_RUNBOOK.md` for the future live switch to Supabase-backed billing persistence.
- Added plan-source traceability so the app can show whether plan resolution comes from subscription persistence, tester fallback, or metadata.
- Exposed activation handoff locations inside the Profile surface so rollout prep is visible from the product UI.
- Added in-product billing return feedback for Stripe success/cancel/portal redirects.
- Added activation progress metrics so Plans/Profile can show checklist completion and rollout maturity.
- Added automatic Supabase profile sync from authenticated account/billing flows for a safer local-to-production persistence transition.
- Added a profile-plan snapshot fallback so premium/free resolution stays stable even when subscription row timing lags during rollout.
- Added handoff completion summaries so production activation can be tracked separately across frontend config, backend env, and schema readiness.
- Added a phase-based switch path so go-live can be followed as an ordered activation sequence.
- Added current-phase and verification-queue visibility so the final switch path is operationally clearer.

## Work Log - 2026-03-25 UI Polish Pass

- Cleaned user-facing `beta`, `preview`, and placeholder wording from `frontend/index.html` so the product reads more like a launch-ready platform than an internal scaffold.
- Updated Gallery, Login, Profile, Shop, Support, and billing copy to reflect the current live stack instead of future-state language.
- Replaced broken visible encoding artifacts in footer, download CTA, status text, and several plan/profile surfaces without changing underlying auth or billing logic.
- Kept the pass intentionally low-risk: no auth, billing, or routing behavior was changed, and the remaining encoding artifacts are currently limited to internal comments rather than user-facing UI.
- Simplified `Plans` and `Profile` so they read like customer-facing product surfaces rather than operator/debug dashboards.
- Removed activation-handoff and runtime-detail blocks from the visible account UI to reduce noise and improve perceived product quality.
- Simplified `Login` into a minimal Google-or-email entry surface and removed extra checklist/status panels that customers do not need to see.
- Reduced `Profile` further so it shows only account, subscription, and usage essentials instead of duplicate stats and helper controls.
- Trimmed the visible `Login` surface even further so customers see only `Account Access` and `Email`, with no extra subtitle-heavy onboarding copy.
- Added a compact centered modal treatment for `Login` and `Profile` so those surfaces feel lighter, less dashboard-like, and more like polished product dialogs over the blurred studio background.
- Redesigned `Login` into a single focused auth card with a cleaner Google-first flow, email divider, and automatic modal close on sign-out so the user lands back in the workspace context.
- Removed the forced desktop scroll behavior from `Login` and shifted the email/password area into a cleaner horizontal layout so the auth dialog feels fixed, balanced, and less like a long form panel.
- Reduced the visible outer shell of the `Login` overlay so the user mainly sees a centered auth card over blur, instead of a larger dashboard-like container behind it.
- Re-expanded the `Login` dialog width after review so the centered auth card keeps the cleaner modal feel without looking cramped on desktop.
- Tightened the outer `Login` shell again so the visible modal frame stays close to the auth card size instead of leaving a large empty panel around it.
- Switched the `Login` shell to auto-fit content width so the title/close layer centers around the auth card instead of stretching as a larger frame.
- Next recommended focus after this pass:
  - visual polish and hierarchy refinement
  - spacing, typography, and card consistency across surfaces
  - only after that, run the first real live-payment smoke test

## Work Log - 2026-03-25 System Audit

- Reviewed the required handoff docs before continuing:
  - `PROJECT_BOARD.md`
  - `AUTH_IMPLEMENTATION_PLAN.md`
  - `SUPABASE_SETUP_CHECKLIST.md`
  - plus the current production/self-host/infra runbooks
- Verified repo baseline:
  - git worktree was clean at audit start
  - head commit matched `89d148c Auto-fit login shell around centered auth card`
- Local backend safety checks passed at the code level:
  - `backend/app` compiled successfully with `python -m compileall app`
  - FastAPI app imported successfully
  - local smoke checks confirmed `GET /` and unauthenticated `GET /api/account/me` return expected healthy responses
- Local billing smoke checks only became fully readable after allowing network access to Supabase:
  - local backend currently reports `activationReady=true`
  - local backend currently reports `goLiveReady=false`
  - local backend currently reports `stripeMode.mode=test`
  - local backend currently reports `domainStatus.mode=temporary`
- Production verification matched the user handoff summary:
  - live Railway `GET /api/billing/activation-status` now returns `activationReady=true`
  - live Railway `GET /api/billing/activation-status` now returns `goLiveReady=true`
  - live Railway now reports `stripeMode.mode=live`
  - live Railway now reports `domainStatus.mode=custom`
  - deployed `https://www.pluto-3d.com/app-config.js` matches the current public frontend config values
- Frontend audit result:
  - external frontend JavaScript files passed `node --check`
  - no UI logic was changed during this audit
- Important operational note:
  - local backend env does not currently mirror the deployed Railway live env for billing/domain mode
  - this means local billing/account runtime indicators can disagree with production until local env is intentionally aligned
- Documentation drift found:
  - `INFRASTRUCTURE_INVENTORY.md` reflects live Stripe/custom-domain status
  - `PLATFORM_ACCOUNTS_OVERVIEW.md` still says Stripe test mode is active
  - future handoff docs should keep the platform overview aligned with the live backend truth
- Technical debt/risk found during the audit:
  - `backend/app/config.py` exposed that Meshy auth was still repo-coupled instead of env-driven
  - this was then moved onto `MESHY_API_KEY` so future deploys can use backend env instead of hardcoded source state
- Meshy hardening follow-up:
  - `Generate 3D PRO` flow has now been reconnected to a real async Meshy task flow instead of expecting an immediate `model_url`
  - Meshy auth is now env-based through `MESHY_API_KEY` instead of a hardcoded repo value
  - local `backend/.env` still needs a real `MESHY_API_KEY` value before local PRO generation will succeed again
  - Railway must also expose `MESHY_API_KEY` before this change is deployed to production
- UI polish follow-up:
  - `Profile` now has a cleaner premium hierarchy with a stronger account overview, clearer subscription state, compact usage stats, and lighter support presentation
  - workspace footer/legal/support presentation is now more structured and less like a temporary note block
  - workspace column rhythm was tightened slightly and the account/footer surfaces now scale more cleanly through the existing responsive layout
  - workspace hierarchy pass added a stronger top rail, cleaner section intros, tighter panel spacing, and a more intentional sidebar rhythm without changing product logic
  - mobile/desktop consistency pass tightened header actions, modal spacing, panel/viewer balance, and mobile breakpoint rhythm so the UI holds together more cleanly across sizes
  - theme polish test now uses sun/moon toggle icons and a deeper universe-style background direction with the thin grid feel removed from the main backdrop
  - theme direction has now moved further toward a Windows-like graphite shell with green accent states across sidebar buttons, profile cards, premium CTAs, viewer controls, progress bars, and drag/drop highlights
  - theme styling is now being refactored onto centralized semantic tokens in `frontend/index.html` so future palette changes can be made from one theme layer instead of hunting hardcoded button and panel colors
  - login shell has now been tightened to sit closer to the auth card itself, with the remaining login-specific blue surface styling moved onto the same graphite/green token direction
  - login modal width is now controlled by a single `--login-modal-width` token so the auth surface can be widened or tightened later without hunting multiple layout rules
  - a few tiny login micro-adjustments are still parked for later visual refinement, but the current width/centering/theme direction is now acceptable as the working baseline
  - the opening product rail/test-ad style surface has now been removed from the workspace, and customer-facing copy across Workspace, Plans, Gallery, Shop, Privacy, Terms, and Support has been cleaned to reduce test/demo/future-state language
  - `Plans`, `Gallery`, and `Shop` now have a cleaner final-pass hierarchy with summary feature blocks and calmer premium copy so those surfaces read more like real product sections than placeholder content
  - the main viewer now stays deep black in both dark and light theme modes so the 3D stage keeps the same stronger visual depth regardless of surrounding UI theme
  - the attempted structural redesign of the `Toy` panel was rolled back after review; the simpler toy layout remains the baseline for now
  - `Toy Studio` launch is now constrained to the `Toy` panel and only appears after a toy model is loaded into the viewer, so the editing flow stays contextual instead of floating globally across the workspace

## Chat Handoff 1

If we continue in a new chat, resume from this exact state:

- Product identity: `Pluto3D Studio`
- Frontend: Vanilla JS
- Backend: FastAPI
- Main docs to review first:
  - `PROJECT_BOARD.md`
  - `AUTH_IMPLEMENTATION_PLAN.md`
  - `SUPABASE_SETUP_CHECKLIST.md`
- Working style:
  - speak to the user in Albanian
  - keep code and comments in English
  - always give exact instructions when the user must do something
  - specify:
    - whether terminal is needed
    - which folder to run from
    - whether `venv` is needed
  - update the board whenever a major decision or blocker appears
- Current product truth:
  - SVG is stable
  - Toy Studio exists and is good enough for beta
  - Print Fix -> STL is core
  - 3D test/demo vs PRO flows are separated
  - Supabase auth is live
  - Google login is live
  - Premium plan can now be resolved from backend
- Recommended next step after handoff:
  - replace local subscription-state storage with Supabase persistence
  - keep frontend install setup simple and config-driven
  - connect webhook-driven premium activation

Updated after the 2026-03-24 session:

- backend auth debug surface is removed
- premium/free locks now follow the real backend plan in live auth mode
- first Stripe billing scaffold is now in place across backend and frontend
- subscription lifecycle scaffold now exists behind the billing API
- frontend public install config now exists for plug-and-play distribution
- next recommended step is:
  - replace local subscription-state storage with Supabase persistence
  - keep frontend install setup simple and config-driven
  - connect webhook-driven premium activation
  - then validate Stripe checkout and portal end-to-end
