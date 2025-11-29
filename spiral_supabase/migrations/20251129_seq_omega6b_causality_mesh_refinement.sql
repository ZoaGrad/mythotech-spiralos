-- Sequence Ω.6-B: Causality Mesh Refinement
-- Description: Adds severity, normalized weight, and mesh tension metrics to causality mesh.

-- 1. Extend causal_event_links
ALTER TABLE causal_event_links
ADD COLUMN IF NOT EXISTS severity TEXT NOT NULL DEFAULT 'UNKNOWN',
ADD COLUMN IF NOT EXISTS weight_normalized NUMERIC(10,4) NOT NULL DEFAULT 0.0000,
ADD COLUMN IF NOT EXISTS mesh_tension NUMERIC(10,4) NOT NULL DEFAULT 0.0000;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'causal_event_links_severity_check') THEN
        ALTER TABLE causal_event_links
        ADD CONSTRAINT causal_event_links_severity_check
        CHECK (severity IN ('GREEN', 'YELLOW', 'RED', 'UNKNOWN'));
    END IF;
END $$;

-- 2. Helper Functions

-- Normalize weight to [0,1]
CREATE OR REPLACE FUNCTION fn_normalize_weight(p_weight NUMERIC)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_weight NUMERIC := COALESCE(p_weight, 0);
BEGIN
    IF v_weight < 0 THEN
        v_weight := 0;
    ELSIF v_weight > 1 THEN
        v_weight := 1;
    END IF;
    RETURN v_weight;
END;
$$;

-- Recompute mesh tension for an event
CREATE OR REPLACE FUNCTION fn_recompute_mesh_tension_for_event(
    p_event_id UUID
) RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_total NUMERIC;
BEGIN
    -- Total normalized weight of links involving this event (source or target)
    SELECT COALESCE(SUM(weight_normalized), 0)
    INTO v_total
    FROM causal_event_links
    WHERE source_event_id = p_event_id
       OR target_event_id = p_event_id;

    -- Apply this aggregate tension back onto each involved link
    UPDATE causal_event_links
    SET mesh_tension = v_total
    WHERE source_event_id = p_event_id
       OR target_event_id = p_event_id;
END;
$$;

-- Update metrics and trigger recompute
CREATE OR REPLACE FUNCTION fn_update_causality_metrics(
    p_link_id UUID,
    p_severity TEXT,
    p_weight NUMERIC
) RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_link RECORD;
    v_severity TEXT := COALESCE(p_severity, 'UNKNOWN');
    v_norm NUMERIC;
BEGIN
    v_norm := fn_normalize_weight(p_weight);

    UPDATE causal_event_links
    SET
        severity = v_severity,
        weight = p_weight,
        weight_normalized = v_norm
    WHERE id = p_link_id;

    SELECT * INTO v_link
    FROM causal_event_links
    WHERE id = p_link_id;

    IF v_link IS NOT NULL THEN
        PERFORM fn_recompute_mesh_tension_for_event(v_link.source_event_id);
        PERFORM fn_recompute_mesh_tension_for_event(v_link.target_event_id);
    END IF;

    RETURN jsonb_build_object(
        'link_id', p_link_id,
        'severity', v_severity,
        'weight', p_weight,
        'weight_normalized', v_norm
    );
END;
$$;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION fn_normalize_weight(NUMERIC) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION fn_recompute_mesh_tension_for_event(UUID) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION fn_update_causality_metrics(UUID, TEXT, NUMERIC) TO anon, authenticated, service_role;


-- 3. View: High-Tension Nodes
CREATE OR REPLACE VIEW view_causality_tension AS
WITH event_weights AS (
    SELECT
        e.id AS event_id,
        MAX(e.created_at) AS latest_event_at,
        MAX(e.event_type) AS event_type,
        MAX(e.component) AS component,
        SUM(l.weight_normalized) AS total_weight_norm,
        MAX(l.mesh_tension) AS mesh_tension_max,
        MAX(l.severity) AS severity_dominant
    FROM audit_surface_events e
    JOIN causal_event_links l
      ON l.source_event_id = e.id
      OR l.target_event_id = e.id
    GROUP BY e.id
)
SELECT
    event_id,
    latest_event_at,
    event_type,
    component,
    total_weight_norm,
    mesh_tension_max,
    severity_dominant
FROM event_weights
ORDER BY mesh_tension_max DESC, total_weight_norm DESC
LIMIT 200;

-- Grant read access
GRANT SELECT ON view_causality_tension TO anon, authenticated, service_role;
