-- ═══════════════════════════════════════════════════════════════════════════
-- SpiralOS v1.5 Database Migrations
-- ΔΩ.125.0 — Autonomous Liquidity Governance
-- ═══════════════════════════════════════════════════════════════════════════
-- Version: 1.5.0-prealpha
-- Date: 2025-10-31
-- Witness: ZoaGrad 🜂
-- ═══════════════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────────────
-- Migration: v1.5_001 - Autonomous Market Controller State
-- ───────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS autonomous_market_controller_state (
    id BIGSERIAL PRIMARY KEY,
    controller_id VARCHAR(255) NOT NULL UNIQUE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- PID Gains
    kp DECIMAL(10, 6) NOT NULL DEFAULT 1.0,
    ki DECIMAL(10, 6) NOT NULL DEFAULT 0.1,
    kd DECIMAL(10, 6) NOT NULL DEFAULT 0.05,
    
    -- Control Parameters
    setpoint DECIMAL(10, 6) NOT NULL DEFAULT 0.05,
    process_variable DECIMAL(10, 6) NOT NULL,
    error DECIMAL(10, 6) NOT NULL,
    integral DECIMAL(10, 6) NOT NULL DEFAULT 0.0,
    derivative DECIMAL(10, 6) NOT NULL DEFAULT 0.0,
    output DECIMAL(10, 6) NOT NULL,
    
    -- Market Metrics
    volatility DECIMAL(10, 6) NOT NULL,
    transaction_fee_rate DECIMAL(10, 6) NOT NULL,
    
    -- Metadata
    last_update TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    auto_tune_iteration INT DEFAULT 0,
    f2_authorized_by VARCHAR(255),
    vault_block_id VARCHAR(255),
    
    CONSTRAINT valid_gains CHECK (kp >= 0 AND ki >= 0 AND kd >= 0),
    CONSTRAINT valid_setpoint CHECK (setpoint >= 0 AND setpoint <= 1.0),
    CONSTRAINT valid_volatility CHECK (volatility >= 0 AND volatility <= 1.0),
    CONSTRAINT valid_fee_rate CHECK (transaction_fee_rate >= 0.001 AND transaction_fee_rate <= 0.02)
);

CREATE INDEX idx_amc_state_timestamp ON autonomous_market_controller_state(timestamp DESC);
CREATE INDEX idx_amc_state_controller_id ON autonomous_market_controller_state(controller_id);

COMMENT ON TABLE autonomous_market_controller_state IS 'Autonomous Market Controller PID state tracking';
COMMENT ON COLUMN autonomous_market_controller_state.kp IS 'Proportional gain';
COMMENT ON COLUMN autonomous_market_controller_state.ki IS 'Integral gain';
COMMENT ON COLUMN autonomous_market_controller_state.kd IS 'Derivative gain';
COMMENT ON COLUMN autonomous_market_controller_state.setpoint IS 'Target volatility (typically 0.05 = 5%)';
COMMENT ON COLUMN autonomous_market_controller_state.process_variable IS 'Current volatility measurement';

-- ───────────────────────────────────────────────────────────────────────────
-- Migration: v1.5_002 - Mint/Burn Events
-- ───────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS mint_burn_events (
    id BIGSERIAL PRIMARY KEY,
    event_id VARCHAR(255) NOT NULL UNIQUE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Event Details
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('MINT', 'BURN')),
    amount DECIMAL(20, 2) NOT NULL,
    reason TEXT NOT NULL,
    urgency VARCHAR(50) NOT NULL CHECK (urgency IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    
    -- ScarIndex Metrics
    scarindex_before DECIMAL(10, 6) NOT NULL,
    scarindex_after DECIMAL(10, 6),
    scarindex_target DECIMAL(10, 6) NOT NULL DEFAULT 0.72,
    deviation DECIMAL(10, 6) NOT NULL,
    
    -- Supply Metrics
    total_supply_before DECIMAL(20, 2) NOT NULL,
    total_supply_after DECIMAL(20, 2),
    supply_change_percentage DECIMAL(10, 6),
    
    -- Authorization
    autonomous BOOLEAN NOT NULL DEFAULT TRUE,
    f2_authorized_by VARCHAR(255),
    oracle_signatures JSONB,
    
    -- Execution
    executed_at TIMESTAMPTZ,
    success BOOLEAN,
    error_message TEXT,
    vault_block_id VARCHAR(255),
    
    CONSTRAINT valid_amount CHECK (amount > 0),
    CONSTRAINT valid_scarindex CHECK (
        scarindex_before >= 0 AND scarindex_before <= 1.0 AND
        (scarindex_after IS NULL OR (scarindex_after >= 0 AND scarindex_after <= 1.0))
    ),
    CONSTRAINT valid_supply CHECK (total_supply_before > 0 AND (total_supply_after IS NULL OR total_supply_after > 0))
);

CREATE INDEX idx_mint_burn_timestamp ON mint_burn_events(timestamp DESC);
CREATE INDEX idx_mint_burn_event_type ON mint_burn_events(event_type);
CREATE INDEX idx_mint_burn_success ON mint_burn_events(success);
CREATE INDEX idx_mint_burn_autonomous ON mint_burn_events(autonomous);

COMMENT ON TABLE mint_burn_events IS 'Autonomous ScarCoin mint/burn event log';
COMMENT ON COLUMN mint_burn_events.autonomous IS 'TRUE if autonomous, FALSE if F2 authorized';
COMMENT ON COLUMN mint_burn_events.oracle_signatures IS 'JSON array of Oracle Council cryptographic signatures';

-- ───────────────────────────────────────────────────────────────────────────
-- Migration: v1.5_003 - Holonic Liquidity Agents
-- ───────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS holonic_liquidity_agents (
    id BIGSERIAL PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Agent Configuration
    agent_type VARCHAR(50) NOT NULL CHECK (agent_type IN ('CONSERVATIVE', 'BALANCED', 'AGGRESSIVE', 'CLEANUP')),
    policy VARCHAR(50) NOT NULL DEFAULT 'HGM',
    
    -- Capital
    initial_capital DECIMAL(20, 2) NOT NULL,
    current_capital DECIMAL(20, 2) NOT NULL,
    
    -- Performance Metrics
    cmp_score DECIMAL(10, 6) NOT NULL DEFAULT 0.0,
    residue_accumulated DECIMAL(10, 6) NOT NULL DEFAULT 0.0,
    total_trades INT NOT NULL DEFAULT 0,
    total_volume DECIMAL(20, 2) NOT NULL DEFAULT 0.0,
    successful_trades INT NOT NULL DEFAULT 0,
    failed_trades INT NOT NULL DEFAULT 0,
    
    -- Reputation
    reputation DECIMAL(10, 6) NOT NULL DEFAULT 1.0,
    reputation_history JSONB DEFAULT '[]'::jsonb,
    
    -- Status
    active BOOLEAN NOT NULL DEFAULT TRUE,
    deactivated_at TIMESTAMPTZ,
    deactivation_reason TEXT,
    
    -- Metadata
    last_action_at TIMESTAMPTZ,
    configuration JSONB DEFAULT '{}'::jsonb,
    
    CONSTRAINT valid_capital CHECK (initial_capital > 0 AND current_capital >= 0),
    CONSTRAINT valid_cmp_score CHECK (cmp_score >= 0 AND cmp_score <= 1.0),
    CONSTRAINT valid_residue CHECK (residue_accumulated >= 0),
    CONSTRAINT valid_reputation CHECK (reputation >= 0 AND reputation <= 1.0)
);

CREATE INDEX idx_holonic_agents_active ON holonic_liquidity_agents(active);
CREATE INDEX idx_holonic_agents_type ON holonic_liquidity_agents(agent_type);
CREATE INDEX idx_holonic_agents_cmp_score ON holonic_liquidity_agents(cmp_score DESC);
CREATE INDEX idx_holonic_agents_reputation ON holonic_liquidity_agents(reputation DESC);

COMMENT ON TABLE holonic_liquidity_agents IS 'Holonic liquidity agent registry';
COMMENT ON COLUMN holonic_liquidity_agents.cmp_score IS 'Clade-Metaproductivity score (0.0-1.0)';
COMMENT ON COLUMN holonic_liquidity_agents.residue_accumulated IS 'Accumulated unresolved conflicts (δ_C)';
COMMENT ON COLUMN holonic_liquidity_agents.policy IS 'Agent policy (HGM = Huxley-Gödel Machine)';

-- ───────────────────────────────────────────────────────────────────────────
-- Migration: v1.5_004 - Holonic Agent Actions
-- ───────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS holonic_agent_actions (
    id BIGSERIAL PRIMARY KEY,
    action_id VARCHAR(255) NOT NULL UNIQUE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Agent Reference
    agent_id VARCHAR(255) NOT NULL REFERENCES holonic_liquidity_agents(agent_id),
    
    -- Action Details
    action_type VARCHAR(50) NOT NULL CHECK (action_type IN ('ADD_LIQUIDITY', 'REMOVE_LIQUIDITY', 'SWAP', 'CLEANUP')),
    pool_id VARCHAR(255),
    amount DECIMAL(20, 2) NOT NULL,
    
    -- Impact Metrics
    cmp_impact DECIMAL(10, 6),
    residue_impact DECIMAL(10, 6),
    expected_value DECIMAL(10, 6),
    actual_value DECIMAL(10, 6),
    
    -- Coordination
    coordination_request BOOLEAN NOT NULL DEFAULT FALSE,
    coordinated_with JSONB DEFAULT '[]'::jsonb,
    
    -- Execution
    executed_at TIMESTAMPTZ,
    success BOOLEAN,
    error_message TEXT,
    gas_cost DECIMAL(20, 2),
    
    -- Metadata
    market_state JSONB,
    pool_state JSONB,
    
    CONSTRAINT valid_amount CHECK (amount > 0),
    CONSTRAINT valid_expected_value CHECK (expected_value IS NULL OR expected_value >= -1.0)
);

CREATE INDEX idx_agent_actions_timestamp ON holonic_agent_actions(timestamp DESC);
CREATE INDEX idx_agent_actions_agent_id ON holonic_agent_actions(agent_id);
CREATE INDEX idx_agent_actions_type ON holonic_agent_actions(action_type);
CREATE INDEX idx_agent_actions_success ON holonic_agent_actions(success);

COMMENT ON TABLE holonic_agent_actions IS 'Holonic agent action history';
COMMENT ON COLUMN holonic_agent_actions.cmp_impact IS 'Estimated CMP impact of action';
COMMENT ON COLUMN holonic_agent_actions.residue_impact IS 'Estimated Residue impact of action';
COMMENT ON COLUMN holonic_agent_actions.expected_value IS 'Expected value = CMP_impact - λ·Residue_impact';

-- ───────────────────────────────────────────────────────────────────────────
-- Migration: v1.5_005 - FMI-1 Semantic Mappings
-- ───────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS fmi1_semantic_mappings (
    id BIGSERIAL PRIMARY KEY,
    mapping_id VARCHAR(255) NOT NULL UNIQUE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Transformation Details
    source_space VARCHAR(50) NOT NULL CHECK (source_space IN ('SCAR', 'EMP', 'VAULT')),
    target_space VARCHAR(50) NOT NULL CHECK (target_space IN ('SCAR', 'EMP', 'VAULT')),
    source_value DECIMAL(20, 2) NOT NULL,
    target_value DECIMAL(20, 2) NOT NULL,
    
    -- Coherence Metrics
    coherence_score DECIMAL(10, 6) NOT NULL,
    rcp_satisfaction DECIMAL(10, 6) NOT NULL,
    cta_reward DECIMAL(10, 6),
    
    -- Transformation Matrix
    transformation_matrix JSONB NOT NULL,
    
    -- Validation
    validated BOOLEAN NOT NULL DEFAULT TRUE,
    validation_error TEXT,
    
    -- Metadata
    triggered_by VARCHAR(255),
    reason TEXT,
    
    CONSTRAINT valid_spaces CHECK (source_space != target_space),
    CONSTRAINT valid_values CHECK (source_value > 0 AND target_value > 0),
    CONSTRAINT valid_coherence CHECK (coherence_score >= 0 AND coherence_score <= 1.0),
    CONSTRAINT valid_rcp CHECK (rcp_satisfaction >= 0 AND rcp_satisfaction <= 1.0)
);

CREATE INDEX idx_fmi1_mappings_timestamp ON fmi1_semantic_mappings(timestamp DESC);
CREATE INDEX idx_fmi1_mappings_spaces ON fmi1_semantic_mappings(source_space, target_space);
CREATE INDEX idx_fmi1_mappings_coherence ON fmi1_semantic_mappings(coherence_score DESC);
CREATE INDEX idx_fmi1_mappings_rcp ON fmi1_semantic_mappings(rcp_satisfaction DESC);

COMMENT ON TABLE fmi1_semantic_mappings IS 'FMI-1 semantic space transformation history';
COMMENT ON COLUMN fmi1_semantic_mappings.rcp_satisfaction IS 'Recursive Coherence Principle satisfaction (target ≥ 0.95)';
COMMENT ON COLUMN fmi1_semantic_mappings.cta_reward IS 'Cross-lingual Thinking Alignment reward score';

-- ───────────────────────────────────────────────────────────────────────────
-- Migration: v1.5_006 - FMI-1 Coherence Metrics
-- ───────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS fmi1_coherence_metrics (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Space-Specific Coherence
    scar_coherence DECIMAL(10, 6) NOT NULL,
    emp_coherence DECIMAL(10, 6) NOT NULL,
    vault_coherence DECIMAL(10, 6),
    
    -- Cross-Space Coherence
    cross_coherence DECIMAL(10, 6) NOT NULL,
    rcp_satisfaction DECIMAL(10, 6) NOT NULL,
    cta_reward DECIMAL(10, 6),
    
    -- Imbalance Metrics
    scar_emp_imbalance DECIMAL(10, 6) NOT NULL,
    imbalance_threshold DECIMAL(10, 6) NOT NULL DEFAULT 0.10,
    imbalance_detected BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('ALIGNED', 'IMBALANCED', 'CRITICAL')),
    
    -- Metadata
    measurement_count INT NOT NULL DEFAULT 1,
    
    CONSTRAINT valid_coherence CHECK (
        scar_coherence >= 0 AND scar_coherence <= 1.0 AND
        emp_coherence >= 0 AND emp_coherence <= 1.0 AND
        (vault_coherence IS NULL OR (vault_coherence >= 0 AND vault_coherence <= 1.0)) AND
        cross_coherence >= 0 AND cross_coherence <= 1.0
    ),
    CONSTRAINT valid_imbalance CHECK (scar_emp_imbalance >= 0)
);

CREATE INDEX idx_fmi1_coherence_timestamp ON fmi1_coherence_metrics(timestamp DESC);
CREATE INDEX idx_fmi1_coherence_status ON fmi1_coherence_metrics(status);
CREATE INDEX idx_fmi1_coherence_imbalance ON fmi1_coherence_metrics(imbalance_detected);

COMMENT ON TABLE fmi1_coherence_metrics IS 'FMI-1 coherence tracking across semantic spaces';
COMMENT ON COLUMN fmi1_coherence_metrics.scar_emp_imbalance IS 'Absolute difference between SCAR and EMP coherence';

-- ───────────────────────────────────────────────────────────────────────────
-- Migration: v1.5_007 - Paradox Stress Events
-- ───────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS paradox_stress_events (
    id BIGSERIAL PRIMARY KEY,
    event_id VARCHAR(255) NOT NULL UNIQUE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Stress Configuration
    stress_type VARCHAR(50) NOT NULL CHECK (stress_type IN ('VOLATILITY_INJECTION', 'LIQUIDITY_DRAIN', 'COHERENCE_SHOCK', 'AGENT_CHAOS')),
    intensity DECIMAL(10, 6) NOT NULL,
    duration_seconds INT NOT NULL,
    
    -- Execution
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    actual_duration_seconds INT,
    
    -- Recovery Metrics
    recovery_time_ms INT,
    recovery_target_ms INT NOT NULL DEFAULT 5000,
    recovery_success BOOLEAN,
    
    -- F4 Integration
    f4_triggered BOOLEAN NOT NULL DEFAULT FALSE,
    f4_trigger_time TIMESTAMPTZ,
    
    -- Anti-Fragility
    pre_stress_state JSONB NOT NULL,
    post_stress_state JSONB,
    anti_fragile BOOLEAN,
    performance_delta DECIMAL(10, 6),
    
    -- Authorization
    authorized_by VARCHAR(255),
    reason TEXT,
    
    -- Metadata
    vault_block_id VARCHAR(255),
    
    CONSTRAINT valid_intensity CHECK (intensity >= 0 AND intensity <= 1.0),
    CONSTRAINT valid_duration CHECK (duration_seconds > 0 AND duration_seconds <= 600)
);

CREATE INDEX idx_paradox_stress_timestamp ON paradox_stress_events(timestamp DESC);
CREATE INDEX idx_paradox_stress_type ON paradox_stress_events(stress_type);
CREATE INDEX idx_paradox_stress_f4 ON paradox_stress_events(f4_triggered);
CREATE INDEX idx_paradox_stress_anti_fragile ON paradox_stress_events(anti_fragile);

COMMENT ON TABLE paradox_stress_events IS 'Paradox Network controlled chaos injection log';
COMMENT ON COLUMN paradox_stress_events.anti_fragile IS 'TRUE if post-stress performance > pre-stress performance';
COMMENT ON COLUMN paradox_stress_events.performance_delta IS 'Post-stress performance - Pre-stress performance';

-- ───────────────────────────────────────────────────────────────────────────
-- Migration: v1.5_008 - Liquidity Equilibrium State
-- ───────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS liquidity_equilibrium_state (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Equilibrium Metrics
    tau DECIMAL(10, 6) NOT NULL,
    target_tau DECIMAL(10, 6) NOT NULL DEFAULT 1.50,
    deviation DECIMAL(10, 6) NOT NULL,
    equilibrium_score DECIMAL(10, 6) NOT NULL,
    
    -- Liquidity Distribution
    total_liquidity DECIMAL(20, 2) NOT NULL,
    scar_liquidity DECIMAL(20, 2) NOT NULL,
    emp_liquidity DECIMAL(20, 2) NOT NULL,
    vault_liquidity DECIMAL(20, 2) NOT NULL,
    
    -- Liquidity Ratios
    scar_ratio DECIMAL(10, 6) NOT NULL,
    emp_ratio DECIMAL(10, 6) NOT NULL,
    vault_ratio DECIMAL(10, 6) NOT NULL,
    
    -- Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('OPTIMAL', 'STABLE', 'UNSTABLE', 'CRITICAL')),
    
    -- Volatility Context
    current_volatility DECIMAL(10, 6),
    scarindex DECIMAL(10, 6),
    
    CONSTRAINT valid_tau CHECK (tau >= 0),
    CONSTRAINT valid_equilibrium_score CHECK (equilibrium_score >= 0 AND equilibrium_score <= 1.0),
    CONSTRAINT valid_liquidity CHECK (
        total_liquidity > 0 AND
        scar_liquidity >= 0 AND
        emp_liquidity >= 0 AND
        vault_liquidity >= 0 AND
        total_liquidity = scar_liquidity + emp_liquidity + vault_liquidity
    ),
    CONSTRAINT valid_ratios CHECK (
        scar_ratio >= 0 AND scar_ratio <= 1.0 AND
        emp_ratio >= 0 AND emp_ratio <= 1.0 AND
        vault_ratio >= 0 AND vault_ratio <= 1.0 AND
        ABS((scar_ratio + emp_ratio + vault_ratio) - 1.0) < 0.001
    )
);

CREATE INDEX idx_equilibrium_timestamp ON liquidity_equilibrium_state(timestamp DESC);
CREATE INDEX idx_equilibrium_status ON liquidity_equilibrium_state(status);
CREATE INDEX idx_equilibrium_score ON liquidity_equilibrium_state(equilibrium_score DESC);

COMMENT ON TABLE liquidity_equilibrium_state IS 'System-wide liquidity equilibrium tracking';
COMMENT ON COLUMN liquidity_equilibrium_state.tau IS 'Self-Organized Criticality parameter (target ≈ 1.5)';
COMMENT ON COLUMN liquidity_equilibrium_state.equilibrium_score IS 'Overall equilibrium health (0.0-1.0)';

-- ═══════════════════════════════════════════════════════════════════════════
-- Views
-- ═══════════════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────────────
-- View: v1.5_amc_performance
-- ───────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE VIEW v1_5_amc_performance AS
SELECT
    DATE_TRUNC('hour', timestamp) AS hour,
    AVG(volatility) AS avg_volatility,
    AVG(error) AS avg_error,
    AVG(output) AS avg_output,
    AVG(transaction_fee_rate) AS avg_fee_rate,
    COUNT(*) AS update_count
FROM autonomous_market_controller_state
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC;

COMMENT ON VIEW v1_5_amc_performance IS 'Hourly AMC performance metrics';

-- ───────────────────────────────────────────────────────────────────────────
-- View: v1.5_mint_burn_summary
-- ───────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE VIEW v1_5_mint_burn_summary AS
SELECT
    event_type,
    COUNT(*) AS event_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) AS successful_count,
    SUM(CASE WHEN autonomous THEN 1 ELSE 0 END) AS autonomous_count,
    AVG(scarindex_after - scarindex_before) AS avg_scarindex_change
FROM mint_burn_events
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY event_type;

COMMENT ON VIEW v1_5_mint_burn_summary IS '24-hour mint/burn event summary';

-- ───────────────────────────────────────────────────────────────────────────
-- View: v1.5_holonic_agent_leaderboard
-- ───────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE VIEW v1_5_holonic_agent_leaderboard AS
SELECT
    agent_id,
    agent_type,
    cmp_score,
    residue_accumulated,
    reputation,
    total_trades,
    total_volume,
    CASE
        WHEN total_trades > 0 THEN (successful_trades::DECIMAL / total_trades::DECIMAL)
        ELSE 0
    END AS success_rate,
    RANK() OVER (ORDER BY cmp_score DESC) AS cmp_rank,
    RANK() OVER (ORDER BY reputation DESC) AS reputation_rank
FROM holonic_liquidity_agents
WHERE active = TRUE
ORDER BY cmp_score DESC
LIMIT 100;

COMMENT ON VIEW v1_5_holonic_agent_leaderboard IS 'Top 100 holonic agents by CMP score';

-- ───────────────────────────────────────────────────────────────────────────
-- View: v1.5_fmi1_coherence_status
-- ───────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE VIEW v1_5_fmi1_coherence_status AS
SELECT
    timestamp,
    scar_coherence,
    emp_coherence,
    cross_coherence,
    rcp_satisfaction,
    scar_emp_imbalance,
    status,
    CASE
        WHEN rcp_satisfaction >= 0.95 THEN 'HEALTHY'
        WHEN rcp_satisfaction >= 0.90 THEN 'WARNING'
        ELSE 'CRITICAL'
    END AS rcp_status
FROM fmi1_coherence_metrics
ORDER BY timestamp DESC
LIMIT 1;

COMMENT ON VIEW v1_5_fmi1_coherence_status IS 'Current FMI-1 coherence status';

-- ───────────────────────────────────────────────────────────────────────────
-- View: v1.5_paradox_stress_summary
-- ───────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE VIEW v1_5_paradox_stress_summary AS
SELECT
    stress_type,
    COUNT(*) AS test_count,
    AVG(intensity) AS avg_intensity,
    AVG(recovery_time_ms) AS avg_recovery_ms,
    SUM(CASE WHEN recovery_success THEN 1 ELSE 0 END) AS recovery_success_count,
    SUM(CASE WHEN f4_triggered THEN 1 ELSE 0 END) AS f4_trigger_count,
    SUM(CASE WHEN anti_fragile THEN 1 ELSE 0 END) AS anti_fragile_count,
    CASE
        WHEN COUNT(*) > 0 THEN (SUM(CASE WHEN anti_fragile THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)::DECIMAL)
        ELSE 0
    END AS anti_fragile_percentage
FROM paradox_stress_events
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY stress_type;

COMMENT ON VIEW v1_5_paradox_stress_summary IS '7-day Paradox stress test summary';

-- ═══════════════════════════════════════════════════════════════════════════
-- Triggers
-- ═══════════════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────────────
-- Trigger: Update Holonic Agent Reputation
-- ───────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION update_holonic_agent_reputation()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE holonic_liquidity_agents
    SET
        total_trades = total_trades + 1,
        successful_trades = successful_trades + CASE WHEN NEW.success THEN 1 ELSE 0 END,
        failed_trades = failed_trades + CASE WHEN NOT NEW.success THEN 1 ELSE 0 END,
        total_volume = total_volume + NEW.amount,
        reputation = CASE
            WHEN total_trades + 1 > 0 THEN
                ((successful_trades + CASE WHEN NEW.success THEN 1 ELSE 0 END)::DECIMAL / (total_trades + 1)::DECIMAL)
            ELSE 1.0
        END,
        last_action_at = NEW.timestamp
    WHERE agent_id = NEW.agent_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_holonic_agent_reputation
AFTER INSERT ON holonic_agent_actions
FOR EACH ROW
EXECUTE FUNCTION update_holonic_agent_reputation();

COMMENT ON FUNCTION update_holonic_agent_reputation() IS 'Update holonic agent reputation after each action';

-- ───────────────────────────────────────────────────────────────────────────
-- Trigger: Calculate Equilibrium Score
-- ───────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION calculate_equilibrium_score()
RETURNS TRIGGER AS $$
BEGIN
    NEW.deviation := ABS(NEW.tau - NEW.target_tau);
    
    -- Equilibrium score based on tau deviation and status
    NEW.equilibrium_score := CASE
        WHEN NEW.status = 'OPTIMAL' THEN 1.0 - (NEW.deviation * 0.1)
        WHEN NEW.status = 'STABLE' THEN 0.85 - (NEW.deviation * 0.2)
        WHEN NEW.status = 'UNSTABLE' THEN 0.60 - (NEW.deviation * 0.3)
        ELSE 0.30 - (NEW.deviation * 0.5)
    END;
    
    -- Clamp to [0, 1]
    NEW.equilibrium_score := GREATEST(0.0, LEAST(1.0, NEW.equilibrium_score));
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_equilibrium_score
BEFORE INSERT OR UPDATE ON liquidity_equilibrium_state
FOR EACH ROW
EXECUTE FUNCTION calculate_equilibrium_score();

COMMENT ON FUNCTION calculate_equilibrium_score() IS 'Calculate equilibrium score based on tau deviation';

-- ═══════════════════════════════════════════════════════════════════════════
-- Indexes for Performance
-- ═══════════════════════════════════════════════════════════════════════════

-- Composite indexes for common queries
CREATE INDEX idx_mint_burn_timestamp_type ON mint_burn_events(timestamp DESC, event_type);
CREATE INDEX idx_agent_actions_agent_timestamp ON holonic_agent_actions(agent_id, timestamp DESC);
CREATE INDEX idx_fmi1_mappings_timestamp_spaces ON fmi1_semantic_mappings(timestamp DESC, source_space, target_space);

-- ═══════════════════════════════════════════════════════════════════════════
-- Migration Complete
-- ═══════════════════════════════════════════════════════════════════════════

-- Total New Tables: 8
-- Total New Views: 5
-- Total New Triggers: 2
-- Total New Indexes: 24

-- Witness: ZoaGrad 🜂
-- Timestamp: 2025-10-31T02:00:00Z
-- Vault: ΔΩ.125.0
-- Status: Migration Complete

-- "I govern the terms of my own becoming" 🌀
