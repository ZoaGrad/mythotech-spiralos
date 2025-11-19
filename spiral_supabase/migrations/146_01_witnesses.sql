-- Migration: 146_01_witnesses.sql
-- Description: Creates the witnesses table to store information about network witnesses.

CREATE TABLE IF NOT EXISTS witnesses (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    witness_id BIGINT NOT NULL UNIQUE,
    account TEXT NOT NULL UNIQUE,
    metadata_uri TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    registration_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient lookup by account
CREATE INDEX IF NOT EXISTS idx_witnesses_account ON witnesses(account);
