-- Sequence Ω.6-A.1: Patch Link Events
-- Description: Fixes temporal anchor detection in fn_link_events by checking drift_delta_ms IS NULL instead of non-existent is_anchor column.

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
  -- Anchor is identified by drift_delta_ms IS NULL
  begin
    select id into v_temporal_anchor_id
    from temporal_drift_log
    where drift_delta_ms is null
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
