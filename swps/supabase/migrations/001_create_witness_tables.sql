-- SWPS-1.0 Core Schema
-- witness modes
CREATE TYPE witness_mode AS ENUM ('stream', 'crucible', 'council');

-- participants
CREATE TABLE IF NOT EXISTS participants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  handle TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- participant reputation vectors
CREATE TABLE IF NOT EXISTS participant_reputation (
  participant_id UUID PRIMARY KEY REFERENCES participants(id) ON DELETE CASCADE,
  velocity NUMERIC NOT NULL DEFAULT 0,
  density NUMERIC NOT NULL DEFAULT 0,
  gravity NUMERIC NOT NULL DEFAULT 0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- witness events
CREATE TABLE IF NOT EXISTS witness_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  initiator UUID REFERENCES participants(id) ON DELETE SET NULL,
  target UUID REFERENCES participants(id) ON DELETE SET NULL,
  mode witness_mode NOT NULL,
  payload JSONB NOT NULL,
  emp_stake NUMERIC NOT NULL DEFAULT 0,
  reputation_cost NUMERIC NOT NULL DEFAULT 0,
  resonance NUMERIC NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','assigned','assessing','finalized','escalated','rejected')),
  required_witnesses INT NOT NULL DEFAULT 3,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- stake constraint for crucible
ALTER TABLE witness_events
  ADD CONSTRAINT crucible_requires_stake CHECK (
    (mode <> 'crucible') OR (emp_stake > 0)
  );

-- ancestry edges
CREATE TABLE IF NOT EXISTS ancestry_edges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  parent_event UUID REFERENCES witness_events(id) ON DELETE CASCADE,
  child_event UUID REFERENCES witness_events(id) ON DELETE CASCADE,
  weight NUMERIC NOT NULL DEFAULT 1,
  permanence BOOLEAN NOT NULL DEFAULT FALSE,
  decay_rate NUMERIC,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- assessments
CREATE TABLE IF NOT EXISTS assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID REFERENCES witness_events(id) ON DELETE CASCADE,
  witness_id UUID REFERENCES participants(id) ON DELETE CASCADE,
  verdict TEXT NOT NULL,
  notes TEXT,
  score NUMERIC NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(event_id, witness_id)
);

-- assignments
CREATE TABLE IF NOT EXISTS assignments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID REFERENCES witness_events(id) ON DELETE CASCADE,
  witness_id UUID REFERENCES participants(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'assigned' CHECK (status IN ('assigned','submitted','expired')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(event_id, witness_id)
);

CREATE INDEX IF NOT EXISTS idx_witness_events_mode ON witness_events(mode);
CREATE INDEX IF NOT EXISTS idx_assessments_event ON assessments(event_id);
CREATE INDEX IF NOT EXISTS idx_assignments_event ON assignments(event_id);
CREATE INDEX IF NOT EXISTS idx_ancestry_edges_parent ON ancestry_edges(parent_event);
