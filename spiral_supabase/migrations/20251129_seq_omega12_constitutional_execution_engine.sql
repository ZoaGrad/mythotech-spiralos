-- Sequence Ω.12: Constitutional Execution Engine
-- Migration: 20251129_seq_omega12_constitutional_execution_engine.sql

-- 1. Create action_rewrites table
CREATE TABLE IF NOT EXISTS public.action_rewrites (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  original_action jsonb NOT NULL,
  rewritten_action jsonb NOT NULL,
  reason text NOT NULL,
  constraint_id text NOT NULL,
  notes text
);

-- 2. Create constitutional_execution_log table
CREATE TABLE IF NOT EXISTS public.constitutional_execution_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp timestamptz NOT NULL DEFAULT timezone('utc', now()),
  action_id uuid,
  executed boolean NOT NULL,
  vetoed boolean NOT NULL,
  rewritten boolean NOT NULL,
  validation_path jsonb NOT NULL,
  applied_constraints jsonb NOT NULL,
  notes text
);

-- 3. Enable RLS (Optional but good practice, keeping open for internal use for now)
ALTER TABLE public.action_rewrites ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.constitutional_execution_log ENABLE ROW LEVEL SECURITY;

-- 4. Create policies (Allow read/write for service role and authenticated users for now)
CREATE POLICY "Allow all access for service role" ON public.action_rewrites
  FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all access for service role" ON public.constitutional_execution_log
  FOR ALL USING (true) WITH CHECK (true);

-- 5. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_action_rewrites_created_at ON public.action_rewrites(created_at);
CREATE INDEX IF NOT EXISTS idx_execution_log_timestamp ON public.constitutional_execution_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_execution_log_action_id ON public.constitutional_execution_log(action_id);
