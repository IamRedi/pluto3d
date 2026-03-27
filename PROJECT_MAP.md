# Pluto3D Project Map

This file is the canonical structural map of the Pluto3D codebase and runtime flow.

## Repository Layout

```text
frontend/
  index.html
  runtime-config.js
  app-config.js
  auth-client.js
  billing-client.js
  viewer.js
  toy-mode.js
  toy-studio.js
  print-mode.js
  test-models.js
  models/

backend/
  app/
    main.py
    config.py
    routes/
    services/
    schemas/
    utils/
  supabase_billing_schema.sql
```

## Frontend Structure

### Main Files

- `frontend/index.html`
  - primary UI shell
  - theme tokens
  - section markup
  - a large share of current workspace logic
- `frontend/runtime-config.js`
  - resolves the API base URL by environment
- `frontend/app-config.js`
  - public install/runtime configuration
- `frontend/auth-client.js`
  - live auth runtime integration
- `frontend/auth-scaffold.js`
  - preview/helper auth state layer
- `frontend/billing-client.js`
  - billing runtime status and checkout/portal helpers
- `frontend/viewer.js`
  - viewer state
  - asset loading
  - download controls
  - print CTA behavior
- `frontend/toy-mode.js`
  - local toy/test generation helpers
- `frontend/toy-studio.js`
  - toy styling controls
- `frontend/print-mode.js`
  - print preparation and browser export helpers
- `frontend/test-models.js`
  - owned test-model registry and prompt matching

### Frontend Assets

- `frontend/models/`
  - local GLB/STL assets
  - paired preview images

## Backend Structure

### Entry And Config

- `backend/app/main.py`
  - FastAPI app entry
  - router registration
  - static mounts
- `backend/app/config.py`
  - env loading
  - upload/output directory handling

### Routes

- `backend/app/routes/upload.py`
  - upload endpoint
- `backend/app/routes/generate.py`
  - core generation endpoints
- `backend/app/routes/svg.py`
  - SVG endpoints
- `backend/app/routes/ai_photo.py`
  - AI image generation endpoint
- `backend/app/routes/print_fix.py`
  - print-fix endpoint
- `backend/app/routes/toy.py`
  - toy generation endpoint
- `backend/app/routes/account.py`
  - authenticated account state
- `backend/app/routes/billing.py`
  - billing config, status, checkout, portal, and webhook endpoints

### Services

- `backend/app/services/ai_engine.py`
  - Meshy-oriented generation helpers
- `backend/app/services/ai_service.py`
  - AI request helpers
- `backend/app/services/auth.py`
  - Supabase user verification
- `backend/app/services/billing.py`
  - billing config and runtime helpers
- `backend/app/services/subscriptions.py`
  - subscription storage and persistence helpers
- `backend/app/services/plans.py`
  - guest/free/premium resolution
- `backend/app/services/svg_engine.py`
  - SVG processing helpers
- `backend/app/services/mesh_repair.py`
  - mesh repair logic
- `backend/app/services/storage_service.py`
  - file persistence helpers
- `backend/app/services/blueprint_engine.py`
  - generation/asset helper logic

## API Routes

### General

- `GET /`
  - backend health root

### Upload

- `POST /api/upload`

### 3D And Job Flow

- `POST /api/generate`
- `POST /api/generate-free`
- `POST /api/image-to-3d`
- `POST /api/image-to-3d-pro`
- `GET /api/job/{task_id}`

### SVG

- `POST /api/svg`
- `POST /api/svg-from-image`
- `POST /api/silhouette`

### AI Photo

- `POST /api/ai-photo`

### Toy And Print

- `POST /api/generate-toy`
- `POST /api/print-fix`

### Account And Billing

- `GET /api/account/me`
- `GET /api/billing/config`
- `GET /api/billing/activation-status`
- `GET /api/billing/activation-handoff`
- `GET /api/billing/status`
- `POST /api/billing/checkout-session`
- `POST /api/billing/portal-session`
- `POST /api/billing/webhook`

## System Flow

### Workspace Source Flow

1. User uploads an image or generates a concept image in the frontend.
2. The active source is stored in the shared preview state.
3. The chosen panel uses that source:
   - `3D Generator`
   - `SVG`
   - `Relief`
4. The result is pushed into the main viewer or download path.

### Test 3D Flow

1. Prompt/source enters the `3D Generator`.
2. Frontend matches the prompt to the owned test-model registry.
3. A selected local GLB is loaded into the viewer.
4. Download and print-oriented flows stay browser-side where possible.

### Premium Real 3D Flow

1. Frontend keeps the active shared source preview.
2. Source is sent to the backend premium 3D route.
3. Backend talks to Meshy.
4. Frontend polls job status.
5. Final model URL is loaded into the viewer.

### SVG Flow

1. Source is prepared in the `SVG` panel.
2. Frontend sends the request to the SVG backend route.
3. Generated SVG is returned.
4. Viewer shows the SVG result and handles download.

### Relief Flow

1. Source is prepared in the `Relief` panel.
2. Frontend builds a local preview in the browser.
3. STL is generated in-browser for supported paths.
4. Viewer shows the result and handles download.

### Auth And Billing Flow

1. Frontend auth client reads or creates session state.
2. Backend verifies user identity through Supabase.
3. Backend resolves guest/free/premium state.
4. Billing client reads runtime status.
5. Stripe checkout/webhook/portal update the subscription lifecycle.

## Configuration Flow

- public frontend values:
  - `frontend/app-config.js`
- optional public auth fallback:
  - `frontend/auth-config.js`
- private backend values:
  - `backend/.env`
- canonical env template:
  - `.env.example`
