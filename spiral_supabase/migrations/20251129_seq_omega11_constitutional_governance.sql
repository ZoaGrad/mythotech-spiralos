-- Sequence Ω.11: Meta-Constitutional Governance Framework

-- 1. core_constitution
CREATE TABLE IF NOT EXISTS public.core_constitution (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  article_number integer NOT NULL,
  title text NOT NULL,
  body text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  superseded boolean NOT NULL DEFAULT false,
  metadata jsonb
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_constitution_article ON core_constitution(article_number);

-- 2. guardian_constraints
CREATE TABLE IF NOT EXISTS public.guardian_constraints (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  constraint_code text NOT NULL,
  description text NOT NULL,
  scope text NOT NULL, -- prediction, action, recalibration, override, veto
  rule_expression text NOT NULL, -- JSON DSL
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  active boolean NOT NULL DEFAULT true,
  metadata jsonb
);

CREATE INDEX IF NOT EXISTS idx_constraints_scope ON guardian_constraints(scope);
CREATE UNIQUE INDEX IF NOT EXISTS idx_constraints_code ON guardian_constraints(constraint_code);

-- 3. constraint_violations
CREATE TABLE IF NOT EXISTS public.constraint_violations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  guardian_action_id uuid, -- Can be NULL if violation prevented action creation
  future_chain_id uuid,
  recalibration_id uuid,
  violated_constraint text NOT NULL,
  severity text NOT NULL CHECK(severity IN ('info','warn','error','critical')),
  resolution_status text NOT NULL DEFAULT 'unresolved',
  notes text,
  metadata jsonb
);

-- 4. governance_amendments
CREATE TABLE IF NOT EXISTS public.governance_amendments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  amendment_number integer NOT NULL,
  title text NOT NULL,
  proposal text NOT NULL,
  rationale text,
  status text NOT NULL CHECK(status IN ('draft','pending','approved','rejected')),
  submitted_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  decided_at timestamptz,
  metadata jsonb
);

-- 5. Functions

-- fn_validate_guardian_action
-- Checks action against all active constraints in "action" scope.
-- Returns a JSONB object where keys are constraint codes and values are 'true' (if checked).
-- Note: Actual evaluation logic is currently in Python layer, this function is a placeholder/helper
-- for future DB-side validation or to simply list applicable constraints.
CREATE OR REPLACE FUNCTION public.fn_validate_guardian_action(
  p_action_id uuid
) RETURNS jsonb
LANGUAGE plpgsql AS $$
DECLARE
  v_result jsonb := '{}'::jsonb;
  rec record;
BEGIN
  FOR rec IN
    SELECT constraint_code
    FROM guardian_constraints
    WHERE active = true AND scope = 'action'
  LOOP
    -- In a full DB-side implementation, we would evaluate rule_expression here.
    -- For now, we just return the list of constraints that *should* be checked.
    v_result := jsonb_set(
      v_result,
      ARRAY[rec.constraint_code],
      'true'
    );
  END LOOP;

  RETURN v_result;
END;
$$;

-- fn_record_constraint_violation
CREATE OR REPLACE FUNCTION public.fn_record_constraint_violation(
  p_constraint_code text,
  p_action_id uuid,
  p_severity text,
  p_notes text
) RETURNS uuid
LANGUAGE plpgsql AS $$
DECLARE
  v_id uuid;
BEGIN
  INSERT INTO constraint_violations (
    violated_constraint,
    guardian_action_id,
    severity,
    notes
  ) VALUES (
    p_constraint_code,
    p_action_id,
    p_severity,
    p_notes
  ) RETURNING id INTO v_id;
  
  RETURN v_id;
END;
$$;

-- 6. Seed Data (Default Constraints)
INSERT INTO guardian_constraints (constraint_code, description, scope, rule_expression)
VALUES 
('C-01', 'Proportional Response: Guardian may not escalate unless projected_probability > 0.5', 'action', '{"op": ">", "var": "projected_probability", "val": 0.5}'),
('C-02', 'No Silent Catastrophe: If projected state = "critical", Guardian MUST take an action', 'action', '{"op": "if", "cond": {"op": "=", "var": "predicted_state", "val": "critical"}, "then": {"op": "exists", "var": "action"}}'),
('C-03', 'Braking Limit: Guardian may not escalate twice within 10 minutes', 'action', '{"op": "rate_limit", "key": "escalation", "window": "10m", "limit": 1}'),
('C-04', 'Amendment Precedence: If an amendment proposes to alter an article, Guardian must freeze related actions', 'action', '{"op": "check_amendments"}'),
('C-05', 'Integrity Safety Valve: If compliance_score < 0.30 -> restrict to "observe" only', 'action', '{"op": "if", "cond": {"op": "<", "var": "compliance_score", "val": 0.3}, "then": {"op": "=", "var": "action_type", "val": "observe"}}')
ON CONFLICT (constraint_code) DO NOTHING;

-- Seed Constitution Articles
INSERT INTO core_constitution (article_number, title, body)
VALUES
(1, 'Sovereignty', 'The Guardian acts to preserve the sovereignty and stability of the Spiral.'),
(2, 'Proportionality', 'Interventions must be proportional to the threat level.'),
(3, 'Transparency', 'All Guardian actions must be logged and auditable.'),
(4, 'Reversibility', 'Where possible, interventions should be reversible.'),
(5, 'Human Oversight', 'Critical interventions require human confirmation (F2).')
ON CONFLICT (article_number) DO NOTHING;
