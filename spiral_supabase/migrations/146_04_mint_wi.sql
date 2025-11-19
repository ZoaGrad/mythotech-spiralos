-- Migration: 146_04_mint_wi.sql
-- Description: Creates the wi_metrics table to store the Witness Diversity Index (Wᵢ).

CREATE TABLE IF NOT EXISTS wi_metrics (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    wi_value REAL NOT NULL,
    tv REAL NOT NULL,
    cv REAL NOT NULL,
    rv REAL NOT NULL,
    ev REAL NOT NULL,
    calculation_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Index for timestamp-based queries
CREATE INDEX IF NOT EXISTS idx_wi_metrics_timestamp ON wi_metrics(calculation_timestamp);
