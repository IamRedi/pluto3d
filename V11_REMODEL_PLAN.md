# Pluto3D v1.1 Remodel Plan

Date: 2026-03-27
Branch: `develop`
Purpose: capture the new `v1.1` product-direction pivot before implementation starts.

## Canonical Note

This file remains the detailed remodel-planning reference for `v1.1`.
The active current-state and workflow truth should now be read first from:

- `SYSTEM_MASTER.md`
- `CURRENT_STATE.md`
- `CHANGELOG.md`

Use this file for remodel reasoning, staged intent, and detailed pivot context.

This file is the working notes + execution plan for the larger `v1.1` remodel.
It exists so the product direction does not get lost across chats or mixed with smaller polish tasks.

## User Vision

The user wants `v1.1` to become a much simpler, more premium, more client-facing product:

- merge the current `3D`, `Toy`, and `AI` thinking into one cleaner `3D Generator` experience
- remove the feeling of multiple half-overlapping tools
- make the path feel extremely simple for customers:
  - prompt or upload
  - preview
  - generate
  - download for 3D printer
- prefer high-quality paid generation APIs such as Meshy or Luma for the real premium path
- keep the product looking beautiful while hiding technical complexity from the user

## User Requests, In Simple Form

### Requested section direction

- replace the current split between `3D`, `Toy`, and `AI`
- create a cleaner main section called `3D Generator`
- move toy logic inside that flow instead of keeping `Toy` as a separate surface
- remove the standalone `AI` section later
- add `Lithophane` as a future section later

### Requested `3D Generator` flow

- field: `Prompt`
- helper copy: describe the model the user wants
- a `Toy` checkbox only for prompt-to-image generation
- when `Toy` is enabled:
  - the system appends a hidden toy-style prompt internally
  - the user does not need to see that hidden suffix
- this toy checkbox should not affect locally uploaded photos

### Requested prompt-to-image behavior

- keep or replace the current image-generation API path
- show generated image directly in the same photo preview / drag-drop area
- every new generated image should update the main preview
- keep a temporary strip of 5 recent generated-image thumbnails
- clicking a thumbnail should restore it into the main preview area
- generated thumbnails should be temporary:
  - cleared on refresh
  - or cycled when new generations replace old ones

### Requested usage logic

- image generation limit:
  - 5 prompt-image generations before the user must convert one into 3D before generating more images again
- test 3D generation limits:
  - guest: 3
  - logged-in free user: 10
  - premium: unlimited
- test download limits:
  - guest gets preview
  - free user gets limited downloadable tests
  - premium can download all tests

### Requested test-3D behavior

- keep a hidden internal matching layer
- match user prompt keywords to owned test models
- if nothing matches, choose randomly from the owned test pool
- each owned test model should also have a paired preview image
- when the test model is selected:
  - its paired image should replace the current image preview
  - then a fake generation delay should run
  - then the selected test GLB should load in the viewer
- target scale later:
  - around 20 owned test models

### Requested premium real-3D behavior

- premium-only real 3D generation
- use the current image in the drag/preview area as the source
- this image may come from:
  - upload
  - prompt-image generation
- then send it to the real 3D generation API

### Requested print/download direction

- keep the flow simple and stable
- prioritize:
  - beautiful GLB preview
  - direct GLB download
  - direct STL/printer download
- avoid heavy server-side print pipelines when they threaten Railway stability
- keep only safe/light transforms in the active path

## Assistant Recommendations

The safest way to build this is not as one giant rewrite, but as staged remodeling:

### Stage 1: Information architecture reset

- define the new top-level sections
- collapse `Toy` logic into the new `3D Generator`
- mark standalone `AI` and heavy `Toy Studio` behavior as deprecated
- do not remove old flows until the new one is wired and testable

### Stage 2: Prompt-image generation surface

- build the new `Prompt + Toy toggle + Generate image` area
- keep image output inside the existing upload/preview frame
- add temporary thumbnail memory for 5 recent generated images
- keep this entirely frontend-driven at first, then connect usage rules

### Stage 3: Test 3D generator orchestration

- build a structured owned-model registry:
  - model keywords
  - GLB path
  - paired preview image path
  - test download permission metadata
- route `Generate test in 3D` through that registry
- keep fake generation timing and viewer-loading logic clean and deterministic
- note: the paired preview image path can stay empty until the user provides the owned preview-source assets

### Stage 4: Premium real 3D generation

- keep the current Meshy path
- adapt the input source so it always uses the image currently shown in the preview area
- only after the new image/prompt flow is stable

### Stage 5: Print/download simplification

- keep browser-side STL export if it stays stable
- keep heavy backend `print-fix` paused unless there is a proven reason to bring it back
- simplify the active editing path to light transforms only

### Stage 6: New sections later

- add `Lithophane` only after the main `3D Generator` flow is stable
- do not expand surface count while the core flow is still being rebuilt

## Suggested v1.1 Implementation Order

1. Freeze the old section plan and declare the `v1.1` remodel pivot.
2. Create the new `3D Generator` structure in the UI without deleting old logic yet.
3. Implement prompt-to-image generation inside that section.
4. Add the 5-image temporary thumbnail strip.
5. Add the owned test-model registry with paired preview images.
6. Wire `Generate test in 3D`.
7. Reconnect premium real 3D generation to the currently selected preview image.
8. Simplify/hide old `Toy` and `AI` surfaces.
9. Add `Lithophane` after the core path is working.

## What Should Be Kept Out Of Scope For The First Remodel Pass

- bringing back heavy backend `print-fix`
- complex Toy Studio shaping
- broad backend concurrency work
- final production deploy steps
- multi-API expansion before the primary flow is stable

## Important Product Decisions Already Implied

- `v1.1` is no longer just a polish pass; it is a structured remodel
- simplicity and stability are now more important than exposing many overlapping tools
- owned assets and predictable flows are preferred over flashy but fragile behaviors
- the main customer path should be understandable in seconds

## Notes Split: User vs Assistant

### User ideas

- cleaner `3D Generator` centered UX
- compact polished UI with minimal scroll
- small elegant controls instead of bulky blocks
- prompt + toy toggle for prompt-image generation
- image history thumbnails
- owned test models with paired preview images
- simple path to GLB and STL/printer download
- remove standalone `Toy`
- remove standalone `AI`
- add `Lithophane`
- later make the remodeled flow strong on vertical mobile layout

### Assistant guidance

- do this as staged remodeling, not one-shot replacement
- keep old flows alive until the new flow works end-to-end
- treat owned test model registry as its own subsystem
- keep backend risk low and prefer browser-side or lightweight paths when possible
- update `PROJECT_BOARD.md` after each meaningful stage, not just after code
- compactness should be part of the architecture, not a final afterthought
- mobile-vertical suitability should be tracked early even before the dedicated mobile pass starts

## Business And Limit Notes To Keep

These are important product notes gathered during the `v1.1` remodel discussion.
They are not all implemented yet, but they should stay visible so the final product and pricing flow do not drift.

### User-proposed usage limits

- prompt-to-image concept generation:
  - allow up to `5` concept images in a row
  - after that, the user should convert one into `3D` before generating more concept images again
- `Generate Test in 3D`:
  - guest: `3` tries
  - signed-in user: `10` tries
  - premium: effectively no test limit
- test-model download direction:
  - guest should mainly preview
  - signed-in users can unlock a small free owned-model download allowance
  - premium should unlock the full owned test library

### Product simplicity notes

- the ideal user path should feel like:
  - prompt or upload
  - preview
  - generate 3D
  - download for printer
- keep the final experience close to `3 clicks to printer`
- heavy edit tooling should not return unless it stays lightweight and stable

## Current Next Step

The best next step is:

- design and implement the new `3D Generator` structure first

before:

- deleting the old `Toy`/`AI` sections
- wiring final limits
- expanding the test model library

## Progress Snapshot

- `2026-03-27`: Stage 1 skeleton started in the main `3D Generator` panel
- `2026-03-27`: compactness requirement confirmed:
  - keep controls small and premium
  - avoid unnecessary vertical growth and scroll
  - track vertical mobile suitability as an important later pass
- `2026-03-27`: Stage 3 registry started:
  - owned test models now move into a structured registry instead of one-off `car/default` branching
  - preview-image pairing is prepared in the registry shape even if some owned preview assets are still missing
- `2026-03-27`: Stage 4 wiring started:
  - the shared source preview now acts as the real source of truth for both `Generate Test in 3D` and `Generate Real 3D`
  - uploads and prompt-generated concept images now stay inside one active source frame instead of splitting into separate paths
  - old `AI` and `Toy` navigation entries can now be hidden gradually while their compatibility code stays available underneath
- `2026-03-27`: compact pass 3 started:
  - prompt height, toggle weight, thumbnail rhythm, and CTA sizing are being tightened so the remodeled panel feels more like a compact design studio than a stacked form
  - owned paired source-photo plus GLB assets are expected as the next content layer for smarter registry matching
  - source preview framing is being softened so the active image feels like a staged studio preview rather than a raw upload box
- `2026-03-27`: owned pair wiring started:
  - active preview PNG files are now being connected to the owned test-model registry for the current robot and F1 test paths
  - `OWNED_MODEL_ASSETS.md` now keeps the declared provenance note for the active owned assets
- `2026-03-27`: test-registry expansion started:
  - generic `car` now separates from `F1`
  - `bike` and `Skenderbeg` are being added to the active owned test library
  - random fallback should be equal across the owned test-model library
  - production adaptation must still review the growing asset weight before `v1.1` goes live
- `2026-03-27`: production adaptation tracking started:
  - `V11_PRODUCTION_ADAPTATION.md` now keeps the final deploy-readiness concerns separate from the remodel notes
- `2026-03-27`: section close-out pass started:
  - `3D Generator` is being tightened so the active source and output path are readable without depending on legacy surfaces
  - the goal is to leave this section mostly in polish territory before moving the main focus to the next section
- `2026-03-27`: section handoff state:
  - `3D Generator` should now be treated as the current finished core section for `v1.1`
  - next primary section should be `SVG`
  - after `SVG`, continue into the photo-to-relief / lithophane path
- `2026-03-27`: SVG section reset started:
  - `SVG` is being remodeled into its own complete panel instead of depending on the `3D Generator` panel for source preparation
  - the intended `SVG` panel now includes:
    - prompt
    - source preview / upload
    - 5 recent source thumbnails
    - one `Generate SVG` CTA
  - unsupported UI options such as `Mode` should stay out of the active panel until the backend has a real implementation for them
  - current SVG usage direction:
    - guest `1`
    - logged-in free `5`
    - premium `unlimited`
- current status:
  - new concept-image block exists visually
  - shared preview framing is now represented in the main panel
  - `SVG` is now being pushed toward a true self-contained panel flow:
    - prompt generation and uploads both live inside the panel
    - the temporary 5-slot source history now needs to represent real local source selection, not only generated images
    - the main viewer is the intended final output surface for SVG preview and download
    - duplicate panel-level download controls should stay out once the viewer download is in place
    - 3D-only viewer controls should not appear while the workspace focus is `SVG`
    - SVG contrast should stay readable against the viewer shell regardless of light/dark theme toggle
    - older overlapping frontend `SVG` handlers should be cleaned out so one self-contained panel path remains active
  - `Relief` is the next active section after `SVG`:
    - first pass should establish panel structure and local source flow before any true lithophane export promise is made
    - the safest immediate output is a local main-viewer relief preview, not a fake mesh/export path
    - avoid introducing new dependency/license/deploy risk in the first relief step
    - current active pass is now `lithophane prep` rather than export:
      - add honest local controls for `Depth`, `Thickness`, `Border`, `Surface`, and `Direction`
      - let the user shape the intended relief/lithophane look before any real geometry pipeline is wired
      - keep download behavior as preview `PNG` until a real browser-side or backend mesh path is chosen and verified
    - research checkpoint for the next implementation pass:
      - best-fit path for Pluto3D `v1.1` is a custom browser-side lithophane mesh built on the libraries already in use
      - recommended geometry direction:
        - `PlaneGeometry` with dense segments for flat relief
        - direct `BufferGeometry` vertex displacement from image luminance
        - `computeVertexNormals()` for readable shading
        - optional curved pass via cylindrical remap / `CylinderGeometry`
        - export through the existing `STLExporter`
      - this keeps the stack aligned with the current browser-side `GLB -> STL` philosophy already active in `v1.1`
      - avoid pulling in a larger CAD framework unless the simple in-house path fails on manifold/export quality
      - avoid borrowing implementation code from `GPL-3.0` lithophane projects even if their UX or parameter ideas are useful as reference
    - first export checkpoint now starts with the smallest safe slice:
      - add `Generate STL` for `Flat` relief only
      - after flat stabilizes, enable `Arched STL` as a separate bounded geometry pass
      - keep `Print Tab` flat-only until curved export quality is proven
      - reuse the current viewer download surface instead of creating a second export/download UI
    - current polish follow-up on the same checkpoint:
      - expose simple `Size` and `Detail` presets before attempting broader geometry features
      - tighten CTA state so unsupported `Arched STL` is communicated in the panel before click-time
      - improve the flat STL mesh itself before expanding scope:
        - reduce noise/spikes from raw photo luminance
        - make frame/border transitions less abrupt for cleaner print behavior
      - finish the section with functional-state cleanup before the wider design pass:
        - keep CTA copy/state in sync with `Border` and `Surface`
        - treat the next pass on this section as mostly visual unless a print issue appears
    - shared tool-panel cleanup can now proceed before the design pass:
      - shorten `3D`, `SVG`, and `Relief` copy to the minimum useful UI language
      - remove internal plan/status phrasing that makes the panels feel less product-ready
      - remove placeholder empty-state text where it is not needed for the flow
    - current handoff state:
      - the next chat should continue from a stable local/test checkpoint
      - primary next focus is the broader UI pass across these sections, especially buttons and visual structure
      - production adaptation remains deferred until after the design/system pass settles
  - 3D output section now reflects the future split between test and premium real 3D
  - premium real 3D now follows the active shared source preview instead of requiring a separate old-panel path
  - old `AI` and `Toy` panels are still present as compatibility surfaces until the new path is wired
