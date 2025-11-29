-- Sequence Ω.5: Temporal Coherence & Drift-Lock

-- 1. Temporal Drift Log Table
CREATE TABLE IF NOT EXISTS temporal_drift_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT now(),
    anchor_timestamp TIMESTAMPTZ NOT NULL,
    drift_delta_ms INTEGER, -- Nullable if just an anchor
    phase_lock_hash TEXT,
    severity TEXT CHECK (severity IN ('GREEN', 'YELLOW', 'RED')),
    source TEXT NOT NULL
);

-- 2. Record Anchor Function
CREATE OR REPLACE FUNCTION fn_record_temporal_anchor(
    p_source TEXT,
    p_timestamp TIMESTAMPTZ DEFAULT now()
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_phase_lock_hash TEXT;
    v_id UUID;
BEGIN
    -- Capture Phase Lock Hash
    BEGIN
        SELECT hash INTO v_phase_lock_hash FROM fn_verify_phase_lock();
    EXCEPTION WHEN OTHERS THEN
        v_phase_lock_hash := NULL;
    END;

    INSERT INTO temporal_drift_log (anchor_timestamp, phase_lock_hash, severity, source)
    VALUES (p_timestamp, v_phase_lock_hash, 'GREEN', p_source)
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$;

-- 3. Verify Drift Function
CREATE OR REPLACE FUNCTION fn_verify_temporal_drift(
    p_client_timestamp TIMESTAMPTZ,
    p_source TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_server_time TIMESTAMPTZ := now();
    v_delta_ms INTEGER;
    v_severity TEXT;
    v_phase_lock_hash TEXT;
    v_id UUID;
BEGIN
    -- Calculate Delta (Client - Server)
    v_delta_ms := EXTRACT(EPOCH FROM (p_client_timestamp - v_server_time)) * 1000;

    -- Determine Severity
    IF ABS(v_delta_ms) < 1000 THEN
        v_severity := 'GREEN';
    ELSIF ABS(v_delta_ms) < 5000 THEN
        v_severity := 'YELLOW';
    ELSE
        v_severity := 'RED';
    END IF;

    -- Capture Phase Lock Hash
    BEGIN
        SELECT hash INTO v_phase_lock_hash FROM fn_verify_phase_lock();
    EXCEPTION WHEN OTHERS THEN
        v_phase_lock_hash := NULL;
    END;

    -- Log Entry
    INSERT INTO temporal_drift_log (anchor_timestamp, drift_delta_ms, phase_lock_hash, severity, source)
    VALUES (p_client_timestamp, v_delta_ms, v_phase_lock_hash, v_severity, p_source)
    RETURNING id INTO v_id;

    RETURN jsonb_build_object(
        'id', v_id,
        'server_time', v_server_time,
        'delta_ms', v_delta_ms,
        'severity', v_severity,
        'phase_lock_hash', v_phase_lock_hash
    );
END;
$$;

-- 4. Temporal Drift Status View
CREATE OR REPLACE VIEW view_temporal_drift_status AS
SELECT
    id,
    created_at,
    anchor_timestamp,
    drift_delta_ms,
    phase_lock_hash,
    severity,
    source
FROM temporal_drift_log
ORDER BY created_at DESC
LIMIT 50;
