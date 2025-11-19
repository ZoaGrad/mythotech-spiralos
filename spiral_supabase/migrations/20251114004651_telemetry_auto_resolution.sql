-- Phase 7.2: Telemetry Auto-Resolution Upgrade
-- Add bridge mapping columns to telemetry_events

-- 1. Extend telemetry_events with bridge metadata
ALTER TABLE public.telemetry_events
  ADD COLUMN IF NOT EXISTS bridge_id uuid,
  ADD COLUMN IF NOT EXISTS gateway_key text;

-- 2. Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_telemetry_bridge_id
  ON public.telemetry_events (bridge_id);

CREATE INDEX IF NOT EXISTS idx_telemetry_gateway_key
  ON public.telemetry_events (gateway_key);

-- 3. Add comment for documentation
COMMENT ON COLUMN public.telemetry_events.bridge_id IS 'Auto-resolved from gateway_key via bridge_gateways lookup';
COMMENT ON COLUMN public.telemetry_events.gateway_key IS 'Gateway identifier used for bridge resolution';
