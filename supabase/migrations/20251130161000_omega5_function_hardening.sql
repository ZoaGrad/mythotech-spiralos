-- Migration: omega5_function_hardening
-- Description: Drops unsafe functions and sets secure search_path for all public functions.

-- 1. Drop unsafe functions
DROP FUNCTION IF EXISTS public.exec_sql(text);
DROP FUNCTION IF EXISTS public.raw_sql(text);

-- 2. Harden search_path for all functions in public schema
DO $$
DECLARE
    func_record record;
BEGIN
    FOR func_record IN 
        SELECT n.nspname as schema_name, p.proname as function_name, pg_get_function_identity_arguments(p.oid) as args
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public'
    LOOP
        BEGIN
            EXECUTE format('ALTER FUNCTION public.%I(%s) SET search_path = public, pg_temp;', func_record.function_name, func_record.args);
        EXCEPTION WHEN OTHERS THEN
            -- Ignore errors for functions we cannot alter (e.g. extension functions)
            RAISE NOTICE 'Skipping function %: %', func_record.function_name, SQLERRM;
        END;
    END LOOP;
END $$;
