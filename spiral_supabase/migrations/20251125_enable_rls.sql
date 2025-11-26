-- Migration: Enable RLS & Apply Policies
-- Sequence F Repair - Migration B

-- List of tables to secure
-- guardian_scarindex_history, assessments, witness_assignments, reputation_vectors,
-- council_judgments, stream_claims, emp_mint_queue, emp_ledger, ancestry_edges,
-- witness_claims, witness_events, scarcoin_bridge, vault_events

DO $$
DECLARE
    tables text[] := ARRAY[
        'guardian_scarindex_history',
        'assessments',
        'witness_assignments',
        'reputation_vectors',
        'council_judgments',
        'stream_claims',
        'emp_mint_queue',
        'emp_ledger',
        'ancestry_edges',
        'witness_claims',
        'witness_events',
        'scarcoin_bridge',
        'vault_events'
    ];
    t text;
BEGIN
    FOREACH t IN ARRAY tables LOOP
        -- Enable RLS
        EXECUTE format('ALTER TABLE IF EXISTS public.%I ENABLE ROW LEVEL SECURITY;', t);

        -- Policy: Public Read
        EXECUTE format('DROP POLICY IF EXISTS "Enable read access for all users" ON public.%I;', t);
        EXECUTE format('CREATE POLICY "Enable read access for all users" ON public.%I FOR SELECT USING (true);', t);

        -- Policy: Service Role Full Access
        EXECUTE format('DROP POLICY IF EXISTS "Enable all for service_role" ON public.%I;', t);
        EXECUTE format('CREATE POLICY "Enable all for service_role" ON public.%I USING (auth.role() = ''service_role'') WITH CHECK (auth.role() = ''service_role'');', t);
    END LOOP;
END$$;
