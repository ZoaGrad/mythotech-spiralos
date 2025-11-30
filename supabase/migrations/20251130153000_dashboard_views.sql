-- Migration: dashboard_views
-- Description: Creates views for the Sovereignty Dashboard.

-- ============================================================================
-- 1. COHERENCE OVERVIEW
-- ============================================================================

CREATE OR REPLACE VIEW public.v_coherence_overview AS
SELECT
  cs.id,
  cs.timestamp,
  cs.scarindex_value,
  cs.panic_frame_triggered,
  -- cs.ache_value, -- Assuming these might be in signal_data or separate tables, adjusting to schema
  -- cs.soc_value,
  (cs.signal_data->>'ache_value')::numeric as ache_value,
  (cs.signal_data->>'soc_value')::numeric as soc_value,
  te.source_id AS telemetry_source,
  te.event_type AS telemetry_event_type
FROM public.coherence_signals cs
LEFT JOIN public.telemetry_events te
  ON cs.telemetry_event_id = te.id
ORDER BY cs.timestamp DESC;

-- ============================================================================
-- 2. GOVERNANCE PULSE
-- ============================================================================

CREATE OR REPLACE VIEW public.v_governance_pulse AS
SELECT
  gp.id AS proposal_id,
  gp.title,
  gp.status,
  gp.created_at,
  gp.proposer_id,
  COUNT(gv.id) AS vote_count,
  SUM(CASE WHEN gv.vote_choice = 'yes' THEN 1 ELSE 0 END) AS yes_votes,
  SUM(CASE WHEN gv.vote_choice = 'no' THEN 1 ELSE 0 END) AS no_votes
FROM public.governance_proposals gp
LEFT JOIN public.governance_votes gv
  ON gv.proposal_id = gp.id
GROUP BY gp.id, gp.title, gp.status, gp.created_at, gp.proposer_id
ORDER BY gp.created_at DESC;

-- ============================================================================
-- 3. GUARDIAN ACTIVITY
-- ============================================================================

CREATE OR REPLACE VIEW public.v_guardian_activity AS
SELECT
  gl.id,
  gl.timestamp,
  gl.agent_id,
  gl.action,
  gl.target,
  gl.result_status,
  gl.metadata
FROM public.guardian_logs gl
ORDER BY gl.timestamp DESC;

-- ============================================================================
-- 4. HOLOECONOMY SNAPSHOTS (STUBS)
-- ============================================================================

-- Stub for ScarCoin Mint Rate
CREATE OR REPLACE VIEW public.v_scarcoin_mint_rate AS
SELECT
    NOW() as timestamp,
    0 as mint_count,
    0 as total_amount
WHERE 1=0; -- Empty for now, replace with actual aggregation when table is populated

-- Stub for VaultNode Health
CREATE OR REPLACE VIEW public.v_vaultnode_health AS
SELECT
    NOW() as timestamp,
    0 as active_nodes,
    0 as total_nodes
WHERE 1=0; -- Empty for now

-- Permissions
GRANT SELECT ON public.v_coherence_overview TO anon, authenticated, service_role;
GRANT SELECT ON public.v_governance_pulse TO anon, authenticated, service_role;
GRANT SELECT ON public.v_guardian_activity TO anon, authenticated, service_role;
GRANT SELECT ON public.v_scarcoin_mint_rate TO anon, authenticated, service_role;
GRANT SELECT ON public.v_vaultnode_health TO anon, authenticated, service_role;
