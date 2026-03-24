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

Suggested project name:

- `pluto3d-main`

### 2. Collect Keys

From the Supabase project settings, collect:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

Where to find them:

- `Project Settings -> API`

### 3. Enable Auth Providers

In Supabase Auth settings:

- enable Email provider
- enable Google provider

Where to do it:

- `Authentication -> Providers`

### 4. Configure Google Login

For Google auth, the user will need:

- Google Cloud project
- OAuth consent screen
- Google OAuth client ID
- Google OAuth client secret

Then add the callback URL from Supabase into Google Cloud.

Where to get the callback URL:

- `Authentication -> Providers -> Google`

What the user should do in Google Cloud:

1. create or choose a Google Cloud project
2. configure OAuth consent screen
3. create a Web application OAuth client
4. paste the Supabase callback URL into `Authorized redirect URIs`
5. copy the Google client ID and secret back into Supabase

Keep this simple:

- one Google project
- one OAuth client
- one Supabase project
- no extra providers yet

### 5. Prepare Frontend Auth Config

Because the frontend is currently a static Vanilla JS app, the first practical setup should use a small config file instead of build-time env injection.

Later the frontend will need:

- `supabaseUrl`
- `supabasePublishableKey`

Reference file:

- `frontend/auth-config.example.js`

When the time comes, copy it to:

- `frontend/auth-config.js`

### 6. Prepare Backend Env

Later the backend will need:

- `SUPABASE_SERVICE_ROLE_KEY`

Reference file:

- `backend/.env.example`

## Exact Values To Bring Back

When the dashboard setup is done, the user should bring back only these values:

### Frontend

- `supabaseUrl`
- `supabasePublishableKey`

### Backend

- `SUPABASE_SERVICE_ROLE_KEY`

### Optional Later

- Google login confirmed as enabled
- screenshot of the Supabase API page if unsure

## What Codex Needs From The User

After setup, the user only needs to say:

- Supabase project created
- Google provider enabled
- keys are ready

Then Codex can continue with the real auth client integration.

## What Codex Will Do After Setup

Once the user completes the checklist above, Codex will:

1. add a real frontend auth client
2. connect login and logout UI
3. read live session state
4. replace preview plan state with real session state
5. prepare backend plan checks

Current codebase note:

- the project now includes `frontend/auth-client.js`
- this file already checks whether `frontend/auth-config.js` exists
- `frontend/auth-config.js` should now use `supabaseUrl` + `supabasePublishableKey`
- after the keys are ready, the next coding step is to replace the placeholder auth calls with the real Supabase client logic

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
- Keep Stripe out of scope until Google login and session state are stable
