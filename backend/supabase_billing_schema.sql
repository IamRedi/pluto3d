create extension if not exists pgcrypto;

create table if not exists public.profiles (
  id uuid primary key,
  email text unique,
  display_name text,
  plan text not null default 'free',
  stripe_customer_id text unique,
  last_login_at timestamptz,
  last_seen_at timestamptz,
  total_active_seconds bigint not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.profiles
  add column if not exists last_login_at timestamptz;

alter table public.profiles
  add column if not exists last_seen_at timestamptz;

alter table public.profiles
  add column if not exists total_active_seconds bigint not null default 0;

create table if not exists public.subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  email text,
  stripe_customer_id text not null,
  stripe_subscription_id text not null unique,
  status text not null,
  plan text not null default 'premium',
  current_period_end timestamptz,
  source_event text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.billing_webhook_events (
  event_id text primary key,
  event_type text,
  created_at timestamptz not null default now()
);

create table if not exists public.usage_buckets (
  id uuid primary key default gen_random_uuid(),
  subject_key text not null,
  subject_type text not null,
  user_id uuid references public.profiles(id) on delete cascade,
  bucket_type text not null,
  feature_key text not null,
  period text,
  window_key text not null default 'lifetime',
  count integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(subject_key, bucket_type, feature_key, window_key)
);

create index if not exists subscriptions_user_id_idx
  on public.subscriptions(user_id);

create index if not exists subscriptions_customer_id_idx
  on public.subscriptions(stripe_customer_id);

create index if not exists usage_buckets_subject_key_idx
  on public.usage_buckets(subject_key);

create index if not exists usage_buckets_user_id_idx
  on public.usage_buckets(user_id);

create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists profiles_touch_updated_at on public.profiles;
create trigger profiles_touch_updated_at
before update on public.profiles
for each row
execute function public.touch_updated_at();

drop trigger if exists subscriptions_touch_updated_at on public.subscriptions;
create trigger subscriptions_touch_updated_at
before update on public.subscriptions
for each row
execute function public.touch_updated_at();

drop trigger if exists usage_buckets_touch_updated_at on public.usage_buckets;
create trigger usage_buckets_touch_updated_at
before update on public.usage_buckets
for each row
execute function public.touch_updated_at();

alter table public.profiles enable row level security;
alter table public.subscriptions enable row level security;
alter table public.billing_webhook_events enable row level security;
alter table public.usage_buckets enable row level security;

drop policy if exists "Users can read own profile" on public.profiles;
create policy "Users can read own profile"
on public.profiles
for select
to authenticated
using (auth.uid() = id);

drop policy if exists "Users can read own subscriptions" on public.subscriptions;
create policy "Users can read own subscriptions"
on public.subscriptions
for select
to authenticated
using (auth.uid() = user_id);

comment on table public.profiles is
'Pluto3D account profile and current plan snapshot.';

comment on table public.subscriptions is
'Stripe-backed subscription records used for premium access resolution.';

comment on table public.billing_webhook_events is
'Processed Stripe webhook events used for idempotency and replay safety.';

comment on table public.usage_buckets is
'Server-side usage counters and credits for guest, free, and premium quota enforcement.';
