-- Ω.6-C — Cross-Mesh Reconciliation Layer
-- Purpose: unify anomaly events, audit events, temporal anchors, and causality links
-- into a coherent cross-mesh surface.

-- 1. Create unified cross-mesh table
CREATE TABLE IF NOT EXISTS public.cross_mesh_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz DEFAULT now(),
    event_type text NOT NULL,
    source_table text NOT NULL,
    source_id uuid NOT NULL,
    temporal_anchor_id uuid,
    phase_lock_hash text,
    mesh_tension numeric DEFAULT 0,
    severity text DEFAULT 'UNKNOWN',
    payload jsonb DEFAULT '{}'::jsonb
);

-- 2. Ingestion function: pulls from the four systems
CREATE OR REPLACE FUNCTION public.fn_emit_cross_mesh_event(
    p_source_table text,
    p_source_id uuid,
    p_event_type text,
    p_payload jsonb DEFAULT '{}'::jsonb
)
RETURNS uuid AS $$
DECLARE
    v_anchor uuid;
    v_hash text;
    v_severity text;
    v_tension numeric := 0;
    v_id uuid;
BEGIN
    -- resolve temporal anchor if available
    SELECT id INTO v_anchor
    FROM public.temporal_drift_log
    WHERE drift_delta_ms IS NULL
    ORDER BY created_at DESC
    LIMIT 1;

    -- resolve severity/tension via causality links (Ω.6-B)
    SELECT COALESCE(MAX(mesh_tension),0), COALESCE(MAX(severity),'UNKNOWN')
    INTO v_tension, v_severity
    FROM public.causal_event_links
    WHERE source_event_id = p_source_id OR target_event_id = p_source_id;

    -- phase lock hash (optional)
    SELECT root_hash INTO v_hash
    FROM public.phase_lock_checkpoints
    WHERE is_active = true
    ORDER BY created_at DESC
    LIMIT 1;

    INSERT INTO public.cross_mesh_events(
        event_type, source_table, source_id,
        temporal_anchor_id, phase_lock_hash,
        mesh_tension, severity, payload
    )
    VALUES (
        p_event_type, p_source_table, p_source_id,
        v_anchor, v_hash, v_tension, v_severity, p_payload
    )
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- 3. View: the unified reconciliation surface
CREATE OR REPLACE VIEW public.view_cross_mesh_surface AS
SELECT
    cme.*,
    coalesce(ae.event_type, ga.alert_type, ge.anomaly_type, te.event_type) AS resolved_type
FROM public.cross_mesh_events cme
LEFT JOIN public.audit_surface_events ae ON ae.id = cme.source_id
LEFT JOIN public.guardian_alerts ga ON ga.id = cme.source_id
LEFT JOIN public.guardian_anomalies ge ON ge.id = cme.source_id
LEFT JOIN public.guardian_telemetry_events te ON te.id = cme.source_id;
