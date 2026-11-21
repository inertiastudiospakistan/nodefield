-- Nodefield — Supabase schema (waitlist + jobs)
-- Status: NOT YET APPLIED. No Supabase project exists yet.
-- Run in the Supabase SQL editor after the founder creates the project.
-- See infra/DEPLOY.md for setup steps, including Row Level Security.

-- GPU contributor registrations (waitlist)
create table if not exists providers (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  name text not null,
  email text not null unique,
  country text,
  gpu_manufacturer text,          -- NVIDIA / AMD / other
  gpu_model text,
  gpu_vram_gb integer,
  system_ram_gb integer,
  operating_system text,          -- Windows / Linux / macOS
  internet_connection text,       -- e.g. fibre 100Mbps, cable, etc.
  available_hours text,           -- e.g. nights, weekends, 24/7
  beta_interest boolean not null default false,
  status text not null default 'waitlisted'  -- waitlisted / invited / active / rejected
);

-- Developer registrations (early access)
create table if not exists developers (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  email text not null unique,
  intended_application text,
  expected_monthly_tokens bigint,
  preferred_models text[],        -- e.g. {Qwen3-8B, Mistral-7B}
  desired_api_features text,
  status text not null default 'waitlisted'  -- waitlisted / invited / active / rejected
);

-- API keys: HASHED ONLY, never plaintext.
-- key_hash = sha256(secret_prefix || plaintext_key); plaintext is shown once at issuance.
create table if not exists api_keys (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  developer_id uuid not null references developers (id) on delete cascade,
  key_prefix text not null,        -- first 8 chars, for identification (e.g. 'nf_live_')
  key_hash text not null unique,
  name text,
  rate_limit_rpm integer not null default 60,
  revoked_at timestamptz,
  last_used_at timestamptz
);

-- Inference jobs (scheduler)
create table if not exists jobs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  developer_id uuid references developers (id) on delete set null,
  api_key_id uuid references api_keys (id) on delete set null,
  model text not null,
  status text not null default 'pending',  -- pending / assigned / running / completed / failed / cancelled
  worker_id text,
  input_tokens integer,
  output_tokens integer,
  latency_ms integer,
  error text,
  completed_at timestamptz
);

create index if not exists jobs_status_idx on jobs (status);
create index if not exists jobs_developer_idx on jobs (developer_id);
create index if not exists api_keys_developer_idx on api_keys (developer_id);

-- NOTE: enable Row Level Security on all tables after creating them and
-- write policies before the API talks to this database. No policies are
-- included here because the auth model (service role vs. authenticated
-- admin) is decided at Supabase setup time.
