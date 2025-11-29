-- Sequence Ω.9: Continuation Engine

-- 1. Table: future_chain_realizations
CREATE TABLE public.future_chain_realizations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    
    future_chain_id uuid NOT NULL,
    
    realized_state text NOT NULL, -- 'stable', 'critical', 'collapsed'
    realized_collapse boolean NOT NULL DEFAULT false,
    
    accuracy_score numeric NOT NULL CHECK (accuracy_score >= 0 AND accuracy_score <= 1),
    notes text NULL,
    
    CONSTRAINT fk_realization_chain FOREIGN KEY (future_chain_id)
        REFERENCES public.future_chain(id)
);

CREATE INDEX idx_realizations_chain_id ON future_chain_realizations(future_chain_id);

-- 2. Table: continuation_metrics
-- Stores aggregated health metrics for the system over time windows
CREATE TABLE public.continuation_metrics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    computed_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    
    window_start timestamptz NOT NULL,
    window_end timestamptz NOT NULL,
    
    total_predictions integer NOT NULL,
    accurate_predictions integer NOT NULL,
    calibration_error numeric NOT NULL, -- Lower is better
    guardian_trust_index numeric NOT NULL, -- 0 to 1
    
    metadata jsonb DEFAULT '{}'::jsonb
);

-- 3. Function: fn_record_future_realization
CREATE OR REPLACE FUNCTION public.fn_record_future_realization(
    p_future_chain_id uuid,
    p_realized_state text,
    p_realized_collapse boolean,
    p_notes text DEFAULT NULL
) RETURNS uuid
LANGUAGE plpgsql
AS $$
DECLARE
    v_chain future_chain%ROWTYPE;
    v_predicted_prob numeric;
    v_accuracy numeric;
    v_new_id uuid;
BEGIN
    -- 1. Get Prediction
    SELECT * INTO v_chain FROM future_chain WHERE id = p_future_chain_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'FutureChain node % not found', p_future_chain_id;
    END IF;
    
    -- 2. Calculate Accuracy
    -- If realized_collapse is true, predicted_prob should have been high.
    -- If realized_collapse is false, predicted_prob should have been low.
    -- Accuracy = 1 - |predicted - realized|
    
    v_predicted_prob := (v_chain.projected_state->>'projected_probability')::numeric;
    
    IF p_realized_collapse THEN
        v_accuracy := v_predicted_prob; -- If prob was 0.9 and it collapsed, accuracy is 0.9. If prob was 0.1, accuracy is 0.1 (bad).
    ELSE
        v_accuracy := 1.0 - v_predicted_prob; -- If prob was 0.1 and didn't collapse, accuracy is 0.9.
    END IF;
    
    -- 3. Insert Realization
    INSERT INTO future_chain_realizations (
        future_chain_id,
        realized_state,
        realized_collapse,
        accuracy_score,
        notes
    ) VALUES (
        p_future_chain_id,
        p_realized_state,
        p_realized_collapse,
        v_accuracy,
        p_notes
    )
    RETURNING id INTO v_new_id;
    
    RETURN v_new_id;
END;
$$;

-- 4. View: view_continuation_health
CREATE OR REPLACE VIEW public.view_continuation_health AS
SELECT
    f.id as chain_id,
    f.created_at as predicted_at,
    f.projected_timestep,
    (f.projected_state->>'projected_probability')::numeric as predicted_probability,
    f.guardian_influence,
    r.created_at as realized_at,
    r.realized_state,
    r.realized_collapse,
    r.accuracy_score
FROM
    future_chain f
LEFT JOIN
    future_chain_realizations r ON f.id = r.future_chain_id;
