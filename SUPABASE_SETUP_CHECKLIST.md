# Pluto3D Supabase Setup Checklist

This file is the practical setup guide for the first real auth milestone.

Use it when moving from preview auth to real account handling.

## Goal

Set up Supabase so Pluto3D can support:

- Google login
- email signup
- real user sessions
- real free vs premium account state later

## What The User Needs To Do

These steps are owned by the user because they require dashboard access.

### 1. Create Supabase Project

- Create a new Supabase project
- Choose a project name for Pluto3D
- Save the database password in a secure place

### 2. Collect Keys

From the Supabase project settings, collect:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

### 3. Enable Auth Providers

In Supabase Auth settings:

- enable Email provider
- enable Google provider

### 4. Configure Google Login

For Google auth, the user will need:

- Google Cloud project
- OAuth consent screen
- Google OAuth client ID
- Google OAuth client secret

Then add the callback URL from Supabase into Google Cloud.

### 5. Prepare Frontend Env

Later the frontend will need:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

### 6. Prepare Backend Env

Later the backend will need:

- `SUPABASE_SERVICE_ROLE_KEY`

## What Codex Will Do After Setup

Once the user completes the checklist above, Codex will:

1. add a real frontend auth client
2. connect login and logout UI
3. read live session state
4. replace preview plan state with real session state
5. prepare backend plan checks

## First Real Auth Milestone

The first auth milestone is complete when:

- Google login works
- logout works
- the header shows the real account state
- the profile page shows the real user identity
- preview login buttons are no longer needed

## Notes

- Keep preview auth logic until real Supabase auth is fully connected
- Do not remove preview mode too early
- Real billing and premium activation come after auth is stable
