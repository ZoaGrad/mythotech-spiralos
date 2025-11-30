-- Migration: AFR Integration
-- Description: Adds AFR-specific columns to existing monitoring tables.

-- 1. Add AFR-specific columns to guardian_telemetry_events
ALTER TABLE guardian_telemetry_events 
ADD COLUMN IF NOT EXISTS afr_flux_vector_norm DECIMAL(10,6),
ADD COLUMN IF NOT EXISTS afr_adjustment_imperative DECIMAL(10,6);

-- 2. Extend scarindex_calculations for AFR predictive modeling
ALTER TABLE scarindex_calculations 
ADD COLUMN IF NOT EXISTS afr_predicted_entropy DECIMAL(10,6),
ADD COLUMN IF NOT EXISTS afr_horizon_cycles INTEGER DEFAULT 10;

-- 3. Ensure system_events and governance_proposals exist (they should, but good to be safe or just rely on existing)
-- No changes needed if they exist.
