-- Migration: 146_03_pairs.sql
-- Description: Creates the witness_pairs table for calculating diversity metrics.

CREATE TABLE IF NOT EXISTS witness_pairs (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    witness_a_id BIGINT NOT NULL REFERENCES witnesses(witness_id),
    witness_b_id BIGINT NOT NULL REFERENCES witnesses(witness_id),
    similarity_score REAL,
    last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(witness_a_id, witness_b_id)
);

-- Index for efficient lookup of pairs
CREATE INDEX IF NOT EXISTS idx_witness_pairs_witness_ids ON witness_pairs(witness_a_id, witness_b_id);
