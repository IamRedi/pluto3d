# Pluto3D Changelog

This is the canonical change history for Pluto3D.
Update it after every meaningful change.

Historical entries below were migrated from the previous board, workflow, and handoff documents.

## 2026-04-08

### Pluto orb assistant launch integration

- Kept the existing sidebar `Pluto` orb hover/focus personality microinteraction intact while changing orb click/keyboard activation to open the embedded AI assistant chat widget.
- Added the external assistant widget bootstrap in `frontend/index.html` using the provided `window.AI_CONFIG` public key and Railway API URL.
- Hid the widget's default floating launcher so the existing sidebar orb remains the only visible trigger and the workspace UI does not visually change.
- Updated the sidebar brand lockup to render `PLUTO` with a smaller `Ai Assist.` subtitle beneath it.
- Repositioned the assistant panel so it opens beside the sidebar orb trigger instead of using the widget's default bottom-right placement.
- Refined the assistant behavior so the panel stays hidden on initial page load, toggles only from the Pluto orb, closes cleanly on repeat click/outside click, and uses a smaller neon-green shell that fits the workspace styling better.

## 2026-03-30

### UI polish: simplify shell surfaces

- Flattened the main workspace shell surfaces by reducing heavy gradients and lowering ambient shadows across the app chrome.
- Simplified the sidebar tool buttons and the theme toggle to rely on the shared control tokens instead of bespoke gradient shells.
- Reduced viewer stage glow intensity so the viewport reads cleaner without changing generation, viewer logic, or export flows.
- Added per-panel prompt augmentation for concept image generation so user prompts automatically gain conversion-friendly cues (e.g. no background, clean contours) depending on whether the user is in `3D`, `SVG`, or `Relief`.
- Updated the desktop workspace grid column sizing to a `clamp(...)`-based middle panel width so the viewer remains usable at default `100%` browser zoom in Chrome/Brave.
- Updated viewer fit/framing to keep zoom centered on the model so test-model zoom no longer drifts upward out of frame.
- Simplified viewer status strip to a text-only treatment with smaller metadata typography.
- Reworked `Relief` option selects into custom popover menus (no native white dropdown) with shorter trigger labels to avoid layout overflow.
- Reworked `SVG` `Detail` and `Background` controls into the same compact popover-select style so the controls remain inside the panel column.
- Added a `v1.1` mobile workspace pass so the layout stacks as `Sidebar` → `Viewer` → `Panel`, the viewer uses a `clamp(...)` height on phones, and SVG/Relief popover menus stay inside the viewport.
- Fixed a mobile CSS override that could collapse the viewer height (making the viewer appear missing) by ensuring the mobile auto-height rule does not apply to the viewer container.
- Updated mobile behavior so the main viewer remains pinned at the top of the workspace while the header can hide on scroll, instead of auto-scrolling the page when users click generation CTAs.
- Adjusted the mobile header into a two-row layout (brand + account actions above, nav below) to avoid overlapping header pills on small screens.
- Fixed `Preview Relief` viewer alignment so the preview image stays centered instead of anchoring to the top-left on some layouts.
- Hardened `svgViewer` centering inside the injected viewer shell so relief preview PNGs remain centered reliably (not dependent on `inset:0` auto-margins).
- Updated usage-limit policy values to the new quota model (Guest, Free, Premium), including a dedicated `premium3dGeneration` counter and enforcement path for premium 3D actions.
- Updated plan/profile surfaces to reflect the new quota messaging (`AI 50+ target`, `200-token premium 3D flow`, `10 model runs`) and show the premium 3D usage metric.
- Simplified premium plan copy by removing parenthetical notes and keeping direct customer-facing lines (`AI photo: 50+ foto generation`, `Premium 3D: 200 token 10+ modele`).
- Updated `Test 3D` owned-model resolver to prioritize prompt keyword similarity (including `moto`-related prompts) and use equal random fallback instead of favoring `Skenderbeg`.
- Added authenticated activity tracking to profile records (`last_login_at`, `last_seen_at`, `total_active_seconds`) plus a new `/api/account/activity/ping` heartbeat path so account state can reflect last access time and accumulated active minutes.
- Added guest activity tracking via `/api/account/guest/ping` and a new Supabase `guest_activity` table so anonymous visits can be listed with first/last seen timestamps, total active seconds, last user-agent, and last IP.
- Refined premium bronze button tokens (lighter, cleaner highlight) so premium CTAs read more polished and consistent.
- Verified local smoke runtime: frontend `http://127.0.0.1:5500` and backend `http://127.0.0.1:8000` respond, and `GET /api/account/me` resolves guest state.
- Kept the pass cosmetic-only inside `frontend/index.html`. Meshy `3D Pro` was intentionally not exercised to avoid consuming credits.

### Documentation: production deploy branch

- Documented the hosted workflow: Railway production tied to branch `develop` (backend root `/backend`), push `develop` for direct backend deploy, and aligning Vercel production branch with the same branch (or merge `develop` → `main` if Vercel stays on `main`) (`CURRENT_STATE.md`, `INSTALL_GUIDE.md`).

## 2026-03-28

### v1.1 production rollout

- Rolled `v1.1` into live production with the following path:
  - prepared and pushed `release/v1.1-rail-candidate`
  - switched Railway backend production source to `release/v1.1-rail-candidate`
  - verified live backend endpoints directly before touching frontend
  - verified the Vercel preview deployment for the same branch
  - merged the verified release candidate into `main` and pushed `main` so Vercel production could update
- Recorded the real operator procedure in `PRODUCTION_ACTIVATION_RUNBOOK.md`, including the Vercel fallback path used when direct preview-to-production promotion was not exposed in the UI.
- Confirmed one preview `Test 3D` smoke check with the heavier `bike` owned model before the production frontend switch, so large test-model assets remain a watch item but did not block this rollout.

### Production rollout runbook pass

- Expanded `PRODUCTION_ACTIVATION_RUNBOOK.md` with a controlled `v1.1` rollout path that now covers:
  - release-candidate branch strategy from `develop`
  - backend-first deploy order
  - ordered production test phases
  - user-only checks for Railway, Vercel, Supabase, and Stripe
  - explicit rollback rules and rollback success criteria for returning to frozen `v1.0`
- Clarified in the rollout runbook that older handoff notes are historical context only, while real rollout decisions should trust the current branch, config, dashboards, and live runtime endpoints.
- Added release-snapshot hygiene for the rollout candidate by ignoring temporary `backend/data/` state files so local smoke/billing state does not get bundled into the production candidate.
- Created the rollout branch `release/v1.1-rail-candidate` and the rollback tag `prod-v1.0-before-v1.1-2026-03-28` so the upcoming production switch has a documented forward path and a fast return point.

### Quota smoke hardening pass

- Hardened `backend/app/services/usage.py` so quota time windows fall back to UTC if the host runtime cannot resolve the configured timezone, preventing local/sandbox crashes during usage snapshot reads.
- Hardened Supabase readiness checks in both `backend/app/services/usage.py` and `backend/app/services/subscriptions.py` so verification now degrades to `not ready` instead of failing outright when Supabase is unreachable.
- Normalized local billing/usage state-file env paths so backend tools started from inside `backend/` no longer create accidental nested paths like `backend/backend/data/...`.
- Added `backend/scripts/quota_billing_smoke.py`, a repeatable backend smoke script that verifies guest/free/premium quota behavior, download-credit handling, and the current billing-readiness snapshot without polluting the main usage state.
- Ran the new smoke pass successfully for quota flows and captured the current billing readiness result:
  - quota checks passed for `Guest`, mocked authenticated `Free Account`, and mocked authenticated `Premium`
  - billing readiness currently stops at `Awaiting schema`
  - the remaining go-live blockers are still `Stripe test mode` and temporary Vercel billing return URLs

### Usage policy implementation pass

- Replaced the old flat preview limits in `frontend/auth-scaffold.js` with per-tier usage rules that support day/week/month windows for `AI image`, `SVG`, `Test 3D`, `Relief STL`, and `Real 3D / Pro`.
- Added the first scoped download-credit policy for viewer test models so `Guest` stays view-only, `Free Account` gets one download per generated test model, and `Premium` keeps unlimited download access.
- Wired `Test 3D`, `Relief STL`, and `Real 3D / Pro` flows to the new usage policy so the main runtime now blocks, increments, and surfaces those allowances more accurately.
- Kept `Relief` preview outside the quota system and limited only real STL generation, matching the intended production policy.
- Updated `Plans` and `Profile` surfaces so the current configured allowances are visible in the product instead of showing only the older simplified counters.
- Added backend quota enforcement plus usage snapshot/consume endpoints, so the server can now track and block the main account-limited features instead of leaving the entire policy in frontend preview state only.
- Added an `auto` usage-store path with a new `usage_buckets` Supabase schema target and a local JSON fallback, so production can move to shared persistence without changing the runtime contract again.
- Updated frontend auth/runtime wiring so live requests send `Authorization` or `X-Pluto-Guest-Key`, backend usage can sync back into the UI, and server-returned limit errors surface as real account-limit messages instead of generic request failures.

### Mobile UI pass

- Reworked the mobile workspace hierarchy so the viewer preview stays first, but uses a more compact small-screen height while the control rail behaves more like a premium bottom dock on smaller screens.
- Tightened mobile spacing, card density, and responsive behavior across `Gallery` and `Profile` so the newer premium account surfaces hold their hierarchy on narrow widths.
- Reduced the mobile viewer footprint slightly so the main generate flow appears sooner without removing the immediate preview-first feel.
- Made the mobile viewer sticky beneath the header so the preview stays in place while the user scrolls deeper into the generator controls.
- Tightened the mobile header action row so the user badge, `Profile`, and `Login` controls sit on one cleaner line, with `Profile` reduced so it competes less with the main login CTA.
- Hid the viewer `Wire` and `Print` mode buttons until a real asset exists, removing idle-state controls before anything has been generated or loaded.
- Scaled down the full mobile viewer instrument cluster more uniformly, including `Surface`, `Wire`, `Print`, `Download`, and the status strip, so the action chrome feels closer to a reduced desktop layout instead of covering too much of the preview.
- Lowered mobile viewer model framing slightly so loaded models sit a bit deeper in the stage and do not place their feet too close to the center of the preview.
- Hardened the premium 3D start flow so frontend requests fail more cleanly before polling begins, and backend Meshy start/status errors now return readable text instead of raw nested objects, including the no-`task_id` edge case.
- Prevented premium 3D polling from showing `100%` before Meshy actually reaches `SUCCEEDED`, so in-progress jobs no longer look falsely finished in the UI.
- Removed the extra viewer kicker, stripped shell backgrounds from non-button viewer metadata, reorganized the lower viewer info into a cleaner side-column treatment, and kept that text-only viewer chrome consistent on mobile breakpoints.
- Removed the ornamental `3D Viewer` title, moved the main `3D` source recent thumbnails into a cleaner side rail on desktop, aligned `Generate Image` with `Toy Assist`, and lowered default desktop viewer framing so loaded figures sit deeper in the stage.
- Simplified the `Source` preview presentation so the uploaded/generated image reads as one cleaner hero preview instead of sitting on top of two decorative shell layers.
- Added one cleaner framed plate behind the `Source` preview and tightened the thumbnail rail styling so the source area reads more intentional without reopening the upload flow.
- Fixed the generated-model viewer framing more completely by lowering the camera target together with the stage placement, and tightened viewer metadata bounds/wrapping so longer details stay inside the frame.
- Reworked generated-model framing again so viewer scale changes use a lower stage anchor plus a lower-mid camera focus, avoiding the old behavior where zoom growth biased too heavily upward from the feet.
- Updated SVG viewer theme handling so SVG strokes stay black in light mode while remaining bright/inverted in dark mode.
- Lightened the main `3D` / `SVG` / `Relief` side buttons and the viewer outer frame specifically for light mode so the workspace no longer feels too dark against the brighter theme.
- Ran a focused final-readiness pass: local backend health is clean, billing activation reports ready, and the remaining go-live blockers are still the expected operational ones (`Stripe test mode` plus temporary billing return URLs).
- Improved billing activation handoff accuracy so local/repo verification can read `frontend/app-config.js` and stop falsely reporting frontend public config as unresolved when those values already exist.
- Rebalanced generated-model viewer focus higher again so scaling behavior no longer stays overly anchored near the feet and the composition sits less top-heavy.
- Replaced the `Relief` export meta bullet separators with clean ASCII text so the visible status copy does not risk mojibake or encoding artifacts.
- Kept the pass visual-only inside `frontend/index.html`, without reopening generator, viewer, auth, billing, or export logic.

### Gallery and Profile UI pass

- Reworked `Gallery` into a simpler showcase/archive surface so it reads closer to a real studio history without feeling overbuilt.
- Rebuilt `Profile` hierarchy around stronger account, subscription, billing, usage, and support presentation while keeping the same auth/billing runtime logic underneath.
- Added the supporting `Gallery`/`Profile` CSS classes directly in `frontend/index.html` so the account-facing surfaces match the newer premium workspace direction.

### Viewer chrome closure polish

- Tightened the viewer title block, toolbar shell, status strip, and print cluster so they read as one premium control family instead of separate floating shells.
- Refined viewer mode-button spacing and metadata chip hierarchy for a more finished studio-control presentation.
- Kept the pass cosmetic-only so the current viewer premium task can close without reopening generation, export, or mode logic.

### SVG and Relief source preview bugfix

- Fixed the `SVG` and `Relief` source dropzones so their preview blur layers now stay contained inside the card instead of spilling across the wider panel.
- Matched their positioned preview-container behavior to the already-correct `3D` source dropzone.

## 2026-03-27

### Documentation system reset

- Added the new canonical documentation set:
  - `SYSTEM_MASTER.md`
  - `CURRENT_STATE.md`
  - `CHANGELOG.md`
  - `INSTALL_GUIDE.md`
  - `PROJECT_MAP.md`
  - `AI_RULES.md`
  - `.env.example`
- Declared `CURRENT_STATE.md` and `CHANGELOG.md` mandatory update points for future work.
- Consolidated workflow, install, infrastructure, and handoff notes into a single scalable documentation system while keeping legacy docs in the repo as migration sources.

### Documentation workflow sync

- Strengthened the new documentation system so it becomes the default working method for future sessions.
- Synced the main legacy planning docs to explicitly point back to the new canonical documents.
- Clarified that legacy docs remain in the repo for history and detailed support, while the new system is now the primary source of truth.

### Hierarchy and icon pass

- Applied the `v1.1` `Hierarchy And Icon Pass` to the active `3D Generator`, `SVG`, and `Photo Relief` panels.
- Added stronger section headers with icon markers and compact workflow badges so the active tools read faster.
- Restored visible generator card support copy and icon chips to improve card hierarchy without reopening existing flow logic.
- Clarified CTA priority for `Real 3D`, `Generate SVG`, and `Generate STL`, while keeping existing action handlers unchanged.
- Removed stale generator references to the old `--text-muted` token inside the same UI pass.

### Compact controls pass

- Reformatted the `Relief` controls from `Depth` through `Mesh Detail` into a tighter two-column grid for desktop-sized layouts.
- Narrowed the `Relief` and `SVG` selects so they read closer to their content instead of stretching full width.
- Kept `SVG` option controls parallel and tightened the `Generate SVG`, `Preview Relief`, and `Generate STL` buttons to a more compact width.
- Preserved a single-column fallback for smaller screens so the controls do not become cramped on mobile.

### Generator CTA refinement

- Narrowed the main generator buttons so they no longer stretch across the full card width on desktop layouts.
- Shifted the active generation CTAs toward a warmer gold accent to separate them more clearly from neutral controls.
- Kept `Preview Relief` visually calmer as a secondary action while preserving the compact CTA sizing rules.
- Preserved full-width fallback for generator buttons on smaller screens.

### Generator CTA color cleanup

- Removed the old green hover bleed from generator buttons so the CTA shadows no longer pick up the card accent color.
- Unified `Generate Image`, `Test 3D`, `Preview Relief`, `Generate SVG`, `Generate STL`, and `Real 3D` into a lighter gold family with cleaner hover states.
- Kept the generator buttons visually distinct from neutral utility controls while preserving the same click behavior and layout rules.

### Generator CTA varnish cleanup

- Removed the remaining ambient blending from generator CTAs by overriding the inherited blur-heavy button treatment on those buttons.
- Switched the generator buttons to a cleaner varnished-gold surface with controlled inner highlight instead of neon-like outer glow.
- Reduced the outer shadow intensity so the button color reads independently from the surrounding green card atmosphere.

### UI foundation cleanup

- Started a broader `v1.1` shell cleanup so the next redesign pass can build on simpler CSS instead of stacked visual effects.
- Removed the animated star background layer and the moving viewer overlay patterns that were adding visual noise behind the workspace.
- Simplified the main shell toward a `Frozen Deep Green` base with more restrained matte surfaces and lower blur/glow usage.
- Rebased sidebar controls, viewer shell, and generator CTAs toward a cleaner green-and-bronze direction that is easier to redesign further.

### Green and bronze shell pass

- Continued the shell cleanup by simplifying header pills, modal backdrops, dropzones, and viewer toolbar controls so they follow the same matte direction.
- Reworked the sidebar buttons and theme toggle toward a cleaner green-and-bronze mechanical look with lower glow and more controlled shadows.
- Tightened section icon blocks and generator buttons so they sit more naturally inside the new `Frozen Deep Green` shell language.

### Bronze accent spread

- Extended the bronze language beyond the main CTAs into workspace pills, plan badges, chips, section badges, viewer title, and footer/meta accents.
- Reduced the remaining green-only highlight islands so the shell now reads more consistently as green base plus bronze mechanical accents.
- Kept the bronze application focused on interactive and identifying UI elements rather than repainting every surface.

### Premium button pass

- Rebuilt the active button language around a more premium mechanical bronze treatment instead of softer matte pills and older green action highlights.
- Unified generator CTAs, premium actions, navigation pills, viewer mode toggles, theme toggle, launch controls, and viewer download into the same sculpted button family.
- Strengthened edge contrast and inset depth on the button system while keeping the surrounding shell restrained and avoiding the earlier neon-style glow bleed.

### Button color rebalance

- Kept the sidebar button family intact by moving the theme toggle back into the same neutral side-control language instead of bronze.
- Switched the header `Login` pill to a brighter illuminated green so it reads as the main access CTA without competing with the bronze action family.
- Lifted the bronze tones on generator and viewer action buttons slightly brighter so the finish reads more luxury and less heavy.

### Header and print CTA cleanup

- Refined the active header navigation pill so the workspace tab reads closer to the brighter bronze system instead of the older flatter accent treatment.
- Reworked the viewer-side print export CTA and helper note into the same premium bronze family, removing one of the remaining green action holdovers.
- Kept these updates scoped to control polish so the dedicated viewer-shell redesign can happen cleanly in the next pass.

### Viewer frame and stage pass

- Added the first premium viewer-shell pass with a clearer outer frame, inner bezel, and more controlled shell shadowing.
- Introduced a subtle stage glow and floor falloff inside the viewer so models sit in a more intentional 3D environment instead of a flatter dark panel.
- Kept the work purely visual, without changing rendering logic, asset switching, download behavior, print controls, or the active tool flows.

### Viewer toolbar and status strip pass

- Rebuilt the viewer chrome into a more instrument-style top bar so the mode controls sit inside a dedicated shell instead of floating as isolated buttons.
- Added a compact in-view status strip for asset, mode, and output state, and synced it across `3D`, `SVG`, `Relief`, image, GLB, and STL viewer states.
- Kept the existing viewer actions intact by wiring the new shell through the current viewer-state sync functions instead of replacing render or export behavior.

### Viewer cache-bust fix

- Added a version query to the viewer script include so local browser testing picks up the latest viewer-shell markup instead of reusing a stale cached `viewer.js`.

### Viewer presence refinement

- Refined the viewer lighting with an added rim/bounce balance so models read with more depth and cleaner edge definition.
- Tuned model fit and camera targeting so the active asset sits more hero-like in the viewer without changing the render or export flows.
- Reduced the visual weight of the viewer title block, toolbar shell, and status strip so the chrome feels more precise and luxury around the model.

### Viewer material and print cluster refinement

- Rebalanced the viewer `Wire` and `Print` materials toward a warmer premium studio finish instead of flatter generic wireframe/print defaults.
- Shifted STL preview materials closer to the same print-oriented luxury language so exported assets feel more consistent inside the viewer.
- Integrated the viewer-side `Print` helper note and download CTA into a cleaner shell block so the export action reads as part of the instrument panel instead of a floating overlay.

### Viewer stage depth and camera elevation pass

- Deepened the viewer stage with a stronger upper ambient wash and floor falloff so the scene reads more like a premium display bay instead of a flatter dark panel.
- Added a shared hero-camera helper so fitted models and STL previews now start from a slightly higher, more elevated angle instead of sitting too parallel to the viewer floor.
- Kept the pass visual-only without changing generation, export, print-mode rules, or viewer state transitions.

### Viewer centering correction pass

- Added a shared stage-alignment helper so GLB, STL, and idle viewer states recenter the model against the viewer axis more consistently after scaling.
- Removed the horizontal camera offset and lifted the default hero framing a little more so the object stays visually centered while keeping the premium elevated angle.
- Kept the correction limited to viewer framing only, without touching export, generation, or mode logic.

### UI handoff checkpoint

- `6c04d9b` Document UI handoff checkpoint.
- `ce8a15e` Remove empty state copy from generator panels.
- `6cbb6f2` Simplify AI image card copy across tools.
- `40f05fb` Clean panel copy for `3D`, `SVG`, and `Relief`.

### Relief export stabilization

- `a073a11` Checkpoint relief and export sections stable.
- `181936a` Finalize relief export state polish.
- `4ab299e` Add arched relief STL export path.
- `020f09c` Refine relief mesh smoothing and frame transitions.
- `801319f` Polish relief STL controls and state.
- `fc4f59b` Add flat relief STL export pass.
- `548efbf` Document relief export research direction.
- `8b0d3c1` Add relief lithophane prep controls.
- `46b8ce6` Start relief panel with local preview flow.

### Remodel checkpoint

- `f0f8d80` Finish SVG panel remodel and production notes.
- `e29781a` Checkpoint `v1.1` remodel and owned test library.
- Treated `3D Generator` as the functionally stabilized core section for the current local/test checkpoint.
- Promoted `SVG` and `Relief` into self-contained panel flows.
- Split production adaptation concerns into a separate tracking path instead of mixing them into active local UI work.

### Licensing and provenance cleanup

- Added commercial-license audit tracking.
- Added owned-asset provenance notes for the active local test library.
- Removed higher-risk sample/dependency leftovers from the active path.

## 2026-03-26

- Froze production `v1` on `main` and `release/v1-launch`.
- Moved active normal development to `develop` as `v1.1`.
- Confirmed live Supabase auth and Google login in the project path.
- Hardened backend plan resolution and premium gating around backend-owned account state.
- Continued friend-test beta preparation while keeping heavy backend `print-fix` work paused for safety.

## 2026-03-25

- Ran a major UI polish pass across workspace and account-facing surfaces.
- Pushed the theme further toward a graphite shell with softer green accents.
- Cleaned `Login`, `Profile`, `Plans`, `Shop`, and `Gallery` toward a more product-like presentation.
- Tightened viewer STL CTA behavior and corrected related idle-viewer regressions.
- Continued centralizing theme/button/card tokens for more controlled visual consistency.

## 2026-03-24

- Collected active Supabase and Stripe setup values for local/test wiring.
- Synced local backend environment values.
- Applied the first Supabase billing schema.
- Continued subscription-state scaffolding and activation-readiness reporting.
- Expanded billing/account visibility so rollout blockers could be seen inside the product.

## 2026-03-23

- Simplified the local model/test asset strategy.
- Reduced dependency on larger local sample-model sets.
- Split key frontend logic into more modular files.
- Fixed AI token handling and stabilized the local generation setup.
- Chose the platform direction:
  - Supabase Auth
  - Supabase Postgres
  - Stripe
  - FastAPI
  - Vercel
  - Railway
- Set the direction toward backend-owned plan checks and premium gating.
