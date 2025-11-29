-- 1. Table: integration_lattice

CREATE TABLE public.integration_lattice (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  fusion_id uuid NOT NULL,
  paradox_map_id uuid NULL,
  collapse_envelope_id uuid NULL,

  curvature_risk numeric NOT NULL CHECK (curvature_risk >= 0 AND curvature_risk <= 1),
  continuation_score numeric NOT NULL CHECK (continuation_score >= 0 AND continuation_score <= 1),
  collapse_probability numeric NOT NULL CHECK (collapse_probability >= 0 AND collapse_probability <= 1),

  lattice_state text NOT NULL CHECK (
    lattice_state = ANY(ARRAY['stable','strained','critical','collapsed'])
  ),

  horizon_start timestamptz NOT NULL,
  horizon_end timestamptz NOT NULL,

  guardian_recommendation text NOT NULL,

  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,

  CONSTRAINT il_fusion_fk FOREIGN KEY (fusion_id)
    REFERENCES public.mesh_temporal_fusion(id),
  CONSTRAINT il_paradox_fk FOREIGN KEY (paradox_map_id)
    REFERENCES public.predictive_paradox_maps(id),
  CONSTRAINT il_collapse_fk FOREIGN KEY (collapse_envelope_id)
    REFERENCES public.collapse_envelopes(id)
);

-- 2. Function: fn_integrate_future_surfaces

CREATE OR REPLACE FUNCTION public.fn_integrate_future_surfaces(
  p_fusion_id uuid
) RETURNS uuid
LANGUAGE plpgsql
AS $$
DECLARE
  v_fusion mesh_temporal_fusion%ROWTYPE;
  v_paradox predictive_paradox_maps%ROWTYPE;
  v_collapse collapse_envelopes%ROWTYPE;

  v_curvature_risk numeric;
  v_collapse_prob numeric;
  v_continuation_score numeric;
  v_lattice_state text;
  v_recommendation text;
  v_horizon_start timestamptz;
  v_horizon_end timestamptz;
  v_id uuid;
  
  -- Metrics
  v_paradox_risk numeric := 0;
  v_collapse_risk numeric := 0;
  v_drift_risk numeric := 0;
  v_tension_risk numeric := 0;
BEGIN
  -- 1. Fetch Fusion
  SELECT * INTO v_fusion FROM mesh_temporal_fusion WHERE id = p_fusion_id;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Fusion node % not found', p_fusion_id;
  END IF;

  -- 2. Fetch latest Paradox Map for this fusion
  SELECT * INTO v_paradox FROM predictive_paradox_maps 
  WHERE fusion_id = p_fusion_id 
  ORDER BY created_at DESC LIMIT 1;

  IF FOUND THEN
    v_paradox_risk := v_paradox.paradox_risk;
    v_drift_risk := v_paradox.drift_risk;
    v_tension_risk := v_paradox.tension_risk;
    
    -- 3. Fetch latest Collapse Envelope for this paradox map
    SELECT * INTO v_collapse FROM collapse_envelopes
    WHERE paradox_map_id = v_paradox.id
    ORDER BY created_at DESC LIMIT 1;
    
    IF FOUND THEN
        v_collapse_risk := v_collapse.collapse_risk;
    END IF;
  END IF;

  -- 4. Derive Curvature Risk
  -- Heuristic: Curvature is a function of paradox intensity and collapse risk, modulated by fusion strength
  -- High fusion strength usually implies stability, but high tension reduces it.
  
  v_curvature_risk := LEAST(1.0, GREATEST(0.0,
    (v_paradox_risk * 0.4) +
    (v_collapse_risk * 0.4) +
    (v_drift_risk * 0.1) +
    (v_tension_risk * 0.1)
  ));

  -- 5. Compute Probabilities
  v_collapse_prob := LEAST(1.0, GREATEST(0.0,
    v_collapse_risk * (1.0 + v_curvature_risk) / 2.0
  ));
  
  v_continuation_score := 1.0 - v_collapse_prob;

  -- 6. Assign Lattice State
  IF v_collapse_prob >= 0.8 THEN
    v_lattice_state := 'collapsed';
    v_recommendation := 'prepare collapse protocol';
  ELSIF v_collapse_prob >= 0.5 THEN
    v_lattice_state := 'critical';
    v_recommendation := 'deploy stabilization';
  ELSIF v_collapse_prob >= 0.2 THEN
    v_lattice_state := 'strained';
    v_recommendation := 'monitor tension';
  ELSE
    v_lattice_state := 'stable';
    v_recommendation := 'allow continuation';
  END IF;

  -- 7. Set Horizon
  -- If we have a collapse envelope, use its horizon. Otherwise use fusion prediction or default.
  IF v_collapse.id IS NOT NULL THEN
    v_horizon_start := v_collapse.horizon_start;
    v_horizon_end := v_collapse.horizon_end;
  ELSIF v_paradox.id IS NOT NULL THEN
    v_horizon_start := v_paradox.prediction_window_start;
    v_horizon_end := v_paradox.prediction_window_end;
  ELSE
    v_horizon_start := timezone('utc', now());
    v_horizon_end := timezone('utc', now()) + interval '2 hours';
  END IF;

  -- 8. Insert
  INSERT INTO integration_lattice (
    fusion_id,
    paradox_map_id,
    collapse_envelope_id,
    curvature_risk,
    continuation_score,
    collapse_probability,
    lattice_state,
    horizon_start,
    horizon_end,
    guardian_recommendation
  ) VALUES (
    v_fusion.id,
    v_paradox.id,
    v_collapse.id,
    v_curvature_risk,
    v_continuation_score,
    v_collapse_prob,
    v_lattice_state,
    v_horizon_start,
    v_horizon_end,
    v_recommendation
  )
  RETURNING id INTO v_id;

  RETURN v_id;
END;
$$;

-- 3. View: view_future_lattice_surface

CREATE OR REPLACE VIEW public.view_future_lattice_surface AS
SELECT
  il.id,
  il.created_at,
  il.lattice_state,
  il.curvature_risk,
  il.collapse_probability,
  il.continuation_score,
  il.guardian_recommendation,
  il.horizon_start,
  il.horizon_end,
  
  f.fusion_strength,
  
  ppm.paradox_risk,
  ppm.risk_band AS paradox_band,
  
  ce.collapse_risk,
  ce.collapse_band
  
FROM integration_lattice il
JOIN mesh_temporal_fusion f ON f.id = il.fusion_id
LEFT JOIN predictive_paradox_maps ppm ON ppm.id = il.paradox_map_id
LEFT JOIN collapse_envelopes ce ON ce.id = il.collapse_envelope_id
ORDER BY il.collapse_probability DESC, il.created_at DESC
LIMIT 300;
