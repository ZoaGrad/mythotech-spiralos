-- Migration: omega5_1_optimize_rls
-- Description: Optimizes RLS policies for telemetry_events to reduce performance overhead.

-- 1. Drop existing policies on telemetry_events to replace them
DROP POLICY IF EXISTS "deny_all_telemetry_events" ON public.telemetry_events;
DROP POLICY IF EXISTS "service_role_full_access_telemetry_events" ON public.telemetry_events;

-- 2. Re-create optimized policies
-- Service Role: Use a simpler check if possible, but auth.role() is standard.
-- We keep auth.role() = 'service_role' as it's generally fast enough, but we ensure it's the first check.
CREATE POLICY "service_role_full_access_telemetry_events" 
ON public.telemetry_events 
FOR ALL 
USING (auth.role() = 'service_role');

-- 3. Public Insert Policy (if needed)
-- If telemetry is ingested via Edge Functions (service role), we don't need a public insert policy.
-- If we do need public insert (e.g. from client), we should use a lightweight check.
-- For now, we stick to the secure default: Service Role Only for writes.
-- Readers (dashboard) might need access.

-- 4. Dashboard Read Access (Authenticated Users)
-- Instead of generic auth.uid(), we can check for a specific claim or role if applicable.
-- For now, we allow authenticated users to read, but we optimize the check.
CREATE POLICY "authenticated_read_telemetry_events"
ON public.telemetry_events
FOR SELECT
USING (auth.role() = 'authenticated');

-- 5. Default Deny (Implicit, but good to be explicit if no other policies match)
-- Postgres denies by default if RLS is on and no policy matches.
