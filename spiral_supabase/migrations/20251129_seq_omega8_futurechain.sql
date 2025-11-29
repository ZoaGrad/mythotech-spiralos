-- Sequence Ω.8: FutureChain Stabilization

-- 1. Table: future_chain
CREATE TABLE public.future_chain (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    
    lattice_id uuid NOT NULL,
    
    projected_timestep integer NOT NULL DEFAULT 1, -- 1 step into the future relative to lattice node
    projected_state jsonb NOT NULL, -- Snapshot of what the lattice node looks like in the future
    confidence numeric NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    
    guardian_influence text NULL, -- The action that influenced this projection
    
    CONSTRAINT fk_future_chain_lattice FOREIGN KEY (lattice_id)
        REFERENCES public.integration_lattice(id)
);

CREATE INDEX idx_future_chain_lattice_id ON future_chain(lattice_id);
CREATE INDEX idx_future_chain_created_at ON future_chain(created_at);

-- 2. Function: fn_extend_future_chain
-- Projects the lattice node one step into the future based on its current state and any Guardian action.

CREATE OR REPLACE FUNCTION public.fn_extend_future_chain(
    p_lattice_id uuid
) RETURNS uuid
LANGUAGE plpgsql
AS $$
DECLARE
    v_lattice integration_lattice%ROWTYPE;
    v_action guardian_action_events%ROWTYPE;
    v_new_id uuid;
    
    v_current_prob numeric;
    v_new_prob numeric;
    v_influence text := 'none';
    v_confidence numeric := 0.9;
BEGIN
    -- 1. Fetch Lattice Node
    SELECT * INTO v_lattice FROM integration_lattice WHERE id = p_lattice_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Lattice node % not found', p_lattice_id;
    END IF;
    
    -- 2. Fetch Guardian Action (if any)
    SELECT * INTO v_action FROM guardian_action_events WHERE lattice_id = p_lattice_id LIMIT 1;
    
    v_current_prob := v_lattice.collapse_probability;
    
    -- 3. Calculate Next State (Simple Predictive Model)
    IF v_action IS NOT NULL THEN
        v_influence := v_action.chosen_action;
        
        IF v_action.chosen_action = 'stabilize' THEN
            -- Strong reduction in collapse probability
            v_new_prob := v_current_prob * 0.5;
            v_confidence := 0.95;
        ELSIF v_action.chosen_action = 'alert' THEN
            -- Mild reduction (awareness effect)
            v_new_prob := v_current_prob * 0.9;
            v_confidence := 0.85;
        ELSIF v_action.chosen_action = 'escalate' THEN
            -- Drastic reduction or containment (but high uncertainty)
            v_new_prob := v_current_prob * 0.3;
            v_confidence := 0.60;
        ELSE
            -- 'observe' or others: Natural drift (slight increase in entropy)
            v_new_prob := LEAST(1.0, v_current_prob * 1.05);
            v_confidence := 0.90;
        END IF;
    ELSE
        -- No action: Natural drift
        v_new_prob := LEAST(1.0, v_current_prob * 1.05);
        v_confidence := 0.80;
    END IF;
    
    -- 4. Insert Projection
    INSERT INTO future_chain (
        lattice_id,
        projected_timestep,
        projected_state,
        confidence,
        guardian_influence
    ) VALUES (
        v_lattice.id,
        1, -- For now, we just project t+1. A real recursive system would loop this.
        jsonb_build_object(
            'original_probability', v_current_prob,
            'projected_probability', v_new_prob,
            'lattice_state', v_lattice.lattice_state,
            'delta', v_new_prob - v_current_prob
        ),
        v_confidence,
        v_influence
    )
    RETURNING id INTO v_new_id;
    
    RETURN v_new_id;
END;
$$;
