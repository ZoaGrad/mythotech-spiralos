-- Migration: omega5_1_secure_views
-- Description: Converts Security Definer views to Security Invoker to respect RLS policies.

DO $$
DECLARE
    v text;
    views text[] := ARRAY[
        'view_council_drift',
        'view_causality_tension',
        'view_temporal_drift_status',
        'view_ache_resonance',
        'view_continuation_health',
        'view_collapse_horizon_surface',
        'view_causal_links',
        'anomaly_status',
        'v_holonic_agent_leaderboard',
        'v_vaultnode_health',
        'v_coherence_overview',
        'v_governance_pulse',
        'v_guardian_activity',
        'daily_sovereignty_metrics',
        'guardian_status',
        'high_sovereignty_transmissions',
        'v_amc_performance',
        'v_consensus_status',
        'v_active_panic_frames'
    ];
BEGIN
    FOREACH v IN ARRAY views
    LOOP
        -- Check if view exists before altering
        IF EXISTS (SELECT 1 FROM pg_views WHERE schemaname = 'public' AND viewname = v) THEN
            EXECUTE format('ALTER VIEW public.%I SET (security_invoker = true);', v);
        END IF;
    END LOOP;
END $$;
