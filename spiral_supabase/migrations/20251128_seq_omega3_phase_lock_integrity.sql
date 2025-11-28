-- Ω.3 — Phase-Lock Integrity Engine
-- Migration: 20251128_seq_omega3_phase_lock_integrity.sql

-- 1. Ensure pgcrypto is available for digest()
create extension if not exists pgcrypto;

-- 2. Phase-lock checkpoints table
create table if not exists phase_lock_checkpoints (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  created_by text not null default 'system',
  root_hash text not null,
  label text not null default 'baseline',
  status jsonb not null,
  is_active boolean not null default true
);

-- 3. Constitutional verification log
create table if not exists constitutional_verification_log (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  check_type text not null, -- 'baseline-or-auto' | 'explicit'
  expected_root_hash text,
  actual_root_hash text not null,
  passed boolean not null,
  checkpoint_id uuid references phase_lock_checkpoints(id),
  details jsonb not null default '{}'::jsonb
);

-- 4. RLS configuration: service_role-only for both tables
alter table phase_lock_checkpoints enable row level security;
alter table constitutional_verification_log enable row level security;

-- Drop existing policies if re-running migration
do $$
begin
  if exists (
    select 1 from pg_policies
    where schemaname = 'public' and tablename = 'phase_lock_checkpoints'
  ) then
    drop policy if exists "phase_lock_checkpoints_service_role_all" on phase_lock_checkpoints;
  end if;

  if exists (
    select 1 from pg_policies
    where schemaname = 'public' and tablename = 'constitutional_verification_log'
  ) then
    drop policy if exists "constitutional_verification_log_service_role_all" on constitutional_verification_log;
  end if;
end$$;

-- Service role can do everything; others: nothing
create policy "phase_lock_checkpoints_service_role_all"
  on phase_lock_checkpoints
  for all
  to public
  using (jwt_role() = 'service_role')
  with check (jwt_role() = 'service_role');

create policy "constitutional_verification_log_service_role_all"
  on constitutional_verification_log
  for all
  to public
  using (jwt_role() = 'service_role')
  with check (jwt_role() = 'service_role');

-- 5. Phase-lock verification function
create or replace function fn_verify_phase_lock(
  p_expected_root_hash text default null,
  p_label text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_status jsonb;
  v_actual_root_hash text;
  v_expected_root_hash text;
  v_checkpoint_id uuid;
  v_log_id uuid;
  v_passed boolean;
begin
  -- Pull latest system status from the consolidated view
  select row_to_json(s)::jsonb
  into v_status
  from view_system_status s
  limit 1;

  if v_status is null then
    raise exception 'view_system_status returned no rows; cannot verify phase lock';
  end if;

  -- Compute root hash over full JSON snapshot
  -- Use public.digest to ensure we find the function, and cast inputs explicitly
  v_actual_root_hash := encode(public.digest(v_status::text, 'sha256'), 'hex');

  -- Resolve expected root hash
  if p_expected_root_hash is not null then
    v_expected_root_hash := p_expected_root_hash;
  else
    select plc.root_hash
    into v_expected_root_hash
    from phase_lock_checkpoints plc
    where plc.is_active
    order by plc.created_at desc
    limit 1;
  end if;

  -- Determine pass/fail
  v_passed := (v_expected_root_hash is null) or (v_expected_root_hash = v_actual_root_hash);

  -- Bootstrap: if no expected hash, create initial baseline checkpoint
  if v_expected_root_hash is null then
    insert into phase_lock_checkpoints (
      created_at, created_by, root_hash, label, status, is_active
    )
    values (
      now(),
      'system',
      v_actual_root_hash,
      coalesce(p_label, 'initial-baseline'),
      v_status,
      true
    )
    returning id, root_hash into v_checkpoint_id, v_expected_root_hash;
  else
    -- Try to find a checkpoint for the expected hash
    select plc.id
    into v_checkpoint_id
    from phase_lock_checkpoints plc
    where plc.root_hash = v_expected_root_hash
    order by plc.created_at desc
    limit 1;
  end if;

  -- Write verification log
  insert into constitutional_verification_log (
    created_at,
    check_type,
    expected_root_hash,
    actual_root_hash,
    passed,
    checkpoint_id,
    details
  )
  values (
    now(),
    case when p_expected_root_hash is null then 'baseline-or-auto' else 'explicit' end,
    v_expected_root_hash,
    v_actual_root_hash,
    v_passed,
    v_checkpoint_id,
    jsonb_build_object(
      'status_snapshot', v_status
    )
  )
  returning id into v_log_id;

  -- Return a structured result
  return jsonb_build_object(
    'passed', v_passed,
    'expected_root_hash', v_expected_root_hash,
    'actual_root_hash', v_actual_root_hash,
    'checkpoint_id', v_checkpoint_id,
    'log_id', v_log_id,
    'status_snapshot', v_status
  );
end;
$$;

-- 6. Phase integrity view (latest verification)
create or replace view view_phase_integrity as
select
  l.id as last_log_id,
  l.created_at as last_check_at,
  l.check_type,
  l.passed,
  l.expected_root_hash,
  l.actual_root_hash,
  l.checkpoint_id,
  c.created_at as checkpoint_created_at,
  c.label as checkpoint_label,
  c.root_hash as checkpoint_root_hash
from constitutional_verification_log l
left join phase_lock_checkpoints c on c.id = l.checkpoint_id
order by l.created_at desc
limit 1;

grant select on view_phase_integrity to anon, authenticated, service_role;
