-- spiral_supabase/migrations/20251204_phase_2_0_constitutional_coupling.sql
-- Constitutional Cognitive Context & Amendment Tables

CREATE TABLE constitutional_cognitive_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    
    -- ARIA Perceptual Frame
    aria_perceptual_frame JSONB NOT NULL DEFAULT '{}'::jsonb,
    noticed_patterns TEXT[] DEFAULT '{}',
    framing_narrative TEXT,
    
    -- AFR Thermodynamic State
    afr_adjustment_imperative DECIMAL(3,2),
    afr_flux_vector_norm DECIMAL(10,6),
    predicted_entropy_at_horizon DECIMAL(10,6),
    
    -- System State Synthesis
    current_ache_level DECIMAL(3,2),
    entropy_horizon_cycles INTEGER,
    liquidity_regime TEXT,
    civic_telemetry JSONB DEFAULT '{}'::jsonb,
    risk_envelope JSONB DEFAULT '{}'::jsonb,
    
    -- Constitutional Implications
    proposed_amendment_type TEXT,
    constitutional_rationale TEXT,
    impact_projection JSONB DEFAULT '{}'::jsonb,
    
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'proposed', 'ratified', 'rejected'))
);

CREATE TABLE constitutional_amendments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ccc_id UUID REFERENCES constitutional_cognitive_context(id),
    
    amendment_number INTEGER,
    title TEXT NOT NULL,
    proposal_text TEXT NOT NULL,
    rationale TEXT NOT NULL,
    
    -- Trigger Conditions
    trigger_conditions JSONB NOT NULL DEFAULT '{}'::jsonb,
    afr_threshold DECIMAL(3,2),
    scarindex_derivative_threshold DECIMAL(5,4),
    
    -- Governance Pathway
    status TEXT DEFAULT 'proposed' CHECK (status IN ('proposed', 'under_review', 'ratified', 'rejected', 'sunset')),
    guardian_review_required BOOLEAN DEFAULT true,
    external_validation_required BOOLEAN DEFAULT false,
    
    -- Temporal Constraints
    proposed_at TIMESTAMPTZ DEFAULT NOW(),
    decided_at TIMESTAMPTZ,
    effective_after TIMESTAMPTZ,
    sunset_at TIMESTAMPTZ,
    
    -- Impact Tracking
    pre_amendment_state JSONB DEFAULT '{}'::jsonb,
    post_amendment_state JSONB DEFAULT '{}'::jsonb,
    effectiveness_score DECIMAL(3,2)
);

-- Enable RLS
ALTER TABLE constitutional_cognitive_context ENABLE ROW LEVEL SECURITY;
ALTER TABLE constitutional_amendments ENABLE ROW LEVEL SECURITY;

-- Create indexes for performance
CREATE INDEX idx_ccc_timestamp ON constitutional_cognitive_context(timestamp);
CREATE INDEX idx_ccc_afr_imperative ON constitutional_cognitive_context(afr_adjustment_imperative);
CREATE INDEX idx_amendments_status ON constitutional_amendments(status);
CREATE INDEX idx_amendments_ccc_id ON constitutional_amendments(ccc_id);
