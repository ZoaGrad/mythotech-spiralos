-- SpiralOS – SWPS Witness Protocol Tables Part 2
-- ΔΩ.147.3 — Missing Tables for First Breath

-- 1. WITNESS ASSESSMENTS
CREATE TABLE IF NOT EXISTS witness_assessments (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id uuid REFERENCES stream_claims(id),
    witness_id uuid NOT NULL,
    verdict text NOT NULL, -- 'verified', 'rejected'
    confidence numeric DEFAULT 1.0,
    comment text,
    created_at timestamptz DEFAULT now()
);

-- 2. WITNESS ASSIGNMENTS (Optional for now, but good to have)
CREATE TABLE IF NOT EXISTS witness_assignments (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id uuid REFERENCES stream_claims(id),
    witness_id uuid NOT NULL,
    status text DEFAULT 'pending',
    assigned_at timestamptz DEFAULT now(),
    expires_at timestamptz
);

-- 3. REPUTATION VECTORS (Optional for now)
CREATE TABLE IF NOT EXISTS reputation_vectors (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id uuid NOT NULL,
    vector_type text NOT NULL, -- 'witness', 'guardian', etc.
    score numeric DEFAULT 0.0,
    confidence numeric DEFAULT 0.0,
    updated_at timestamptz DEFAULT now()
);
