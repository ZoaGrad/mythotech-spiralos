-- Sequence G: The Mirror Layer Migration

-- 1. Create quantum_tags table
CREATE TABLE IF NOT EXISTS quantum_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    origin TEXT NOT NULL CHECK (origin IN ('ZoaGrad', 'System', 'Pantheon', 'Governance', 'Reflection')),
    intent TEXT NOT NULL,
    certainty FLOAT NOT NULL CHECK (certainty >= 0.0 AND certainty <= 1.0),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for faster lookups by entity
CREATE INDEX IF NOT EXISTS idx_quantum_tags_entity ON quantum_tags(entity_id, entity_type);

-- 2. Extend system_reflections table
-- We use DO block to avoid errors if columns already exist (idempotency)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'system_reflections' AND column_name = 'state_vector') THEN
        ALTER TABLE system_reflections ADD COLUMN state_vector JSONB;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'system_reflections' AND column_name = 'coherence_score') THEN
        ALTER TABLE system_reflections ADD COLUMN coherence_score FLOAT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'system_reflections' AND column_name = 'triggered_repair') THEN
        ALTER TABLE system_reflections ADD COLUMN triggered_repair BOOLEAN DEFAULT FALSE;
    END IF;
END $$;
