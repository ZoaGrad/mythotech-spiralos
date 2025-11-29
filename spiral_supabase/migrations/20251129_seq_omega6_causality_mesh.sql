-- Sequence Ω.6-A: Causality Mesh
-- Description: Adds causal linking between audit events, correlated with Phase-Lock and Temporal state.

-- 1. Table: causal_event_links
create table if not exists causal_event_links (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  created_by text not null default 'system',

  source_event_id uuid not null
    references audit_surface_events(id) on delete cascade,
  target_event_id uuid not null
    references audit_surface_events(id) on delete cascade,

  cause_type text not null,                -- e.g. 'guardian_response', 'temporal_correction'
  weight numeric(10,4) not null default 1, -- causal strength, default 1.0
  notes jsonb not null default '{}'::jsonb,

  phase_lock_hash text,                   -- snapshot from fn_verify_phase_lock()
  temporal_anchor_id uuid                 -- optional link to temporal_drift_log.id if available
);

alter table causal_event_links enable row level security;

-- RLS Policies
create policy "Enable read access for all users"
on causal_event_links for select
using (true);

create policy "Enable insert for service_role only"
on causal_event_links for insert
with check (auth.role() = 'service_role');

-- 2. Function: fn_link_events
create or replace function fn_link_events(
  p_source_event_id uuid,
  p_target_event_id uuid,
  p_cause_type text,
  p_weight numeric default 1.0,
  p_notes jsonb default '{}'::jsonb
) returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
  v_phase_lock_hash text;
  v_temporal_anchor_id uuid;
  v_link_id uuid;
begin
  -- Try to capture current phase-lock hash (if fn_verify_phase_lock exists)
  begin
    select hash into v_phase_lock_hash
    from fn_verify_phase_lock();
  exception when others then
    v_phase_lock_hash := null;
  end;

  -- Try to capture latest temporal anchor (if temporal_drift_log exists)
  begin
    select id into v_temporal_anchor_id
    from temporal_drift_log
    where is_anchor = true
    order by created_at desc
    limit 1;
  exception when others then
    v_temporal_anchor_id := null;
  end;

  insert into causal_event_links (
    source_event_id,
    target_event_id,
    cause_type,
    weight,
    notes,
    phase_lock_hash,
    temporal_anchor_id
  ) values (
    p_source_event_id,
    p_target_event_id,
    p_cause_type,
    p_weight,
    coalesce(p_notes, '{}'::jsonb),
    v_phase_lock_hash,
    v_temporal_anchor_id
  )
  returning id into v_link_id;

  return v_link_id;
end;
$$;

-- Grant execute permissions
grant usage on schema public to anon, authenticated, service_role;
grant execute on function fn_link_events(uuid, uuid, text, numeric, jsonb)
  to anon, authenticated, service_role;

-- 3. View: view_causal_links
create or replace view view_causal_links as
select
  l.id,
  l.created_at,
  l.created_by,
  l.cause_type,
  l.weight,
  l.notes,
  l.phase_lock_hash,
  l.temporal_anchor_id,

  l.source_event_id,
  s.created_at as source_created_at,
  s.event_type as source_event_type,
  s.component as source_component,
  s.payload   as source_payload,

  l.target_event_id,
  t.created_at as target_created_at,
  t.event_type as target_event_type,
  t.component as target_component,
  t.payload   as target_payload

from causal_event_links l
join audit_surface_events s on s.id = l.source_event_id
join audit_surface_events t on t.id = l.target_event_id
order by l.created_at desc
limit 500;

-- Grant select permissions
grant select on view_causal_links to anon, authenticated, service_role;
