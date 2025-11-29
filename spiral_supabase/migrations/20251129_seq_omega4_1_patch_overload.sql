-- Patch Ω.4.1: Audit Surface Overload
-- Adds a 2-argument overload for fn_emit_audit_surface_event to default 'component' to 'System'

CREATE OR REPLACE FUNCTION fn_emit_audit_surface_event(
    p_event_type TEXT,
    p_payload JSONB
) RETURNS UUID
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN fn_emit_audit_surface_event(p_event_type, 'System', p_payload);
END;
$$;
