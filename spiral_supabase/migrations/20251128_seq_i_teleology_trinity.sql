-- Sequence I: Teleology Trinity Migration

-- 1. Create teleology_mandates table
CREATE TABLE IF NOT EXISTS teleology_mandates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    priority INTEGER NOT NULL,
    directive TEXT NOT NULL,
    constraints JSONB NOT NULL DEFAULT '[]',
    tau_component TEXT NOT NULL,
    tau_weight FLOAT NOT NULL,
    tau_certainty FLOAT NOT NULL,
    timescale TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    priority_locked BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create indexes
CREATE INDEX IF NOT EXISTS idx_teleology_mandates_code ON teleology_mandates(code);
CREATE INDEX IF NOT EXISTS idx_teleology_mandates_priority ON teleology_mandates(priority);
CREATE INDEX IF NOT EXISTS idx_teleology_mandates_active ON teleology_mandates(active);

-- 3. Insert Mandates
INSERT INTO teleology_mandates (code, priority, directive, constraints, tau_component, tau_weight, tau_certainty, timescale)
VALUES
    (
        'ΔΩ.I.1',
        1,
        'Preserve future coherence at all scales.',
        '[
            "No operation may reduce projected coherence by more than 0.07.",
            "All resolutions must prefer coherence-stable outcomes.",
            "Teleology weight overrides static governance heuristics."
        ]'::jsonb,
        'coherence_preservation',
        0.816,
        0.93,
        'indefinite'
    ),
    (
        'ΔΩ.I.2',
        2,
        'Continuously sharpen and clarify system identity.',
        '[
            "Mirror Layer reflections must include identity drift metrics.",
            "Paradox resolutions must prefer identity refinement paths.",
            "Identity history must be retained beyond 1,000,000 reflections."
        ]'::jsonb,
        'identity_refinement',
        0.572,
        0.88,
        'generational'
    ),
    (
        'ΔΩ.I.3',
        3,
        'Prefer minimal, beautiful, low-friction governance.',
        '[
            "When multiple resolutions are valid, choose the least complex.",
            "Permit ParadoxEngine to collapse decisions toward symmetry.",
            "Reject governance changes that significantly increase rule entropy."
        ]'::jsonb,
        'governance_elegance',
        0.427,
        0.79,
        'cyclical'
    )
ON CONFLICT (code) DO UPDATE SET
    priority = EXCLUDED.priority,
    directive = EXCLUDED.directive,
    constraints = EXCLUDED.constraints,
    tau_component = EXCLUDED.tau_component,
    tau_weight = EXCLUDED.tau_weight,
    tau_certainty = EXCLUDED.tau_certainty,
    timescale = EXCLUDED.timescale,
    updated_at = NOW();
