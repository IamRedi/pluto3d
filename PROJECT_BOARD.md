# Pluto3D Studio Project Board

This file is the working memory for the project.
Use it to keep product direction, active tasks, decisions, and next steps in one place.

## Product Summary

Pluto3D Studio is a web app for non-expert users that:

- generates images from prompts
- converts images into SVG
- prepares 3D models for preview and 3D printing
- offers a toy-style editing workflow

Current hosting:

- Frontend: Vercel
- Backend: Railway

Core product direction:

- keep the app simple and premium-looking
- use APIs for expensive generation tasks
- keep editing, cleanup, print-fix, and presentation as Pluto3D's real value

## Current Architecture

### Frontend

- Main UI shell: `frontend/index.html`
- Viewer logic: `frontend/viewer.js`
- Print actions: `frontend/print-mode.js`
- Toy mode logic: `frontend/toy-mode.js`
- Toy Studio controls: `frontend/toy-studio.js`
- Runtime API config: `frontend/runtime-config.js`
- Test models config: `frontend/test-models.js`

### Backend

- FastAPI app entry: `backend/app/main.py`
- AI image route: `backend/app/routes/ai_photo.py`
- SVG route: `backend/app/routes/svg.py`
- Print fix route: `backend/app/routes/print_fix.py`
- Mesh cleanup service: `backend/app/services/mesh_repair.py`

## Stable Product Decisions

- Keep only two local test models:
  - `Robot.glb`
  - `f1car.glb`
- Do not depend on TripoSR in the main product flow
- Toy mode is a lightweight test/demo path
- Real 3D generation can later come from an external API
- Print Fix is a core premium-value feature
- Viewer stays unified for image, SVG, GLB, and STL
- Toy Studio edits should be visible in the main viewer, not inside a second preview viewer

## Current Working Features

- AI image generation
- SVG conversion
- Local toy generation with test models
- 3D free test flow using test models
- Print Fix pipeline:
  - GLB input
  - topology cleanup
  - STL output
- Toy Studio floating control panel
- Viewer modes:
  - Wire
  - Print

## Current UI Direction

- App-style desktop layout
- Fixed viewer panel on the right
- Independent scrolling middle panel
- Mobile layout stacks vertically
- Toy Studio is a compact floating glass panel over the middle column
- Main viewer remains the only live preview surface

## Near-Term Roadmap

### Phase 1: Stabilize The Core Studio

- refine Toy Studio controls
- improve presets and styling behavior
- add part-aware editing when models have multiple meshes
- keep viewer controls minimal and elegant

### Phase 2: Product Platform Layer

- add login and signup
- add Google login
- define user plans:
  - Guest
  - Logged-in Free
  - Premium
- lock premium-only features in frontend and backend

### Phase 3: Monetization Layer

- Stripe subscription flow
- premium activation
- free plan limits
- premium plan with no ads and better access

### Phase 4: Ad / Sponsor Layer

- show sponsor or upgrade panel during generation
- keep ad experience elegant, not noisy
- no ads for premium users

## Suggested Plan Tiers

### Guest

- basic app access
- toy test mode
- SVG tools
- limited AI image generation
- no premium 3D generation

### Logged-in Free

- more generous limits
- toy studio
- print fix
- sponsor or ad panel during generation

### Premium

- premium 3D generation
- no ads
- faster or priority processing
- higher usage limits

## Serious-App Basics To Add

- top navbar
- pricing section
- account section
- support/contact
- privacy policy
- terms of service
- footer
- sponsor/partner area
- upgrade prompts
- polished loading states
- empty states
- beta messaging for early testers

## Current Active Tasks

1. Keep Toy Studio small, stable, and useful
2. Improve styling presets and controls
3. Prepare the app structure for auth and plans
4. Add serious product sections like pricing, footer, and legal pages

## Next Recommended Tasks

1. Improve Toy Studio presets and part-aware editing
2. Add a `Night Mode` toggle
3. Add a serious landing/product layer:
   - hero
   - pricing
   - sponsor strip
   - footer
4. Add auth system planning and scaffolding

## Decisions Log

### 2026-03-23

- Removed heavy dependence on large local model sets
- Reduced toy test assets to two models
- Split key frontend logic into modular files
- Added local `.env` loading for backend tokens
- Fixed AI token handling
- Built compact Toy Studio panel and kept preview in the main viewer
- Decided to move toward a real product platform with auth, plans, premium access, and sponsor/ad loading states

## How To Use This File

Whenever we start a new work session, review:

- Product Summary
- Stable Product Decisions
- Current Active Tasks
- Next Recommended Tasks

Whenever a major decision changes, add it to:

- Decisions Log

Whenever a task is completed, move the board forward instead of keeping old temporary notes in chat.
