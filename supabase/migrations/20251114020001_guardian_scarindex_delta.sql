

-- Phase 8.2: ScarIndex Delta Engine
-- Creates guardian_scarindex_current and guardian_scarindex_history tables

-- ============================================================================
-- TABLE: guardian_scarindex_current
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.guardian_scarindex_current (
  -- Identity
  bridge_id UUID PRIMARY KEY REFERENCES public.bridge_nodes(id) ON DELETE CASCADE,
  
  -- ScarIndex Value
  scar_value NUMERIC(5,4) CHECK (scar_value >= 0 AND scar_value <= 100),
  
  -- Metadata
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  
  -- Timestamps
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- TABLE: guardian_scarindex_history
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.guardian_scarindex_history (
  -- Identity
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bridge_id UUID REFERENCES public.bridge_nodes(id) ON DELETE CASCADE,
  
  -- ScarIndex Value & Delta
  scar_value NUMERIC(5,4) CHECK (scar_value >= 0 AND scar_value <= 100),
  delta NUMERIC(5,4),
  
  -- Source & Context
  source TEXT NOT NULL DEFAULT 'telemetry_normalize',
  
  -- Metadata
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  
  -- Timestamp
  timestamp TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_scarindex_history_bridge 
  ON public.guardian_scarindex_history(bridge_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_scarindex_history_timestamp 
  ON public.guardian_scarindex_history(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_scarindex_history_source 
  ON public.guardian_scarindex_history(source);

-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================
ALTER TABLE public.guardian_scarindex_current ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.guardian_scarindex_history ENABLE ROW LEVEL SECURITY;

-- Service role has full access
CREATE POLICY "Service role full access to scarindex current" 
  ON public.guardian_scarindex_current
  FOR ALL 
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role full access to scarindex history" 
  ON public.guardian_scarindex_history
  FOR ALL 
  USING (true)
  WITH CHECK (true);

-- Authenticated users can read
CREATE POLICY "Authenticated read access to scarindex current" 
  ON public.guardian_scarindex_current
  FOR SELECT 
  USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated read access to scarindex history" 
  ON public.guardian_scarindex_history
  FOR SELECT 
  USING (auth.role() = 'authenticated');

-- ============================================================================
-- GRANTS
-- ============================================================================
GRANT USAGE ON SCHEMA public TO authenticated, service_role;
GRANT SELECT ON public.guardian_scarindex_current TO authenticated;
GRANT ALL ON public.guardian_scarindex_current TO service_role;
GRANT SELECT ON public.guardian_scarindex_history TO authenticated;
GRANT ALL ON public.guardian_scarindex_history TO service_role;

-- ============================================================================
-- FUNCTION: scarindex_delta
-- ============================================================================
CREATE OR REPLACE FUNCTION public.scarindex_delta(
  p_bridge_id UUID,
  p_new_value NUMERIC,
  p_source TEXT DEFAULT 'telemetry_normalize',
  p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS JSONB AS $$
DECLARE
  v_old_value NUMERIC;
  v_delta NUMERIC;
  v_result JSONB;
BEGIN
  -- Get current value
  SELECT scar_value INTO v_old_value
  FROM public.guardian_scarindex_current
  WHERE bridge_id = p_bridge_id;
  
  -- Calculate delta
  IF v_old_value IS NULL THEN
    v_old_value := 0.5; -- default baseline
    v_delta := p_new_value - v_old_value;
  ELSE
    v_delta := p_new_value - v_old_value;
  END IF;
  
  -- Update or insert current value (idempotent)
  INSERT INTO public.guardian_scarindex_current (bridge_id, scar_value, updated_at)
  VALUES (p_bridge_id, p_new_value, NOW())
  ON CONFLICT (bridge_id) 
  DO UPDATE SET 
    scar_value = p_new_value,
    updated_at = NOW();
  
  -- Insert history record
  INSERT INTO public.guardian_scarindex_history (bridge_id, scar_value, delta, source, metadata)
  VALUES (p_bridge_id, p_new_value, v_delta, p_source, p_metadata);
  
  -- Return result
  v_result := jsonb_build_object(
    'bridge_id', p_bridge_id,
    'old_value', v_old_value,
    'new_value', p_new_value,
    'delta', v_delta,
    'source', p_source
  );
  
  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- COMMENTS
-- ============================================================================
COMMENT ON TABLE public.guardian_scarindex_current IS 
  'Phase 8.2: Current ScarIndex values for each bridge';

COMMENT ON TABLE public.guardian_scarindex_history IS 
  'Phase 8.2: Historical ScarIndex values and deltas';

COMMENT ON FUNCTION public.scarindex_delta IS 
  'Phase 8.2: Idempotent function to update ScarIndex and record delta';

