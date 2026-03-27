# Pluto3D Frontend v1.1 Blocks

This file is the working plan for safe frontend-only improvements in `v1.1`.
Use it to keep each pass small, focused, and easy to review without mixing unrelated UI work.

## Working Rule

- stay on `develop` as the active integration branch unless a clean checkpoint clearly justifies a separate feature branch
- work on one frontend block at a time
- define `in scope` and `out of scope` before editing
- test only the touched surface before moving on
- update this file and `PROJECT_BOARD.md` after each meaningful step
- ask the user only when a decision changes product behavior, not just styling polish

## Block Format

Each block should define:

- goal
- surfaces
- in scope
- out of scope
- done when
- status

## Current Sequence

## Remodel Pivot

As of `2026-03-27`, `v1.1` is no longer only a frontend polish sequence.
The product is pivoting toward a broader remodel centered on a new unified `3D Generator` flow.

Primary remodel notes now live in:

- `V11_REMODEL_PLAN.md`

This file still matters, but from this point onward it should support the remodel instead of assuming only small polish passes.

### Block 1: Frontend Copy Cleanup

- status: `active`
- goal: remove remaining test/demo/placeholder/future-facing copy so the product reads clean and client-facing
- surfaces:
  - `Gallery`
  - `Profile`
  - `Shop`
  - supporting workspace/account copy where needed
- in scope:
  - delete leftover placeholder wording
  - tighten awkward or repetitive descriptions
  - remove language that sounds internal, temporary, or unfinished
  - keep premium/product language calm and real
- out of scope:
  - layout redesign
  - backend logic
  - auth/billing behavior
  - mobile layout changes
  - icon swaps
- done when:
  - obvious `test`, `preview`, `placeholder`, and weak future-state copy is cleaned from the targeted surfaces
  - the touched sections read like a live product, not a scaffold
- progress:
  - first pass completed on `Gallery`, `Shop`, and `Profile` copy
  - remaining frontend `preview/test` references are now mostly technical names, CSS hooks, local placeholders, or internal asset labels rather than customer-facing product copy

### Block 2: Theme Refinement Pass

- status: `active`
- goal: refine theme tokens, button contrast, and accent usage without changing structure
- surfaces:
  - shared theme tokens
  - buttons
  - cards
  - accent states
- progress:
  - first pass completed on shared surface/header/chip tokens
  - cards and plan cards now use centralized surface styling instead of flatter one-off fills
  - light theme featured cards now stay in the graphite/green family instead of drifting into off-palette tones
  - theme toggle now follows the same button system as the rest of the UI

### Block 3: Hierarchy And Icon Pass

- status: `queued`
- goal: improve section hierarchy, CTA clarity, and icon consistency
- surfaces:
  - section headers
  - card titles
  - CTA groups
  - icon usage

### Block 4: Gallery And Profile UI Pass

- status: `queued`
- goal: clean the structure and readability of `Gallery` and `Profile` after copy cleanup
- surfaces:
  - `Gallery`
  - `Profile`

### Block 5: Mobile UI Pass

- status: `queued`
- goal: tighten spacing, stacking, and touch behavior on mobile without reopening desktop polish
- surfaces:
  - mobile header
  - panel stacking
  - modal spacing
  - touch targets

## Notes

- if a task starts affecting more than one block, stop and split it
- copy cleanup should happen before hierarchy and mobile polish so later passes are not wasted on weak content
- the new `v1.1` remodel may replace or retire some earlier queued polish blocks if the unified `3D Generator` flow supersedes them
- compactness is now a standing UI rule for the remodel:
  - keep controls smaller and cleaner when possible
  - avoid unnecessary vertical growth
  - avoid adding scroll unless the content truly requires it
- vertical mobile suitability should be treated as an important remodel concern even before the dedicated mobile pass begins
- current remodel runtime notes:
  - the `3D Generator` shared source preview should stay the single source of truth for upload and prompt-generated concept images
  - new flow wiring should prefer hiding old surfaces gradually instead of deleting them before the replacement path is stable
  - sidebar cleanup can remove old entry points early as long as compatibility code remains available underneath
  - compact button sizing and shorter labels are valid remodel changes when they reduce scroll and visual weight without hurting clarity
  - owned preview PNG plus GLB pairs should be wired in the registry before the test-library expansion starts growing
