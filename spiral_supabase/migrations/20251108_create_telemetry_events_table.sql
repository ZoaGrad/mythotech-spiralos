-- Create telemetry_events table for system monitoring
CREATE TABLE public.telemetry_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  success_state BOOLEAN NOT NULL DEFAULT true,
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create indexes for fast queries
CREATE INDEX idx_telemetry_events_agent_id ON public.telemetry_events(agent_id);
CREATE INDEX idx_telemetry_events_event_type ON public.telemetry_events(event_type);
CREATE INDEX idx_telemetry_events_created_at ON public.telemetry_events(created_at DESC);
CREATE INDEX idx_telemetry_events_success ON public.telemetry_events(success_state);

-- Enable RLS
ALTER TABLE public.telemetry_events ENABLE ROW LEVEL SECURITY;

-- RLS policy: service role can insert and select all
CREATE POLICY "Enable select for service role" ON public.telemetry_events
  FOR SELECT USING (true);

CREATE POLICY "Enable insert for service role" ON public.telemetry_events
  FOR INSERT WITH CHECK (true);

-- Create trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_telemetry_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER telemetry_updated_at_trigger
  BEFORE UPDATE ON public.telemetry_events
  FOR EACH ROW
  EXECUTE FUNCTION update_telemetry_updated_at();

-- Grant permissions to authenticated users (read-only) and service role (full)
GRANT USAGE ON SCHEMA public TO authenticated, service_role;
GRANT SELECT ON public.telemetry_events TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.telemetry_events TO service_role;
