CREATE TABLE IF NOT EXISTS public.council_judgments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    claim_id UUID,
    claim_summary TEXT,
    council_payload JSONB NOT NULL,
    recommended_verdict TEXT CHECK (recommended_verdict IN ('verified', 'rejected', 'flagged')),
    sovereign_confidence NUMERIC,
    ache_weight NUMERIC,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS council_judgments_claim_id_idx ON public.council_judgments (claim_id);
CREATE INDEX IF NOT EXISTS council_judgments_created_at_idx ON public.council_judgments (created_at DESC);
