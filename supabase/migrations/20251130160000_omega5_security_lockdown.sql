-- Migration: omega5_security_lockdown
-- Description: Enables RLS on exposed tables and applies default-deny policies (with service_role bypass).

DO $$
DECLARE
    t text;
    tables text[] := ARRAY[
        'audit_surface_events',
        'cross_mesh_events',
        'mesh_temporal_fusion',
        'temporal_drift_log',
        'predictive_paradox_maps',
        'collapse_envelopes',
        'integration_lattice',
        'guardian_action_events',
        'guardian_action_playbooks',
        'future_chain',
        'future_chain_realizations',
        'continuation_metrics',
        'guardian_recalibration_log',
        'intervention_outcomes',
        'guardian_constraints',
        'core_constitution',
        'constraint_violations',
        'governance_amendments',
        'mint_burn_events',
        'autonomous_market_controller_state',
        'holonic_agent_actions',
        'holonic_liquidity_agents',
        'fmi1_semantic_mappings',
        'fmi1_coherence_metrics',
        'paradox_stress_events',
        'liquidity_equilibrium_state'
    ];
BEGIN
    FOREACH t IN ARRAY tables
    LOOP
        -- 1. Enable RLS
        EXECUTE format('ALTER TABLE IF EXISTS public.%I ENABLE ROW LEVEL SECURITY;', t);

        -- 2. Create Deny All Policy (for public/anon/authenticated by default)
        -- We check if policy exists to avoid errors on re-run
        IF NOT EXISTS (
            SELECT 1 FROM pg_policies WHERE tablename = t AND policyname = 'deny_all_' || t
        ) THEN
            EXECUTE format('CREATE POLICY "deny_all_%1$s" ON public.%1$I FOR ALL USING (false) WITH CHECK (false);', t);
        END IF;

        -- 3. Create Service Role Full Access Policy
        IF NOT EXISTS (
            SELECT 1 FROM pg_policies WHERE tablename = t AND policyname = 'service_role_full_access_' || t
        ) THEN
            EXECUTE format('CREATE POLICY "service_role_full_access_%1$s" ON public.%1$I FOR ALL USING (auth.role() = ''service_role'');', t);
        END IF;
    END LOOP;
END $$;
