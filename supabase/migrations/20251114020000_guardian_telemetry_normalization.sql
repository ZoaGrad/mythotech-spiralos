
-- Phase 8.1: Telemetry Normalization Engine
-- Creates guardian_telemetry_events table for normalized, analyzable telemetry

-- ============================================================================
-- TABLE: guardian_telemetry_events
-- ============================================================================
CREATE TABLE public.guardian_telemetry_events (
  -- Identity
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bridge_id UUID REFERENCES public.bridge_nodes(id) ON DELETE CASCADE,
  gateway_key TEXT NOT NULL,
  
  -- Event Classification
  event_type TEXT NOT NULL,
  source TEXT NOT NULL, -- discord_bot, github_webhook, manual, etc.
  signal_type TEXT, -- classified signal type
  
  -- Canonical Timestamping
  timestamp_iso TIMESTAMPTZ NOT NULL,
  timestamp_epoch BIGINT NOT NULL,
  timestamp_drift_ms INTEGER, -- drift from server time
  
  -- Payload Storage
  payload JSONB NOT NULL DEFAULT '{}'::jsonb, -- original payload
  normalized_payload JSONB, -- processed/normalized payload
  
  -- Ache & Agent Metrics
  ache_signature NUMERIC(5,4) CHECK (ache_signature >= 0 AND ache_signature <= 1), -- 0-1 scale
  agent_health NUMERIC(5,4) CHECK (agent_health >= 0 AND agent_health <= 1), -- 0-1 scale
  
  -- Performance Metrics
  latency_ms INTEGER,
  
  -- Sovereign State
  sovereign_state TEXT, -- fingerprint of system state
  
  -- Metadata
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX idx_guardian_telemetry_bridge_id 
  ON public.guardian_telemetry_events(bridge_id);

CREATE INDEX idx_guardian_telemetry_gateway_key 
  ON public.guardian_telemetry_events(gateway_key);

CREATE INDEX idx_guardian_telemetry_event_type 
  ON public.guardian_telemetry_events(event_type);

CREATE INDEX idx_guardian_telemetry_timestamp 
  ON public.guardian_telemetry_events(timestamp_iso DESC);

CREATE INDEX idx_guardian_telemetry_source 
  ON public.guardian_telemetry_events(source);

CREATE INDEX idx_guardian_telemetry_signal_type 
  ON public.guardian_telemetry_events(signal_type);

CREATE INDEX idx_guardian_telemetry_ache 
  ON public.guardian_telemetry_events(ache_signature DESC) 
  WHERE ache_signature IS NOT NULL;

CREATE INDEX idx_guardian_telemetry_health 
  ON public.guardian_telemetry_events(agent_health DESC) 
  WHERE agent_health IS NOT NULL;

-- Composite index for time-series queries
CREATE INDEX idx_guardian_telemetry_bridge_time 
  ON public.guardian_telemetry_events(bridge_id, timestamp_iso DESC);

-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================
ALTER TABLE public.guardian_telemetry_events ENABLE ROW LEVEL SECURITY;

-- Service role has full access
CREATE POLICY "Service role full access" 
  ON public.guardian_telemetry_events
  FOR ALL 
  USING (true)
  WITH CHECK (true);

-- Authenticated users can read all
CREATE POLICY "Authenticated read access" 
  ON public.guardian_telemetry_events
  FOR SELECT 
  USING (auth.role() = 'authenticated');

-- ============================================================================
-- GRANTS
-- ============================================================================
GRANT USAGE ON SCHEMA public TO authenticated, service_role;
GRANT SELECT ON public.guardian_telemetry_events TO authenticated;
GRANT ALL ON public.guardian_telemetry_events TO service_role;

-- ============================================================================
-- COMMENTS
-- ============================================================================
COMMENT ON TABLE public.guardian_telemetry_events IS 
  'Phase 8.1: Normalized telemetry events with canonical timestamping, ache signatures, and agent health metrics';

COMMENT ON COLUMN public.guardian_telemetry_events.bridge_id IS 
  'Reference to bridge_nodes - resolved from gateway_key';

COMMENT ON COLUMN public.guardian_telemetry_events.gateway_key IS 
  'Gateway identifier for cross-validation';

COMMENT ON COLUMN public.guardian_telemetry_events.timestamp_drift_ms IS 
  'Milliseconds drift between client timestamp and server time';

COMMENT ON COLUMN public.guardian_telemetry_events.ache_signature IS 
  'Ache intensity signature (0-1 scale) - higher indicates stronger signal';

COMMENT ON COLUMN public.guardian_telemetry_events.agent_health IS 
  'Estimated agent health (0-1 scale) based on event patterns';

COMMENT ON COLUMN public.guardian_telemetry_events.sovereign_state IS 
  'Fingerprint of system sovereign state at event time';

COMMENT ON COLUMN public.guardian_telemetry_events.latency_ms IS 
  'Processing latency in milliseconds';

