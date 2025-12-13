-- SQL schema for the metrics table in Supabase (PostgreSQL)
-- This table stores historical metric data from Datadog

CREATE TABLE IF NOT EXISTS metrics (
    id BIGSERIAL PRIMARY KEY,
    host VARCHAR(255) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_metrics_host ON metrics(host);
CREATE INDEX IF NOT EXISTS idx_metrics_metric_name ON metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_host_metric_timestamp ON metrics(host, metric_name, timestamp DESC);

-- Add a comment to the table
COMMENT ON TABLE metrics IS 'Stores historical metric data ingested from Datadog API';
COMMENT ON COLUMN metrics.host IS 'The hostname or host identifier from Datadog';
COMMENT ON COLUMN metrics.metric_name IS 'The name of the metric (e.g., system.cpu.idle, system.load.1)';
COMMENT ON COLUMN metrics.value IS 'The metric value (averaged by host)';
COMMENT ON COLUMN metrics.timestamp IS 'The timestamp of the metric data point';
COMMENT ON COLUMN metrics.created_at IS 'When this record was inserted into the database';
