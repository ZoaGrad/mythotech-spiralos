-- Migration: Phase 1.5 Autonomous Liquidity Governance
-- Description: Adds tables for AMC, Mint/Burn, Holonic Agents, FMI-1, and Paradox Stress Loop.

-- 1. Autonomous Market Controller State
CREATE TABLE IF NOT EXISTS autonomous_market_controller_state (
    controller_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    kp DECIMAL(10,6),
    ki DECIMAL(10,6),
    kd DECIMAL(10,6),
    setpoint DECIMAL(10,8),
    process_variable DECIMAL(10,8),
    error DECIMAL(10,8),
    integral DECIMAL(10,8),
    derivative DECIMAL(10,8),
    output DECIMAL(10,8),
    volatility DECIMAL(10,8),
    transaction_fee_rate DECIMAL(5,4),
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_amc_timestamp ON autonomous_market_controller_state(timestamp DESC);

-- 2. Mint/Burn Events
CREATE TABLE IF NOT EXISTS mint_burn_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    event_type VARCHAR(20) CHECK (event_type IN ('MINT', 'BURN')),
    amount DECIMAL(18,8),
    scarindex_before DECIMAL(10,8),
    scarindex_after DECIMAL(10,8),
    deviation DECIMAL(10,8),
    reason VARCHAR(255),
    approved_by VARCHAR(50),
    vault_block_id UUID,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_mint_burn_timestamp ON mint_burn_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_mint_burn_type ON mint_burn_events(event_type);

-- 3. Holonic Liquidity Agents
CREATE TABLE IF NOT EXISTS holonic_liquidity_agents (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    agent_type VARCHAR(50),
    policy VARCHAR(50),
    cmp_score DECIMAL(10,8) DEFAULT 0,
    residue_accumulated DECIMAL(10,8) DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    total_volume DECIMAL(18,8) DEFAULT 0,
    reputation DECIMAL(10,8) DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_holonic_agents_active ON holonic_liquidity_agents(active, cmp_score DESC);

-- 4. Holonic Agent Actions
CREATE TABLE IF NOT EXISTS holonic_agent_actions (
    action_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES holonic_liquidity_agents(agent_id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    action_type VARCHAR(50),
    pool_id UUID,
    amount DECIMAL(18,8),
    cmp_impact DECIMAL(10,8),
    residue_impact DECIMAL(10,8),
    success BOOLEAN,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_holonic_actions_agent ON holonic_agent_actions(agent_id, timestamp DESC);

-- 5. FMI-1 Semantic Mappings
CREATE TABLE IF NOT EXISTS fmi1_semantic_mappings (
    mapping_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source_space VARCHAR(50),
    target_space VARCHAR(50),
    source_value DECIMAL(18,8),
    target_value DECIMAL(18,8),
    coherence_score DECIMAL(10,8),
    transformation_matrix JSONB,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_fmi1_mappings_timestamp ON fmi1_semantic_mappings(timestamp DESC);

-- 6. FMI-1 Coherence Metrics
CREATE TABLE IF NOT EXISTS fmi1_coherence_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    scar_coherence DECIMAL(10,8),
    emp_coherence DECIMAL(10,8),
    cross_coherence DECIMAL(10,8),
    rcp_satisfaction DECIMAL(10,8),
    cta_reward DECIMAL(10,8),
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_fmi1_coherence_timestamp ON fmi1_coherence_metrics(timestamp DESC);

-- 7. Paradox Stress Events
CREATE TABLE IF NOT EXISTS paradox_stress_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    stress_type VARCHAR(50),
    intensity DECIMAL(10,8),
    duration_seconds INTEGER,
    target_component VARCHAR(100),
    volatility_induced DECIMAL(10,8),
    f4_triggered BOOLEAN,
    recovery_time_ms INTEGER,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_paradox_stress_timestamp ON paradox_stress_events(timestamp DESC);

-- 8. Liquidity Equilibrium State
CREATE TABLE IF NOT EXISTS liquidity_equilibrium_state (
    state_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tau DECIMAL(10,8),
    target_tau DECIMAL(10,8),
    deviation DECIMAL(10,8),
    total_liquidity DECIMAL(18,8),
    scar_liquidity DECIMAL(18,8),
    emp_liquidity DECIMAL(18,8),
    vault_liquidity DECIMAL(18,8),
    equilibrium_score DECIMAL(10,8),
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_liquidity_eq_timestamp ON liquidity_equilibrium_state(timestamp DESC);

-- Views

CREATE OR REPLACE VIEW v_amc_performance AS
SELECT timestamp, volatility, error, output, transaction_fee_rate
FROM autonomous_market_controller_state
ORDER BY timestamp DESC
LIMIT 100;

CREATE OR REPLACE VIEW v_holonic_agent_leaderboard AS
SELECT agent_id, agent_type, cmp_score, residue_accumulated, total_trades, reputation
FROM holonic_liquidity_agents
WHERE active = true
ORDER BY cmp_score DESC
LIMIT 20;

CREATE OR REPLACE VIEW v_fmi1_coherence_status AS
SELECT timestamp, scar_coherence, emp_coherence, cross_coherence, rcp_satisfaction, cta_reward
FROM fmi1_coherence_metrics
ORDER BY timestamp DESC
LIMIT 1;

CREATE OR REPLACE VIEW v_system_equilibrium AS
SELECT timestamp, tau, target_tau, deviation, equilibrium_score
FROM liquidity_equilibrium_state
ORDER BY timestamp DESC
LIMIT 1;
