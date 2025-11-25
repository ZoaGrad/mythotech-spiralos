-- ΔΩ.12: Views for projecting external telemetry into ScarIndex-compatible lenses
CREATE OR REPLACE VIEW public.external_scarindex_view AS
SELECT
    witness_id,
    source,
    event_type,
    trust_score,
    timestamp AS received_at,
    ingested_at,
    payload,
    metadata
FROM public.external_witness_events;
