-- 1. Table: collapse_envelopes

CREATE TABLE public.collapse_envelopes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  paradox_map_id uuid NOT NULL,
  
  collapse_risk numeric NOT NULL CHECK (collapse_risk >= 0 AND collapse_risk <= 1),
  drift_component numeric NOT NULL CHECK (drift_component >= 0 AND drift_component <= 1),
  tension_component numeric NOT NULL CHECK (tension_component >= 0 AND tension_component <= 1),

  envelope_kind text NOT NULL CHECK (
    envelope_kind = ANY(ARRAY['DRIFT','TENSION','FUSION','COMPOSITE'])
  ),

  collapse_band text NOT NULL CHECK (
    collapse_band = ANY(ARRAY['LOW','MEDIUM','HIGH','CRITICAL'])
  ),

  horizon_start timestamptz NOT NULL,
  horizon_end timestamptz NOT NULL,
  decay_half_life_minutes integer NOT NULL DEFAULT 120,

  realized_panic_frame_id uuid NULL,
  realized_at timestamptz NULL,
  realized_outcome text NULL CHECK (
    realized_outcome = ANY(ARRAY['collapse','averted','false_alarm'])
  ),

  status text NOT NULL DEFAULT 'open' CHECK (
    status = ANY(ARRAY['open','stabilized','collapsed','expired'])
  ),

  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,

  CONSTRAINT ce_paradox_fk FOREIGN KEY (paradox_map_id)
    REFERENCES public.predictive_paradox_maps(id),
  CONSTRAINT ce_panic_fk FOREIGN KEY (realized_panic_frame_id)
    REFERENCES public.panic_frames(id)
);

-- 2. Function: fn_project_collapse_from_paradox

CREATE OR REPLACE FUNCTION public.fn_project_collapse_from_paradox(
  p_paradox_map_id uuid,
  p_window_minutes integer DEFAULT 120,
  p_context jsonb DEFAULT NULL
) RETURNS uuid
LANGUAGE plpgsql
AS $$
DECLARE
  v_paradox predictive_paradox_maps%ROWTYPE;
  v_collapse_risk numeric;
  v_drift_component numeric;
  v_tension_component numeric;
  v_collapse_band text;
  v_envelope_kind text;
  v_horizon_start timestamptz;
  v_horizon_end timestamptz;
  v_id uuid;
BEGIN
  SELECT * INTO v_paradox FROM predictive_paradox_maps WHERE id = p_paradox_map_id;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Paradox map % not found', p_paradox_map_id;
  END IF;

  -- Derive components
  v_drift_component := v_paradox.drift_risk;
  v_tension_component := v_paradox.tension_risk;

  -- Compute collapse risk
  v_collapse_risk := LEAST(1.0, GREATEST(
    0.0,
    v_paradox.paradox_risk
    + 0.3 * v_drift_component
    + 0.3 * v_tension_component
  ));

  -- Map to collapse band
  v_collapse_band :=
    CASE
      WHEN v_collapse_risk >= 0.75 THEN 'CRITICAL'
      WHEN v_collapse_risk >= 0.5 THEN 'HIGH'
      WHEN v_collapse_risk >= 0.25 THEN 'MEDIUM'
      ELSE 'LOW'
    END;

  -- Determine envelope kind based on dominant factor
  IF v_drift_component > v_tension_component AND v_drift_component > 0.5 THEN
    v_envelope_kind := 'DRIFT';
  ELSIF v_tension_component > v_drift_component AND v_tension_component > 0.5 THEN
    v_envelope_kind := 'TENSION';
  ELSE
    v_envelope_kind := 'COMPOSITE';
  END IF;

  -- Set horizon
  v_horizon_start := v_paradox.prediction_window_end;
  v_horizon_end := v_paradox.prediction_window_end + (p_window_minutes * interval '1 minute');

  INSERT INTO collapse_envelopes (
    paradox_map_id,
    collapse_risk,
    drift_component,
    tension_component,
    envelope_kind,
    collapse_band,
    horizon_start,
    horizon_end,
    metadata
  ) VALUES (
    v_paradox.id,
    v_collapse_risk,
    v_drift_component,
    v_tension_component,
    v_envelope_kind,
    v_collapse_band,
    v_horizon_start,
    v_horizon_end,
    COALESCE(p_context, '{}'::jsonb)
  )
  RETURNING id INTO v_id;

  RETURN v_id;
END;
$$;

-- 3. View: view_collapse_horizon_surface

CREATE OR REPLACE VIEW public.view_collapse_horizon_surface AS
SELECT
  ce.id,
  ce.created_at,
  ce.collapse_risk,
  ce.collapse_band,
  ce.envelope_kind,
  ce.horizon_start,
  ce.horizon_end,
  ce.status,
  ce.realized_outcome,
  ce.realized_at,
  ppm.paradox_risk,
  ppm.risk_band AS paradox_risk_band,
  ppm.drift_risk,
  ppm.tension_risk,
  pf.scarindex_value,
  pf.status AS panic_status
FROM collapse_envelopes ce
JOIN predictive_paradox_maps ppm ON ppm.id = ce.paradox_map_id
LEFT JOIN panic_frames pf ON pf.id = ce.realized_panic_frame_id
ORDER BY ce.collapse_risk DESC, ce.created_at DESC
LIMIT 300;
