# Pluto3D Commercial License Audit

Date: 2026-03-27
Branch: `develop` (`v1.1`)
Purpose: practical audit of libraries, models, fonts, textures, and third-party AI/service terms relevant to selling Pluto3D as a commercial product.

This is not formal legal advice. It is an engineering and product-risk audit based on current project usage and primary-source license pages.

## Scope Reviewed

Current runtime usage found in repo:

- Frontend:
  - `frontend/index.html`
  - `frontend/models.json`
  - `frontend/auth-client.js`
  - `frontend/models/pluto-robot.glb`
  - `frontend/models/f1car.glb`
  - `frontend/models/print-ready-preview.stl`
- Backend:
  - `backend/app/routes/ai_photo.py`
  - `backend/app/routes/generate.py`
  - `backend/app/routes/svg.py`
  - `backend/app/routes/toy.py`
  - `backend/app/services/mesh_repair.py`
  - `backend/app/services/blueprint_engine.py`
  - `backend/yolov8n.pt`

## Result In One Line

Jo plotësisht ende, por pas cleanup-it të 2026-03-27 rreziku kryesor u ul: `Horse.glb` u hoq nga frontend gallery dhe `ultralytics` / `yolov8n` u hoqën nga repo-ja aktive. Pikat që mbeten janë kryesisht provenance/dokumentim asetesh dhe disa sample assets me attribution ose licencë të paqartë.

## Safe Or Low-Risk For Commercial Use

These look commercially usable under permissive or business-friendly licenses:

- `three.js` and the loader/control files from the same project: MIT
  - Source: https://github.com/mrdoob/three.js
- `@supabase/supabase-js`: MIT
  - Source: https://github.com/supabase/supabase-js
- `FastAPI`: MIT
  - Source: https://github.com/FastAPI/FastAPI
- `uvicorn`: BSD-3-Clause
  - Source: https://github.com/Kludex/uvicorn
- `requests`: Apache-2.0
  - Source: https://github.com/psf/requests
- `replicate-python`: Apache-2.0
  - Source: https://github.com/replicate/replicate-python
- `rembg`: MIT
  - Source: https://github.com/danielgatis/rembg
- `trimesh`: MIT
  - Source: https://github.com/mikedh/trimesh
- `opencv-python` / OpenCV 4.5+ runtime: Apache 2.0
  - Source: https://opencv.org/license/
- `svgwrite==1.4.3`: MIT on current PyPI metadata
  - Source: https://pypi.org/pypi/svgwrite/1.4.3

Notes:

- `svgwrite` is not a copyright blocker, but its upstream repo is archived/unmaintained.
  - Source: https://github.com/mozman/svgwrite
- These library licenses still require preserving notices where applicable in distribution.

## Fonts

- `Inter`: SIL Open Font License 1.1
  - Source: https://github.com/google/fonts/tree/main/ofl/inter
- `Orbitron`: SIL Open Font License 1.1
  - Source: https://github.com/google/fonts/tree/main/ofl/orbitron

Practical result:

- Both are generally fine for commercial product use.
- Keep font license texts if you redistribute/self-host them.
- OFL is usually not a blocker for SaaS/app sales.

## Conditional: Commercially Usable, But With Important Terms

### Meshy

Meshy itself is not the blocker if used correctly, but rights depend on plan and source material:

- Paid plan: Meshy says you retain full private ownership of generated assets, if you do not violate others' copyrights and do not publish publicly to Meshy Community.
- Free plan: Meshy says generated assets are under CC BY 4.0 and require attribution.

Sources:

- https://help.meshy.ai/en/articles/10137554-what-is-the-ownership-of-the-generated-models
- https://help.meshy.ai/en/collections/10642992-privacy-and-policy

Practical result:

- If Pluto3D is using a paid Meshy plan for production generation, this is generally acceptable for commercial sale.
- If any generated sample/demo asset came from a free Meshy plan, it should be treated as attribution-required.

### Replicate

Replicate platform use is not automatically a copyright problem, but model-by-model terms matter:

- Replicate says model licenses vary.
- Replicate terms require compliance with the third-party terms and licenses of each model used through the service.

Sources:

- https://replicate.com/terms
- https://replicate.com/docs/reference/how-does-replicate-work/
- https://replicate.com/docs/topics/models/

Practical result:

- The `replicate` Python client is fine as software.
- The actual AI model behind `AI Photo` must be checked separately on its Replicate model page before sale.
- Without documenting the exact Replicate model license, this area is not fully cleared.

### Mixkit audio

The orb sound currently points to a Mixkit sound effect:

- `frontend/index.html` uses `https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3`

Mixkit states its free sound effects are under the Mixkit License and can be used in commercial projects.

Sources:

- https://mixkit.co/license/
- https://mixkit.co/free-sound-effects/

Practical result:

- Likely acceptable commercially.
- Keep a record of the exact asset page or download source for audit purposes.

### CC-BY sample assets

Some remote sample models appear commercially usable only if attribution is preserved:

- `Astronaut.glb`: modelviewer.dev example pages identify it as "Astronaut by Poly, licensed under CC-BY."
  - Source: https://modelviewer.dev/examples/augmentedreality/index.html
  - Also seen in: https://modelviewer.dev/examples/loading/index.html
- `RobotExpressive.glb`: modelviewer.dev example pages identify it as CC0.
  - Source: https://modelviewer.dev/examples/animation/

Practical result:

- `RobotExpressive.glb` is low-risk.
- `Astronaut.glb` should only remain if you keep proper attribution.

## High-Risk Or Not Cleared For Sale Yet

### 1. Owner-created local models still need provenance notes

Files:

- `frontend/models/pluto-robot.glb`
- `frontend/models/f1car.glb`

Current finding:

- user clarified these are owner-created assets generated from the user's own photos in Meshy and then manually modified in 3D Builder
- that makes them materially safer than third-party sample assets
- the repo now includes a local provenance note in `OWNED_MODEL_ASSETS.md`
- external proof should still be kept outside the repo for sale readiness

Practical result:

- These should be treated as commercially workable owner-created assets.
- Before sale, keep the repo provenance note updated and retain external proof of source inputs and paid Meshy usage.

### 2. `print-ready-preview.stl` still needs provenance confirmation

File:

- `frontend/models/print-ready-preview.stl`

Current finding:

- no license/readme/attribution file was found next to this asset in the repo
- no embedded provenance was visible during local inspection

Practical result:

- Keep only if this STL is also your own asset or replace it with a clearly documented in-house placeholder.

### 3. Toy fallback asset cleanup

Found in:

- `backend/app/routes/toy.py`

Current finding:

- the old remote `Car.glb` fallback has been replaced with the owned `pluto-robot.glb` asset path
- this removes the remaining sample-car license ambiguity from the toy fallback path

Practical result:

- No active `Car.glb` sample dependency remains in the toy fallback code.

### 4. Transparent Textures background

Found in:

- `frontend/index.html`

Current usage:

- `https://www.transparenttextures.com/patterns/stardust.png`

Current finding:

- the site clearly exposes downloadable patterns and authors, but a clear commercial license statement for this exact asset was not verified from a primary license page during this audit

Source:

- https://www.transparenttextures.com/

Practical result:

- Replace with a self-created texture or a clearly licensed texture before sale.

## Recommended Actions Before Selling Pluto3D

1. Add provenance for:
   - keep `OWNED_MODEL_ASSETS.md` updated for `frontend/models/pluto-robot.glb`
   - keep `OWNED_MODEL_ASSETS.md` updated for `frontend/models/f1car.glb`
   - `frontend/models/print-ready-preview.stl`
2. Replace the Transparent Textures background with an internally-created or clearly licensed asset.
3. Document the exact Replicate model used by `AI Photo` and save its license/terms snapshot.
4. Create an `ATTRIBUTIONS.md` file if keeping any CC-BY assets such as `Astronaut.glb`.
5. Keep proof that production Meshy usage is on a paid plan if generated assets are sold.

## Ship Decision Today

### Safe to keep

- Core open-source libraries listed in "Safe Or Low-Risk"
- `RobotExpressive.glb` if needed
- `Inter` and `Orbitron`
- owner-created Meshy + manual-edit assets once documented:
  - `frontend/models/pluto-robot.glb`
  - `frontend/models/f1car.glb`

### Safe only with documentation / attribution / model-specific review

- Meshy-generated assets
- Replicate-powered outputs
- `Astronaut.glb`
- Mixkit orb sound

### Replace before selling

- Transparent Textures background
- `print-ready-preview.stl` if provenance cannot be confirmed

## Cleanup Already Applied On 2026-03-27

- Removed `Horse.glb` from `frontend/models.json`
- Removed `ultralytics` and `ultralytics-thop` from root `requirements.txt`
- Removed `backend/yolov8n.pt` from the repo active path
- Replaced toy sample fallback assets with owned local GLB assets
- Added `OWNED_MODEL_ASSETS.md` to capture the declared provenance of the active owned test assets
