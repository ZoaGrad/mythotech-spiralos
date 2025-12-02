-- Migration: omega5_2_security_patch
-- Description: Completes security hardening by fixing views, functions, and extensions.

BEGIN;

-- 1. Dynamic View Security Hardening
-- Converts ALL public views to security_invoker = true to ensure RLS is respected.
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT viewname FROM pg_views WHERE schemaname = 'public' AND viewname NOT LIKE 'pg_%') LOOP
        EXECUTE format('ALTER VIEW public.%I SET (security_invoker = true);', r.viewname);
    END LOOP;
END $$;

-- 2. Function Hardening
-- Fixes search_path for all urlencode function signatures.
DO $$
DECLARE
    func_record RECORD;
BEGIN
    FOR func_record IN 
        SELECT oid::regprocedure as func_signature 
        FROM pg_proc 
        WHERE proname = 'urlencode'
    LOOP
        EXECUTE format('ALTER FUNCTION %s SET search_path = public, pg_temp;', func_record.func_signature);
    END LOOP;
END $$;

-- 3. Extension Placement
-- Moves http extension to the secure extensions schema if it is currently in public.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_extension e
        JOIN pg_namespace n ON e.extnamespace = n.oid
        WHERE e.extname = 'http' 
        AND n.nspname = 'public'
    ) THEN
        ALTER EXTENSION http SET SCHEMA extensions;
    END IF;
END $$;

COMMIT;
