-- =========================================================
-- ΔΩ.K — Constitutional Rhythm & Custody
-- =========================================================

-- Helper: ensure jwt_role() exists (idempotent)
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
-- 1. Custody Registry
-- =========================================================

CREATE TABLE IF NOT EXISTS custody_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity TEXT NOT NULL,                -- e.g. 'service_role', 'guardian_daemon'
    permission_set JSONB NOT NULL,       -- e.g. {"can_approve_j2": true, ...}
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE custody_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE custody_registry FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS custody_registry_service_role_all ON custody_registry;

CREATE POLICY custody_registry_service_role_all
ON custody_registry
AS PERMISSIVE
FOR ALL
TO public
USING (jwt_role() = 'service_role')
WITH CHECK (jwt_role() = 'service_role');


-- =========================================================
-- 2. Constitution Ledger
-- =========================================================

CREATE TABLE IF NOT EXISTS constitution_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component TEXT NOT NULL,       -- e.g. 'teleology_mandates', 'rls_policies'
    hash TEXT NOT NULL,            -- SHA-384 hex
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE constitution_ledger ENABLE ROW LEVEL SECURITY;
ALTER TABLE constitution_ledger FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS constitution_ledger_public_read ON constitution_ledger;
DROP POLICY IF EXISTS constitution_ledger_service_role_insert ON constitution_ledger;

CREATE POLICY constitution_ledger_public_read
ON constitution_ledger
AS PERMISSIVE
FOR SELECT
TO public
USING (true);

CREATE POLICY constitution_ledger_service_role_insert
ON constitution_ledger
AS PERMISSIVE
FOR INSERT
TO public
WITH CHECK (jwt_role() = 'service_role');


-- =========================================================
-- 3. Telemetry: Register K Sequence
-- =========================================================

INSERT INTO system_events (event_type, payload)
VALUES (
  'CONSTITUTION_SEQUENCE_APPLIED',
  jsonb_build_object(
    'code', 'ΔΩ.K',
    'components', jsonb_build_array('custody_registry', 'constitution_ledger'),
    'applied_at', NOW()
  )
);
