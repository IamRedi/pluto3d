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

## Version Tracks

### Frozen Production

- live version: `v1`
- live domain: `https://www.pluto-3d.com`
- frozen baseline branch: `main`
- frozen release branch: `release/v1-launch`
- frozen release tag: `v1-launch-2026-03-26`

Rule:

- do not use this line for normal feature work
- only production bug fixes should touch it

### Active Development

- active version: `v1.1`
- active branch: `develop`

Rule:

- all new implementation work should continue here
- keep version-tracking notes in `VERSION_WORKFLOW.md`

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

1. Keep `v1` production stable and frozen unless a real live bug requires a hotfix
2. Continue all normal product work on `v1.1` through `develop`
3. Collect UX issues without destabilizing auth, billing, or backend runtime
4. Keep client-facing surfaces premium, minimal, and non-technical
5. Leave heavy backend work paused unless it directly protects stability
6. Keep documentation and handoff notes current after every meaningful step
7. Preserve plug-and-play deployment value for future buyer installs
8. Build the `.1` backlog from real testing feedback instead of speculation

## Working Board

### Now

- keep live production visually polished and stable for friend testing
- keep the current graphite/green premium UI direction across the whole app
- keep `3D`, `Toy`, `SVG`, and `AI` easy to test on localhost without production limits
- keep `print-fix` paused in public testing mode so backend memory spikes do not take down prod
- log beta feedback and push risky fixes into `.1` unless they are clearly required now

### Next

- run the friend-test round and collect real production feedback
- verify deploy behavior between `Vercel` frontend and `Railway` backend when something looks stale
- clean remaining micro-issues in `Login`, `Profile`, and viewer mode/CTA behavior
- decide after feedback whether the next safe focus is:
  - lightweight UI refinement
  - real `Generate 3D PRO` smoke test
  - billing smoke test
- keep notes on what belongs to `.1` instead of patching everything immediately

### Later

- real gallery/history backed by user data
- shop/catalog population
- deeper toy-editing improvements
- post-beta brand/content refinement

### Parked

- YOLO / Ultralytics auto-focus for SVG
- any heavy segmentation pipeline on Railway
- version `.1` backend scaling work:
  - real concurrent `print-fix` queue / worker path
  - memory sizing strategy for Railway or alternate compute host
  - broader multi-user load handling beyond `print-fix`
  - decision on whether STL export stays placeholder-backed or returns to true repair in prod

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

- `Friend-test triage from production feedback`

Why:

- it improves the product’s core editing value
- stability and issue triage matter more than new feature work right now
- this protects the product from unnecessary churn during the beta round
- it helps separate urgent beta issues from `.1` backlog ideas

Suggested scope for that task:

- collect feedback from friends using the live site
- classify issues into:
  - production blocker
  - polish issue
  - `.1` backlog
- keep only the smallest safe fixes in the current beta branch
- avoid reopening heavy backend experiments unless production stability requires it

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

- `VERSION_WORKFLOW.md`
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

1. Let friends test the live product and gather real issues
2. Keep production stable and avoid risky backend changes
3. Fix only high-signal polish bugs during the beta round
4. Keep `print-fix` paused and memory-safe until `.1`
5. Turn repeated feedback into a clean post-beta roadmap

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

1. `Friend-test issue triage`
   - production blockers
   - confusing UX
   - cache/deploy confusion
2. `3D PRO smoke test`
   - Meshy path
   - result polling
   - download/result quality
3. `Billing smoke test`
   - Stripe checkout
   - activation sync
   - portal behavior
4. `.1 backlog shaping`
   - print-fix architecture
   - memory/concurrency strategy
   - real STL export return path

## Next Recommended Tasks

1. Triaging friend-test feedback from live production
2. Real `Generate 3D PRO` smoke test with current Meshy-backed flow
3. Stripe live smoke test with a deliberate real payment
4. Version `.1` planning for backend memory/concurrency work

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
  - Supabase user verification as the required auth gate
  - JWT payload claim merge only for missing verified fields like email or metadata
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
  - `Profile` metadata and usage counters are being flattened away from glass-chip/button treatment so only real actions read as buttons while account information reads like plain product data
  - the green accent palette has been softened slightly at the theme-token level so the Windows-like graphite look stays cleaner and less loud across buttons, controls, progress, and accents
  - `Gallery` is being simplified into two clean sections: latest history on top and featured best work below, with `Robot.glb` and `f1car.glb` used as the current showcase anchors
  - `Shop` is being reduced to a single clean placeholder field so it can later grow into a real catalog/gallery surface without carrying half-finished filler blocks
  - the sidebar orb has been decoupled visually from the green accent palette and moved to a softer grey-blue pulse, while the sidebar label itself stays `Pluto` instead of inheriting the full `Pluto3D` app name
  - the top header brand now drops the square icon and keeps only the `Pluto3D` wordmark with subtitle so the main navigation bar feels cleaner and less logo-heavy
  - the main viewer can now fall back to a slow-rotating idle featured GLB when no active asset is loaded, using `frontend/app-config.js` (`idleViewerModelUrl`) so the placeholder model can be swapped later without changing viewer logic
  - the idle viewer test model has been switched from `Robot.glb` to `f1car.glb`, with a slightly faster rotation and a lower resting position so the featured placeholder sits better in the frame
  - the first idle-viewer pass introduced two frontend regressions that are now being corrected: real GLB/STL loads must keep the download button visible, and the shared viewer asset setter must still update print status instead of losing that feedback to the idle-viewer helper layer
  - production `3D` free generation is also showing a separate backend issue in Railway HTTP logs: `POST /api/print-fix` is returning `502`, so that path needs backend-side investigation and should not be confused with the viewer-only regressions
  - localhost testing now bypasses guest/free usage limits, premium locks, and sponsor wait states so the full frontend can be exercised safely on `127.0.0.1` / `localhost` before validating production behavior
  - the idle `f1car` placeholder is being kept intentionally separate from real generated models and tuned with a lighter double-sided hologram material so it reads as a featured ambient preview rather than a dark silhouette
  - Railway `print-fix` investigation found a concrete backend bug: the repair pipeline was calling outdated `trimesh` methods (`remove_degenerate_faces`, `remove_duplicate_faces`, `simplify_quadratic_decimation`) that do not exist in the pinned version, so the mesh repair layer is being updated to use the compatible `nondegenerate_faces`, `unique_faces`, and `simplify_quadric_decimation` path instead
  - `print-fix` is now being hardened for low-RAM production: uploaded GLBs are streamed to disk in chunks instead of being fully read into memory, the repair/export path is serialized behind a single-job queue, temporary upload files are cleaned up after each request, and the repair pipeline itself has been lightened by disabling the extra simplify step for now
  - localhost testing is now being opened up deliberately: guest/free usage limits and premium locks are bypassed only on `127.0.0.1` / `localhost`, and sponsor preview waits are disabled there so full workspace testing can happen cleanly before checking production again
  - real `print-fix` is now intentionally paused for the current social-circle/public testing round so repeated STL repair attempts cannot take down the main backend; the button keeps a short preparation feel and then serves a stable placeholder STL download until version `.1` revisits the proper queue/worker solution
  - `3D test` preview no longer routes the viewer through the temporary STL/print-fix path; it now loads the same GLB-style test asset path used by `Toy test`, so preview quality stays consistent across both surfaces
  - the empty-viewer `f1car` fallback is now being shifted back toward real GLB presentation instead of a full material override, using dedicated idle-only lights so the car stays visible without diverging too far from the cleaner `Toy` viewer look
  - print-mode viewer UX is being extended with a dedicated STL download CTA: when `Print` mode is active, a plain-text printer note and a second large STL-focused button appear near the top-right controls so printer-targeted export feels explicit without replacing the main GLB download CTA
  - the STL CTA is now being tightened so it appears only for real loaded/generated models (GLB/STL), with a smaller `Direct to printer` note and a cleaner `Bambu Lab / Prusa .stl` button presentation under the `Wire / Print` controls
  - viewer mode now resets back to `Wire` on load and on each new asset so the STL CTA stays hidden until the user explicitly presses `Print`
  - the STL CTA now also uses an explicit user-action flag, so it only appears after the user has actively pressed `Print` in the current viewer session rather than from any carried viewer state
  - viewer CTA gating has been tightened again so the STL CTA is now tied to the currently loaded asset and the actually active `Print` button state; the idle showroom model also stays visually clean in `Wire` instead of turning into dense mesh noise after a `Print -> Wire` toggle
  - the idle rotating showroom GLB has been scaled up again so the empty-viewer hero model reads larger and more intentional inside the stage before any real user asset is loaded

### 2026-03-26 Auth Hardening

- backend auth no longer accepts a raw decoded JWT payload as a fallback authenticated user when Supabase verification fails
- JWT claims are now used only to fill missing verified fields after `/auth/v1/user` succeeds, which keeps premium/account routes safer during auth API failures or malformed tokens

### 2026-03-26 Version Split

- `v1` is now treated as the first frozen launch version
- `main` remains the frozen production baseline for `v1`
- `release/v1-launch` and `v1-launch-2026-03-26` were created as stable release references
- active development now moves to `develop` as `v1.1`
- `VERSION_WORKFLOW.md` is now the internal manual for branch usage, hotfix flow, and version-state recovery

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

## Chat Handoff 2 - 2026-03-26 Production Friend-Test Beta

Use this section first when a new chat resumes the project.

### Project Truth

- Pluto3D Studio is now live in production and visually polished enough for real friend testing.
- Frontend stack: Vanilla JS.
- Backend stack: FastAPI.
- Auth: Supabase auth is live.
- Google login: live.
- Billing: Stripe live config is in place.
- Main domain: `https://www.pluto-3d.com`
- Fallback frontend: `https://pluto3d.vercel.app`
- Live backend: `https://pluto3d-production.up.railway.app`

### Primary Reference Order

If anything is unclear, check these first in this order:

1. `VERSION_WORKFLOW.md`
2. `PROJECT_BOARD.md`
3. `AUTH_IMPLEMENTATION_PLAN.md`
4. `SUPABASE_SETUP_CHECKLIST.md`
5. `PRODUCTION_ACTIVATION_RUNBOOK.md`
6. `SELF_HOST_QUICKSTART.md`
7. `INFRASTRUCTURE_INVENTORY.md`
8. `PLATFORM_ACCOUNTS_OVERVIEW.md`
9. `PLUG_AND_PLAY_DEPLOY_CHECKLIST.md`
10. `STRIPE_LIVE_SWITCH_CHECKLIST.md`

### How We Work In This Project

- Speak with the user in Albanian.
- Keep code and code comments in English.
- When the user must do something, give exact instructions only:
  - whether terminal is needed
  - which folder to use
  - whether `venv` is needed
  - the exact command if there is one
- Prefer small safe changes, test, then refine.
- Keep `PROJECT_BOARD.md` updated after important decisions, blockers, parked work, and meaningful changes.
- Do not make risky destructive changes casually.
- Preserve the project DNA: premium, clean, serious, and client-facing rather than technical-dashboard looking.

### Current Product Shape

- `Workspace`, `Gallery`, `Plans`, and `Shop` have gone through a major UI cleanup pass.
- `Login` and `Profile` are much cleaner and more premium than before, though a few micro-polish items remain for later.
- The main viewer now keeps a deep black stage in both themes.
- The overall theme is now a Windows-like graphite shell with softer green accents.
- The sidebar orb now reads as `Pluto` with a softer grey-blue pulse.
- the sidebar orb now also restores a small personality microinteraction:
  - hover shows a short greeting
  - click returns a short follow-up reply
  - the effect stays decorative and does not interfere with navigation or product logic
- The top brand keeps only the wordmark and subtitle, without the square icon.
- `Gallery` is now split into latest history and featured best work.
- `Shop` is intentionally simplified into one clean placeholder surface for now.
- frontend `v1.1` polish now follows a block-based workflow tracked in `FRONTEND_V11_BLOCKS.md` so copy, theme, hierarchy, icon, and mobile passes stay separated.
- first `Frontend Copy Cleanup` pass has now cleaned the most obvious future-state / placeholder wording from `Gallery`, `Shop`, and `Profile` without changing layout or product logic.
- first `Theme Refinement` pass has now centralized card/header/chip styling a bit further so the UI feels less flat and the light theme stays closer to the main graphite/green direction.

### Viewer / 3D State

- Empty viewer state now uses a rotating idle GLB hero model (`f1car.glb`) instead of a blank stage.
- The idle model has dedicated idle-only lighting and a larger scale so the stage still feels premium before a user loads anything.
- Free `3D test` preview now uses the same GLB-style path as `Toy test`, which fixed the quality mismatch that previously made `3D` previews look worse.
- The Meshy generation path is now hardened a bit further in `v1.1`:
  - backend `uploads` / `outputs` use backend-root absolute paths instead of fragile relative paths
  - Meshy polling now returns clearer terminal failure states instead of only hanging on success-only logic
  - frontend polling now stops cleanly on transport or Meshy task failures and only loads the model when a final URL exists
- The dedicated STL CTA near `Wire / Print` exists, but its final behavior is not fully finished yet:
  - current state is acceptable for beta
  - exact show/hide logic can be refined later without urgency
- The idle model no longer turns into ugly dense wire noise when switching `Print -> Wire`.

### Toy / Print State

- `Toy Studio` remains intentionally simple after a rollback of a heavier redesign.
- `Toy Studio` launches only from the `Toy` panel and only when a toy model is loaded.
- Real `print-fix` backend repair work is intentionally paused for the current beta round.
- Current public-testing behavior:
  - user still gets a believable `Fix To Print` flow
  - the system returns a stable placeholder STL for download
  - this protects production from Railway memory crashes during friend testing

### Local Testing Mode

- Localhost (`127.0.0.1` / `localhost`) is intentionally more open than production.
- Guest/free limits are bypassed there.
- Premium locks are bypassed there.
- Sponsor/ad wait states are bypassed there.
- This is only for safe full-flow testing locally and does not change live production behavior.

### Current Working Environment For `v1.1`

- Active implementation branch: `develop`
- Current stage: local `v1.1` build/test iteration before any `v1.1` production deploy
- Frontend local test URL: `http://127.0.0.1:5500/frontend/`
- Backend local test URL: `http://127.0.0.1:8000`
- Backend local runtime should use `backend` `venv`
- Git work and commits for ongoing `v1.1` changes should happen locally on `develop`
- Local code changes, local servers, and local commits do not modify the frozen live `v1` on Vercel/Railway by themselves
- Production `v1` remains untouched unless there is an explicit push/deploy/hotfix workflow

### Production Notes

- Frontend deploys go through `Vercel`, not `Railway`.
- Backend deploys go through `Railway`.
- If a frontend change looks missing on `pluto-3d.com`, check `Vercel` first before assuming backend or code problems.
- Railway memory pressure was real around `print-fix`; that is why true repair is paused for now.

### Intentional Pauses / Parked Decisions

- `print-fix` real repair pipeline is paused for public testing stability.
- Heavy backend scaling and concurrency work is parked for version `.1`.
- YOLO / heavy SVG auto-focus work remains parked.
- The STL printer CTA still needs one more refinement pass later, but is not a blocker for this beta round.

### What Is Still Open

- Friend-test feedback collection from real users
- real `Generate 3D PRO` smoke test with Meshy
- real Stripe live smoke test
- login/profile micro-polish
- final viewer CTA refinement
- commercial licensing cleanup before sale:
  - add provenance notes for owned local models
  - replace unclear Transparent Textures background
- `v1.1` remodel pivot:
  - unify `3D`, `Toy`, and `AI` thinking into one `3D Generator`
  - build prompt-image generation + recent thumbnail strip
  - build owned test-model registry with paired preview images
  - reconnect premium real 3D generation to the active preview image
  - later add `Lithophane`
- `.1` planning for:
  - Railway memory sizing or alternate compute strategy
  - proper queued/background print repair
  - broader multi-user concurrency strategy

### Latest Relevant Commits

- `075dbef` Tighten viewer print gating and enlarge idle model
- `2593e58` Gate STL CTA on explicit print action
- `8fe0b9a` Reset viewer mode before showing STL CTA
- `66d6e73` Refine print mode download CTA
- `9f3aa9f` Align free 3D preview with toy viewer
- `fec8e08` Pause print fix for public testing
- `4009ab5` Reduce print fix memory pressure
- `977b3be` Fix trimesh compatibility in print repair

### Recommended Resume Logic For The Next Chat

1. Read this board first, especially this handoff section and the latest work log notes.
2. Confirm whether the next goal is:
   - beta bug triage
   - UI micro-polish
   - Meshy smoke test
   - Stripe smoke test
   - `.1` planning
3. Avoid reopening heavy backend work unless production stability requires it.
4. Keep using `PROJECT_BOARD.md` as the primary memory instead of relying on chat history.

### Commercial Licensing Audit Snapshot

- Audit file added: `COMMERCIAL_LICENSE_AUDIT.md`
- Core app libraries are mostly permissive and low-risk for sale.
- Cleanup already applied:
  - `Horse.glb` removed from frontend gallery
  - `ultralytics` / `yolov8n` removed from the active repo path
  - toy fallback sample assets replaced with owned local assets
- Latest toy asset mapping update:
  - `robot` now uses owned `pluto-robot.glb`
  - `car` / `f1` now use owned `f1car.glb`
  - legacy `frontend/models/Robot.glb` removed from active usage
  - localhost frontend now forces local backend `127.0.0.1:8000` instead of reusing the public production API base
  - local toy assets now use a cache-busting version query so replaced GLB files do not keep showing stale browser copies
  - toy/print flow is being simplified for `v1.1` stability:
    - heavy Toy Studio shaping is removed from the active path
    - `Bambu Lab / Prusa .stl` now exports STL directly in the browser from the current GLB instead of depending on backend `print-fix`
    - `Fix To Print` is now only a lightweight preparation step for direct browser-side STL export
    - `Print` preview is being kept as a simple clay-style view rather than a backend-dependent print pipeline preview
- Remaining commercial cleanup is mostly asset provenance and sample replacement:
  - local owned-asset provenance notes
  - unclear commercial clearance for current Transparent Textures background

### v1.1 Remodel Pivot

- `v1.1` is now being reframed as a larger product remodel, not only a polish pass.
- New reference file:
  - `V11_REMODEL_PLAN.md`
- Current remodel direction:
  - move toward one cleaner `3D Generator` section
  - fold toy behavior into the main generation path instead of keeping it as a separate surface
  - use prompt-image generation and owned test models inside one unified workflow
  - keep real premium 3D generation connected to the currently selected preview image
  - keep the customer path simple, premium, and low-friction
  - keep the remodeled UI compact, low-scroll, and suitable for a later vertical-mobile optimization pass
  - keep business-limit ideas documented even before implementation so the remodel and pricing logic can stay aligned later
- Stage 1 now started:
  - main `3D` panel is being reshaped into the future `3D Generator` skeleton
  - prompt-image, shared preview, and output blocks are now represented in the core panel structure
  - old `AI` and `Toy` panels remain temporarily for compatibility until the new path is wired
  - compact prompt/toggle/card direction is now part of the remodel rules instead of a later polish-only note
  - compact pass 2 now reduces visible planning/helper copy so the panel reads closer to the intended real product shape
  - `Generate Test in 3D` now accepts either an uploaded image or the active generated concept image in the shared preview frame
  - Stage 3 registry work has started:
    - owned test models now resolve through a structured keyword-based registry
    - the simple `car/default` branch is being replaced by explicit model metadata
    - preview-image pairing is prepared in the registry structure and can be filled as owned source images are added
  - Stage 4 shared-source wiring is now in progress:
    - upload preview and prompt-generated concept preview now feed the same active `Source Preview` state
    - `Generate Real 3D` now follows the active shared source preview instead of forcing the older separated path
    - upload-to-Meshy and image-url-to-Meshy are now selected from the active source type rather than from separate panels
  - active workspace cleanup pass:
    - old `AI` and `Toy` entries are now hidden from the main sidebar so the remodel reads as one cleaner path
    - compatibility panels still remain in code as fallback surfaces while the new `3D Generator` path is being completed
    - footer/support copy is being aligned with the remodeled product path instead of the older multi-surface wording
  - compact UI pass 3:
    - prompt, toggle, thumbnail strip, and CTA sizing in `3D Generator` are being tightened so the panel reads more like a compact premium studio
    - button labels are being shortened where that improves rhythm without hiding meaning
    - paired source-photo plus owned-GLB mapping is expected as the next content step once owned asset pairs are prepared
    - `Source Preview` is also being polished away from a plain upload look toward a softer studio-style framed image treatment with gentler transitions
    - a light premium glass/frame treatment is also being added so the preview feels more curated and less like a raw upload box
  - owned test-pair wiring started:
    - active test registry now begins connecting owned preview PNG files to the matching owned GLB test assets
    - `OWNED_MODEL_ASSETS.md` now records the declared provenance of the active owned test library
    - the current staging folder for preview pairs can be normalized later without losing the registry direction already in progress
  - test-registry prompt refinement:
    - generic `car` should resolve to the owned car model, while `f1` and `sport car` should resolve to the owned F1 model
    - `bike` is now part of the owned test library
    - `Skenderbeg` should resolve for `toy`, `hero`, and `warrior` style prompts and is intentionally weighted higher in random fallback
  - pre-production asset-delivery note:
    - the owned test-model library is growing in file size, so final `v1.1` production adaptation must verify whether local static delivery is acceptable
    - if Railway/Vercel or the final deployment shape does not handle the asset weight comfortably, move heavy owned model assets to a cleaner delivery path such as object storage or CDN before release
  - production adaptation note added:
    - `V11_PRODUCTION_ADAPTATION.md` now tracks the final pre-production checks for heavy owned assets, delivery strategy, browser STL export, Meshy smoke tests, and release readiness
  - section close-out pass started:
    - `3D Generator` is being tightened toward a feature-complete state with clearer active-source messaging and cleaner output guidance
    - after this pass, the section should mainly need polish and final user-action planning rather than more structural changes
  - `3D Generator` section status:
    - treat this section as functionally closed for now on `v1.1`
    - remaining work here should be polish, final user-action planning, and late production adaptation checks
    - next main build focus should move to `SVG`
    - after `SVG`, continue with the photo-to-relief / lithophane direction
  - `SVG` section reset started:
    - `SVG` should now be remodeled as its own full panel instead of feeling like only a side action from `3D Generator`
    - the intended `SVG` panel structure is now:
      - prompt
      - source preview / upload
      - 5 recent source thumbnails
      - one `Generate SVG` CTA
    - unsupported `Mode` variants should not stay visible in the UI until the backend actually supports them
    - the active SVG control set remains intentionally small:
      - `Detail`
      - `Clean Background`
    - target SVG usage tiers are now:
      - guest `1`
      - logged-in free `5`
      - premium `unlimited`
    - the `SVG` panel direction is now more explicit:
      - prompt and upload both stay inside the `SVG` panel itself
      - recent source history should hold up to 5 local SVG source picks, including uploads
      - the generated SVG should resolve into the main viewer with direct download behavior
    - viewer behavior for `SVG` is now also being tightened:
      - remove duplicate in-panel SVG download UI
      - keep `Wire`, `Print`, and printer export controls out of the viewer while `SVG` is the active surface
      - keep SVG line contrast readable against the dark viewer shell in both theme modes
      - keep only one active `SVG` source/convert path in the frontend instead of preserving older overlapping handlers
  - `Relief` section foundation has started:
    - first pass should mirror the safe `SVG` approach:
      - prompt
      - upload/source preview
      - 5 recent source thumbnails
      - one honest local relief preview path
    - do not imply true lithophane STL/export until that path is genuinely wired
    - keep deploy/licensing risk low by avoiding new dependencies for the first relief pass
