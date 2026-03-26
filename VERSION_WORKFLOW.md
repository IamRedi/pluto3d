# Pluto3D Version Workflow

This file explains how Pluto3D is being handled after the first public launch.
Use it whenever the current branch, release state, or hotfix flow is unclear.

## Current Version Split

### Frozen Production

- product version: `v1`
- live domain: `https://www.pluto-3d.com`
- protected branch baseline: `main`
- frozen release branch: `release/v1-launch`
- frozen release tag: `v1-launch-2026-03-26`

Meaning:

- `v1` is the first launched version
- it should stay stable
- it should not receive normal feature work
- only targeted production bug fixes should touch this line

### Active Development

- working version: `v1.1`
- active development branch: `develop`

Meaning:

- all new improvements should start from `develop`
- `v1.1` is where polishing, optimization, and future work continue
- documentation for the active work should be updated here as work moves forward

## Branch Intent

- `main`
  - frozen production baseline for `v1`
- `release/v1-launch`
  - backup release reference for the first launched version
- `develop`
  - active branch for `v1.1`
- `feature/...`
  - short-lived branches for individual `v1.1` tasks
- `hotfix/...`
  - short-lived branches for urgent fixes that must go to production first

## Daily Working Rule

When working normally:

1. start from `develop`
2. discuss the task first
3. make the change for `v1.1`
4. test it
5. keep notes updated in project docs

When production has a real bug:

1. branch from `main`
2. create `hotfix/...`
3. fix only the production bug
4. test the fix
5. merge or push that fix to production
6. bring the same fix back into `develop`

This keeps `v1` stable without losing the fix in `v1.1`.

## Production Change Policy

Allowed on `v1`:

- real bug fixes
- broken auth or billing fixes
- broken API or deploy fixes
- small safe UI regressions that affect live users

Not allowed on `v1`:

- redesigns
- broad refactors
- experiments
- unfinished product ideas
- normal `v1.1` improvements

## Source Of Truth

Use these files in this order when the project state is unclear:

1. `VERSION_WORKFLOW.md`
2. `PROJECT_BOARD.md`
3. `AUTH_IMPLEMENTATION_PLAN.md`
4. `SUPABASE_SETUP_CHECKLIST.md`

## Current Working Notes

- the old `dev` branch exists, but it is not the active `v1.1` branch
- active development now continues on `develop`
- production checks before the split confirmed:
  - live `AI Photo` works again after the Railway `REPLICATE_API_TOKEN` refresh
  - live `Generate 3D PRO` had already returned a valid Meshy task id before the split

## Communication Rule

Before any meaningful code change:

- explain what is about to happen
- explain why it is being done
- call out if the change is for `v1` or `v1.1`
- ask before any important product or workflow decision

## User-Owned Actions

These still belong to the user when needed:

- dashboard updates in Vercel
- dashboard updates in Railway
- dashboard updates in Supabase
- dashboard updates in Stripe
- secret key changes
- final production-domain decisions

## Codex-Owned Actions

These can be handled inside the repo:

- code changes
- documentation updates
- branch setup guidance
- version tracking notes
- hotfix preparation
- `v1.1` implementation work
