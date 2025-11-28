-- =========================================================
-- Ω.2 — Dashboard Enhancements
-- =========================================================

-- Drop previous view/function to recreate with new schema
DROP FUNCTION IF EXISTS fn_status_api();
DROP VIEW IF EXISTS view_system_status;

CREATE OR REPLACE VIEW view_system_status AS
WITH 
    latest_lock AS (
        SELECT is_locked, reason, created_at, created_by FROM constitutional_lock LIMIT 1
    ),
    latest_event AS (
        SELECT event_type, created_at, payload FROM system_events ORDER BY created_at DESC LIMIT 1
    ),
    event_stats AS (
        SELECT count(*) as total_events FROM system_events
    ),
    guardian_state AS (
        SELECT json_agg(gv) as vows FROM (SELECT subsystem, active, last_verified_at FROM guardian_vows) gv
    ),
    const_hashes AS (
        -- Get the latest hash for each component
        SELECT json_object_agg(component, hash) as hashes 
        FROM (
            SELECT DISTINCT ON (component) component, hash 
            FROM constitution_ledger 
            ORDER BY component, created_at DESC
        ) t
    ),
    safety_stats AS (
        SELECT 
            (SELECT count(*) FROM structural_operation_whitelist) as whitelist_count,
            (SELECT count(*) FROM structural_safety_policies) as policy_count
    )
SELECT
    (SELECT row_to_json(l) FROM latest_lock l) as lock_status,
    (SELECT row_to_json(e) FROM latest_event e) as latest_event,
    (SELECT row_to_json(s) FROM event_stats s) as event_stats,
    (SELECT vows FROM guardian_state) as guardian_vows,
    (SELECT hashes FROM const_hashes) as constitution_state,
    (SELECT row_to_json(ss) FROM safety_stats ss) as safety_state,
    'vΩ.1' as system_version;

-- RPC function
CREATE OR REPLACE FUNCTION fn_status_api()
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    result json;
BEGIN
    SELECT row_to_json(s) INTO result FROM view_system_status s;
    RETURN result;
END;
$$;

GRANT EXECUTE ON FUNCTION fn_status_api() TO anon, authenticated, service_role;
GRANT SELECT ON view_system_status TO anon, authenticated, service_role;
