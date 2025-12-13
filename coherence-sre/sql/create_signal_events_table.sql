-- SQL schema for signal_events table in Supabase (PostgreSQL)
-- This table stores synthetic and real metric events for the Coherence SRE platform

CREATE TABLE signal_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ts TIMESTAMPTZ NOT NULL,
  host TEXT NOT NULL,
  service TEXT NOT NULL,
  fingerprint TEXT NOT NULL, -- format: "host:metric"
  severity TEXT NOT NULL, -- info | warn | error
  metric TEXT NOT NULL,   -- cpu | memory | disk | error
  value NUMERIC NOT NULL,
  synthetic BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX idx_signal_events_fingerprint ON signal_events(fingerprint);
CREATE INDEX idx_signal_events_ts ON signal_events(ts);
CREATE INDEX idx_signal_events_host ON signal_events(host);
CREATE INDEX idx_signal_events_severity ON signal_events(severity);

-- Add comments for documentation
COMMENT ON TABLE signal_events IS 'Stores metric events and incidents for SRE correlation analysis';
COMMENT ON COLUMN signal_events.fingerprint IS 'Unique identifier format: host:metric';
COMMENT ON COLUMN signal_events.severity IS 'Event severity level: info, warn, or error';
COMMENT ON COLUMN signal_events.metric IS 'Metric type: cpu, memory, disk, or error';
COMMENT ON COLUMN signal_events.synthetic IS 'True if generated synthetically for testing';
