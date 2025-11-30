-- Create guardian_configs table for dynamic configuration
CREATE TABLE IF NOT EXISTS public.guardian_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT NOT NULL UNIQUE,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES auth.users(id)
);

-- Enable RLS
ALTER TABLE public.guardian_configs ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Service role has full access
CREATE POLICY "Service role full access" ON public.guardian_configs
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Authenticated users (Guardians) can read
CREATE POLICY "Authenticated read access" ON public.guardian_configs
    FOR SELECT
    TO authenticated
    USING (true);

-- Authenticated users (Guardians) can update if they have specific role (simplified to authenticated for now)
CREATE POLICY "Authenticated update access" ON public.guardian_configs
    FOR UPDATE
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- Anon has no access (internal config)
