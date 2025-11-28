-- =========================================================
-- ΔΩ.L — Living Constitution & ScarLock
-- =========================================================

-- Ensure jwt_role() exists
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
-- 1. Constitutional Lock Table (ScarLock)
-- =========================================================

CREATE TABLE IF NOT EXISTS constitutional_lock (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    is_locked BOOLEAN NOT NULL DEFAULT FALSE,
    reason TEXT,
    created_by TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    released_at TIMESTAMPTZ
);

ALTER TABLE constitutional_lock ENABLE ROW LEVEL SECURITY;
ALTER TABLE constitutional_lock FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS constitutional_lock_service_role_all ON constitutional_lock;

CREATE POLICY constitutional_lock_service_role_all
ON constitutional_lock
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


-- Seed a single row to act as the global lock record if none exists
INSERT INTO constitutional_lock (is_locked, reason, created_by)
SELECT FALSE, 'initial_state', 'system'
WHERE NOT EXISTS (SELECT 1 FROM constitutional_lock);


-- =========================================================
-- 2. Guardian Vows Table
-- =========================================================

CREATE TABLE IF NOT EXISTS guardian_vows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subsystem TEXT NOT NULL,            -- e.g. 'teleology', 'autopoiesis', 'mirror', 'paradox'
    vow TEXT NOT NULL,                  -- human-readable vow text
    vow_hash TEXT NOT NULL,             -- e.g. sha384(vow)
    active BOOLEAN NOT NULL DEFAULT TRUE,
    last_verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE guardian_vows ENABLE ROW LEVEL SECURITY;
ALTER TABLE guardian_vows FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS guardian_vows_public_read ON guardian_vows;
DROP POLICY IF EXISTS guardian_vows_service_role_all ON guardian_vows;

CREATE POLICY guardian_vows_public_read
ON guardian_vows
AS PERMISSIVE
FOR SELECT
TO public
USING (true);

CREATE POLICY guardian_vows_service_role_all
ON guardian_vows
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


-- Seed core vows (idempotent)
-- Note: pgcrypto extension is needed for digest function. 
-- Assuming it is enabled or we can use a simpler hash or just insert pre-calculated hashes if extension is missing.
-- We will enable pgcrypto just in case.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

INSERT INTO guardian_vows (subsystem, vow, vow_hash)
SELECT
  'teleology',
  'Uphold ΔΩ.I.1–3 as supreme purpose: coherence, identity refinement, governance elegance.',
  encode(digest('teleology_vow_v1', 'sha384'), 'hex')
WHERE NOT EXISTS (
  SELECT 1 FROM guardian_vows WHERE subsystem = 'teleology'
);

INSERT INTO guardian_vows (subsystem, vow, vow_hash)
SELECT
  'autopoiesis',
  'No structural mutation may bypass τ-alignment, safety policies, or custody registry.',
  encode(digest('autopoiesis_vow_v1', 'sha384'), 'hex')
WHERE NOT EXISTS (
  SELECT 1 FROM guardian_vows WHERE subsystem = 'autopoiesis'
);

INSERT INTO guardian_vows (subsystem, vow, vow_hash)
SELECT
  'mirror',
  'Reflections must be faithful to recorded reality; no silent alteration of past state.',
  encode(digest('mirror_vow_v1', 'sha384'), 'hex')
WHERE NOT EXISTS (
  SELECT 1 FROM guardian_vows WHERE subsystem = 'mirror'
);

INSERT INTO guardian_vows (subsystem, vow, vow_hash)
SELECT
  'paradox',
  'Paradox resolution must favor coherence without erasing contradictory evidence.',
  encode(digest('paradox_vow_v1', 'sha384'), 'hex')
WHERE NOT EXISTS (
  SELECT 1 FROM guardian_vows WHERE subsystem = 'paradox'
);


-- =========================================================
-- 3. Telemetry Registration
-- =========================================================

INSERT INTO system_events (event_type, payload)
VALUES (
  'LIVING_CONSTITUTION_SEQUENCE_APPLIED',
  jsonb_build_object(
    'code', 'ΔΩ.L',
    'components', jsonb_build_array('constitutional_lock', 'guardian_vows'),
    'applied_at', NOW()
  )
);
