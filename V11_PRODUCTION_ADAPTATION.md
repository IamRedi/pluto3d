# Pluto3D v1.1 Production Adaptation

Purpose: keep the final pre-production checks for `v1.1` in one place so local remodel work does not drift away from deployment reality.

## Canonical Note

This file remains the detailed pre-production adaptation reference for `v1.1`.
The active day-to-day workflow should now follow the canonical docs first:

- `SYSTEM_MASTER.md`
- `CURRENT_STATE.md`
- `CHANGELOG.md`

Use this file when the project is intentionally moving from local/test stability toward release-readiness checks.

This file is not the release checklist itself.
It is the adaptation checklist for moving the current local `develop` remodel into a stable deployable production shape later.

## Current Working Assumption

- `v1.1` is being built and tested locally on `develop`
- live production remains frozen on `v1`
- final `v1.1` production adaptation will happen only after the remodeled flow is stable

## Main Risks To Revisit Before Production

### 1. Owned model asset weight

The owned test-model library is getting heavier.

Current local examples include:

- `frontend/models/pluto-robot.glb`
- `frontend/models/f1car.glb`
- `frontend/models/models with png foto previewe/bike.glb`
- `frontend/models/models with png foto previewe/car.glb`
- `frontend/models/models with png foto previewe/Skenderbeg.glb`

Before production:

- confirm whether the final hosting path serves these files comfortably
- check first-load performance and cache behavior
- confirm whether Railway/Vercel can tolerate the current asset strategy cleanly

If not:

- move heavy owned model assets to object storage or CDN
- keep preview PNGs and GLBs on a cleaner delivery path
- update `frontend/test-models.js` registry URLs accordingly

### 2. Local staging folder normalization

The current local pair folder:

- `frontend/models/models with png foto previewe/`

is acceptable while building, but should be reviewed before release.

Before production:

- normalize folder names
- keep paths readable and intentional
- verify every registry path after the rename

### 3. Final print/export path verification

The current `v1.1` direction is:

- browser-side STL export
- no heavy backend `print-fix` in the active public path
- first `Relief` preview pass should stay frontend-local and avoid new dependencies until the real lithophane/export path is defined
- the first `Relief` prep layer now adds only local UI/preview controls (`Thickness`, `Border`, `Surface`) and still avoids new mesh/export libraries
- the first real `Relief` export slice should stay limited to `Flat -> STL` in-browser before `Arched` or more advanced print presets are attempted
- use lightweight local presets (`Size`, `Mesh Detail`) before considering heavier export tuning or external geometry tooling

For the later real `Relief` export step:

- review browser-side mesh generation weight before adding any geometry helper library
- review commercial/license terms before introducing height-map, mesh, or CAD export dependencies
- verify that any future lithophane/STL path stays compatible with the planned Railway/Vercel deployment shape
- current recommended route is:
  - use the already-loaded `three.js` stack for the first real lithophane mesh pass
  - generate geometry locally in-browser from the active image source
  - export with the existing `STLExporter` path instead of adding a second export service
- defer heavier alternatives unless proven necessary:
  - backend `trimesh` generation adds more deployment surface and pulls this feature away from the current `v1.1` browser-first export direction
  - `OpenJSCAD` is MIT, but it is still a larger modeling stack than this first relief export pass appears to need
- do not copy from `GPL-3.0` lithophane generators into product code; keep Pluto3D implementation in-house even if external tools inform parameter defaults

Before production:

- verify printer export on the intended user machines
- confirm download naming and export quality
- confirm there is no accidental dependency on the paused backend print pipeline

### 4. Real 3D premium path verification

Before production:

- smoke test the active Meshy path from the remodeled `3D Generator`
- confirm local/source preview behavior matches production config
- confirm generated source image and uploaded source image both reach the premium 3D path cleanly

### 5. Licensing and provenance

Before production:

- keep `COMMERCIAL_LICENSE_AUDIT.md` current
- keep `OWNED_MODEL_ASSETS.md` current
- verify any newly added asset before wiring it into the public path
- keep proof of paid Meshy usage for owned generated assets

## When To Use This File

Use this file near the end of the `v1.1` cycle when the remodeled product path feels stable and attention shifts from design/build to deployment readiness.
