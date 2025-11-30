-- Migration: omega5_1_harden_functions
-- Description: Hardens remaining functions (urlencode) by setting explicit search_path.

DO $$
DECLARE
    func_record record;
BEGIN
    -- Find all variants of urlencode in public schema
    FOR func_record IN 
        SELECT n.nspname as schema_name, p.proname as function_name, pg_get_function_identity_arguments(p.oid) as args
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public' AND p.proname = 'urlencode'
    LOOP
        BEGIN
            EXECUTE format('ALTER FUNCTION public.%I(%s) SET search_path = public, pg_temp;', func_record.function_name, func_record.args);
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Skipping function %: %', func_record.function_name, SQLERRM;
        END;
    END LOOP;
END $$;
