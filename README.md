# Pluto3D Studio

Pluto3D Studio is a web app that converts images and prompts into SVG or 3D outputs, then prepares 3D models for printing through a simple non-expert workflow.

## Current Product Direction

- Frontend: vanilla HTML/CSS/JavaScript with a unified viewer
- Backend: FastAPI
- Hosting:
  - Frontend on Vercel
  - Backend on Railway
- Core value:
  - generate with APIs
  - clean, preview, and prepare outputs inside Pluto3D
  - sell practical results, not just raw generation

## Active Features

- AI photo generation
- SVG conversion
- 3D generation
- Toy test mode with local reference models
- backend cooldown and rate-limit protection on cost-sensitive generation routes
- Print Fix:
  - GLB input
  - topology cleanup
  - STL export
  - ready-for-print preview flow

## Project Structure

- [`frontend/index.html`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/frontend/index.html): main UI shell
- [`frontend/app-config.js`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/frontend/app-config.js): public install config for brand, API, support, and auth
- [`frontend/runtime-config.js`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/frontend/runtime-config.js): environment-aware backend URL
- [`frontend/test-models.js`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/frontend/test-models.js): local QA models for toy mode
- [`frontend/print-mode.js`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/frontend/print-mode.js): print fix and transform logic
- [`frontend/toy-mode.js`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/frontend/toy-mode.js): toy generator logic
- [`frontend/viewer.js`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/frontend/viewer.js): GLB/STL/fake preview viewer logic
- [`backend/app/main.py`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/backend/app/main.py): FastAPI app entry
- [`backend/app/routes/print_fix.py`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/backend/app/routes/print_fix.py): print repair route
- [`SELF_HOST_QUICKSTART.md`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/SELF_HOST_QUICKSTART.md): plug-and-play deployment guide
- [`PRODUCTION_ACTIVATION_RUNBOOK.md`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/PRODUCTION_ACTIVATION_RUNBOOK.md): live billing/subscription activation sequence
- [`INFRASTRUCTURE_INVENTORY.md`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/INFRASTRUCTURE_INVENTORY.md): operator map of domains, services, billing surfaces, and secret boundaries
- [`PLATFORM_ACCOUNTS_OVERVIEW.md`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/PLATFORM_ACCOUNTS_OVERVIEW.md): plain-language map of which account/service does what and where costs are likely to appear
- [`PLUG_AND_PLAY_DEPLOY_CHECKLIST.md`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/PLUG_AND_PLAY_DEPLOY_CHECKLIST.md): buyer/self-host install checklist for the packaged stack
- [`STRIPE_LIVE_SWITCH_CHECKLIST.md`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/STRIPE_LIVE_SWITCH_CHECKLIST.md): exact checklist for moving billing from Stripe test mode to live mode

## Local Development

### 1. Start backend

From the project root:

```powershell
.\backend\venv\Scripts\Activate.ps1
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Notes:

- If VS Code or the terminal closes, activate the backend venv again.
- `--reload` is intentionally avoided because it caused issues on this Windows setup.

### 2. Start frontend

Open a second terminal from the project root:

```powershell
cd frontend
python -m http.server 5500
```

### 3. Open local app

- Frontend: `http://127.0.0.1:5500`
- Backend docs: `http://127.0.0.1:8000/docs`

## Standard Local Test Checklist

Run this checklist before commit or deploy:

1. Frontend opens on `127.0.0.1:5500`
2. Backend docs open on `127.0.0.1:8000/docs`
3. Toy mode test works with:
   - `robot`
   - `car`
4. Viewer still handles:
   - image preview
   - GLB preview
   - STL preview
5. Print Mode works:
   - `Generate Toy`
   - `Fix for Print`
   - `Apply Transform`
   - `Download`

## Reference QA Models

Keep test mode intentionally small and stable.

Current local reference models:

- [`frontend/models/Robot.glb`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/frontend/models/Robot.glb)
- [`frontend/models/f1car.glb`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/frontend/models/f1car.glb)

These two models are the default QA baseline for future changes.

## Git Workflow

Before pushing:

```powershell
git status
```

If everything looks correct:

```powershell
git add <files>
git commit -m "Clear message here"
git push origin main
```

## Deploy Workflow

### Frontend

- Vercel deploys from the GitHub repository
- after `git push origin main`, verify the new deployment in Vercel
- hard refresh if the browser still shows old frontend behavior

### Backend

- Railway deploys from the GitHub repository
- after `git push origin main`, confirm:
  - build logs complete
  - deploy logs show application startup complete

## Plug-And-Play Direction

Pluto3D is now being structured in two compatible modes:

- flagship platform on your own domain
- self-host / buyer install version with config-driven setup

The install surface should stay simple:

- edit `frontend/app-config.js`
- edit `backend/.env`
- connect domain, auth, and billing

Reference:

- [`SELF_HOST_QUICKSTART.md`](/c:/Users/Lenovo/Desktop/photo-to-3d-app/SELF_HOST_QUICKSTART.md)

## Team Rules

- Keep code comments in English
- Keep user-facing collaboration in Albanian
- Extend working flows without breaking them
- Prefer modular frontend files instead of adding more logic into `index.html`
- Use local reference models for QA before introducing new features
- Remove heavy or unused infrastructure instead of carrying dead weight

## Next Technical Priorities

- finish frontend modular cleanup
- define a stable local/dev/deploy routine
- add simple editing tools that create real customer value
- add premium API-powered generation where local compute is not practical
