
-- Phase 8.4: Auto-Regulation Engine
-- Creates guardian_autoregulation_history and guardian_correction_profiles tables
-- for autonomous healing strategies and correction tracking

-- ============================================================================
-- TABLE: guardian_autoregulation_history
-- ============================================================================
CREATE TABLE public.guardian_autoregulation_history (
  -- Identity
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bridge_id UUID REFERENCES public.bridge_nodes(id) ON DELETE CASCADE,
  anomaly_id UUID, -- REFERENCES public.guardian_anomalies(id), soft reference for now
  
  -- Correction Details
  correction_type TEXT NOT NULL,
  correction_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  severity_level TEXT NOT NULL CHECK (severity_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
  success BOOLEAN NOT NULL DEFAULT FALSE,
  
  -- Metadata & Tracking
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- TABLE: guardian_correction_profiles
-- ============================================================================
CREATE TABLE public.guardian_correction_profiles (
  -- Identity
  profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bridge_id UUID REFERENCES public.bridge_nodes(id) ON DELETE CASCADE,
  
  -- Baseline & Configuration
  baseline_health NUMERIC(5,4) CHECK (baseline_health >= 0 AND baseline_health <= 1),
  preferred_correction_types TEXT[] NOT NULL DEFAULT '{}',
  
  -- Mutation & Budget Controls
  last_mutation TIMESTAMPTZ,
  correction_budget INTEGER DEFAULT 100,
  cooldown_seconds INTEGER DEFAULT 300,
  
  -- Metadata & Timestamps
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- INDEXES: guardian_autoregulation_history
-- ============================================================================
-- Index for bridge-based history queries with time ordering
CREATE INDEX idx_guardian_autoreg_history_bridge_time 
  ON public.guardian_autoregulation_history(bridge_id, created_at DESC);

-- Index for anomaly-based lookups
CREATE INDEX idx_guardian_autoreg_history_anomaly 
  ON public.guardian_autoregulation_history(anomaly_id) 
  WHERE anomaly_id IS NOT NULL;

-- Index for correction type analysis
CREATE INDEX idx_guardian_autoreg_history_correction_type 
  ON public.guardian_autoregulation_history(correction_type);

-- ============================================================================
-- INDEXES: guardian_correction_profiles
-- ============================================================================
-- Index for bridge-based profile lookups
CREATE INDEX idx_guardian_correction_profiles_bridge 
  ON public.guardian_correction_profiles(bridge_id);

-- Index for health-based sorting and analysis
CREATE INDEX idx_guardian_correction_profiles_health 
  ON public.guardian_correction_profiles(baseline_health DESC) 
  WHERE baseline_health IS NOT NULL;

-- Index for recently updated profiles
CREATE INDEX idx_guardian_correction_profiles_updated 
  ON public.guardian_correction_profiles(updated_at DESC);

-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================
ALTER TABLE public.guardian_autoregulation_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.guardian_correction_profiles ENABLE ROW LEVEL SECURITY;

-- Service role has full access to both tables
CREATE POLICY "Service role full access to autoregulation history" 
  ON public.guardian_autoregulation_history
  FOR ALL 
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role full access to correction profiles" 
  ON public.guardian_correction_profiles
  FOR ALL 
  USING (true)
  WITH CHECK (true);

-- Authenticated users can read autoregulation history
CREATE POLICY "Authenticated read access to autoregulation history" 
  ON public.guardian_autoregulation_history
  FOR SELECT 
  USING (auth.role() = 'authenticated');

-- Authenticated users can read correction profiles
CREATE POLICY "Authenticated read access to correction profiles" 
  ON public.guardian_correction_profiles
  FOR SELECT 
  USING (auth.role() = 'authenticated');

-- ============================================================================
-- GRANTS
-- ============================================================================
GRANT USAGE ON SCHEMA public TO authenticated, service_role;
GRANT SELECT ON public.guardian_autoregulation_history TO authenticated;
GRANT ALL ON public.guardian_autoregulation_history TO service_role;
GRANT SELECT ON public.guardian_correction_profiles TO authenticated;
GRANT ALL ON public.guardian_correction_profiles TO service_role;

-- ============================================================================
-- VIEW: guardian_autoregulation_recent
-- ============================================================================
CREATE OR REPLACE VIEW public.guardian_autoregulation_recent AS
SELECT 
  h.id,
  h.bridge_id,
  b.node_name as bridge_name,
  h.anomaly_id,
  h.correction_type,
  h.severity_level,
  h.success,
  h.correction_payload,
  h.metadata,
  h.created_at
FROM public.guardian_autoregulation_history h
LEFT JOIN public.bridge_nodes b ON h.bridge_id = b.id
WHERE h.created_at >= NOW() - INTERVAL '24 hours'
ORDER BY h.created_at DESC;

-- Grant access to the view
GRANT SELECT ON public.guardian_autoregulation_recent TO authenticated, service_role;

-- ============================================================================
-- COMMENTS
-- ============================================================================
COMMENT ON TABLE public.guardian_autoregulation_history IS 
  'Phase 8.4: Tracks all auto-regulation corrections applied by the Guardian system';

COMMENT ON COLUMN public.guardian_autoregulation_history.correction_type IS 
  'Type of correction: SCARINDEX_RECOVERY_PULSE, SOVEREIGNTY_STABILIZER, ACHE_BUFFER, HEARTBEAT_CORRECTION, ENTROPY_CORRECTION, SELF_PRESERVATION_FREEZE';

COMMENT ON COLUMN public.guardian_autoregulation_history.correction_payload IS 
  'Details of the correction applied, including parameters and affected entities';

COMMENT ON COLUMN public.guardian_autoregulation_history.severity_level IS 
  'Severity level of the anomaly being corrected: LOW, MEDIUM, HIGH, CRITICAL';

COMMENT ON COLUMN public.guardian_autoregulation_history.success IS 
  'Whether the correction was successfully applied';

COMMENT ON TABLE public.guardian_correction_profiles IS 
  'Phase 8.4: Configuration profiles for bridge-specific auto-regulation behavior';

COMMENT ON COLUMN public.guardian_correction_profiles.baseline_health IS 
  'Baseline health score (0-1) for the bridge, used to calibrate corrections';

COMMENT ON COLUMN public.guardian_correction_profiles.preferred_correction_types IS 
  'Array of preferred correction types for this bridge';

COMMENT ON COLUMN public.guardian_correction_profiles.correction_budget IS 
  'Remaining correction budget to prevent over-correction (resets periodically)';

COMMENT ON COLUMN public.guardian_correction_profiles.cooldown_seconds IS 
  'Minimum seconds between corrections for this bridge';

COMMENT ON VIEW public.guardian_autoregulation_recent IS 
  'Phase 8.4: Recent auto-regulation corrections (last 24 hours) with bridge details';

-- ============================================================================
-- FUNCTION: update_correction_profile_timestamp
-- ============================================================================
CREATE OR REPLACE FUNCTION update_correction_profile_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic updated_at maintenance
CREATE TRIGGER trigger_update_correction_profile_timestamp
  BEFORE UPDATE ON public.guardian_correction_profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_correction_profile_timestamp();

COMMENT ON FUNCTION update_correction_profile_timestamp() IS 
  'Automatically updates the updated_at timestamp when correction profiles are modified';

