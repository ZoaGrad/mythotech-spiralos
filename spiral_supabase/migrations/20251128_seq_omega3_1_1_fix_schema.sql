-- Ω.3.1.1 - Fix schema mismatch in fn_verify_phase_lock()

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
  v_status jsonb;
  v_actual_root_hash text;
  v_effective_label text := coalesce(p_label, 'omega3-initial');
  v_now timestamptz := now();
  v_existing_root text;
  v_is_match boolean;
  v_mode text;
  v_checkpoint_id uuid;
begin
  -- 1) Pull current system status
  select row_to_json(vs.*)::jsonb
  into v_status
  from view_system_status as vs
  limit 1;

  if v_status is null then
    raise exception 'view_system_status returned no rows'
      using errcode = 'P0001';
  end if;

  -- 2) Compute actual root hash (FIXED: correct type casting)
  v_actual_root_hash :=
    encode(
      digest(v_status::text::bytea, 'sha256'::text),
      'hex'
    );

  -- 3) Load existing checkpoint for this label
  select plc.root_hash
  into v_existing_root
  from phase_lock_checkpoints plc
  where plc.label = v_effective_label
    and plc.is_active = true
  order by plc.created_at desc
  limit 1;

  if v_existing_root is null or p_expected_root_hash is null then
    -- BASELINE MODE: No existing checkpoint, create initial baseline
    v_mode := 'baseline';
    v_is_match := true; -- Always passes on first run

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
        'mode', v_mode,
        'status_snapshot', v_status
      ),
      true
    )
    returning id into v_checkpoint_id;

    -- Insert verification log (FIXED: use correct schema)
    insert into constitutional_verification_log (
      id,
      created_at,
      check_type,
      expected_root_hash,
      actual_root_hash,
      passed,
      checkpoint_id,
      details
    )
    values (
      gen_random_uuid(),
      v_now,
      'baseline-or-auto',
      v_actual_root_hash,  -- Expected = actual for baseline
      v_actual_root_hash,
      true,
      v_checkpoint_id,
      jsonb_build_object(
        'message', 'Baseline Phase-Lock established.',
        'status_snapshot', v_status
      )
    );

  else
    -- VERIFY MODE: Compare against existing checkpoint
    v_mode := 'verify';
    v_is_match := (v_existing_root = v_actual_root_hash);

    -- Lookup checkpoint ID
    select plc.id
    into v_checkpoint_id
    from phase_lock_checkpoints plc
    where plc.label = v_effective_label
      and plc.is_active = true
    order by plc.created_at desc
    limit 1;

    -- Insert verification log (FIXED: use correct schema)
    insert into constitutional_verification_log (
      id,
      created_at,
      check_type,
      expected_root_hash,
      actual_root_hash,
      passed,
      checkpoint_id,
      details
    )
    values (
      gen_random_uuid(),
      v_now,
      'explicit',
      v_existing_root,  -- Expected from checkpoint
      v_actual_root_hash,
      v_is_match,
      v_checkpoint_id,
      jsonb_build_object(
        'message', case
          when v_is_match then 'Phase-Lock verified: hash matches.'
          else 'Phase-Lock DRIFT detected!'
        end,
        'status_snapshot', v_status
      )
    );
  end if;

  -- Return result
  return jsonb_build_object(
    'ok', true,
    'mode', v_mode,
    'hash_match', v_is_match,
    'expected_root_hash', coalesce(v_existing_root, v_actual_root_hash),
    'actual_root_hash', v_actual_root_hash,
    'checkpoint_id', v_checkpoint_id
  );
end;
$$;
