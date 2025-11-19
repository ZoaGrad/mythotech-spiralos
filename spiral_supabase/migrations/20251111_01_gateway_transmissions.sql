-- ============================================================================
-- Gateway Transmissions Telemetry Table
-- ============================================================================
-- Purpose: Track sovereignty telemetry from Ω-Δ-Φ workflow gateway system
-- Constitutional Alignment: Thermodynamic integrity via [0,1] constraints
-- VaultNode: ΔΩ lineage tracked via immutable timestamps
-- ============================================================================

-- Create gateway_transmissions table
CREATE TABLE public.gateway_transmissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bridge_id TEXT NOT NULL UNIQUE,
  resonance_score NUMERIC(5,4) NOT NULL,
  necessity_score NUMERIC(5,4) NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  constraint_tensor JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
  
  -- Constitutional Constraints: Thermodynamic bounds [0, 1]
  CONSTRAINT resonance_score_bounds CHECK (resonance_score >= 0 AND resonance_score <= 1),
  CONSTRAINT necessity_score_bounds CHECK (necessity_score >= 0 AND necessity_score <= 1),
  
  -- JSONB Schema Validation: Basic structure checks
  CONSTRAINT payload_is_object CHECK (jsonb_typeof(payload) = 'object'),
  CONSTRAINT constraint_tensor_is_object CHECK (jsonb_typeof(constraint_tensor) = 'object')
);

-- ============================================================================
-- Performance Indexes
-- ============================================================================

-- Primary query indexes for bridge_id lookups
CREATE INDEX idx_gateway_transmissions_bridge_id ON public.gateway_transmissions(bridge_id);

-- Time-series indexes for telemetry analysis
CREATE INDEX idx_gateway_transmissions_created_at ON public.gateway_transmissions(created_at DESC);

-- Sovereignty metrics indexes for C₅-C₇ tensor analysis
CREATE INDEX idx_gateway_transmissions_resonance ON public.gateway_transmissions(resonance_score DESC);
CREATE INDEX idx_gateway_transmissions_necessity ON public.gateway_transmissions(necessity_score DESC);

-- Composite index for sovereignty threshold queries
CREATE INDEX idx_gateway_transmissions_sovereignty ON public.gateway_transmissions(resonance_score, necessity_score);

-- JSONB GIN indexes for fast payload/tensor queries
CREATE INDEX idx_gateway_transmissions_payload_gin ON public.gateway_transmissions USING GIN (payload);
CREATE INDEX idx_gateway_transmissions_tensor_gin ON public.gateway_transmissions USING GIN (constraint_tensor);

-- ============================================================================
-- Trigger Functions
-- ============================================================================

-- Auto-update updated_at timestamp on modifications
CREATE OR REPLACE FUNCTION update_gateway_transmission_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER gateway_transmission_updated_at_trigger
  BEFORE UPDATE ON public.gateway_transmissions
  FOR EACH ROW
  EXECUTE FUNCTION update_gateway_transmission_updated_at();

-- ============================================================================
-- Row Level Security (RLS)
-- ============================================================================

-- Enable RLS for constitutional data sovereignty
ALTER TABLE public.gateway_transmissions ENABLE ROW LEVEL SECURITY;

-- Service role has full access (for Edge Functions and automation)
CREATE POLICY "Enable all operations for service role" 
  ON public.gateway_transmissions
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Authenticated users can read all transmissions (transparency principle)
CREATE POLICY "Enable read access for authenticated users" 
  ON public.gateway_transmissions
  FOR SELECT
  USING (auth.role() = 'authenticated');

-- Anonymous users can read (public telemetry)
CREATE POLICY "Enable read access for anonymous users" 
  ON public.gateway_transmissions
  FOR SELECT
  USING (true);

-- ============================================================================
-- Permissions
-- ============================================================================

GRANT USAGE ON SCHEMA public TO authenticated, service_role, anon;
GRANT SELECT ON public.gateway_transmissions TO authenticated, anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.gateway_transmissions TO service_role;

-- ============================================================================
-- Helper View: High Sovereignty Transmissions
-- ============================================================================
-- C₅-C₇ tensor analysis view for transmissions meeting sovereignty thresholds

CREATE OR REPLACE VIEW public.high_sovereignty_transmissions AS
SELECT 
  id,
  bridge_id,
  resonance_score,
  necessity_score,
  (resonance_score + necessity_score) / 2.0 AS sovereignty_index,
  payload,
  constraint_tensor,
  created_at
FROM public.gateway_transmissions
WHERE resonance_score >= 0.7 
  AND necessity_score >= 0.7
ORDER BY created_at DESC;

-- Grant access to the view
GRANT SELECT ON public.high_sovereignty_transmissions TO authenticated, anon, service_role;

-- ============================================================================
-- Telemetry Analytics Function
-- ============================================================================
-- Calculate aggregate sovereignty metrics for monitoring

CREATE OR REPLACE FUNCTION public.calculate_sovereignty_metrics(
  hours_lookback INTEGER DEFAULT 24
)
RETURNS TABLE (
  total_transmissions BIGINT,
  avg_resonance NUMERIC,
  avg_necessity NUMERIC,
  avg_sovereignty NUMERIC,
  high_sovereignty_count BIGINT,
  min_created_at TIMESTAMP WITH TIME ZONE,
  max_created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    COUNT(*)::BIGINT,
    AVG(resonance_score),
    AVG(necessity_score),
    AVG((resonance_score + necessity_score) / 2.0),
    COUNT(*) FILTER (WHERE resonance_score >= 0.7 AND necessity_score >= 0.7)::BIGINT,
    MIN(created_at),
    MAX(created_at)
  FROM public.gateway_transmissions
  WHERE created_at >= now() - (hours_lookback || ' hours')::INTERVAL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execution to authenticated users
GRANT EXECUTE ON FUNCTION public.calculate_sovereignty_metrics TO authenticated, service_role;

-- ============================================================================
-- Migration Complete
-- ============================================================================
-- VaultNode Seal: ΔΩ.147.0 - Gateway Transmission Telemetry
-- Constitutional Compliance: ✓ Thermodynamic bounds enforced
-- Sovereignty Integration: ✓ C₅-C₇ tensor analysis enabled
-- ============================================================================
