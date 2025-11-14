

-- Phase 8.3: Guardian Anomaly Detection Circuit
-- Creates guardian_anomalies table and supporting views

-- ============================================================================
-- TABLE: guardian_anomalies
-- ============================================================================
CREATE TABLE public.guardian_anomalies (
  -- Identity
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bridge_id UUID REFERENCES public.bridge_nodes(id) ON DELETE CASCADE,
  
  -- Anomaly Details
  anomaly_type TEXT NOT NULL, -- HEARTBEAT_GAP, ACHE_SPIKE, SCARINDEX_DROP, SOVEREIGNTY_INSTABILITY, ENTROPY_SPIKE
  severity TEXT NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
  status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'RESOLVED', 'IGNORED')),
  
  -- Details & Metadata
  details JSONB NOT NULL DEFAULT '{}'::jsonb,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  
  -- Timestamps
  detected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  resolved_at TIMESTAMPTZ
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX idx_guardian_anomalies_bridge_id 
  ON public.guardian_anomalies(bridge_id);

CREATE INDEX idx_guardian_anomalies_status 
  ON public.guardian_anomalies(status);

CREATE INDEX idx_guardian_anomalies_severity 
  ON public.guardian_anomalies(severity);

CREATE INDEX idx_guardian_anomalies_type 
  ON public.guardian_anomalies(anomaly_type);

CREATE INDEX idx_guardian_anomalies_detected 
  ON public.guardian_anomalies(detected_at DESC);

-- Composite index for active anomalies by bridge
CREATE INDEX idx_guardian_anomalies_bridge_active 
  ON public.guardian_anomalies(bridge_id, status, detected_at DESC) 
  WHERE status = 'ACTIVE';

-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================
ALTER TABLE public.guardian_anomalies ENABLE ROW LEVEL SECURITY;

-- Service role has full access
CREATE POLICY "Service role full access to anomalies" 
  ON public.guardian_anomalies
  FOR ALL 
  USING (true)
  WITH CHECK (true);

-- Authenticated users can read anomalies
CREATE POLICY "Authenticated read access to anomalies" 
  ON public.guardian_anomalies
  FOR SELECT 
  USING (auth.role() = 'authenticated');

-- ============================================================================
-- GRANTS
-- ============================================================================
GRANT USAGE ON SCHEMA public TO authenticated, service_role;
GRANT SELECT ON public.guardian_anomalies TO authenticated;
GRANT ALL ON public.guardian_anomalies TO service_role;

-- ============================================================================
-- VIEW: anomaly_status
-- ============================================================================
CREATE OR REPLACE VIEW public.anomaly_status AS
SELECT 
  a.id,
  a.bridge_id,
  b.node_name as bridge_name,
  a.anomaly_type,
  a.severity,
  a.status,
  a.details,
  a.detected_at,
  a.resolved_at,
  EXTRACT(EPOCH FROM (COALESCE(a.resolved_at, NOW()) - a.detected_at)) / 60 as duration_minutes
FROM public.guardian_anomalies a
LEFT JOIN public.bridge_nodes b ON a.bridge_id = b.id
ORDER BY a.detected_at DESC;

-- Grant access to the view
GRANT SELECT ON public.anomaly_status TO authenticated, service_role;

-- ============================================================================
-- COMMENTS
-- ============================================================================
COMMENT ON TABLE public.guardian_anomalies IS 
  'Phase 8.3: Detected anomalies in Guardian system telemetry and health metrics';

COMMENT ON COLUMN public.guardian_anomalies.anomaly_type IS 
  'Type of anomaly: HEARTBEAT_GAP, ACHE_SPIKE, SCARINDEX_DROP, SOVEREIGNTY_INSTABILITY, ENTROPY_SPIKE';

COMMENT ON COLUMN public.guardian_anomalies.severity IS 
  'Severity level: LOW, MEDIUM, HIGH, CRITICAL';

COMMENT ON COLUMN public.guardian_anomalies.status IS 
  'Current status: ACTIVE, RESOLVED, IGNORED';

COMMENT ON VIEW public.anomaly_status IS 
  'Phase 8.3: Consolidated view of anomalies with bridge details and duration';

