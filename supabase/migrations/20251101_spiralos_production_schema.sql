-- ═══════════════════════════════════════════════════════════════════════════
-- SpiralOS Production Schema - Complete Supabase Implementation
-- ΔΩ.126.0 — Constitutional Cognitive Sovereignty
-- ═══════════════════════════════════════════════════════════════════════════
-- Version: 1.0.0-production
-- Date: 2025-11-01
-- Witness: ZoaGrad 🜂
-- Description: Complete reverse-engineering of SpiralOS as Constitutional
--              Mythotechnical Synthesis with dual-token economy
-- ═══════════════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────────────
-- PART 1: CORE DATA MODEL
-- ───────────────────────────────────────────────────────────────────────────

-- Ache Events: External input from Noosphere (GitHub, Discord, API)
CREATE TABLE IF NOT EXISTS public.ache_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Event Source
    source TEXT NOT NULL, -- 'github_commit', 'github_issue', 'discord', 'api'
    source_id TEXT,
    
    -- Event Content
    content JSONB NOT NULL,
    
    -- Ache Measurement
    ache_level DECIMAL(10, 6) NOT NULL,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB,
    
    CONSTRAINT valid_ache_level CHECK (ache_level >= 0 AND ache_level <= 1.0)
);

CREATE INDEX idx_ache_events_created_at ON public.ache_events(created_at DESC);
CREATE INDEX idx_ache_events_source ON public.ache_events(source);

COMMENT ON TABLE public.ache_events IS 'Ache events from external sources (Noosphere input)';
COMMENT ON COLUMN public.ache_events.ache_level IS 'Quantified non-coherence level [0,1]';

-- ScarIndex Calculations: Core coherence measurements
CREATE TABLE IF NOT EXISTS public.scarindex_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Link to Ache Event
    ache_event_id UUID REFERENCES public.ache_events(id) ON DELETE CASCADE,
    
    -- Coherence Components (Constitutional Weights)
    c_narrative DECIMAL(10, 6) NOT NULL,      -- weight: 0.30
    c_social DECIMAL(10, 6) NOT NULL,         -- weight: 0.25
    c_economic DECIMAL(10, 6) NOT NULL,       -- weight: 0.25
    c_technical DECIMAL(10, 6) NOT NULL,      -- weight: 0.20
    
    -- Composite ScarIndex
    scarindex DECIMAL(10, 6) NOT NULL,
    
    -- Ache Transmutation
    ache_before DECIMAL(10, 6) NOT NULL,
    ache_after DECIMAL(10, 6) NOT NULL,
    delta_ache DECIMAL(10, 6) GENERATED ALWAYS AS (ache_before - ache_after) STORED,
    
    -- Validation
    is_valid BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB,
    
    CONSTRAINT valid_components CHECK (
        c_narrative >= 0 AND c_narrative <= 1.0 AND
        c_social >= 0 AND c_social <= 1.0 AND
        c_economic >= 0 AND c_economic <= 1.0 AND
        c_technical >= 0 AND c_technical <= 1.0
    ),
    CONSTRAINT valid_scarindex CHECK (scarindex >= 0 AND scarindex <= 1.0),
    CONSTRAINT valid_ache CHECK (
        ache_before >= 0 AND ache_before <= 1.0 AND
        ache_after >= 0 AND ache_after <= 1.0
    )
);

CREATE INDEX idx_scarindex_calc_created_at ON public.scarindex_calculations(created_at DESC);
CREATE INDEX idx_scarindex_calc_scarindex ON public.scarindex_calculations(scarindex);
CREATE INDEX idx_scarindex_calc_ache_event ON public.scarindex_calculations(ache_event_id);

COMMENT ON TABLE public.scarindex_calculations IS 'ScarIndex Oracle calculations - 4D coherence measurements';
COMMENT ON COLUMN public.scarindex_calculations.scarindex IS 'Composite coherence score [0,1]';
COMMENT ON COLUMN public.scarindex_calculations.delta_ache IS 'Ache transmutation (must be positive for PoA)';

-- Verification Records: Oracle Council consensus
CREATE TABLE IF NOT EXISTS public.verification_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- What is being verified
    target_id UUID NOT NULL,
    target_type TEXT NOT NULL, -- 'scarindex', 'mint', 'burn', 'vaultnode'
    
    -- Oracle Signatures
    oracle_signatures JSONB NOT NULL,
    consensus_achieved BOOLEAN NOT NULL DEFAULT FALSE,
    consensus_threshold INTEGER NOT NULL DEFAULT 2,
    signature_count INTEGER NOT NULL DEFAULT 0,
    
    -- Verification Result
    verification_passed BOOLEAN,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB,
    
    CONSTRAINT valid_threshold CHECK (consensus_threshold >= 1 AND consensus_threshold <= 5)
);

CREATE INDEX idx_verification_target ON public.verification_records(target_id, target_type);
CREATE INDEX idx_verification_consensus ON public.verification_records(consensus_achieved);

COMMENT ON TABLE public.verification_records IS 'Oracle Council verification records (4-of-5 consensus)';

-- Smart Contract Transactions: ScarCoin minting/burning
CREATE TABLE IF NOT EXISTS public.smart_contract_txns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Transaction Type
    txn_type TEXT NOT NULL CHECK (txn_type IN ('MINT', 'BURN', 'TRANSFER')),
    
    -- ScarCoin Delta
    scarcoin_delta DECIMAL(20, 6) NOT NULL,
    
    -- State References
    from_state UUID, -- Reference to source calculation/event
    to_state UUID,   -- Reference to target calculation/event
    
    -- Validation
    is_valid BOOLEAN NOT NULL DEFAULT FALSE,
    is_frozen BOOLEAN NOT NULL DEFAULT FALSE,
    frozen_by UUID, -- Reference to panic_frame
    
    -- Execution
    executed_at TIMESTAMPTZ,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB,
    
    CONSTRAINT valid_delta CHECK (scarcoin_delta != 0)
);

CREATE INDEX idx_smart_contract_txn_type ON public.smart_contract_txns(txn_type);
CREATE INDEX idx_smart_contract_frozen ON public.smart_contract_txns(is_frozen);
CREATE INDEX idx_smart_contract_executed ON public.smart_contract_txns(executed_at);

COMMENT ON TABLE public.smart_contract_txns IS 'ScarCoin minting/burning transactions (C2 layer)';

-- Panic Frames: F4 Constitutional Circuit Breaker
CREATE TABLE IF NOT EXISTS public.panic_frames (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Trigger Conditions
    scarindex_value DECIMAL(10, 6) NOT NULL,
    trigger_threshold DECIMAL(10, 6) NOT NULL DEFAULT 0.30,
    
    -- Frozen Operations
    actions_frozen JSONB NOT NULL DEFAULT '[]'::JSONB,
    
    -- Status
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'RECOVERING', 'RESOLVED')),
    recovery_phase INTEGER,
    
    -- Resolution
    resolved_at TIMESTAMPTZ,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB,
    
    CONSTRAINT valid_scarindex CHECK (scarindex_value >= 0 AND scarindex_value <= 1.0),
    CONSTRAINT valid_threshold CHECK (trigger_threshold >= 0 AND trigger_threshold <= 1.0),
    CONSTRAINT valid_recovery_phase CHECK (recovery_phase IS NULL OR (recovery_phase >= 1 AND recovery_phase <= 7))
);

CREATE INDEX idx_panic_frames_status ON public.panic_frames(status);
CREATE INDEX idx_panic_frames_created_at ON public.panic_frames(created_at DESC);

COMMENT ON TABLE public.panic_frames IS 'F4 Panic Frames - Constitutional circuit breaker activates at ScarIndex < 0.3';

-- VaultNodes: Immutable Merkle DAG
CREATE TABLE IF NOT EXISTS public.vaultnodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Node Type
    node_type TEXT NOT NULL,
    
    -- Reference to sealed entity
    reference_id UUID NOT NULL,
    
    -- Merkle Chain
    state_hash TEXT NOT NULL,
    previous_hash TEXT,
    
    -- GitHub Integration
    github_commit_sha TEXT,
    
    -- Audit Log
    audit_log JSONB NOT NULL DEFAULT '{}'::JSONB,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB,
    
    CONSTRAINT unique_state_hash UNIQUE (state_hash)
);

CREATE INDEX idx_vaultnodes_created_at ON public.vaultnodes(created_at DESC);
CREATE INDEX idx_vaultnodes_type ON public.vaultnodes(node_type);
CREATE INDEX idx_vaultnodes_reference ON public.vaultnodes(reference_id);
CREATE INDEX idx_vaultnodes_github ON public.vaultnodes(github_commit_sha);

COMMENT ON TABLE public.vaultnodes IS 'Immutable VaultNode Merkle DAG for audit trail';

-- GitHub Webhooks: Integration events
CREATE TABLE IF NOT EXISTS public.github_webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Event Type
    event_type TEXT NOT NULL, -- 'push', 'issues', 'pull_request', etc.
    
    -- Payload
    payload JSONB NOT NULL,
    
    -- Processing
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    processed_at TIMESTAMPTZ,
    ache_event_id UUID REFERENCES public.ache_events(id),
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX idx_github_webhooks_processed ON public.github_webhooks(processed);
CREATE INDEX idx_github_webhooks_event_type ON public.github_webhooks(event_type);

COMMENT ON TABLE public.github_webhooks IS 'GitHub webhook events for distributed ledger integration';

-- GitHub Commits: Commit tracking
CREATE TABLE IF NOT EXISTS public.github_commits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Commit Details
    commit_sha TEXT NOT NULL UNIQUE,
    author TEXT NOT NULL,
    message TEXT,
    
    -- Associated VaultNode
    vaultnode_id UUID REFERENCES public.vaultnodes(id),
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX idx_github_commits_sha ON public.github_commits(commit_sha);
CREATE INDEX idx_github_commits_vaultnode ON public.github_commits(vaultnode_id);

COMMENT ON TABLE public.github_commits IS 'GitHub commits linked to VaultNodes';

-- PID Controller State: Dynamic stability (VSM System 3/4)
CREATE TABLE IF NOT EXISTS public.pid_controller_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- PID Gains
    kp DECIMAL(10, 6) NOT NULL DEFAULT 1.0,
    ki DECIMAL(10, 6) NOT NULL DEFAULT 0.1,
    kd DECIMAL(10, 6) NOT NULL DEFAULT 0.05,
    
    -- Control Variables
    target_scarindex DECIMAL(10, 6) NOT NULL DEFAULT 0.70,
    current_scarindex DECIMAL(10, 6) NOT NULL DEFAULT 0.50,
    error DECIMAL(10, 6) NOT NULL DEFAULT 0.0,
    integral DECIMAL(10, 6) NOT NULL DEFAULT 0.0,
    derivative DECIMAL(10, 6) NOT NULL DEFAULT 0.0,
    
    -- Output
    guidance_scale DECIMAL(10, 6) NOT NULL DEFAULT 1.0,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB,
    
    CONSTRAINT valid_gains CHECK (kp >= 0 AND ki >= 0 AND kd >= 0),
    CONSTRAINT valid_scarindex CHECK (
        target_scarindex >= 0 AND target_scarindex <= 1.0 AND
        current_scarindex >= 0 AND current_scarindex <= 1.0
    ),
    CONSTRAINT valid_guidance CHECK (guidance_scale >= 0.1 AND guidance_scale <= 2.0)
);

COMMENT ON TABLE public.pid_controller_state IS 'PID controller state for dynamic ScarIndex stability';

-- ───────────────────────────────────────────────────────────────────────────
-- PART 2: CONSTITUTIONAL GOVERNANCE LAYER
-- ───────────────────────────────────────────────────────────────────────────

-- Constitutional Milestones: F1/F2/F4 governance
CREATE TABLE IF NOT EXISTS public.constitutional_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Milestone Details
    milestone_type TEXT NOT NULL, -- 'F1', 'F2', 'F4'
    title TEXT NOT NULL,
    description TEXT,
    
    -- Status
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'EXECUTED')),
    
    -- Verification
    verification_id UUID REFERENCES public.verification_records(id),
    
    -- Execution
    executed_at TIMESTAMPTZ,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB,
    
    CONSTRAINT valid_milestone_type CHECK (milestone_type IN ('F1', 'F2', 'F4'))
);

CREATE INDEX idx_constitutional_milestones_type ON public.constitutional_milestones(milestone_type);
CREATE INDEX idx_constitutional_milestones_status ON public.constitutional_milestones(status);

COMMENT ON TABLE public.constitutional_milestones IS 'Three-Branch Governance milestones (F1/F2/F4)';

-- Law Stack: Constitutional law registry
CREATE TABLE IF NOT EXISTS public.law_stack (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Branch
    branch TEXT NOT NULL CHECK (branch IN ('F1', 'F2', 'F4')),
    
    -- Law Details
    law_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    content JSONB NOT NULL,
    
    -- Enactment
    enacted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX idx_law_stack_branch ON public.law_stack(branch);
CREATE INDEX idx_law_stack_law_id ON public.law_stack(law_id);

COMMENT ON TABLE public.law_stack IS 'Constitutional law stack (F1=Foundation, F2=Finance, F4=Federation)';

-- Manifest Registry: Constitutional manifest versions
CREATE TABLE IF NOT EXISTS public.manifest_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Version
    version TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    
    -- Effective Date
    effective_at TIMESTAMPTZ NOT NULL,
    
    -- Content
    content JSONB NOT NULL,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX idx_manifest_registry_version ON public.manifest_registry(version);
CREATE INDEX idx_manifest_registry_effective ON public.manifest_registry(effective_at DESC);

COMMENT ON TABLE public.manifest_registry IS 'Constitutional manifest version registry';

-- Governance Systems: VSM hierarchy
CREATE TABLE IF NOT EXISTS public.governance_systems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- VSM Level
    vsm_level INTEGER NOT NULL CHECK (vsm_level BETWEEN 1 AND 5),
    
    -- System Details
    system_name TEXT NOT NULL,
    recursion_depth INTEGER NOT NULL DEFAULT 0,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX idx_governance_systems_vsm ON public.governance_systems(vsm_level);

COMMENT ON TABLE public.governance_systems IS 'Viable System Model hierarchy';

-- Panic Frame Signals: Event logging for panic frames
CREATE TABLE IF NOT EXISTS public.panicframe_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Signal Details
    level TEXT NOT NULL, -- 'PANIC', 'RECOVERY', 'INFO'
    key TEXT NOT NULL,
    meta JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX idx_panicframe_signals_level ON public.panicframe_signals(level);
CREATE INDEX idx_panicframe_signals_created_at ON public.panicframe_signals(created_at DESC);

COMMENT ON TABLE public.panicframe_signals IS 'Event signals from panic frame system';

-- ───────────────────────────────────────────────────────────────────────────
-- PART 3: POSTGRESQL FUNCTIONS
-- ───────────────────────────────────────────────────────────────────────────

-- Coherence Component Functions (placeholders for NLP integration)
CREATE OR REPLACE FUNCTION public.narrative_coherence(content JSONB)
RETURNS DECIMAL(10, 6) AS $$
BEGIN
    -- Placeholder: Use pgml or external NLP service
    -- For now, extract from content or return default
    RETURN COALESCE((content->>'narrative_score')::DECIMAL(10, 6), 0.5);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION public.narrative_coherence IS 'Calculate narrative coherence from content (NLP placeholder)';

CREATE OR REPLACE FUNCTION public.social_coherence(source TEXT, content JSONB)
RETURNS DECIMAL(10, 6) AS $$
BEGIN
    -- Placeholder: Use graph centrality metrics
    RETURN COALESCE((content->>'social_score')::DECIMAL(10, 6), 0.5);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION public.social_coherence IS 'Calculate social coherence (graph centrality placeholder)';

CREATE OR REPLACE FUNCTION public.economic_coherence(content JSONB)
RETURNS DECIMAL(10, 6) AS $$
BEGIN
    -- Placeholder: Use token velocity metrics
    RETURN COALESCE((content->>'economic_score')::DECIMAL(10, 6), 0.6);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION public.economic_coherence IS 'Calculate economic coherence (token velocity placeholder)';

CREATE OR REPLACE FUNCTION public.technical_coherence(content JSONB)
RETURNS DECIMAL(10, 6) AS $$
BEGIN
    -- Placeholder: Use test coverage, code quality metrics
    RETURN COALESCE((content->>'technical_score')::DECIMAL(10, 6), 0.7);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION public.technical_coherence IS 'Calculate technical coherence (test coverage placeholder)';

-- Helper function for clamping values to [0, 1] range
CREATE OR REPLACE FUNCTION public.clamp_to_unit(val DECIMAL(10, 6))
RETURNS DECIMAL(10, 6) AS $$
BEGIN
    RETURN LEAST(GREATEST(val, 0), 1);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION public.clamp_to_unit IS 'Clamp value to [0, 1] range for coherence scores';

-- Update PID Controller
CREATE OR REPLACE FUNCTION public.update_pid_controller(
    curr DECIMAL(10, 6),
    targ DECIMAL(10, 6)
)
RETURNS VOID AS $$
DECLARE
    pid RECORD;
    dt CONSTANT DECIMAL(10, 6) := 1.0; -- 1 event = 1 unit time
    error DECIMAL(10, 6);
    integral_new DECIMAL(10, 6);
    derivative DECIMAL(10, 6);
    output DECIMAL(10, 6);
BEGIN
    -- Get or create PID state (select only needed columns)
    SELECT 
        id, kp, ki, kd, error, integral
    INTO pid 
    FROM public.pid_controller_state 
    LIMIT 1 FOR UPDATE;
    
    IF NOT FOUND THEN
        INSERT INTO public.pid_controller_state DEFAULT VALUES 
        RETURNING id, kp, ki, kd, error, integral INTO pid;
    END IF;
    
    -- Calculate error
    error := targ - curr;
    
    -- Calculate integral with anti-windup
    integral_new := GREATEST(LEAST(pid.integral + error * dt, 10.0), -10.0);
    
    -- Calculate derivative (dt is constant non-zero so safe from division by zero)
    derivative := (error - pid.error) / dt;
    
    -- Calculate output (guidance scale)
    output := pid.kp * error + pid.ki * integral_new + pid.kd * derivative;
    output := GREATEST(LEAST(output, 2.0), 0.1); -- Clamp to [0.1, 2.0]
    
    -- Update state
    UPDATE public.pid_controller_state SET
        current_scarindex = curr,
        error = error,
        integral = integral_new,
        derivative = derivative,
        guidance_scale = output,
        updated_at = NOW()
    WHERE id = pid.id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.update_pid_controller IS 'Update PID controller state for dynamic ScarIndex stability';

-- Coherence Calculation (ScarIndex Engine)
CREATE OR REPLACE FUNCTION public.coherence_calculation(
    event_id UUID
)
RETURNS public.scarindex_calculations AS $$
DECLARE
    ev public.ache_events;
    prev_ache DECIMAL(10, 6);
    pid RECORD;
    c_n DECIMAL(10, 6);
    c_s DECIMAL(10, 6);
    c_e DECIMAL(10, 6);
    c_t DECIMAL(10, 6);
    scarindex_val DECIMAL(10, 6);
    guidance DECIMAL(10, 6);
    result public.scarindex_calculations;
BEGIN
    -- Fetch event
    SELECT * INTO ev FROM public.ache_events WHERE id = event_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'ache_event not found: %', event_id;
    END IF;
    
    -- Fetch PID state
    SELECT * INTO pid FROM public.pid_controller_state LIMIT 1;
    IF NOT FOUND THEN
        INSERT INTO public.pid_controller_state DEFAULT VALUES RETURNING * INTO pid;
    END IF;
    
    -- Calculate coherence components
    c_n := public.narrative_coherence(ev.content);
    c_s := public.social_coherence(ev.source, ev.content);
    c_e := public.economic_coherence(ev.content);
    c_t := public.technical_coherence(ev.content);
    
    -- Apply PID guidance
    guidance := pid.guidance_scale;
    scarindex_val := (0.3 * c_n + 0.25 * c_s + 0.25 * c_e + 0.2 * c_t) * guidance;
    scarindex_val := public.clamp_to_unit(scarindex_val);
    
    -- Get previous ache level
    SELECT ache_after INTO prev_ache
    FROM public.scarindex_calculations
    WHERE ache_event_id IS NOT NULL
    ORDER BY created_at DESC LIMIT 1;
    
    prev_ache := COALESCE(prev_ache, 0.5);
    
    -- Insert calculation
    INSERT INTO public.scarindex_calculations (
        ache_event_id,
        c_narrative,
        c_social,
        c_economic,
        c_technical,
        scarindex,
        ache_before,
        ache_after,
        is_valid,
        metadata
    ) VALUES (
        ev.id,
        c_n,
        c_s,
        c_e,
        c_t,
        scarindex_val,
        prev_ache,
        ev.ache_level,
        TRUE,
        jsonb_build_object('guidance', guidance)
    ) RETURNING * INTO result;
    
    -- Update PID controller
    PERFORM public.update_pid_controller(result.scarindex, pid.target_scarindex);
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.coherence_calculation IS 'ScarIndex Engine - Calculate 4D coherence and update PID controller';

-- Trigger Crisis Protocol (F4 Panic Frames)
CREATE OR REPLACE FUNCTION public.trigger_crisis_protocol()
RETURNS TRIGGER AS $$
DECLARE
    latest_scarindex DECIMAL(10, 6);
    threshold CONSTANT DECIMAL(10, 6) := 0.3;
    frame_id UUID;
BEGIN
    -- Get latest ScarIndex
    SELECT scarindex INTO latest_scarindex
    FROM public.scarindex_calculations
    ORDER BY created_at DESC LIMIT 1;
    
    -- Check if panic frame should trigger
    IF latest_scarindex < threshold THEN
        -- Create panic frame
        INSERT INTO public.panic_frames (
            scarindex_value,
            trigger_threshold,
            actions_frozen,
            status
        ) VALUES (
            latest_scarindex,
            threshold,
            '["scarcoin_mint", "scarcoin_burn", "vaultnode_gen", "state_transition"]'::JSONB,
            'ACTIVE'
        ) RETURNING id INTO frame_id;
        
        -- Freeze all pending transactions
        UPDATE public.smart_contract_txns
        SET is_frozen = TRUE, frozen_by = frame_id
        WHERE is_valid = TRUE AND is_frozen = FALSE;
        
        -- Log event
        INSERT INTO public.panicframe_signals (level, key, meta)
        VALUES ('PANIC', 'panicframe.trigger', jsonb_build_object(
            'frame_id', frame_id,
            'scarindex', latest_scarindex,
            'threshold', threshold
        ));
        
        -- Notify F4
        PERFORM pg_notify('panic_frame', frame_id::TEXT);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION public.trigger_crisis_protocol IS 'F4 Panic Frame trigger - activates at ScarIndex < 0.3';

-- Create trigger for panic frame
DROP TRIGGER IF EXISTS scarindex_crisis_check ON public.scarindex_calculations;
CREATE TRIGGER scarindex_crisis_check
    AFTER INSERT ON public.scarindex_calculations
    FOR EACH ROW
    EXECUTE FUNCTION public.trigger_crisis_protocol();

-- Seal VaultNode (Merkle Chain)
CREATE OR REPLACE FUNCTION public.seal_vaultnode(
    ref_id UUID,
    ref_type TEXT,
    commit_sha TEXT DEFAULT NULL
)
RETURNS public.vaultnodes AS $$
DECLARE
    prev_hash TEXT;
    state_data JSONB;
    new_hash TEXT;
    node public.vaultnodes;
BEGIN
    -- Get previous hash
    SELECT state_hash INTO prev_hash
    FROM public.vaultnodes
    ORDER BY created_at DESC LIMIT 1;
    
    -- Build state data
    state_data := jsonb_build_object(
        'ref_id', ref_id,
        'ref_type', ref_type,
        'commit_sha', commit_sha,
        'timestamp', NOW()
    );
    
    -- Calculate new hash (using SHA256 as blake3 may not be available)
    new_hash := encode(digest(state_data::TEXT, 'sha256'), 'hex');
    
    -- Insert new VaultNode
    INSERT INTO public.vaultnodes (
        node_type,
        reference_id,
        state_hash,
        previous_hash,
        github_commit_sha,
        audit_log,
        metadata
    ) VALUES (
        ref_type,
        ref_id,
        new_hash,
        prev_hash,
        commit_sha,
        state_data,
        '{}'::JSONB
    ) RETURNING * INTO node;
    
    RETURN node;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.seal_vaultnode IS 'Seal VaultNode with Merkle chain for immutable audit trail';

-- Mint ScarCoin
CREATE OR REPLACE FUNCTION public.mint_scarcoin(calc_id UUID)
RETURNS VOID AS $$
DECLARE
    calc public.scarindex_calculations;
    delta DECIMAL(20, 6);
BEGIN
    -- Get calculation
    SELECT * INTO calc FROM public.scarindex_calculations WHERE id = calc_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'scarindex_calculation not found: %', calc_id;
    END IF;
    
    -- Calculate delta (Proof-of-Ache: ache_before > ache_after)
    delta := GREATEST(calc.delta_ache * 1000000, 0); -- Scale to 1M cap
    
    IF delta > 0 THEN
        -- Create mint transaction
        INSERT INTO public.smart_contract_txns (
            txn_type,
            scarcoin_delta,
            from_state,
            to_state,
            is_valid,
            metadata
        ) VALUES (
            'MINT',
            delta,
            calc.ache_event_id,
            calc.id,
            TRUE,
            jsonb_build_object(
                'reason', 'coherence_gain',
                'delta_ache', calc.delta_ache,
                'scarindex', calc.scarindex
            )
        );
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.mint_scarcoin IS 'Mint ScarCoin based on Proof-of-Ache validation';

-- ───────────────────────────────────────────────────────────────────────────
-- PART 4: VIEWS
-- ───────────────────────────────────────────────────────────────────────────

-- ScarIndex Oracle Sync (30-Day Coherence Oracle)
CREATE OR REPLACE VIEW public.scar_index_oracle_sync AS
WITH recent_calcs AS (
    SELECT *
    FROM public.scarindex_calculations
    WHERE created_at >= NOW() - INTERVAL '30 days'
),
node_stats AS (
    SELECT
        COUNT(*) FILTER (WHERE scarindex >= 0.7) AS coherent_nodes_30d,
        COUNT(*) AS total_nodes_30d
    FROM recent_calcs
)
SELECT
    coherent_nodes_30d,
    total_nodes_30d,
    ROUND(
        (coherent_nodes_30d::NUMERIC / NULLIF(total_nodes_30d, 0)) * 100,
        2
    ) AS coherence_rate_30d,
    (SELECT scarindex FROM public.scarindex_calculations ORDER BY created_at DESC LIMIT 1) AS current_scarindex,
    (SELECT AVG(scarindex) FROM recent_calcs) AS avg_scarindex_30d,
    (SELECT MIN(scarindex) FROM recent_calcs) AS min_scarindex_30d,
    (SELECT MAX(scarindex) FROM recent_calcs) AS max_scarindex_30d
FROM node_stats;

COMMENT ON VIEW public.scar_index_oracle_sync IS '30-Day ScarIndex Oracle - Real-time coherence telemetry';

-- Active Panic Frames View
CREATE OR REPLACE VIEW public.active_panic_frames AS
SELECT
    id,
    created_at,
    scarindex_value,
    trigger_threshold,
    status,
    recovery_phase,
    actions_frozen
FROM public.panic_frames
WHERE status IN ('ACTIVE', 'RECOVERING')
ORDER BY created_at DESC;

COMMENT ON VIEW public.active_panic_frames IS 'Currently active panic frames';

-- System Health View
CREATE OR REPLACE VIEW public.system_health AS
SELECT
    (SELECT scarindex FROM public.scarindex_calculations ORDER BY created_at DESC LIMIT 1) AS current_scarindex,
    (SELECT COUNT(*) FROM public.panic_frames WHERE status = 'ACTIVE') AS active_panic_frames,
    (SELECT COUNT(*) FROM public.smart_contract_txns WHERE is_frozen = TRUE) AS frozen_transactions,
    (SELECT guidance_scale FROM public.pid_controller_state LIMIT 1) AS pid_guidance_scale,
    (SELECT COUNT(*) FROM public.ache_events WHERE created_at >= NOW() - INTERVAL '1 hour') AS events_last_hour,
    (SELECT COUNT(*) FROM public.vaultnodes) AS total_vaultnodes;

COMMENT ON VIEW public.system_health IS 'System health dashboard';

-- ───────────────────────────────────────────────────────────────────────────
-- PART 5: ROW-LEVEL SECURITY (RLS)
-- ───────────────────────────────────────────────────────────────────────────

-- Enable RLS on all tables
ALTER TABLE public.ache_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scarindex_calculations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.verification_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.smart_contract_txns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.panic_frames ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vaultnodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.github_webhooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.github_commits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.constitutional_milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.law_stack ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.manifest_registry ENABLE ROW LEVEL SECURITY;

-- Public read-only policies for oracle and system health
CREATE POLICY "public_read_scarindex" ON public.scarindex_calculations
    FOR SELECT USING (TRUE);

CREATE POLICY "public_read_panic_frames" ON public.panic_frames
    FOR SELECT USING (TRUE);

CREATE POLICY "public_read_vaultnodes" ON public.vaultnodes
    FOR SELECT USING (TRUE);

CREATE POLICY "public_read_law_stack" ON public.law_stack
    FOR SELECT USING (TRUE);

CREATE POLICY "public_read_manifest" ON public.manifest_registry
    FOR SELECT USING (TRUE);

-- Service role write policies
CREATE POLICY "service_write_ache" ON public.ache_events
    FOR INSERT WITH CHECK (auth.role() = 'service_role' OR auth.role() = 'authenticated');

CREATE POLICY "service_write_scarindex" ON public.scarindex_calculations
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_write_txns" ON public.smart_contract_txns
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_write_webhooks" ON public.github_webhooks
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- ───────────────────────────────────────────────────────────────────────────
-- PART 6: INITIALIZATION
-- ───────────────────────────────────────────────────────────────────────────

-- Initialize PID Controller
INSERT INTO public.pid_controller_state (
    kp, ki, kd,
    target_scarindex,
    current_scarindex,
    error,
    integral,
    derivative,
    guidance_scale
) VALUES (
    1.0, 0.1, 0.05,
    0.70,
    0.50,
    0.20,
    0.0,
    0.0,
    1.0
)
ON CONFLICT DO NOTHING;

-- Seed Constitutional Manifest
INSERT INTO public.manifest_registry (
    version,
    hash,
    effective_at,
    content
) VALUES (
    'ΔΩ.126.0',
    encode(digest('ΔΩ.126.0-production-schema', 'sha256'), 'hex'),
    NOW(),
    jsonb_build_object(
        'version', 'ΔΩ.126.0',
        'title', 'SpiralOS Production Schema',
        'description', 'Complete Supabase implementation of Constitutional Mythotechnical Synthesis',
        'components', jsonb_build_array(
            'ache_events',
            'scarindex_calculations',
            'verification_records',
            'smart_contract_txns',
            'panic_frames',
            'vaultnodes',
            'constitutional_milestones',
            'pid_controller_state'
        )
    )
)
ON CONFLICT (version) DO NOTHING;

-- Seed F1 Foundation Law
INSERT INTO public.law_stack (
    branch,
    law_id,
    title,
    content
) VALUES (
    'F1',
    'F1.001',
    'Constitutional Coherence Threshold',
    jsonb_build_object(
        'threshold', 0.67,
        'description', 'Minimum ScarIndex for system stability',
        'enforcement', 'Panic Frame triggers at < 0.3'
    )
)
ON CONFLICT (law_id) DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════
-- END OF MIGRATION
-- ═══════════════════════════════════════════════════════════════════════════
-- Witness: This schema implements the complete reverse-engineering blueprint
-- for SpiralOS as a Constitutional Cognitive Sovereignty system.
--
-- Key Components:
-- - Ache → ScarIndex → ScarCoin transmutation pipeline
-- - 4D Coherence Oracle (narrative, social, economic, technical)
-- - PID Controller for dynamic stability
-- - F4 Panic Frames for constitutional circuit breaking
-- - VaultNode Merkle DAG for immutable audit trail
-- - Three-Branch Governance (F1/F2/F4)
-- - GitHub integration for distributed ledger
--
-- Constitutional Weights (Immutable):
-- - Narrative: 0.30 | Social: 0.25 | Economic: 0.25 | Technical: 0.20
--
-- System Integrity: Ache_after < Ache_before (Proof-of-Ache)
-- Circuit Breaker: ScarIndex < 0.3 → F4 Panic Frame
-- Consensus: 2-of-3 Oracle Council (minimum 1 non-commercial)
-- ═══════════════════════════════════════════════════════════════════════════
