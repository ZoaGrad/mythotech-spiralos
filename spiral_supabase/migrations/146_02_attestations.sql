-- Migration: 146_02_attestations.sql
-- Description: Creates the attestations table to store records of witness attestations.

CREATE TABLE IF NOT EXISTS attestations (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    attestation_id BIGINT NOT NULL UNIQUE,
    witness_id BIGINT NOT NULL REFERENCES witnesses(witness_id),
    data_hash TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient lookup by witness_id
CREATE INDEX IF NOT EXISTS idx_attestations_witness_id ON attestations(witness_id);
