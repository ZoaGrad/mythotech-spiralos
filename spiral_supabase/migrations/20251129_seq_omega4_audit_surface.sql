-- Sequence Ω.4: Global Audit Surface

-- 1. Audit Surface Events Table
CREATE TABLE IF NOT EXISTS audit_surface_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT now(),
    event_type TEXT NOT NULL,
    component TEXT NOT NULL,
    payload JSONB DEFAULT '{}'::jsonb,
    phase_lock_hash TEXT
);

-- 2. Emit Function
CREATE OR REPLACE FUNCTION fn_emit_audit_surface_event(
    p_event_type TEXT,
    p_component TEXT,
    p_payload JSONB
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_phase_lock_hash TEXT;
    v_event_id UUID;
BEGIN
    -- Attempt to get current phase lock hash (if available)
    -- We use a sub-transaction or safe call to avoid failing if phase lock is invalid
    BEGIN
        SELECT hash INTO v_phase_lock_hash FROM fn_verify_phase_lock();
    EXCEPTION WHEN OTHERS THEN
        v_phase_lock_hash := NULL;
    END;

    INSERT INTO audit_surface_events (event_type, component, payload, phase_lock_hash)
    VALUES (p_event_type, p_component, p_payload, v_phase_lock_hash)
    RETURNING id INTO v_event_id;

    RETURN v_event_id;
END;
$$;

-- 3. Global Audit View
CREATE OR REPLACE VIEW view_global_audit_surface AS
SELECT
    id,
    created_at,
    event_type,
    component,
    payload,
    phase_lock_hash
FROM audit_surface_events
ORDER BY created_at DESC
LIMIT 500;
