-- 1. Table: guardian_action_playbooks

CREATE TABLE public.guardian_action_playbooks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  lattice_state text NOT NULL CHECK (
    lattice_state = ANY(ARRAY['stable','strained','critical','collapsed'])
  ),
  
  min_collapse_probability numeric NOT NULL CHECK (min_collapse_probability >= 0 AND min_collapse_probability <= 1),
  max_collapse_probability numeric NOT NULL CHECK (max_collapse_probability >= 0 AND max_collapse_probability <= 1),

  default_action text NOT NULL,
  severity integer NOT NULL CHECK (severity >= 0 AND severity <= 10),
  recommended_channel text NOT NULL,

  metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

-- Seed Data
INSERT INTO guardian_action_playbooks 
(lattice_state, min_collapse_probability, max_collapse_probability, default_action, severity, recommended_channel)
VALUES
('stable',    0.00, 0.19, 'observe',   0, 'log'),
('strained',  0.20, 0.49, 'alert',     3, 'dashboard'),
('critical',  0.50, 0.79, 'stabilize', 7, 'dashboard+webhook'),
('collapsed', 0.80, 1.00, 'escalate',  9, 'dashboard+webhook');


-- 2. Table: guardian_action_events

CREATE TABLE public.guardian_action_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  lattice_id uuid NOT NULL,
  fusion_id uuid NOT NULL,
  paradox_map_id uuid NOT NULL,
  collapse_envelope_id uuid NULL,

  lattice_state text NOT NULL,
  collapse_probability numeric NOT NULL,
  curvature_risk numeric NOT NULL,
  continuation_score numeric NOT NULL,

  chosen_action text NOT NULL,
  severity integer NOT NULL,
  guardian_recommendation text NOT NULL,
  
  playbook_id uuid NULL,
  
  status text NOT NULL DEFAULT 'pending' CHECK (
    status = ANY(ARRAY['pending','sent','acked','dismissed'])
  ),

  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,

  CONSTRAINT gae_lattice_fk FOREIGN KEY (lattice_id)
    REFERENCES public.integration_lattice(id),
  CONSTRAINT gae_fusion_fk FOREIGN KEY (fusion_id)
    REFERENCES public.mesh_temporal_fusion(id),
  CONSTRAINT gae_paradox_fk FOREIGN KEY (paradox_map_id)
    REFERENCES public.predictive_paradox_maps(id),
  CONSTRAINT gae_collapse_fk FOREIGN KEY (collapse_envelope_id)
    REFERENCES public.collapse_envelopes(id),
  CONSTRAINT gae_playbook_fk FOREIGN KEY (playbook_id)
    REFERENCES public.guardian_action_playbooks(id)
);

CREATE INDEX idx_guardian_action_events_status_created_at ON guardian_action_events(status, created_at);
CREATE INDEX idx_guardian_action_events_lattice_id ON guardian_action_events(lattice_id);


-- 3. Function: fn_guardian_plan_for_lattice

CREATE OR REPLACE FUNCTION public.fn_guardian_plan_for_lattice(
  p_lattice_id uuid
) RETURNS uuid
LANGUAGE plpgsql
AS $$
DECLARE
  v_lattice integration_lattice%ROWTYPE;
  v_playbook guardian_action_playbooks%ROWTYPE;
  v_existing_id uuid;
  v_new_id uuid;
BEGIN
  -- 1. Check if action already exists for this lattice node (Idempotency)
  SELECT id INTO v_existing_id FROM guardian_action_events WHERE lattice_id = p_lattice_id LIMIT 1;
  IF v_existing_id IS NOT NULL THEN
    RETURN v_existing_id;
  END IF;

  -- 2. Fetch Lattice Node
  SELECT * INTO v_lattice FROM integration_lattice WHERE id = p_lattice_id;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Lattice node % not found', p_lattice_id;
  END IF;

  -- 3. Find Matching Playbook
  -- We match primarily on state, and secondarily on probability range overlap if needed.
  -- For simplicity, we just match state and probability range.
  SELECT * INTO v_playbook FROM guardian_action_playbooks
  WHERE lattice_state = v_lattice.lattice_state
    AND v_lattice.collapse_probability >= min_collapse_probability
    AND v_lattice.collapse_probability <= max_collapse_probability
  ORDER BY severity DESC
  LIMIT 1;

  -- Fallback if no exact range match (e.g. edge cases), just match state
  IF NOT FOUND THEN
    SELECT * INTO v_playbook FROM guardian_action_playbooks
    WHERE lattice_state = v_lattice.lattice_state
    ORDER BY severity DESC
    LIMIT 1;
  END IF;
  
  -- If still not found (shouldn't happen with seeds), default to observe
  IF NOT FOUND THEN
     -- Create a dummy playbook record in memory or just insert with defaults
     -- We'll just proceed with defaults
     v_playbook.default_action := 'observe';
     v_playbook.severity := 0;
     v_playbook.id := NULL;
  END IF;

  -- 4. Insert Action Event
  INSERT INTO guardian_action_events (
    lattice_id,
    fusion_id,
    paradox_map_id,
    collapse_envelope_id,
    lattice_state,
    collapse_probability,
    curvature_risk,
    continuation_score,
    chosen_action,
    severity,
    guardian_recommendation,
    playbook_id
  ) VALUES (
    v_lattice.id,
    v_lattice.fusion_id,
    v_lattice.paradox_map_id,
    v_lattice.collapse_envelope_id,
    v_lattice.lattice_state,
    v_lattice.collapse_probability,
    v_lattice.curvature_risk,
    v_lattice.continuation_score,
    v_playbook.default_action,
    v_playbook.severity,
    v_lattice.guardian_recommendation,
    v_playbook.id
  )
  RETURNING id INTO v_new_id;

  RETURN v_new_id;
END;
$$;
