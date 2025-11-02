-- ═══════════════════════════════════════════════════════════════════════════
-- Comet Gate Migration - Issue #10 Fix
-- ═══════════════════════════════════════════════════════════════════════════
-- Version: 1.0.1-comet-gate
-- Date: 2025-11-01
-- Description: Fix schema drift and add idempotency safeguards for webhook processing
-- ═══════════════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────────────
-- PART 1: Schema Fixes - Default Values for Binary Payloads
-- ───────────────────────────────────────────────────────────────────────────

-- Ensure github_webhooks table has proper default for payload
ALTER TABLE IF EXISTS public.github_webhooks 
  ALTER COLUMN payload SET DEFAULT '{}'::JSONB;

-- Ensure ache_events table has proper default for content
ALTER TABLE IF EXISTS public.ache_events 
  ALTER COLUMN content SET DEFAULT '{}'::JSONB;

-- Ensure scarindex_calculations table has proper defaults
ALTER TABLE IF EXISTS public.scarindex_calculations 
  ALTER COLUMN metadata SET DEFAULT '{}'::JSONB;

-- ───────────────────────────────────────────────────────────────────────────
-- PART 2: Idempotent Table Creation - scar_index lookup table
-- ───────────────────────────────────────────────────────────────────────────

-- Create scar_index table if it doesn't exist (for fast webhook lookups)
CREATE TABLE IF NOT EXISTS public.scar_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- External identifier (for idempotent operations)
    external_id TEXT NOT NULL UNIQUE,
    external_source TEXT NOT NULL, -- 'github_commit', 'github_issue', etc.
    
    -- Reference to scarindex calculation
    scarindex_calculation_id UUID REFERENCES public.scarindex_calculations(id) ON DELETE SET NULL,
    
    -- Cached scarindex value for fast lookup
    scarindex_value DECIMAL(10, 6),
    
    -- Processing status
    processing_status TEXT NOT NULL DEFAULT 'pending' 
      CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    
    -- Error tracking
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB
);

-- ───────────────────────────────────────────────────────────────────────────
-- PART 3: Performance Indexes
-- ───────────────────────────────────────────────────────────────────────────

-- Index for fast lookup by external_id (used by webhook to check if already processed)
CREATE INDEX IF NOT EXISTS idx_scar_index_external_id 
  ON public.scar_index(external_id);

-- Index for fast lookup by source
CREATE INDEX IF NOT EXISTS idx_scar_index_external_source 
  ON public.scar_index(external_source);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_scar_index_status 
  ON public.scar_index(processing_status);

-- Compound index for webhook queries
CREATE INDEX IF NOT EXISTS idx_scar_index_source_status 
  ON public.scar_index(external_source, processing_status);

-- ───────────────────────────────────────────────────────────────────────────
-- PART 4: Update Trigger for updated_at
-- ───────────────────────────────────────────────────────────────────────────

-- Create trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add trigger to scar_index table
DROP TRIGGER IF EXISTS update_scar_index_updated_at ON public.scar_index;
CREATE TRIGGER update_scar_index_updated_at
    BEFORE UPDATE ON public.scar_index
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ───────────────────────────────────────────────────────────────────────────
-- PART 5: Row-Level Security
-- ───────────────────────────────────────────────────────────────────────────

-- Enable RLS
ALTER TABLE public.scar_index ENABLE ROW LEVEL SECURITY;

-- Public read policy
CREATE POLICY "public_read_scar_index" ON public.scar_index
    FOR SELECT USING (TRUE);

-- Service role write policy
CREATE POLICY "service_write_scar_index" ON public.scar_index
    FOR ALL USING (auth.role() = 'service_role');

-- ───────────────────────────────────────────────────────────────────────────
-- PART 6: Comments
-- ───────────────────────────────────────────────────────────────────────────

COMMENT ON TABLE public.scar_index IS 'Fast lookup table for webhook idempotency and duplicate prevention';
COMMENT ON COLUMN public.scar_index.external_id IS 'Unique external identifier (e.g., commit SHA, issue number)';
COMMENT ON COLUMN public.scar_index.external_source IS 'Source of the external event';
COMMENT ON COLUMN public.scar_index.processing_status IS 'Current processing status';

-- ═══════════════════════════════════════════════════════════════════════════
-- END OF MIGRATION
-- ═══════════════════════════════════════════════════════════════════════════
