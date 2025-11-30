-- Enable extensions
create extension if not exists "pgcrypto";

-- Witness registry
create table if not exists witnesses (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  public_key text not null unique,
  reputation_score numeric default 0,
  created_at timestamptz not null default now()
);

-- Events and ache log
create table if not exists events (
  id uuid primary key default gen_random_uuid(),
  type text not null,
  severity text not null check (severity in ('low','medium','high','critical')),
  description text,
  metadata jsonb,
  impact_score numeric default 0,
  occurred_at timestamptz default now(),
  created_at timestamptz not null default now(),
  witnessed_by uuid references witnesses(id) on delete set null
);
create index if not exists events_type_idx on events(type);
create index if not exists events_severity_idx on events(severity);
create index if not exists events_occurred_at_idx on events(occurred_at);

-- Proposals
create table if not exists proposals (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  body text not null,
  proposer text,
  category text,
  impact_radius numeric,
  amount numeric,
  status text not null default 'pending' check (status in ('pending','approved','flagged','rejected','in_review')),
  risk_score numeric,
  risk_level text check (risk_level in ('low','medium','high')),
  ssd_decision text check (ssd_decision in ('approve','reject','needs_human_review')),
  findings jsonb default '[]'::jsonb,
  created_at timestamptz not null default now(),
  reviewed_at timestamptz
);
create index if not exists proposals_status_idx on proposals(status);
create index if not exists proposals_created_idx on proposals(created_at);

-- Proposal events (audit trail)
create table if not exists proposal_events (
  id bigserial primary key,
  proposal_id uuid not null references proposals(id) on delete cascade,
  event_type text not null,
  payload jsonb not null,
  created_at timestamptz not null default now()
);
create index if not exists proposal_events_proposal_idx on proposal_events(proposal_id);
create index if not exists proposal_events_created_idx on proposal_events(created_at);

-- ScarIndex oracle state (singleton row)
create table if not exists scar_index_state (
  id integer primary key default 1,
  score numeric not null,
  trend text not null check (trend in ('up','down','flat')),
  sample_size integer not null default 0,
  window_hours integer not null default 168,
  updated_at timestamptz not null default now()
);

-- SSD Guard error sink (optional but recommended)
create table if not exists ssd_errors (
  id bigserial primary key,
  proposal_id uuid references proposals(id) on delete set null,
  error_message text not null,
  stacktrace text,
  context jsonb,
  created_at timestamptz not null default now()
);
create index if not exists ssd_errors_proposal_idx on ssd_errors(proposal_id);
create index if not exists ssd_errors_created_idx on ssd_errors(created_at);
