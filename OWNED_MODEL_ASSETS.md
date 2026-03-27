# Pluto3D Owned Model Assets

This file records user-declared provenance for local 3D test assets used inside `v1.1`.

## Ownership statement

The current local test assets below were declared by the project owner as:

- created from the owner's own photos or AI-generated concept images
- generated into 3D using Meshy on a paid premium plan
- manually edited by the owner after generation

This note is meant to keep the repo aligned with the commercial-license cleanup work.
Before sale, keep external proof of:

- the source inputs used for the models
- the Meshy paid-plan account used for generation
- any manual editing workflow that turned the raw generations into final owned assets

## Active `v1.1` test-library assets

### Pluto Robot

- GLB:
  - `frontend/models/pluto-robot.glb`
- paired preview image:
  - `frontend/models/models with png foto previewe/pluto-robot.png`
- current usage:
  - active `Generate Test in 3D` owned model

### F1 Car

- GLB:
  - `frontend/models/f1car.glb`
- paired preview image:
  - `frontend/models/models with png foto previewe/f1car.png`
- current usage:
  - active `Generate Test in 3D` owned model

### Car

- GLB:
  - `frontend/models/models with png foto previewe/car.glb`
- paired preview image:
  - `frontend/models/models with png foto previewe/car.png`
- current usage:
  - active `Generate Test in 3D` owned model for generic `car` prompts

### Bike

- GLB:
  - `frontend/models/models with png foto previewe/bike.glb`
- paired preview image:
  - `frontend/models/models with png foto previewe/bike.png`
- current usage:
  - active `Generate Test in 3D` owned model for `bike` prompts

### Skenderbeg

- GLB:
  - `frontend/models/models with png foto previewe/Skenderbeg.glb`
- paired preview image:
  - `frontend/models/models with png foto previewe/Skenderbeg.png`
- current usage:
  - active `Generate Test in 3D` owned model for `toy`, `hero`, and `warrior` prompts
  - also intentionally weighted higher for random fallback selection

## Staging Note

Some active `v1.1` owned pairs currently live inside:

- `frontend/models/models with png foto previewe/`

This is acceptable during local remodel work.
Before production release, normalize the folder structure if needed, then update the registry paths in `frontend/test-models.js`.
