# Pluto3D Current State

Last updated: `2026-03-28`
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

- production `v1` is frozen on `main`
- active development continues on `develop` as `v1.1`
- local/test work does not change production by itself

### Core Workspace

- `3D Generator` is functionally stabilized for the current local/test checkpoint
- shared source preview is the active source of truth for:
  - uploads
  - prompt-generated concept images
  - test 3D generation
  - premium real 3D generation
- recent concept/source thumbnail strips exist in the remodel flow
- active `3D`, `SVG`, and `Relief` panels now use stronger section headers, visible card chips, and clearer CTA priority for faster scanning
- `SVG` and `Relief` option controls now use a more compact layout, with narrower selects and parallel field placement where the space allows it
- generator CTAs in the active creation panels now sit on content-sized widths on desktop and use a cleaner varnished-gold treatment with reduced ambient bleed from card and hover effects
- the workspace shell is now being simplified toward a cleaner `Frozen Deep Green` foundation:
  - animated star/background layers were removed
  - viewer neural overlays were removed
  - heavy blur and glow usage was reduced across the main shell
  - sidebar and shell controls now lean more matte and restrained
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
- gallery and profile UI pass
- spacing, rhythm, and CTA clarity polish across account-facing surfaces
- keeping the remodel compact and premium-looking without reopening backend architecture

## Next Tasks

- treat `SYSTEM_MASTER.md`, `CURRENT_STATE.md`, and `CHANGELOG.md` as the primary working documentation
- continue the shell redesign from the simplified `Frozen Deep Green` base:
  - cleaner sidebar
  - cleaner viewer frame
- continue with `Gallery And Profile UI Pass`
- finish the UI pass for:
  - spacing
  - visual clarity
- continue with `Mobile UI Pass`
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

## Current Working Boundaries

- do not treat this checkpoint as a production adaptation phase yet
- do not reopen heavy backend scaling work unless stability requires it
- do not break already working `3D`, `SVG`, or `Relief` behavior for cosmetic-only changes
- keep the new canonical documentation system as the default project workflow from now on
- every meaningful change must update:
  - `CURRENT_STATE.md`
  - `CHANGELOG.md`
