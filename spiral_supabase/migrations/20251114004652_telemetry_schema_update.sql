-- Phase 7.2: Update telemetry_events schema for gateway integration
-- Make agent_id nullable and add source/payload columns

-- 1. Make agent_id nullable (for gateway telemetry)
ALTER TABLE public.telemetry_events
  ALTER COLUMN agent_id DROP NOT NULL;

-- 2. Add source column if not exists
ALTER TABLE public.telemetry_events
  ADD COLUMN IF NOT EXISTS source text;

-- 3. Add payload column if not exists (separate from metadata)
ALTER TABLE public.telemetry_events
  ADD COLUMN IF NOT EXISTS payload jsonb DEFAULT '{}'::jsonb;

-- 4. Create index on source
CREATE INDEX IF NOT EXISTS idx_telemetry_source
  ON public.telemetry_events (source);

-- 5. Add comments
COMMENT ON COLUMN public.telemetry_events.agent_id IS 'Agent identifier (nullable for gateway telemetry)';
COMMENT ON COLUMN public.telemetry_events.source IS 'Telemetry source (e.g., discord_bot, github_webhook)';
COMMENT ON COLUMN public.telemetry_events.payload IS 'Event-specific payload data';
