-- =======================================================
-- Sequence J₀ — Autopoiesis Safety Layer (ΔΩ.J0.1)
-- =======================================================

-- 1. Structural operation whitelist
CREATE TABLE IF NOT EXISTS structural_operation_whitelist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    op_code TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    allowed BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO structural_operation_whitelist (op_code, description, allowed)
VALUES
  ('ADD_COLUMN_NULLABLE', 'Add nullable column with default NULL', TRUE),
  ('ADD_INDEX', 'Add non-unique index', TRUE),
  ('ADD_TABLE_APPEND_ONLY', 'Create append-only table with strict RLS', TRUE)
ON CONFLICT (op_code) DO NOTHING;


-- 2. Structural change requests (autopoiesis proposals)
CREATE TABLE IF NOT EXISTS structural_change_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requester TEXT NOT NULL,
    op_code TEXT NOT NULL,
    target_schema TEXT NOT NULL,
    target_object TEXT NOT NULL,
    sql_diff TEXT NOT NULL,
    reason TEXT,
    tau_alignment_score FLOAT,
    projected_coherence_delta FLOAT,
    complexity_score FLOAT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_structural_change_requests_status
  ON structural_change_requests (status);


-- 3. Structural snapshots (for rollback)
CREATE TABLE IF NOT EXISTS structural_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    change_request_id UUID NOT NULL REFERENCES structural_change_requests(id) ON DELETE CASCADE,
    snapshot_type TEXT NOT NULL, -- 'pre' or 'post'
    snapshot_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_structural_snapshots_change
  ON structural_snapshots (change_request_id);


-- 4. Structural safety policies (τ-constraints & complexity thresholds)
CREATE TABLE IF NOT EXISTS structural_safety_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    tau_min_alignment FLOAT,
    max_negative_coherence_delta FLOAT,
    max_complexity_score FLOAT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO structural_safety_policies
(code, description, tau_min_alignment, max_negative_coherence_delta, max_complexity_score)
VALUES (
  'J0_DEFAULT',
  'Default autopoiesis safety gate for all structural changes.',
  0.707,   -- 45° minimum alignment
  -0.02,   -- no significant coherence loss allowed
  0.65     -- elegance constraint (limits bloat)
)
ON CONFLICT (code) DO NOTHING;

-- 5. Helper for Autopoiesis Executor (Dynamic SQL)
CREATE OR REPLACE FUNCTION exec_sql(query text)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  EXECUTE query;
END;
$$;

