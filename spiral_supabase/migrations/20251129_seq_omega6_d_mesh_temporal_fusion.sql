-- Ω.6-D — Mesh Temporal Fusion
-- Goal: Bind causal mesh tension with temporal drift anchors to create predictive fusion nodes.

-- 1. Fusion node table
CREATE TABLE IF NOT EXISTS public.mesh_temporal_fusion (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz DEFAULT now(),

    -- references into both worlds
    causal_link_id uuid NOT NULL,
    temporal_anchor_id uuid NOT NULL,

    -- computed fusion metrics
    fusion_strength numeric NOT NULL DEFAULT 0,
    predicted_drift_ms numeric NOT NULL DEFAULT 0,
    predicted_tension numeric NOT NULL DEFAULT 0,

    -- raw snapshots for audit
    temporal_snapshot jsonb DEFAULT '{}'::jsonb,
    causal_snapshot jsonb DEFAULT '{}'::jsonb,
    context jsonb DEFAULT '{}'::jsonb,

    CONSTRAINT fusion_link_fk FOREIGN KEY (causal_link_id)
        REFERENCES public.causal_event_links(id),

    CONSTRAINT fusion_anchor_fk FOREIGN KEY (temporal_anchor_id)
        REFERENCES public.temporal_drift_log(id)
);

-- 2. Fusion function
CREATE OR REPLACE FUNCTION public.fn_fuse_mesh_temporal(
    p_causal_link_id uuid,
    p_context jsonb DEFAULT '{}'::jsonb
)
RETURNS uuid AS $$
DECLARE
    v_anchor uuid;
    v_tension numeric;
    v_severity text;
    v_drift numeric;
    v_id uuid;
BEGIN
    -- latest anchor
    SELECT id, drift_delta_ms
    INTO v_anchor, v_drift
    FROM public.temporal_drift_log
    ORDER BY created_at DESC
    LIMIT 1;

    -- mesh tension + severity
    SELECT mesh_tension, severity
    INTO v_tension, v_severity
    FROM public.causal_event_links
    WHERE id = p_causal_link_id;

    INSERT INTO public.mesh_temporal_fusion(
        causal_link_id,
        temporal_anchor_id,
        fusion_strength,
        predicted_drift_ms,
        predicted_tension,
        temporal_snapshot,
        causal_snapshot,
        context
    )
    VALUES (
        p_causal_link_id,
        v_anchor,
        GREATEST(v_tension * (CASE WHEN v_severity='RED' THEN 2 ELSE 1 END), 0),
        COALESCE(v_drift,0),
        COALESCE(v_tension,0),
        (SELECT row_to_json(t.*) FROM public.temporal_drift_log t WHERE t.id = v_anchor),
        (SELECT row_to_json(c.*) FROM public.causal_event_links c WHERE c.id = p_causal_link_id),
        p_context
    )
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- 3. Fusion view
CREATE OR REPLACE VIEW public.view_mesh_temporal_fusion AS
SELECT
    f.*,
    c.source_event_id,
    c.target_event_id,
    c.severity,
    c.mesh_tension,
    t.anchor_timestamp,
    t.drift_delta_ms
FROM public.mesh_temporal_fusion f
JOIN public.causal_event_links c ON c.id = f.causal_link_id
JOIN public.temporal_drift_log t ON t.id = f.temporal_anchor_id;
