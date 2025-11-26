-- Migration: Consistency Fixes
-- Sequence F Repair - Patch D

-- 1. Fix view_emp_velocity timestamp alignment
-- Dropping and recreating to ensure correct column usage
DROP VIEW IF EXISTS public.view_emp_velocity;

CREATE OR REPLACE VIEW public.view_emp_velocity AS
SELECT
    user_id,
    COUNT(*) as transaction_count,
    SUM(amount) as total_volume,
    MAX(minted_at) as last_active_at -- using minted_at as it exists in emp_ledger
FROM public.emp_ledger
GROUP BY user_id;

-- 2. Ensure Security Posture
-- Explicitly set SECURITY INVOKER for views to avoid unnecessary privilege escalation
ALTER VIEW public.view_emp_velocity SECURITY INVOKER;

-- Check other views if they exist and adjust
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_views WHERE viewname = 'witness_reputation_view') THEN
        ALTER VIEW public.witness_reputation_view SECURITY INVOKER;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_views WHERE viewname = 'witness_stream_pending_view') THEN
        ALTER VIEW public.witness_stream_pending_view SECURITY INVOKER;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_views WHERE viewname = 'witness_stream_complete_view') THEN
        ALTER VIEW public.witness_stream_complete_view SECURITY INVOKER;
    END IF;
END$$;
