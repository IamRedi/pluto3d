# Pluto3D AI Rules

This file defines the working rules for AI-assisted changes in Pluto3D.
Follow these rules every time.

## Communication Rules

- communicate with the user in Albanian
- write code, comments, documentation, file names, and system structure in English
- explain what will change and why before any meaningful edit
- do not do important work without making that change path clear first
- call out whether a meaningful change belongs to frozen `v1` or active `v1.1`
- ask the user only for decisions with real product, workflow, or risk impact

## Safety Rules

- do not break working features
- make minimal changes only
- do not reopen stable flows without a clear reason
- do not touch frozen production `v1` for normal feature work
- avoid destructive git or filesystem actions unless explicitly requested

## Branch And Version Rules

- treat `main` as frozen production for `v1`
- treat `release/v1-launch` as the frozen release backup
- do normal implementation work on `develop` for `v1.1`
- use hotfix logic only for real production bugs

## Documentation Rules

- always update `CHANGELOG.md` after every meaningful change
- always update `CURRENT_STATE.md` after every meaningful change
- keep important notes in the repo, not only in chat
- treat the canonical documentation set as the default workflow system for the project
- use the canonical docs first:
  - `SYSTEM_MASTER.md`
  - `CURRENT_STATE.md`
  - `CHANGELOG.md`
  - `INSTALL_GUIDE.md`
  - `PROJECT_MAP.md`
  - `AI_RULES.md`
- use legacy docs only as supporting source material during the migration period

## Technical Rules

- preserve already working `3D Generator`, `SVG`, `Relief`, auth, and billing behavior
- prefer small targeted edits over broad refactors
- test the touched surface before moving on
- keep frontend public configuration in `frontend/app-config.js`
- keep backend private configuration in `backend/.env`
- keep deploy/install behavior config-driven where possible

## Product Rules

- keep the UI premium, clean, and client-facing
- keep the current focus on:
  - buttons
  - hierarchy
  - spacing
  - visual clarity
- do not mix production adaptation work into normal local UI polish unless the user explicitly asks for it
- keep heavy backend `print-fix` and scaling work paused unless stability requires deeper work
- prefer browser-side export paths when they stay stable and safe

## Licensing And Asset Rules

- update `COMMERCIAL_LICENSE_AUDIT.md` when dependencies, assets, or third-party services change in a meaningful way
- update `OWNED_MODEL_ASSETS.md` when owned model assets change
- do not copy GPL code into the project
- keep secrets and private credentials out of repo documentation

## Default Working Principle

If a change can be done safely in a smaller way, do the smaller way.
If a note can prevent future confusion, write it in the repo.
