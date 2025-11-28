-- =========================================================
-- ΔΩ.RLS-LOCK v1 — Hybrid RLS Lockdown for SpiralOS
-- Option C: Teleology/Safety hard-lock, Mirror/Paradox public-read
-- =========================================================

-- Helper: Extract JWT role (Supabase convention)
CREATE OR REPLACE FUNCTION public.jwt_role()
RETURNS text
LANGUAGE sql
STABLE
AS $$
  SELECT COALESCE(
    current_setting('request.jwt.claims', true)::jsonb->>'role',
    'anon'
  );
$$;


-- =========================================================
-- 1. TELEOLOGY LAYER (HARD LOCK)
--    teleology_mandates, system_events
-- =========================================================

ALTER TABLE teleology_mandates ENABLE ROW LEVEL SECURITY;
ALTER TABLE teleology_mandates FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS teleology_mandates_rw ON teleology_mandates;

CREATE POLICY teleology_mandates_service_role_all
ON teleology_mandates
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


ALTER TABLE system_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_events FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS system_events_rw ON system_events;

CREATE POLICY system_events_service_role_all
ON system_events
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


-- =========================================================
-- 2. SAFETY LAYER (J₀) — HARD LOCK
--    structural_operation_whitelist,
--    structural_change_requests,
--    structural_snapshots,
--    structural_safety_policies
-- =========================================================

ALTER TABLE structural_operation_whitelist ENABLE ROW LEVEL SECURITY;
ALTER TABLE structural_operation_whitelist FORCE ROW LEVEL SECURITY;

CREATE POLICY structural_operation_whitelist_service_role_all
ON structural_operation_whitelist
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


ALTER TABLE structural_change_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE structural_change_requests FORCE ROW LEVEL SECURITY;

CREATE POLICY structural_change_requests_service_role_all
ON structural_change_requests
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


ALTER TABLE structural_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE structural_snapshots FORCE ROW LEVEL SECURITY;

CREATE POLICY structural_snapshots_service_role_all
ON structural_snapshots
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


ALTER TABLE structural_safety_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE structural_safety_policies FORCE ROW LEVEL SECURITY;

CREATE POLICY structural_safety_policies_service_role_all
ON structural_safety_policies
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


-- =========================================================
-- 3. AUTOPOIESIS PATH (J-D) — SERVICE_ROLE ONLY
--    proposal_patterns, autopoiesis_execution_history,
--    autopoiesis_log, rollback_journal, teleology_weights
-- =========================================================

ALTER TABLE proposal_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE proposal_patterns FORCE ROW LEVEL SECURITY;

CREATE POLICY proposal_patterns_service_role_all
ON proposal_patterns
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


ALTER TABLE autopoiesis_execution_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE autopoiesis_execution_history FORCE ROW LEVEL SECURITY;

CREATE POLICY autopoiesis_execution_history_service_role_all
ON autopoiesis_execution_history
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


ALTER TABLE autopoiesis_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE autopoiesis_log FORCE ROW LEVEL SECURITY;

CREATE POLICY autopoiesis_log_service_role_all
ON autopoiesis_log
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


ALTER TABLE rollback_journal ENABLE ROW LEVEL SECURITY;
ALTER TABLE rollback_journal FORCE ROW LEVEL SECURITY;

CREATE POLICY rollback_journal_service_role_all
ON rollback_journal
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


ALTER TABLE teleology_weights ENABLE ROW LEVEL SECURITY;
ALTER TABLE teleology_weights FORCE ROW LEVEL SECURITY;

CREATE POLICY teleology_weights_service_role_all
ON teleology_weights
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


-- =========================================================
-- 4. MIRROR LAYER (G) — PUBLIC READ, SERVICE_ROLE WRITE
--    quantum_tags, system_reflections
-- =========================================================

ALTER TABLE quantum_tags ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS quantum_tags_public_read ON quantum_tags;
DROP POLICY IF EXISTS quantum_tags_service_role_all ON quantum_tags;

CREATE POLICY quantum_tags_public_read
ON quantum_tags
AS PERMISSIVE
FOR SELECT
TO public
USING (true);

CREATE POLICY quantum_tags_service_role_all
ON quantum_tags
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


-- system_reflections already had RLS; normalize to Hybrid pattern
ALTER TABLE system_reflections ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS system_reflections_public_read ON system_reflections;
DROP POLICY IF EXISTS system_reflections_service_role_all ON system_reflections;

CREATE POLICY system_reflections_public_read
ON system_reflections
AS PERMISSIVE
FOR SELECT
TO public
USING (true);

CREATE POLICY system_reflections_service_role_all
ON system_reflections
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


-- =========================================================
-- 5. PARADOX LAYER (H) — PUBLIC READ, SERVICE_ROLE WRITE
--    paradox_events, paradox_resolutions
-- =========================================================

ALTER TABLE paradox_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE paradox_resolutions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS paradox_events_public_read ON paradox_events;
DROP POLICY IF EXISTS paradox_events_service_role_all ON paradox_events;
DROP POLICY IF EXISTS paradox_resolutions_public_read ON paradox_resolutions;
DROP POLICY IF EXISTS paradox_resolutions_service_role_all ON paradox_resolutions;

CREATE POLICY paradox_events_public_read
ON paradox_events
AS PERMISSIVE
FOR SELECT
TO public
USING (true);

CREATE POLICY paradox_events_service_role_all
ON paradox_events
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


CREATE POLICY paradox_resolutions_public_read
ON paradox_resolutions
AS PERMISSIVE
FOR SELECT
TO public
USING (true);

CREATE POLICY paradox_resolutions_service_role_all
ON paradox_resolutions
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


-- =========================================================
-- 6. TELEMETRY: REGISTER LOCKDOWN EVENT
-- =========================================================

INSERT INTO system_events (event_type, payload)
VALUES (
  'RLS_LOCK_APPLIED',
  jsonb_build_object(
    'code', 'ΔΩ.RLS-LOCK.v1',
    'mode', 'HYBRID',
    'applied_at', NOW()
  )
);
