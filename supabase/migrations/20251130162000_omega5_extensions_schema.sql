-- Migration: omega5_extensions_schema
-- Description: Moves system extensions to a dedicated schema to clean up public.

CREATE SCHEMA IF NOT EXISTS extensions;

-- Move extensions if they exist
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
        ALTER EXTENSION pgcrypto SET SCHEMA extensions;
    END IF;

    -- http extension does not support SET SCHEMA, skipping
    -- IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'http') THEN
    --    ALTER EXTENSION http SET SCHEMA extensions;
    -- END IF;

    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        ALTER EXTENSION vector SET SCHEMA extensions;
    END IF;
END $$;

-- Grant usage on extensions schema to public (so functions can still be called if needed, or restrict as necessary)
GRANT USAGE ON SCHEMA extensions TO PUBLIC;
