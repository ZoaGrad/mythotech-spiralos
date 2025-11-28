-- 20251128_seq_omega3_1_fix_digest.sql
-- Ω.3.1 — Fix pgcrypto digest() usage and stabilize Phase-Lock

-- Ensure pgcrypto exists (no-op if already there)
create extension if not exists pgcrypto with schema public;

create or replace function public.fn_verify_phase_lock(
  p_expected_root_hash text default null,
  p_label text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_status           jsonb;
  v_actual_root_hash text;
  v_effective_label  text := coalesce(p_label, 'omega3-initial');
  v_now              timestamptz := now();
  v_existing_root    text;
  v_is_match         boolean;
  v_mode             text;
begin
  -- 1) Pull the current canonical system status snapshot
  select row_to_json(vs.*)::jsonb
  into v_status
  from view_system_status as vs
  limit 1;

  if v_status is null then
    raise exception 'view_system_status returned no rows'
      using errcode = 'P0001';
  end if;

  -- 2) Compute the actual root hash from the status JSON
  --    IMPORTANT: cast to bytea + cast hash type to text
  v_actual_root_hash :=
    encode(
      digest(v_status::text::bytea, 'sha256'::text),
      'hex'
    );

  -- 3) Load any existing active checkpoint for this label (if any)
  select plc.root_hash
  into v_existing_root
  from phase_lock_checkpoints plc
  where plc.label = v_effective_label
    and plc.is_active = true
  order by plc.created_at desc
  limit 1;

  if v_existing_root is null or p_expected_root_hash is null then
    ----------------------------------------------------------------
    -- BASELINE MODE
    -- No existing checkpoint (or caller passes NULL) → create baseline
    ----------------------------------------------------------------
    v_mode := 'baseline';

    insert into phase_lock_checkpoints (
      id,
      created_at,
      created_by,
      root_hash,
      label,
      status,
      is_active
    )
    values (
      gen_random_uuid(),
      v_now,
      'fn_verify_phase_lock',
      v_actual_root_hash,
      v_effective_label,
      jsonb_build_object(
        'mode',            v_mode,
        'status_snapshot', v_status
      ),
      true
    );

    insert into constitutional_verification_log (
      id,
      created_at,
      root_hash,
      label,
      mode,
      details
    )
    values (
      gen_random_uuid(),
      v_now,
      v_actual_root_hash,
      v_effective_label,
      v_mode,
      jsonb_build_object(
        'message', 'Baseline Phase-Lock established.',
        'status_snapshot', v_status
      )
    );

    return jsonb_build_object(
      'ok', true,
      'mode', v_mode,
      'root_hash', v_actual_root_hash,
      'label', v_effective_label,
      'created_at', v_now,
      'baseline_created', true
    );
  else
    ----------------------------------------------------------------
    -- VERIFICATION MODE
    -- Existing checkpoint + expected hash → verify integrity
    ----------------------------------------------------------------
    v_mode := 'verify';

    v_is_match := (v_actual_root_hash = coalesce(p_expected_root_hash, v_existing_root));

    insert into constitutional_verification_log (
      id,
      created_at,
      root_hash,
      label,
      mode,
      details
    )
    values (
      gen_random_uuid(),
      v_now,
      v_actual_root_hash,
      v_effective_label,
      v_mode,
      jsonb_build_object(
        'expected_root_hash', coalesce(p_expected_root_hash, v_existing_root),
        'actual_root_hash',   v_actual_root_hash,
        'hash_match',         v_is_match,
        'status_snapshot',    v_status
      )
    );

    return jsonb_build_object(
      'ok',           v_is_match,
      'mode',         v_mode,
      'root_hash',    v_actual_root_hash,
      'label',        v_effective_label,
      'created_at',   v_now,
      'hash_match',   v_is_match
    );
  end if;
end;
$$;
