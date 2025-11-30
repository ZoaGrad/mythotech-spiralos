-- Migration: telemetry_hardening
-- Description: Updates telemetry_events table to match hardened schema requirements.

-- Rename columns to match new spec
ALTER TABLE telemetry_events RENAME COLUMN timestamp TO event_timestamp;
ALTER TABLE telemetry_events RENAME COLUMN source TO source_id;

-- Add new columns
ALTER TABLE telemetry_events ADD COLUMN IF NOT EXISTS processed_status TEXT NOT NULL DEFAULT 'pending';
ALTER TABLE telemetry_events ADD COLUMN IF NOT EXISTS processing_log JSONB;
ALTER TABLE telemetry_events ADD COLUMN IF NOT EXISTS signature TEXT;
ALTER TABLE telemetry_events ADD COLUMN IF NOT EXISTS metadata JSONB;

-- Add indexes for new columns
CREATE INDEX IF NOT EXISTS idx_telemetry_processed_status ON telemetry_events(processed_status);

-- Update comments
COMMENT ON TABLE telemetry_events IS 'Stores raw telemetry data for processing by the Coherence Core.';
COMMENT ON COLUMN telemetry_events.source_id IS 'Identifier for the origin of the telemetry (e.g., GitHub, Gateway-X)';
COMMENT ON COLUMN telemetry_events.processed_status IS 'Status of processing: pending, processed, failed';
