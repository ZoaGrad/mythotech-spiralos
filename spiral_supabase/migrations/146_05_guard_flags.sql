-- Migration: 146_05_guard_flags.sql
-- Description: Creates a table to store guardrail flags related to the Wᵢ metric.

CREATE TABLE IF NOT EXISTS guard_flags (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    flag_name TEXT NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT FALSE,
    last_checked TIMESTAMPTZ
);

-- Insert the initial Wᵢ guard flag
INSERT INTO guard_flags (flag_name, is_active) VALUES ('wi_ok', FALSE)
ON CONFLICT (flag_name) DO NOTHING;
