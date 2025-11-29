-- 1.1 Table: predictive_paradox_maps

CREATE TABLE public.predictive_paradox_maps (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  fusion_id uuid NOT NULL,
  causal_link_id uuid NOT NULL,
  temporal_anchor_id uuid NOT NULL,

  paradox_risk numeric NOT NULL CHECK (paradox_risk >= 0 AND paradox_risk <= 1),
  drift_risk numeric NOT NULL CHECK (drift_risk >= 0 AND drift_risk <= 1),
  tension_risk numeric NOT NULL CHECK (tension_risk >= 0 AND tension_risk <= 1),

  risk_band text NOT NULL CHECK (
    risk_band = ANY (ARRAY['LOW','MEDIUM','HIGH','CRITICAL'])
  ),
  prediction_window_start timestamptz NOT NULL,
  prediction_window_end timestamptz NOT NULL,

  realized_paradox_id uuid NULL,
  realized_at timestamptz NULL,
  realized_outcome text NULL CHECK (
    realized_outcome = ANY (ARRAY['hit','near_miss','false_alarm'])
  ),

  fusion_snapshot jsonb NOT NULL DEFAULT '{}'::jsonb,
  mesh_snapshot jsonb NOT NULL DEFAULT '{}'::jsonb,
  temporal_snapshot jsonb NOT NULL DEFAULT '{}'::jsonb,
  guardian_snapshot jsonb NOT NULL DEFAULT '{}'::jsonb,

  status text NOT NULL DEFAULT 'open' CHECK (
    status = ANY (ARRAY['open','decayed','realized'])
  ),

  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,

  CONSTRAINT ppm_fusion_fk FOREIGN KEY (fusion_id)
    REFERENCES public.mesh_temporal_fusion(id),
  CONSTRAINT ppm_causal_fk FOREIGN KEY (causal_link_id)
    REFERENCES public.causal_event_links(id),
  CONSTRAINT ppm_temporal_fk FOREIGN KEY (temporal_anchor_id)
    REFERENCES public.temporal_drift_log(id),
  CONSTRAINT ppm_paradox_fk FOREIGN KEY (realized_paradox_id)
    REFERENCES public.paradox_events(id)
);

-- 1.2 Function: fn_project_paradox_from_fusion

CREATE OR REPLACE FUNCTION public.fn_project_paradox_from_fusion(
  p_fusion_id uuid,
  p_window_minutes integer DEFAULT 30,
  p_context jsonb DEFAULT '{}'::jsonb
) RETURNS uuid
LANGUAGE plpgsql
AS $$
DECLARE
  v_f mesh_temporal_fusion%ROWTYPE;
  v_link causal_event_links%ROWTYPE;
  v_anchor temporal_drift_log%ROWTYPE;

  v_paradox_risk numeric;
  v_drift_risk numeric;
  v_tension_risk numeric;
  v_risk_band text;
  v_now timestamptz;
  v_id uuid;
BEGIN
  v_now := timezone('utc', now());

  SELECT * INTO v_f FROM mesh_temporal_fusion WHERE id = p_fusion_id;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Fusion node % not found', p_fusion_id;
  END IF;

  SELECT * INTO v_link FROM causal_event_links WHERE id = v_f.causal_link_id;
  SELECT * INTO v_anchor FROM temporal_drift_log WHERE id = v_f.temporal_anchor_id;

  -- basic derived metrics
  v_tension_risk := LEAST(1.0, GREATEST(0.0, COALESCE(v_f.predicted_tension, 0) / 10.0));
  v_drift_risk   := LEAST(1.0, GREATEST(0.0, ABS(COALESCE(v_anchor.drift_delta_ms, 0)) / 60000.0));

  v_paradox_risk :=
      LEAST(
        1.0,
        GREATEST(
          0.0,
          (COALESCE(v_f.fusion_strength, 0) / 10.0)
          + 0.4 * v_tension_risk
          + 0.4 * v_drift_risk
        )
      );

  v_risk_band :=
    CASE
      WHEN v_paradox_risk >= 0.8 THEN 'CRITICAL'
      WHEN v_paradox_risk >= 0.6 THEN 'HIGH'
      WHEN v_paradox_risk >= 0.3 THEN 'MEDIUM'
      ELSE 'LOW'
    END;

  INSERT INTO predictive_paradox_maps (
    fusion_id,
    causal_link_id,
    temporal_anchor_id,
    paradox_risk,
    drift_risk,
    tension_risk,
    risk_band,
    prediction_window_start,
    prediction_window_end,
    fusion_snapshot,
    mesh_snapshot,
    temporal_snapshot,
    guardian_snapshot,
    metadata
  ) VALUES (
    v_f.id,
    v_f.causal_link_id,
    v_f.temporal_anchor_id,
    v_paradox_risk,
    v_drift_risk,
    v_tension_risk,
    v_risk_band,
    v_now,
    v_now + make_interval(mins => p_window_minutes),
    to_jsonb(v_f),
    (SELECT to_jsonb(c) FROM causal_event_links c WHERE c.id = v_f.causal_link_id),
    (SELECT to_jsonb(t) FROM temporal_drift_log t WHERE t.id = v_f.temporal_anchor_id),
    '{}'::jsonb,
    COALESCE(p_context, '{}'::jsonb)
  )
  RETURNING id INTO v_id;

  RETURN v_id;
END;
$$;

-- 1.3 View: view_paradox_risk_surface

CREATE OR REPLACE VIEW public.view_paradox_risk_surface AS
SELECT
  ppm.id,
  ppm.created_at,
  ppm.paradox_risk,
  ppm.risk_band,
  ppm.drift_risk,
  ppm.tension_risk,
  ppm.prediction_window_start,
  ppm.prediction_window_end,
  ppm.status,
  ppm.realized_paradox_id,
  ppm.realized_at,
  ppm.realized_outcome,
  c.cause_type,
  c.severity AS link_severity,
  c.mesh_tension,
  f.fusion_strength,
  f.predicted_drift_ms,
  f.predicted_tension
FROM predictive_paradox_maps ppm
JOIN mesh_temporal_fusion f ON f.id = ppm.fusion_id
JOIN causal_event_links c ON c.id = ppm.causal_link_id
ORDER BY ppm.paradox_risk DESC, ppm.created_at DESC
LIMIT 300;
