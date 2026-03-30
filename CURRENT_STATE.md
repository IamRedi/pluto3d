# Pluto3D Current State

Last updated: `2026-03-30`
Active branch: `develop`
Local checkpoint used for this snapshot: `6c04d9b` + current working tree updates

This file is the canonical project snapshot.
Update it after every meaningful change.

## Documentation Workflow

- primary working docs are:
  - `SYSTEM_MASTER.md`
  - `CURRENT_STATE.md`
  - `CHANGELOG.md`
  - `INSTALL_GUIDE.md`
  - `PROJECT_MAP.md`
  - `AI_RULES.md`
- legacy docs are still kept as support/archive material
- new session memory should be written into the canonical docs first

## What Is Working

### Versioning And Release Split

- production now runs the `v1.1` rollout that was merged into `main` on `2026-03-28`
- active development continues on `develop` as `v1.1`
- local/test work does not change production by itself
- the previous production rollback anchor is tagged as `prod-v1.0-before-v1.1-2026-03-28`

### Hosted production deploy (operator workflow)

This records how **hosted** backend/frontend update today; it is configured in **Railway / Vercel dashboards**, not in repo files.

- **Railway (backend, production)**: service **`pluto3d`** uses root **`/backend`** and is connected so that pushes to branch **`develop`** deploy automatically to the **production** environment (“branch connected to production”).
- **Direct path (this is the intended flow now)**: work on **`develop`**, commit, then **`git push origin develop`** → Railway rebuilds and ships the backend without a separate release branch.
- **Vercel (frontend)**: the repo links to **`pluto3d.vercel.app`**. If Vercel **Production Branch** is still **`main`**, the live site will not update until you either merge **`develop` → `main`** (e.g. GitHub “Compare & pull request”) **or** change Vercel’s production branch to **`develop`** so it matches Railway. Align the two hosts to the same branch to avoid API/UI drift.

### Core Workspace

- `3D Generator` is functionally stabilized for the current local/test checkpoint
- shared source preview is the active source of truth for:
  - uploads
  - prompt-generated concept images
  - test 3D generation
  - premium real 3D generation
- concept-image prompts now receive per-panel augmentation so generated sources are more conversion-friendly (e.g. cleaner contours and no-background cues for `3D`, `SVG`, and `Relief`)
- desktop workspace layout now uses a `clamp(...)`-based middle column width so the viewer remains usable at default `100%` browser zoom across Chrome/Brave without relying on manual zoom tweaks
- viewer framing now zooms around the model center (bounding box/sphere) so test-model zoom does not drift upward out of frame
- viewer status strip now uses a text-only treatment (no shell) with smaller metadata typography
- recent concept/source thumbnail strips exist in the remodel flow
- active `3D`, `SVG`, and `Relief` panels now use stronger section headers, visible card chips, and clearer CTA priority for faster scanning
- `SVG` and `Relief` option controls now use a more compact layout, with narrower selects and parallel field placement where the space allows it
- generator CTAs in the active creation panels now sit on content-sized widths on desktop and use a cleaner varnished-gold treatment with reduced ambient bleed from card and hover effects
- the workspace shell is now being simplified toward a cleaner `Frozen Deep Green` foundation:
  - animated star/background layers were removed
  - viewer neural overlays were removed
  - heavy blur and glow usage was reduced across the main shell
  - sidebar and shell controls now lean more matte and restrained
- an additional UI simplification pass was applied to further reduce visual load:
  - flattened the main shell surfaces (body, sidebar, panel, viewer) by reducing heavy gradients and ambient shadows
  - simplified the sidebar tool buttons and theme toggle to rely on the shared control tokens instead of bespoke gradient shells
  - reduced viewer stage glow intensity so the viewport reads cleaner without changing any render logic
  - kept the pass cosmetic-only inside `frontend/index.html`
- header navigation, sidebar controls, viewer toolbar, and generator CTAs are now being rebased toward a more consistent green-and-bronze language instead of mixed glow-heavy accents
- bronze accents now extend into pills, badges, chips, viewer labels, and secondary shell metadata so the workspace reads as one visual family
- the active button family is now more premium and mechanically consistent:
  - generator CTAs use a deeper bronze varnish with cleaner edge contrast
  - navigation pills and viewer mode toggles use the same machined-button language
  - launch and download controls now align with the bronze CTA family instead of older green highlights
  - the `Login` pill now acts as the brighter green accent CTA in the header
  - the sidebar theme toggle now matches the sidebar control family again instead of using bronze
  - bronze button tones were lifted slightly brighter for a lighter, more luxury read
- header nav active state and viewer-side print CTA now use the same brighter bronze family, reducing the remaining older green action islands before the dedicated viewer premium pass
- the first viewer premium phase is now in place:
  - the viewer shell has a clearer outer frame and inner bezel
  - the viewport includes a subtle stage glow and floor falloff for stronger 3D depth
  - viewer visuals were upgraded without changing render logic, asset switching, or export controls
- the second viewer premium phase is now in place:
  - viewer controls are grouped into a cleaner instrument-style top bar
  - a compact status strip now reports asset, mode, and output state inside the viewer shell
  - toolbar/status chrome syncs to `3D`, `SVG`, `Relief`, image, GLB, and STL states without changing the underlying viewer behavior
  - the viewer shell script is now cache-busted from `index.html` so local browser tests load the newest viewer chrome instead of stale cached markup
- the third viewer premium phase is now in place:
  - base viewer lighting now includes a more refined rim and bounce contribution for stronger model definition
  - model framing is tuned to feel more hero-centered through safer fit and camera targeting
  - top bar and status strip spacing were reduced slightly so the chrome feels more precise and luxury without crowding the scene
- the next viewer refinement pass is now in place:
  - `Wire` and `Print` materials were rebalanced toward a warmer premium studio look instead of flatter generic defaults
  - STL preview materials now sit closer to the same luxury print language as the main viewer modes
  - the viewer-side `Print` export cluster now sits inside a cleaner shell block so the CTA reads as part of the viewer instrument panel
- the latest viewer staging pass is now in place:
  - the viewer stage now uses a deeper upper ambient wash and a stronger floor falloff so the scene reads more like a real display bay
  - default hero camera framing now starts slightly higher and more elevated for both model-fit and STL preview states instead of reading too parallel to the floor
  - the camera/framing change remains visual-only and does not alter export, generation, or mode-switching behavior
- the latest viewer framing correction is now in place:
  - model centering is now handled by one shared stage-alignment helper so GLB, STL, and idle states sit on the center axis of the viewer more consistently
  - the default hero camera was lifted a bit further while removing the horizontal offset that was making the object read off-center
  - the correction remains visual-only and does not change render/export behavior
- the final viewer chrome polish for this task is now in place:
  - the title block, toolbar shell, status strip, and print cluster now share a tighter premium shell treatment instead of reading like separate floating boxes
  - mode buttons and viewer metadata chips now use slightly cleaner spacing and hierarchy for a more finished studio-control look
  - this pass stays cosmetic-only and is intended to close the current viewer premium task without reopening working flows
- mobile workspace stacking has been stabilized for `v1.1`:
  - the mobile workspace now stacks as `Sidebar (horizontal)` → `Viewer` → `Panel` to keep the preview visible early in the flow
  - the viewer height now uses a `clamp(...)` rule on mobile so it stays usable across phone sizes without crushing the generator panel
  - SVG/Relief popover menus are constrained on mobile so they remain inside the viewport
  - fixed a mobile CSS override that could collapse the viewer height (causing the canvas to disappear) by preventing the mobile auto-height rule from applying to the viewer container
- viewer auto-focus behavior is now enabled for the main creation flows:
  - the viewer now stays pinned at the top of the mobile workspace while the header can hide on scroll, so users keep the output surface in view as they move through the panels
  - the mobile header now uses a two-row layout (brand + account actions above, nav below) to prevent the brand and auth pills from overlapping on small screens
  - relief preview images now remain centered in the main viewer across breakpoints instead of anchoring to the top-left
  - viewer-injected `svgViewer` markup now uses explicit centering rules so relief preview PNGs remain centered reliably
- the `SVG` and `Relief` source preview bug is now fixed:
  - their dropzones now use the same positioned preview container rules as `3D`
  - blurred preview layers no longer escape the source card and spill across the panel background
- the `Gallery And Profile UI Pass` is now in place:
  - `Gallery` now reads as a simpler showcase plus recent-archive surface instead of a flat placeholder list or an overbuilt account panel
  - `Profile` now presents account state, subscription, billing, usage, and support with stronger hierarchy and a cleaner premium account-surface layout
  - the pass stays on the existing runtime/account logic and does not reopen auth or billing behavior
- the `Mobile UI Pass` is now in place:
  - the main workspace now stacks more cleanly on smaller screens, with the viewer preview remaining first, using a more compact mobile height, and now staying pinned near the top while the user scrolls deeper into the generator panel
  - the mobile header action row is now tighter, keeping the user badge, `Profile`, and `Login` controls on one cleaner line with a smaller profile pill
  - the mobile sidebar now behaves more like a bottom control dock so the active tools stay reachable without reopening desktop layout logic
  - `Wire` and `Print` viewer mode buttons now stay hidden until a real viewer asset exists, avoiding idle-state controls before any output is loaded
  - the full viewer-side instrument cluster now scales down more uniformly on mobile, including `Surface`, `Wire`, `Print`, `Download`, and the status strip, so the controls feel closer to a reduced desktop layout without occupying as much of the preview
  - mobile viewer framing now drops loaded models slightly lower inside the viewport so feet and lower geometry do not sit too close to the visual center line
  - `Gallery` and `Profile` premium cards now compress more gracefully on narrow widths while keeping the `Frozen Deep Green + bronze` hierarchy intact
  - the pass stays responsive/cosmetic-only and does not change generator, viewer, auth, billing, or export behavior
- light mode is now a bit more balanced:
  - the main `3D` / `SVG` / `Relief` side buttons now use lighter shells in light mode instead of keeping the heavier dark treatment
  - the viewer outer frame now reads lighter in light mode, closer to the inner stage treatment instead of staying overly dark
- the premium 3D path is now a bit more production-safe:
  - frontend start requests now fail more cleanly if Meshy/startup calls break before a `task_id` is returned
  - backend Meshy start/status failures now resolve to readable string details instead of surfacing raw nested objects to the UI, including the no-`task_id` edge case
  - job polling no longer reports a full `100%` while a Meshy task is still `IN_PROGRESS`, reducing false-finished progress states in the UI
- a focused local final-readiness pass has now been run:
  - local backend runtime is healthy on `http://127.0.0.1:8000`, with `/` and `/docs` responding correctly
  - unauthenticated `GET /api/account/me` correctly resolves to guest state
  - billing activation runtime reports `activationReady: true`
  - the current go-live blockers remain operational, not product-bug blockers:
    - Stripe is still configured in `test` mode
    - billing return URLs still point to a temporary domain
  - authenticated `/api/billing/status`, checkout, webhook, and portal verification are still pending as the remaining live-readiness checks
- billing activation handoff is now more truthful during repo/local verification:
  - it reads `frontend/app-config.js` when available and marks frontend public config entries as configured instead of always treating them as unresolved external work
  - the switch phase can now advance past `frontend_public_config` during local production-prep checks when those values are already present
- the current production usage policy is now wired into the active frontend runtime:
  - usage limits now support `day`, `week`, and `month` windows instead of one flat counter model
  - `Guest`, `Free Account`, and `Premium` now have separate configured allowances for `AI image`, `SVG`, `Test 3D`, `Relief STL`, and `Real 3D / Pro`
  - `Guest` test 3D now stays viewer-only with no download access, while `Free Account` receives one download credit per generated test model and `Premium` keeps unlimited download access
  - `Relief` preview remains unmetered, while only `Generate STL` consumes the configured relief allowance
  - `Plans` and `Profile` now reflect the configured production policy instead of only the older simplified preview counters
  - live auth and guest requests now send account-aware quota headers so backend routes can resolve `guest`, `free`, and `premium` subjects before consuming usage
- backend quota enforcement is now in place for the active production path:
  - server-side usage tracking now exists for `AI image`, `SVG`, `Toy`, and `Real 3D / Pro` routes
  - the account layer now exposes usage snapshots plus backend `consume` / `consume-credit` actions so local studio flows like `Test 3D`, `Relief STL`, and test-model download credits can also sync against one server authority
  - usage persistence now supports `auto` store selection:
    - `Supabase usage_buckets` becomes the shared production store once the schema is applied
    - local JSON fallback remains available for scaffold/dev recovery
  - frontend usage rendering now prefers backend usage state when available, so `Plans`, `Profile`, prompts, and viewer download access can reflect the server-tracked account allowance instead of only local preview counters
  - fully local features still depend on the official frontend flow to hit the backend usage endpoints before/while they run, so the strongest commercial protection is now in place for server-handled actions and substantially improved for local-preview workflows
  - usage window calculation now falls back safely to UTC if the host runtime cannot resolve the configured IANA timezone, preventing local usage snapshot crashes on stricter Windows/Python installs
  - usage-store and subscription-schema readiness checks now degrade to a safe `not ready` state if Supabase cannot be reached during local or sandbox verification, instead of crashing the readiness path outright
  - local state-file env paths are now normalized more safely, so running backend tools from inside `backend/` no longer creates accidental nested paths like `backend/backend/data/...`
  - a dedicated backend smoke script now exists at `backend/scripts/quota_billing_smoke.py`
  - the current smoke pass from that script confirms:
    - `Guest` test 3D consume plus download-credit grant/consume works
    - `Guest` AI image limit blocks on the third consume as expected
    - mocked authenticated `Free Account` test 3D quota blocks on the fourth weekly consume as expected
    - mocked authenticated `Premium` still reports unlimited toy generation plus allowed test-model download access
  - the current billing readiness snapshot from that same smoke pass reports:
    - current phase: `Awaiting schema`
    - subscription store mode remains `supabase`, but schema readiness is still unresolved in this verification environment
    - the remaining go-live blockers are still the expected operational blockers:
      - Stripe is still configured in `test` mode
      - billing return URLs still point to a temporary Vercel domain
- the `v1.1` rollout is now live in production:
  - Railway backend is connected to branch `release/v1.1-rail-candidate`
  - Vercel production was updated by verifying the preview deployment first, then merging the same release-candidate into `main`
  - direct backend verification passed before the frontend switch:
    - `GET /api/billing/activation-status`
    - `GET /api/account/usage`
  - preview verification passed for the main user-facing changes:
    - `3D Generator`
    - `Gallery`
    - `Profile`
    - theme switching
  - one preview `Test 3D` smoke check with `bike` succeeded, reducing the immediate risk from the heavier owned test-model assets before the frontend production switch
- the viewer chrome is now cleaner and more text-first:
  - the upper `Pluto3D Studio` kicker was removed from the viewer shell
  - non-button viewer metadata now reads as clean text without shell backgrounds
  - the lower viewer status metadata now sits as a lighter side column instead of a wide bottom shell bar
  - mobile viewer overrides now preserve that text-only treatment instead of reintroducing padded metadata shells on smaller breakpoints
  - the ornamental `3D Viewer` title is now removed entirely so the top viewer edge stays cleaner and more product-like
- the `3D` generator control flow is now tighter:
  - `Generate Image` now sits on the same row as `Toy Assist` in the main `3D` prompt card
  - the `3D` source card now places recent source thumbnails in a cleaner side rail when desktop width allows it, while collapsing back to a stacked layout on smaller screens
  - the `Source` preview image now uses a cleaner single-image presentation, with the old double shell-like decorative layers behind the preview removed
  - the `Source` preview now sits on one cleaner framed stage and the side thumbnail rail has a slightly more premium, clearer selected-state treatment
- viewer model framing now sits lower by default on non-mobile viewports as well, so loaded figures do not ride too high in the stage on desktop
- viewer stage placement is now more correct for generated models:
  - the camera target now follows the lowered stage placement instead of continuing to center the old higher position
  - desktop generated models now sit deeper in the viewer stage instead of snapping back toward the upper center after load
  - generated-model framing now uses a separate lower stage anchor and a higher lower-mid camera focus, so scale changes no longer pivot mainly from the feet and push growth almost entirely upward
  - the viewer focus point has now been raised further on generated assets so scale and zoom behavior rebalance away from the old top-heavy framing
- viewer metadata is now more bounded:
  - longer filenames and labels wrap inside the viewer status strip instead of spilling outside the stage
  - upper-right viewer chrome and print CTA keep stricter width bounds inside the viewer frame
- SVG viewer theme behavior is now cleaner:
  - SVG lines stay light in dark mode for contrast
  - SVG lines now remain black in light mode instead of being inverted to white
- `Relief` export meta copy now uses clean ASCII separators instead of a risky special-character bullet in the visible status text
- owned test-model registry is active and includes:
  - Pluto Robot
  - F1 Car
  - Car
  - Bike
  - Skenderbeg

### SVG

- `SVG` is a self-contained panel flow
- prompt generation, upload, source preview, and recent-source thumbnails live inside the panel
- backend SVG conversion path is active
- main viewer is the output surface for SVG preview/download
- 3D-only viewer controls are hidden while `SVG` is the active surface

### Relief

- `Relief` is a self-contained panel flow
- local relief preview works in the main viewer
- prep controls are active:
  - `Depth`
  - `Thickness`
  - `Border`
  - `Surface`
  - `Direction`
  - `Output Size`
  - `Mesh Detail`
- browser-side `Flat STL` export is active
- browser-side `Arched STL` export is active for supported paths
- mesh smoothing and border/frame transition cleanup were already added

### Viewer And Print Direction

- viewer handles image, SVG, GLB, and STL states
- printer-oriented export stays browser-side in the active local/test path
- heavy backend `print-fix` remains intentionally paused in the public-facing path for stability

### Platform Layer

- Supabase auth is live in the project architecture
- Google login is supported
- backend account plan resolution is active
- premium locks follow backend-owned account state
- Stripe billing scaffold and activation endpoints exist
- local testing remains intentionally more permissive than production

## What Is In Progress

- migration to the new canonical documentation system
- broader UI and visual-system pass across `3D Generator`, `SVG`, and `Relief`
- shell-level CSS cleanup so the next redesign steps sit on a simpler theme foundation
- responsive smoke validation and edge-case spacing polish across workspace and account-facing surfaces
- keeping the remodel compact and premium-looking without reopening backend architecture
- preparing a controlled `v1.1` production rollout path with explicit backend-first testing, limited tester exposure, and documented rollback to `v1.0`
- release-candidate prep is now underway on top of `develop`, including rollback tagging strategy and local deploy-snapshot cleanup so temporary backend state files do not leak into the production candidate
- the current rollout snapshot is now frozen on branch `release/v1.1-rail-candidate`
- the current rollback anchor for frozen production is tagged as `prod-v1.0-before-v1.1-2026-03-28`
- early post-rollout observation on the live `v1.1` production path with the current small tester group before broader promotion

## Next Tasks

- treat `SYSTEM_MASTER.md`, `CURRENT_STATE.md`, and `CHANGELOG.md` as the primary working documentation
- apply `usage_buckets` plus the billing schema in the target Supabase project, then rerun `backend/scripts/quota_billing_smoke.py`
- rerun billing readiness in the target environment after switching off Stripe `test` mode and replacing the temporary Vercel billing URLs
- keep the just-used March 28 rollout path as the default operational playbook:
  - Railway backend from `release/v1.1-rail-candidate`
  - Vercel preview verification first
  - then merge the verified release candidate into `main` if direct Vercel production promotion is not available
- follow the updated `PRODUCTION_ACTIVATION_RUNBOOK.md` for:
  - release-candidate rollout from `develop`
  - production test order
  - Railway/Vercel/Supabase/Stripe manual checks
  - fast rollback to the frozen `v1.0` line if needed
- continue the shell redesign from the simplified `Frozen Deep Green` base:
  - cleaner sidebar
  - cleaner viewer frame
- finish the UI pass for:
  - spacing
  - visual clarity
- run a focused mobile smoke pass across `Workspace`, `Gallery`, and `Profile`
- run a real `3D Generator` premium-path smoke test before production adaptation
- verify Relief export quality on intended user machines
- normalize owned-asset staging folders before `v1.1` release if they remain active
- revisit production adaptation only after the design/system pass is stable

## Known Issues

- legacy documentation files still exist and should be treated as source/archive during the migration period
- the owned asset staging folder name is not release-ready:
  - `frontend/models/models with png foto previewe/`
- owned model asset weight may require CDN or object storage before `v1.1` production release
- `frontend/models/print-ready-preview.stl` still needs explicit provenance confirmation
- the current Transparent Textures background should be replaced or fully cleared before sale
- the exact Replicate model license snapshot still needs to be recorded for commercial readiness
- final live Stripe checkout, webhook, and portal smoke tests are still operational follow-up work
- target-environment Supabase schema reachability still needs confirmation before billing verification can move from `Awaiting schema` to live smoke testing
- owned test-model asset weight is still a production watch item even though the first preview `bike` smoke test succeeded during rollout

## Current Working Boundaries

- do not treat this checkpoint as a production adaptation phase yet
- do not reopen heavy backend scaling work unless stability requires it
- do not break already working `3D`, `SVG`, or `Relief` behavior for cosmetic-only changes
- keep the new canonical documentation system as the default project workflow from now on
- treat older deployment/live-status notes in legacy docs as historical context only; before rollout, trust the current branch, current config, dashboards, and live runtime endpoints
- every meaningful change must update:
  - `CURRENT_STATE.md`
  - `CHANGELOG.md`
