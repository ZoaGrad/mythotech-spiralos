-- =========================================================
-- Ω.1 — Status API Activation
-- =========================================================

-- Create a view for easier querying of the latest status
CREATE OR REPLACE VIEW view_system_status AS
SELECT
    (SELECT row_to_json(cl) FROM (SELECT is_locked, reason, created_at FROM constitutional_lock LIMIT 1) cl) as lock_status,
    (SELECT row_to_json(se) FROM (SELECT event_type, created_at, payload FROM system_events ORDER BY created_at DESC LIMIT 1) se) as latest_event,
    (SELECT json_agg(gv) FROM (SELECT subsystem, active, last_verified_at FROM guardian_vows) gv) as guardian_vows;

-- RPC function to expose this view securely
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

-- Grant access to anon and service_role for the API
GRANT EXECUTE ON FUNCTION fn_status_api() TO anon, authenticated, service_role;
GRANT SELECT ON view_system_status TO anon, authenticated, service_role;
